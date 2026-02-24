"""
Telesign Usage Monitoring Script with Cloud Database Support

Run this script to get real-time usage statistics:
    python -m my_app.server.scripts.monitor_telesign
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from my_app.server.telesign_logger import get_telesign_logger

def main():
    logger = get_telesign_logger()
    
    print("=" * 60)
    print("TELESIGN API USAGE SUMMARY")
    print("=" * 60)
    
    # Check if DynamoDB is enabled
    dynamodb_enabled = os.getenv("TELESIGN_USE_DYNAMODB", "false").lower() == "true"
    
    if dynamodb_enabled:
        print("📊 Data Source: DynamoDB (Cloud)")
        if logger.dynamodb and logger.dynamodb.enabled:
            print("✅ DynamoDB connection: Active")
        else:
            print("⚠️ DynamoDB connection: Failed (using local fallback)")
    else:
        print("📁 Data Source: Local files only")
    
    print()
    
    # Get usage summary
    summary = logger.get_usage_summary(days=7)
    
    print(f"Total API Calls: {summary['total_api_calls']}")
    print(f"Total Estimated Cost: ${summary['total_cost']:.2f}")
    
    if 'successful_calls' in summary:
        print(f"Successful Calls: {summary['successful_calls']}")
        print(f"Failed Calls: {summary['failed_calls']}")
        success_rate = (summary['successful_calls'] / summary['total_api_calls'] * 100) if summary['total_api_calls'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"\nCalls by Type:")
    for api_type, count in summary['calls_by_type'].items():
        print(f"  - {api_type}: {count} calls")
    
    print(f"\nLast Updated: {summary['last_updated']}")
    print(f"Data Source: {summary.get('data_source', 'unknown')}")
    print("=" * 60)
    
    # Get recent calls if DynamoDB is enabled
    if dynamodb_enabled and logger.dynamodb and logger.dynamodb.enabled:
        print("\n📋 Recent API Calls (Last 10):")
        print("-" * 60)
        recent_calls = logger.get_recent_calls(limit=10)
        
        for i, call in enumerate(recent_calls, 1):
            status_icon = "✅" if call.get('success') else "❌"
            print(f"{i}. {status_icon} {call.get('method', 'N/A')} - {call.get('api_type', 'N/A')}")
            print(f"   Time: {call.get('timestamp', 'N/A')}")
            print(f"   Status: {call.get('status_code', 'N/A')}")
            if not call.get('success'):
                print(f"   Error: {call.get('error_message', 'N/A')}")
            print()
    
    # Export logs
    print("Exporting logs...")
    export_file = logger.export_logs_to_json()
    print(f"✅ Logs exported to: {export_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()