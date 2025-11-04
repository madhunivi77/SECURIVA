"""
Transaction logging for Telesign API calls
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Path to log file
LOG_FILE = Path(__file__).parent / "telesign_transactions.json"


def log_transaction(
    transaction_type: str,
    phone_number: str,
    status_code: int,
    reference_id: str = None,
    message: str = None,
    response_data: dict = None,
    error: str = None
) -> None:
    """
    Log a Telesign transaction to local file
    
    Args:
        transaction_type: Type of transaction (SMS, WhatsApp, PhoneID, etc.)
        phone_number: Target phone number
        status_code: HTTP status code
        reference_id: Telesign reference ID
        message: Message content (optional)
        response_data: Full response data
        error: Error message if any
    """
    # Create log entry
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "transaction_type": transaction_type,
        "phone_number": phone_number,
        "status_code": status_code,
        "reference_id": reference_id,
        "message": message,
        "error": error,
        "response": response_data,
        "success": status_code == 200
    }
    
    # Read existing logs
    logs = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    
    # Append new log
    logs.append(log_entry)
    
    # Keep only last 1000 transactions (optional)
    logs = logs[-1000:]
    
    # Write back to file
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"[LOG] {transaction_type} to {phone_number}: Status {status_code}")


def get_recent_transactions(limit: int = 50) -> List[Dict]:
    """
    Get recent transactions from log
    
    Args:
        limit: Maximum number of transactions to return
    
    Returns:
        List of transaction dictionaries
    """
    if not LOG_FILE.exists():
        return []
    
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
        return logs[-limit:]
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def get_transactions_by_phone(phone_number: str) -> List[Dict]:
    """
    Get all transactions for a specific phone number
    
    Args:
        phone_number: Phone number to search for
    
    Returns:
        List of transactions for that phone number
    """
    if not LOG_FILE.exists():
        return []
    
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
        return [log for log in logs if log['phone_number'] == phone_number]
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def get_failed_transactions() -> List[Dict]:
    """
    Get all failed transactions
    
    Returns:
        List of failed transactions
    """
    if not LOG_FILE.exists():
        return []
    
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
        return [log for log in logs if not log['success']]
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def get_transaction_summary() -> Dict:
    """
    Get summary statistics of all transactions
    
    Returns:
        Dictionary with summary stats
    """
    if not LOG_FILE.exists():
        return {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "by_type": {}
        }
    
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
        
        total = len(logs)
        successful = sum(1 for log in logs if log['success'])
        failed = total - successful
        
        # Count by type
        by_type = {}
        for log in logs:
            tx_type = log['transaction_type']
            by_type[tx_type] = by_type.get(tx_type, 0) + 1
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "by_type": by_type,
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "N/A"
        }
    except (json.JSONDecodeError, FileNotFoundError):
        return {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "by_type": {}
        }


def clear_logs() -> None:
    """Clear all transaction logs"""
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    print("Transaction logs cleared")