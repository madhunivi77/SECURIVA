"""
Test script to verify DynamoDB connection and table setup
"""

import boto3
import os
from pathlib import Path
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

if not os.getenv('AWS_ACCESS_KEY_ID'):
    print("⚠️  Warning: AWS credentials not found in .env file")
    print(f"   Looking for .env at: {env_path.absolute()}")
    print("   Make sure the .env file contains AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION")
    exit(1)

def check_dynamodb_connection():
    """Check if DynamoDB is accessible with current credentials"""
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # List tables to verify connection
        response = dynamodb.list_tables()
        print("✅ DynamoDB connection successful!")
        print(f"Available tables: {response.get('TableNames', [])}")
        return True
    except ClientError as e:
        print(f"❌ DynamoDB connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def check_table_exists(table_name="SecuriVAChats"):
    """Check if the specified table exists"""
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        table = dynamodb.Table(table_name)
        table.load()  # This will raise an exception if table doesn't exist
        
        print(f"✅ Table '{table_name}' exists")
        print(f"   Status: {table.table_status}")
        print(f"   Item count: {table.item_count}")
        print(f"   Table ARN: {table.table_arn}")
        
        # Show table schema
        print("\nTable Schema:")
        print(f"   Partition Key: {table.key_schema[0]['AttributeName']} ({table.key_schema[0]['KeyType']})")
        if len(table.key_schema) > 1:
            print(f"   Sort Key: {table.key_schema[1]['AttributeName']} ({table.key_schema[1]['KeyType']})")
        
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Table '{table_name}' does not exist")
            print("\nTo create the table, run:")
            print(f"   python backend/tests/create_dynamodb_table.py")
        else:
            print(f"❌ Error checking table: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_read_write(table_name="SecuriVAChats"):
    """Test basic read/write operations"""
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-2')
        )
        table = dynamodb.Table(table_name)
        
        # Test write
        test_item = {
            "user_id": "test_user",
            "session_timestamp": "test_123456789",
            "version": 1,
            "title": "Test Chat",
            "messages": [{"role": "user", "content": "test"}]
        }
        
        table.put_item(Item=test_item)
        print("✅ Write test successful")
        
        # Test read
        response = table.get_item(
            Key={
                "user_id": "test_user",
                "session_timestamp": "test_123456789"
            }
        )
        
        if 'Item' in response:
            print("✅ Read test successful")
            
            # Clean up test data
            table.delete_item(
                Key={
                    "user_id": "test_user",
                    "session_timestamp": "test_123456789"
                }
            )
            print("✅ Cleanup successful")
            return True
        else:
            print("❌ Read test failed - item not found")
            return False
            
    except ClientError as e:
        print(f"❌ Read/Write test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("DynamoDB Connection Test")
    print("=" * 60)
    
    # Step 1: Check connection
    print("\n1. Checking DynamoDB connection...")
    if not check_dynamodb_connection():
        print("\n⚠️  Fix AWS credentials in .env file and try again")
        exit(1)
    
    # Step 2: Check table
    print("\n2. Checking table existence...")
    if not check_table_exists():
        print("\n⚠️  Create the table before proceeding")
        exit(1)
    
    # Step 3: Test operations
    print("\n3. Testing read/write operations...")
    if test_read_write():
        print("\n✅ All tests passed! DynamoDB is ready to use.")
    else:
        print("\n⚠️  Read/write tests failed")
        exit(1)
