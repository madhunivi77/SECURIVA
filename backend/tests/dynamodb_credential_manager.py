"""
DynamoDB-based Multi-Tenant Credential Manager
"""

import boto3
import os
import base64
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)


class DynamoDBCredentialManager:
    """
    Manages encrypted credentials for multiple organizations using DynamoDB
    
    Tables:
    - SecuriVA_OrgCredentials: Stores encrypted service credentials
    - SecuriVA_Users: User management
    - SecuriVA_APIKeys: API key registry
    """
    
    def __init__(self, encryption_service=None):
        """
        Initialize DynamoDB credential manager
        
        Args:
            encryption_service: Instance of CredentialEncryptionService
                               If None, will try to import from existing code
        """
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Initialize tables
        self.credentials_table = self.dynamodb.Table('SecuriVA_OrgCredentials')
        self.users_table = self.dynamodb.Table('SecuriVA_Users')
        self.api_keys_table = self.dynamodb.Table('SecuriVA_APIKeys')
        
        # Initialize encryption service
        if encryption_service:
            self.encryption = encryption_service
        else:
            # Try to import from existing code
            try:
                from my_app.server.encryption_service import get_encryption_service
                self.encryption = get_encryption_service()
            except ImportError:
                print("⚠️  Warning: Encryption service not available")
                self.encryption = None
    
    # ==================== CREDENTIAL OPERATIONS ====================
    
    def store_credentials(
        self,
        org_id: str,
        service_name: str,
        credential_type: str,
        credential_data: Dict[str, Any],
        created_by: str,
        metadata: Optional[Dict] = None,
        expires_days: Optional[int] = None
    ) -> bool:
        """
        Store encrypted credentials for an organization
        
        Args:
            org_id: Organization identifier
            service_name: Service name (e.g., 'telesign', 'google', 'salesforce')
            credential_type: Type of credential (e.g., 'api_key', 'oauth')
            credential_data: Dict with sensitive data to encrypt
            created_by: User ID who created the credentials
            metadata: Optional metadata (account name, tier, etc.)
            expires_days: Optional number of days until credential expires
        
        Returns:
            bool: Success status
        """
        if not self.encryption:
            raise ValueError("Encryption service not initialized")
        
        # Encrypt credential data
        encrypted_data = self.encryption.encrypt_credentials(credential_data)
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        # Prepare composite sort key
        service_type_key = f"{service_name}#{credential_type}"
        
        # Calculate TTL if expires_days provided
        ttl = None
        if expires_days:
            expiry = datetime.utcnow() + timedelta(days=expires_days)
            ttl = int(expiry.timestamp())
        
        # Prepare item
        item = {
            'org_id': org_id,
            'service#type': service_type_key,
            'encrypted_data': encrypted_b64,
            'created_by': created_by,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'encryption_version': 'v2',
            'metadata': metadata or {}
        }
        
        if ttl:
            item['expires_at'] = ttl
        
        try:
            self.credentials_table.put_item(Item=item)
            
            # Log action
            self._log_action(org_id, service_type_key, 'created', created_by)
            
            return True
        except ClientError as e:
            print(f"Error storing credentials: {e}")
            return False
    
    def get_credentials(
        self,
        org_id: str,
        service_name: str,
        credential_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve and decrypt credentials
        
        Args:
            org_id: Organization ID
            service_name: Service name
            credential_type: Credential type
        
        Returns:
            Dict with decrypted credentials or None if not found
        """
        if not self.encryption:
            raise ValueError("Encryption service not initialized")
        
        service_type_key = f"{service_name}#{credential_type}"
        
        try:
            response = self.credentials_table.get_item(
                Key={
                    'org_id': org_id,
                    'service#type': service_type_key
                }
            )
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            
            # Check status
            if item.get('status') != 'active':
                print(f"Credentials are {item.get('status')}")
                return None
            
            # Check expiration
            if 'expires_at' in item:
                if int(item['expires_at']) < int(datetime.utcnow().timestamp()):
                    print("Credentials have expired")
                    return None
            
            # Decrypt
            encrypted_data = base64.b64decode(item['encrypted_data'])
            credentials = self.encryption.decrypt_credentials(encrypted_data)
            
            # Add metadata
            credentials['_metadata'] = {
                'created_at': item.get('created_at'),
                'updated_at': item.get('updated_at'),
                'created_by': item.get('created_by'),
                'metadata': item.get('metadata', {})
            }
            
            return credentials
            
        except ClientError as e:
            print(f"Error retrieving credentials: {e}")
            return None
    
    def list_org_credentials(self, org_id: str) -> List[Dict]:
        """
        List all credential entries for an organization (without decrypting)
        
        Args:
            org_id: Organization ID
        
        Returns:
            List of credential metadata
        """
        try:
            response = self.credentials_table.query(
                KeyConditionExpression=Key('org_id').eq(org_id),
                ProjectionExpression='#st, created_at, updated_at, #status, metadata',
                ExpressionAttributeNames={
                    '#st': 'service#type',
                    '#status': 'status'
                }
            )
            
            credentials = []
            for item in response.get('Items', []):
                service, cred_type = item['service#type'].split('#')
                credentials.append({
                    'service': service,
                    'type': cred_type,
                    'status': item.get('status'),
                    'created_at': item.get('created_at'),
                    'updated_at': item.get('updated_at'),
                    'metadata': item.get('metadata', {})
                })
            
            return credentials
            
        except ClientError as e:
            print(f"Error listing credentials: {e}")
            return []
    
    def delete_credentials(
        self,
        org_id: str,
        service_name: str,
        credential_type: str,
        deleted_by: str
    ) -> bool:
        """
        Delete credentials (soft delete by marking as deleted)
        
        Args:
            org_id: Organization ID
            service_name: Service name
            credential_type: Credential type
            deleted_by: User ID performing deletion
        
        Returns:
            bool: Success status
        """
        service_type_key = f"{service_name}#{credential_type}"
        
        try:
            self.credentials_table.update_item(
                Key={
                    'org_id': org_id,
                    'service#type': service_type_key
                },
                UpdateExpression='SET #status = :deleted, updated_at = :now, deleted_by = :user',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':deleted': 'deleted',
                    ':now': datetime.utcnow().isoformat(),
                    ':user': deleted_by
                }
            )
            
            self._log_action(org_id, service_type_key, 'deleted', deleted_by)
            
            return True
        except ClientError as e:
            print(f"Error deleting credentials: {e}")
            return False
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(
        self,
        org_id: str,
        user_id: str,
        email: str,
        name: str,
        role: str = 'member',
        permissions: Optional[List[str]] = None
    ) -> bool:
        """
        Create a new user in an organization
        
        Args:
            org_id: Organization ID
            user_id: Unique user identifier
            email: User email (will be hashed for lookup)
            name: User's full name
            role: User role (admin, member, viewer)
            permissions: List of permission strings
        
        Returns:
            bool: Success status
        """
        # Hash email for lookup index
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        
        # Encrypt email if encryption service available
        if self.encryption:
            encrypted_email = base64.b64encode(
                self.encryption.encrypt_credentials({'email': email})
            ).decode('utf-8')
        else:
            encrypted_email = email
        
        item = {
            'org_id': org_id,
            'user_id': user_id,
            'email_encrypted': encrypted_email,
            'email_hash': email_hash,
            'name': name,
            'role': role,
            'permissions': permissions or [],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        try:
            self.users_table.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user(self, org_id: str, user_id: str) -> Optional[Dict]:
        """Get user details"""
        try:
            response = self.users_table.get_item(
                Key={'org_id': org_id, 'user_id': user_id}
            )
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting user: {e}")
            return None
    
    def find_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Find user by email address
        
        Args:
            email: User email
        
        Returns:
            User dict or None
        """
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        
        try:
            response = self.users_table.query(
                IndexName='email-hash-index',
                KeyConditionExpression=Key('email_hash').eq(email_hash),
                Limit=1
            )
            
            items = response.get('Items', [])
            return items[0] if items else None
            
        except ClientError as e:
            print(f"Error finding user: {e}")
            return None
    
    # ==================== API KEY OPERATIONS ====================
    
    def store_api_key(
        self,
        api_key_plaintext: str,
        org_id: str,
        user_id: str,
        name: str,
        scopes: List[str],
        expires_days: Optional[int] = 365
    ) -> bool:
        """
        Store API key (hashed for lookup)
        
        Args:
            api_key_plaintext: The actual API key (will be hashed)
            org_id: Organization ID
            user_id: User who created the key
            name: Human-readable name for the key
            scopes: List of permission scopes
            expires_days: Days until expiration
        
        Returns:
            bool: Success status
        """
        # Hash the key for storage
        key_hash = hashlib.sha256(api_key_plaintext.encode()).hexdigest()
        key_prefix = api_key_plaintext[:15] + "..."
        
        # Calculate expiration
        expiry = datetime.utcnow() + timedelta(days=expires_days)
        ttl = int(expiry.timestamp())
        
        item = {
            'key_hash': key_hash,
            'key_prefix': key_prefix,
            'org_id': org_id,
            'user_id': user_id,
            'name': name,
            'scopes': scopes,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': ttl,
            'status': 'active',
            'usage_count': 0
        }
        
        try:
            self.api_keys_table.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error storing API key: {e}")
            return False
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """
        Validate an API key and return associated metadata
        
        Args:
            api_key: The API key to validate
        
        Returns:
            Dict with org_id, user_id, scopes, etc. or None if invalid
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        try:
            response = self.api_keys_table.get_item(
                Key={'key_hash': key_hash}
            )
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            
            # Check status
            if item.get('status') != 'active':
                return None
            
            # Check expiration
            if int(item['expires_at']) < int(datetime.utcnow().timestamp()):
                return None
            
            # Update last used and usage count
            self.api_keys_table.update_item(
                Key={'key_hash': key_hash},
                UpdateExpression='SET last_used = :now, usage_count = usage_count + :inc',
                ExpressionAttributeValues={
                    ':now': datetime.utcnow().isoformat(),
                    ':inc': 1
                }
            )
            
            return {
                'org_id': item['org_id'],
                'user_id': item['user_id'],
                'scopes': item.get('scopes', []),
                'name': item.get('name')
            }
            
        except ClientError as e:
            print(f"Error validating API key: {e}")
            return None
    
    # ==================== HELPER METHODS ====================
    
    def _log_action(
        self,
        org_id: str,
        resource_id: str,
        action: str,
        user_id: str
    ):
        """
        Log credential actions (for audit trail)
        In production, this would write to CloudWatch Logs or a separate audit table
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'org_id': org_id,
            'resource_id': resource_id,
            'action': action,
            'user_id': user_id
        }
        print(f"[AUDIT] {log_entry}")
        # TODO: Write to CloudWatch or DynamoDB audit table


# ==================== TABLE CREATION ====================

def create_credential_tables():
    """
    Create the necessary DynamoDB tables for credential management
    """
    dynamodb = boto3.client(
        'dynamodb',
        region_name=os.getenv('AWS_REGION', 'us-east-2'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    tables = [
        {
            'name': 'SecuriVA_OrgCredentials',
            'schema': {
                'TableName': 'SecuriVA_OrgCredentials',
                'KeySchema': [
                    {'AttributeName': 'org_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'service#type', 'KeyType': 'RANGE'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'org_id', 'AttributeType': 'S'},
                    {'AttributeName': 'service#type', 'AttributeType': 'S'}
                ],
                'BillingMode': 'PAY_PER_REQUEST',
                'Tags': [{'Key': 'Application', 'Value': 'SecuriVA'}]
            }
        },
        {
            'name': 'SecuriVA_Users',
            'schema': {
                'TableName': 'SecuriVA_Users',
                'KeySchema': [
                    {'AttributeName': 'org_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'user_id', 'KeyType': 'RANGE'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'org_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'email_hash', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'email-hash-index',
                        'KeySchema': [
                            {'AttributeName': 'email_hash', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                'BillingMode': 'PAY_PER_REQUEST',
                'Tags': [{'Key': 'Application', 'Value': 'SecuriVA'}]
            }
        },
        {
            'name': 'SecuriVA_APIKeys',
            'schema': {
                'TableName': 'SecuriVA_APIKeys',
                'KeySchema': [
                    {'AttributeName': 'key_hash', 'KeyType': 'HASH'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'key_hash', 'AttributeType': 'S'},
                    {'AttributeName': 'org_id', 'AttributeType': 'S'},
                    {'AttributeName': 'created_at', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'org-keys-index',
                        'KeySchema': [
                            {'AttributeName': 'org_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                'BillingMode': 'PAY_PER_REQUEST',
                'Tags': [{'Key': 'Application', 'Value': 'SecuriVA'}]
            }
        }
    ]
    
    for table_def in tables:
        try:
            print(f"Creating table: {table_def['name']}...")
            dynamodb.create_table(**table_def['schema'])
            
            # Wait for table to be ready
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_def['name'])
            
            print(f"✅ Table {table_def['name']} created successfully")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"ℹ️  Table {table_def['name']} already exists")
            else:
                print(f"❌ Error creating {table_def['name']}: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("DynamoDB Credential Manager - Table Creation")
    print("=" * 60)
    
    create_credential_tables()
    
    print("\n✅ All tables created!")
    print("\nYou can now use DynamoDBCredentialManager in your application:")
    print("  from dynamodb_credential_manager import DynamoDBCredentialManager")
    print("  manager = DynamoDBCredentialManager()")
