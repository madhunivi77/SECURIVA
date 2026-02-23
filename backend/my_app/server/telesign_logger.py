"""
Telesign API Usage Logging and Token Management with Cloud Database Support

This module provides:
1. Comprehensive logging for all Telesign API calls
2. Token/credential usage tracking
3. API quota monitoring
4. Cost tracking per API call
5. Error logging and alerting
6. **DynamoDB integration for cloud storage**
"""

import os
import json
import logging
import boto3
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from logging.handlers import RotatingFileHandler
from dataclasses import dataclass, asdict
from enum import Enum
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal import Decimal


class TelesignAPIType(Enum):
    """Types of Telesign API calls"""
    SMS = "sms"
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    VERIFY = "verify"
    PHONEID = "phoneid"
    SCORE = "score"
    STATUS = "status"


@dataclass
class TelesignAPICall:
    """Data class for tracking API calls"""
    timestamp: str
    api_type: str
    method: str
    phone_number: str
    user_id: Optional[str]
    reference_id: Optional[str]
    status_code: int
    success: bool
    error_message: Optional[str]
    cost: Optional[float]
    customer_id: str
    request_payload: Optional[Dict]
    response_payload: Optional[Dict]
    duration_ms: Optional[float]


class DynamoDBStorage:
    """
    DynamoDB storage backend for Telesign logs
    
    Table Structure:
    - Table Name: TelesignLogs
    - Partition Key: log_type (STRING) - "api_call", "error", "quota", "metadata"
    - Sort Key: timestamp (STRING) - ISO8601 timestamp
    - TTL: expiration_time (NUMBER) - Unix timestamp for auto-deletion
    """
    
    def __init__(self, table_name: str = "TelesignLogs", region: str = "us-east-2"):
        """
        Initialize DynamoDB storage
        
        Args:
            table_name: DynamoDB table name
            region: AWS region
        """
        self.table_name = table_name
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = None
        self.enabled = os.getenv("TELESIGN_USE_DYNAMODB", "false").lower() == "true"
        
        if self.enabled:
            try:
                self.table = self.dynamodb.Table(table_name)
                # Verify table exists
                self.table.load()
                print(f"✅ Connected to DynamoDB table: {table_name}")
            except ClientError as e:
                print(f"⚠️ DynamoDB table not found: {e}. Will use local storage only.")
                self.enabled = False
    
    def save_api_call(self, api_call: TelesignAPICall):
        """Save API call log to DynamoDB"""
        if not self.enabled:
            return
        
        try:
            # Convert float to Decimal for DynamoDB
            item = self._prepare_item(api_call)
            item['log_type'] = 'api_call'
            
            # Add TTL (30 days retention)
            retention_days = int(os.getenv("TELESIGN_LOG_RETENTION_DAYS", "30"))
            expiration_time = int((datetime.now(timezone.utc) + timedelta(days=retention_days)).timestamp())
            item['expiration_time'] = expiration_time
            
            self.table.put_item(Item=item)
            
        except Exception as e:
            print(f"❌ Failed to save to DynamoDB: {e}")
    
    def save_error(self, error_data: Dict):
        """Save error log to DynamoDB"""
        if not self.enabled:
            return
        
        try:
            item = {
                'log_type': 'error',
                'timestamp': error_data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                'api_type': error_data.get('api_type', 'unknown'),
                'method': error_data.get('method', 'unknown'),
                'status_code': error_data.get('status_code', 0),
                'error': error_data.get('error', ''),
                'reference_id': error_data.get('reference_id', '')
            }
            
            # Add TTL
            retention_days = int(os.getenv("TELESIGN_LOG_RETENTION_DAYS", "30"))
            expiration_time = int((datetime.now(timezone.utc) + timedelta(days=retention_days)).timestamp())
            item['expiration_time'] = expiration_time
            
            self.table.put_item(Item=item)
            
        except Exception as e:
            print(f"❌ Failed to save error to DynamoDB: {e}")
    
    def save_metadata(self, metadata: Dict):
        """Save token metadata to DynamoDB"""
        if not self.enabled:
            return
        
        try:
            item = {
                'log_type': 'metadata',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_api_calls': metadata.get('total_api_calls', 0),
                'api_calls_by_type': json.dumps(metadata.get('api_calls_by_type', {})),
                'total_cost': Decimal(str(metadata.get('total_cost', 0.0))),
                'last_updated': metadata.get('last_updated', ''),
                'credentials': json.dumps(metadata.get('credentials', {}))
            }
            
            self.table.put_item(Item=item)
            
        except Exception as e:
            print(f"❌ Failed to save metadata to DynamoDB: {e}")
    
    def get_recent_api_calls(self, limit: int = 100, api_type: str = None) -> List[Dict]:
        """
        Retrieve recent API calls from DynamoDB
        
        Args:
            limit: Maximum number of records to retrieve
            api_type: Filter by API type (optional)
        
        Returns:
            List of API call records
        """
        if not self.enabled:
            return []
        
        try:
            # Query by log_type
            response = self.table.query(
                KeyConditionExpression=Key('log_type').eq('api_call'),
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            items = response.get('Items', [])
            
            # Filter by api_type if specified
            if api_type:
                items = [item for item in items if item.get('api_type') == api_type]
            
            return items
            
        except Exception as e:
            print(f"❌ Failed to query DynamoDB: {e}")
            return []
    
    def get_usage_statistics(self, days: int = 7) -> Dict:
        """
        Calculate usage statistics from DynamoDB
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Usage statistics dictionary
        """
        if not self.enabled:
            return {}
        
        try:
            # Calculate cutoff timestamp
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            cutoff_iso = cutoff.isoformat()
            
            # Query API calls
            response = self.table.query(
                KeyConditionExpression=Key('log_type').eq('api_call') & Key('timestamp').gte(cutoff_iso),
                ScanIndexForward=False
            )
            
            items = response.get('Items', [])
            
            # Calculate statistics
            total_calls = len(items)
            calls_by_type = {}
            total_cost = 0.0
            successful_calls = 0
            failed_calls = 0
            
            for item in items:
                # Count by type
                api_type = item.get('api_type', 'unknown')
                calls_by_type[api_type] = calls_by_type.get(api_type, 0) + 1
                
                # Sum costs
                cost = item.get('cost')
                if cost:
                    total_cost += float(cost)
                
                # Count success/failure
                if item.get('success', False):
                    successful_calls += 1
                else:
                    failed_calls += 1
            
            return {
                "period_days": days,
                "total_api_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "calls_by_type": calls_by_type,
                "total_cost": round(total_cost, 2),
                "average_cost_per_call": round(total_cost / total_calls, 2) if total_calls > 0 else 0,
                "data_source": "dynamodb"
            }
            
        except Exception as e:
            print(f"❌ Failed to get statistics from DynamoDB: {e}")
            return {}
    
    def _prepare_item(self, api_call: TelesignAPICall) -> Dict:
        """Convert APICall dataclass to DynamoDB-compatible dict"""
        item = asdict(api_call)
        
        # Convert float to Decimal for DynamoDB
        if item.get('cost') is not None:
            item['cost'] = Decimal(str(item['cost']))
        if item.get('duration_ms') is not None:
            item['duration_ms'] = Decimal(str(item['duration_ms']))
        
        # Convert complex types to JSON strings
        if item.get('request_payload'):
            item['request_payload'] = json.dumps(item['request_payload'])
        if item.get('response_payload'):
            item['response_payload'] = json.dumps(item['response_payload'])
        
        return item


class TelesignLogger:
    """
    Centralized logger for Telesign API usage with DynamoDB support
    
    Features:
    - Local file logging (always enabled)
    - DynamoDB cloud storage (optional)
    - Automatic failover to local if DynamoDB unavailable
    - Token usage tracking
    """
    
    def __init__(self, log_dir: str = None, use_dynamodb: bool = None):
        """
        Initialize Telesign logger
        
        Args:
            log_dir: Directory for local log files
            use_dynamodb: Override DynamoDB usage (default: from env var)
        """
        # Setup local logging
        if log_dir is None:
            log_dir = Path(__file__).parent / "logs" / "telesign"
        else:
            log_dir = Path(log_dir)
        
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = log_dir
        
        # Initialize file loggers
        self.api_logger = self._setup_logger("telesign_api", log_dir / "api_calls.log")
        self.error_logger = self._setup_logger("telesign_errors", log_dir / "errors.log")
        self.quota_logger = self._setup_logger("telesign_quota", log_dir / "quota_usage.log")
        
        # Initialize DynamoDB storage
        if use_dynamodb is None:
            use_dynamodb = os.getenv("TELESIGN_USE_DYNAMODB", "false").lower() == "true"
        
        self.dynamodb = DynamoDBStorage() if use_dynamodb else None
        
        # Load token metadata
        self.token_metadata_file = log_dir / "token_metadata.json"
        self.token_metadata = self._load_token_metadata()
    
    def _setup_logger(self, name: str, log_file: Path) -> logging.Logger:
        """Setup a rotating file logger"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        if logger.handlers:
            return logger
        
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "data": %(message)s}'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _load_token_metadata(self) -> Dict:
        """Load token usage metadata from file or DynamoDB"""
        # Try DynamoDB first
        if self.dynamodb and self.dynamodb.enabled:
            try:
                response = self.dynamodb.table.query(
                    KeyConditionExpression=Key('log_type').eq('metadata'),
                    ScanIndexForward=False,
                    Limit=1
                )
                items = response.get('Items', [])
                if items:
                    item = items[0]
                    return {
                        "total_api_calls": item.get('total_api_calls', 0),
                        "api_calls_by_type": json.loads(item.get('api_calls_by_type', '{}')),
                        "total_cost": float(item.get('total_cost', 0.0)),
                        "last_updated": item.get('last_updated', ''),
                        "credentials": json.loads(item.get('credentials', '{}'))
                    }
            except Exception as e:
                print(f"⚠️ Failed to load metadata from DynamoDB: {e}")
        
        # Fallback to local file
        if self.token_metadata_file.exists():
            try:
                with open(self.token_metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.error_logger.error(json.dumps({
                    "action": "load_token_metadata",
                    "error": str(e)
                }))
        
        # Initialize default metadata
        return {
            "total_api_calls": 0,
            "api_calls_by_type": {},
            "total_cost": 0.0,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "credentials": {
                "customer_id": os.getenv("TELESIGN_CUSTOMER_ID", "")[:8] + "...",
                "api_key_prefix": os.getenv("TELESIGN_API_KEY", "")[:8] + "...",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def _save_token_metadata(self):
        """Save token usage metadata to file and DynamoDB"""
        try:
            self.token_metadata["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # Save to local file
            with open(self.token_metadata_file, 'w') as f:
                json.dump(self.token_metadata, f, indent=2)
            
            # Save to DynamoDB
            if self.dynamodb:
                self.dynamodb.save_metadata(self.token_metadata)
                
        except Exception as e:
            self.error_logger.error(json.dumps({
                "action": "save_token_metadata",
                "error": str(e)
            }))
    
    def log_api_call(
        self,
        api_type: TelesignAPIType,
        method: str,
        phone_number: str,
        status_code: int,
        reference_id: Optional[str] = None,
        user_id: Optional[str] = None,
        error_message: Optional[str] = None,
        cost: Optional[float] = None,
        request_payload: Optional[Dict] = None,
        response_payload: Optional[Dict] = None,
        duration_ms: Optional[float] = None
    ):
        """
        Log a Telesign API call to both local files and DynamoDB
        """
        # Create API call record
        api_call = TelesignAPICall(
            timestamp=datetime.now(timezone.utc).isoformat(),
            api_type=api_type.value,
            method=method,
            phone_number=self._sanitize_phone(phone_number),
            user_id=user_id,
            reference_id=reference_id,
            status_code=status_code,
            success=200 <= status_code < 300,
            error_message=error_message,
            cost=cost,
            customer_id=os.getenv("TELESIGN_CUSTOMER_ID", "UNKNOWN")[:8] + "...",
            request_payload=self._sanitize_payload(request_payload),
            response_payload=self._sanitize_payload(response_payload),
            duration_ms=duration_ms
        )
        
        # Log to local file
        self.api_logger.info(json.dumps(asdict(api_call)))
        
        # Log to DynamoDB
        if self.dynamodb:
            self.dynamodb.save_api_call(api_call)
        
        # Log errors separately
        if not api_call.success:
            error_data = {
                "timestamp": api_call.timestamp,
                "api_type": api_call.api_type,
                "method": api_call.method,
                "status_code": api_call.status_code,
                "error": error_message,
                "reference_id": reference_id
            }
            self.error_logger.error(json.dumps(error_data))
            
            if self.dynamodb:
                self.dynamodb.save_error(error_data)
        
        # Update token metadata
        self._update_token_metadata(api_call)
    
    def _update_token_metadata(self, api_call: TelesignAPICall):
        """Update token usage statistics"""
        self.token_metadata["total_api_calls"] += 1
        
        api_type = api_call.api_type
        if api_type not in self.token_metadata["api_calls_by_type"]:
            self.token_metadata["api_calls_by_type"][api_type] = 0
        self.token_metadata["api_calls_by_type"][api_type] += 1
        
        if api_call.cost:
            self.token_metadata["total_cost"] += api_call.cost
        
        # Save every 10 calls
        if self.token_metadata["total_api_calls"] % 10 == 0:
            self._save_token_metadata()
    
    def _sanitize_phone(self, phone_number: str) -> str:
        """Mask phone number for privacy"""
        if not phone_number:
            return "N/A"
        phone = str(phone_number)
        if len(phone) > 4:
            return f"***{phone[-4:]}"
        return "****"
    
    def _sanitize_payload(self, payload: Optional[Dict]) -> Optional[Dict]:
        """Remove sensitive data from payloads"""
        if not payload:
            return None
        
        sanitized = payload.copy()
        sensitive_keys = ['api_key', 'password', 'token', 'secret', 'auth']
        for key in sensitive_keys:
            if key in sanitized:
                sanitized[key] = "***REDACTED***"
        
        return sanitized
    
    def get_usage_summary(self, days: int = 7) -> Dict:
        """
        Get API usage summary from DynamoDB or local metadata
        
        Tries DynamoDB first, falls back to local metadata
        """
        # Try DynamoDB first
        if self.dynamodb and self.dynamodb.enabled:
            stats = self.dynamodb.get_usage_statistics(days=days)
            if stats:
                return stats
        
        # Fallback to local metadata
        return {
            "total_api_calls": self.token_metadata["total_api_calls"],
            "calls_by_type": self.token_metadata["api_calls_by_type"],
            "total_cost": self.token_metadata["total_cost"],
            "last_updated": self.token_metadata["last_updated"],
            "period_days": days,
            "data_source": "local_file"
        }
    
    def get_recent_calls(self, limit: int = 100, api_type: str = None) -> List[Dict]:
        """
        Get recent API calls from DynamoDB
        
        Args:
            limit: Maximum number of records
            api_type: Filter by API type
        
        Returns:
            List of API call records
        """
        if self.dynamodb and self.dynamodb.enabled:
            return self.dynamodb.get_recent_api_calls(limit=limit, api_type=api_type)
        return []
    
    def log_quota_warning(self, api_type: str, remaining: int, total: int):
        """Log quota warnings"""
        percentage = (remaining / total) * 100 if total > 0 else 0
        
        if percentage < 20:
            warning_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "api_type": api_type,
                "remaining": remaining,
                "total": total,
                "percentage": percentage,
                "alert": "Low quota - less than 20% remaining"
            }
            self.quota_logger.warning(json.dumps(warning_data))
    
    def export_logs_to_json(self, output_file: str = None) -> str:
        """Export all logs to JSON file"""
        if output_file is None:
            date_str = datetime.now().strftime("%Y%m%d")
            output_file = self.log_dir / f"export_{date_str}.json"
        
        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "token_metadata": self.token_metadata,
            "api_calls": [],
            "errors": [],
            "data_source": "mixed"  # local files + DynamoDB
        }
        
        # Get data from DynamoDB if available
        if self.dynamodb and self.dynamodb.enabled:
            export_data["api_calls"] = self.dynamodb.get_recent_api_calls(limit=1000)
            export_data["data_source"] = "dynamodb"
        else:
            # Read from local files
            api_log_file = self.log_dir / "api_calls.log"
            if api_log_file.exists():
                with open(api_log_file, 'r') as f:
                    for line in f:
                        try:
                            export_data["api_calls"].append(json.loads(line))
                        except:
                            pass
            
            error_log_file = self.log_dir / "errors.log"
            if error_log_file.exists():
                with open(error_log_file, 'r') as f:
                    for line in f:
                        try:
                            export_data["errors"].append(json.loads(line))
                        except:
                            pass
        
        # Write export
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return str(output_file)


# Global logger instance
_logger_instance = None

def get_telesign_logger() -> TelesignLogger:
    """Get or create global Telesign logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = TelesignLogger()
    return _logger_instance


# Estimated API costs
TELESIGN_API_COSTS = {
    TelesignAPIType.SMS: 0.05,
    TelesignAPIType.WHATSAPP: 0.01,
    TelesignAPIType.VOICE: 0.10,
    TelesignAPIType.VERIFY: 0.08,
    TelesignAPIType.PHONEID: 0.02,
    TelesignAPIType.SCORE: 0.03,
    TelesignAPIType.STATUS: 0.00,
}

def get_estimated_cost(api_type: TelesignAPIType) -> float:
    """Get estimated cost for an API call type"""
    return TELESIGN_API_COSTS.get(api_type, 0.0)