"""
DynamoDB management utility - Common operations for SecuriVA chat storage
"""

import boto3
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from datetime import datetime

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)


class DynamoDBManager:
    """Helper class for managing SecuriVA DynamoDB operations"""
    
    def __init__(self, table_name="SecuriVAChats"):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.table = self.dynamodb.Table(table_name)
    
    def get_user_chats(self, user_id: str):
        """Get all chats for a specific user"""
        try:
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error fetching chats: {e}")
            return []
    
    def get_chat_count(self, user_id: str) -> int:
        """Count total chats for a user"""
        chats = self.get_user_chats(user_id)
        return len(chats)
    
    def delete_user_data(self, user_id: str, confirm=False):
        """Delete all data for a specific user (use with caution!)"""
        if not confirm:
            print("⚠️  Set confirm=True to delete user data")
            return False
        
        try:
            chats = self.get_user_chats(user_id)
            
            with self.table.batch_writer() as batch:
                for chat in chats:
                    batch.delete_item(
                        Key={
                            'user_id': chat['user_id'],
                            'session_timestamp': chat['session_timestamp']
                        }
                    )
            
            print(f"✅ Deleted {len(chats)} chats for user {user_id}")
            return True
        except ClientError as e:
            print(f"❌ Error deleting user data: {e}")
            return False
    
    def get_all_users(self):
        """Get list of all unique users in the table"""
        try:
            response = self.table.scan(
                ProjectionExpression='user_id'
            )
            
            user_ids = set(item['user_id'] for item in response.get('Items', []))
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    ProjectionExpression='user_id',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                user_ids.update(item['user_id'] for item in response.get('Items', []))
            
            return sorted(list(user_ids))
        except ClientError as e:
            print(f"Error scanning users: {e}")
            return []
    
    def get_table_stats(self):
        """Get statistics about the DynamoDB table"""
        try:
            # Get table metadata
            table_info = self.table.meta.client.describe_table(
                TableName=self.table.table_name
            )
            
            table_data = table_info['Table']
            
            stats = {
                'table_name': table_data['TableName'],
                'status': table_data['TableStatus'],
                'item_count': table_data.get('ItemCount', 0),
                'size_bytes': table_data.get('TableSizeBytes', 0),
                'size_mb': round(table_data.get('TableSizeBytes', 0) / (1024**2), 2),
                'creation_date': table_data['CreationDateTime'].strftime('%Y-%m-%d %H:%M:%S'),
                'billing_mode': table_data['BillingModeSummary']['BillingMode'],
            }
            
            return stats
        except ClientError as e:
            print(f"Error getting table stats: {e}")
            return None
    
    def export_user_chats(self, user_id: str, output_file: str):
        """Export all chats for a user to JSON file"""
        try:
            chats = self.get_user_chats(user_id)
            
            # Sort by version
            chats.sort(key=lambda x: x.get('version', 0))
            
            with open(output_file, 'w') as f:
                json.dump({
                    'user_id': user_id,
                    'export_date': datetime.now().isoformat(),
                    'chat_count': len(chats),
                    'chats': chats
                }, f, indent=2)
            
            print(f"✅ Exported {len(chats)} chats to {output_file}")
            return True
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def import_chats(self, json_file: str):
        """Import chats from JSON file"""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            chats = data.get('chats', [])
            
            with self.table.batch_writer() as batch:
                for chat in chats:
                    batch.put_item(Item=chat)
            
            print(f"✅ Imported {len(chats)} chats")
            return True
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
    
    def cleanup_old_chats(self, days: int, dry_run=True):
        """Delete chats older than specified days"""
        import time
        
        cutoff_timestamp = int((time.time() - (days * 24 * 60 * 60)) * 1000)
        
        try:
            # Scan for old items
            response = self.table.scan(
                FilterExpression='session_timestamp < :cutoff',
                ExpressionAttributeValues={
                    ':cutoff': str(cutoff_timestamp)
                }
            )
            
            old_items = response.get('Items', [])
            
            if dry_run:
                print(f"🔍 Found {len(old_items)} chats older than {days} days")
                print("   Run with dry_run=False to delete")
                return old_items
            
            # Delete old items
            with self.table.batch_writer() as batch:
                for item in old_items:
                    batch.delete_item(
                        Key={
                            'user_id': item['user_id'],
                            'session_timestamp': item['session_timestamp']
                        }
                    )
            
            print(f"✅ Deleted {len(old_items)} old chats")
            return old_items
        except ClientError as e:
            print(f"❌ Cleanup failed: {e}")
            return []


# CLI Interface
def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python dynamodb_utils.py stats              - Show table statistics")
        print("  python dynamodb_utils.py users              - List all users")
        print("  python dynamodb_utils.py count <user_id>    - Count chats for user")
        print("  python dynamodb_utils.py list <user_id>     - List chats for user")
        print("  python dynamodb_utils.py export <user_id> <file.json>  - Export user chats")
        print("  python dynamodb_utils.py import <file.json>  - Import chats")
        print("  python dynamodb_utils.py cleanup <days>      - Preview cleanup (dry run)")
        return
    
    manager = DynamoDBManager()
    command = sys.argv[1]
    
    if command == "stats":
        stats = manager.get_table_stats()
        if stats:
            print("\n📊 Table Statistics:")
            for key, value in stats.items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
    
    elif command == "users":
        users = manager.get_all_users()
        print(f"\n👥 Found {len(users)} users:")
        for user in users:
            count = manager.get_chat_count(user)
            print(f"   - {user} ({count} chats)")
    
    elif command == "count" and len(sys.argv) >= 3:
        user_id = sys.argv[2]
        count = manager.get_chat_count(user_id)
        print(f"User {user_id} has {count} chats")
    
    elif command == "list" and len(sys.argv) >= 3:
        user_id = sys.argv[2]
        chats = manager.get_user_chats(user_id)
        print(f"\n💬 Chats for {user_id}:")
        for chat in sorted(chats, key=lambda x: x.get('version', 0)):
            print(f"   Version {chat['version']}: {chat.get('title', 'Untitled')}")
            print(f"      {len(chat.get('messages', []))} messages")
    
    elif command == "export" and len(sys.argv) >= 4:
        user_id = sys.argv[2]
        output_file = sys.argv[3]
        manager.export_user_chats(user_id, output_file)
    
    elif command == "import" and len(sys.argv) >= 3:
        json_file = sys.argv[2]
        manager.import_chats(json_file)
    
    elif command == "cleanup" and len(sys.argv) >= 3:
        days = int(sys.argv[2])
        manager.cleanup_old_chats(days, dry_run=True)
    
    else:
        print("❌ Invalid command or missing arguments")


if __name__ == "__main__":
    main()
