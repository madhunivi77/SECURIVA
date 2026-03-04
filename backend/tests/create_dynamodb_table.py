"""
Script to create the DynamoDB table for SecuriVA
"""

import boto3
import os
from pathlib import Path
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)


def create_securiva_table(table_name="SecuriVAChats"):
    """
    Create DynamoDB table with proper schema for chat storage
    
    Schema:
    - Partition Key: user_id (String)
    - Sort Key: session_timestamp (String)
    - Attributes: version (Number), title (String), messages (List)
    """
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Create table with composite primary key
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'session_timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'  # String
                },
                {
                    'AttributeName': 'session_timestamp',
                    'AttributeType': 'S'  # String (using timestamp as string)
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand billing (no need to provision capacity)
            Tags=[
                {
                    'Key': 'Environment',
                    'Value': 'Production'
                },
                {
                    'Key': 'Application',
                    'Value': 'SecuriVA'
                }
            ]
        )
        
        print(f"⏳ Creating table '{table_name}'...")
        print("   This may take 30-60 seconds...")
        
        # Wait until the table exists
        table.wait_until_exists()
        
        print(f"✅ Table '{table_name}' created successfully!")
        print(f"   Status: {table.table_status}")
        print(f"   ARN: {table.table_arn}")
        print(f"   Billing Mode: PAY_PER_REQUEST")
        
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"ℹ️  Table '{table_name}' already exists")
        else:
            print(f"❌ Error creating table: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def delete_table(table_name="SecuriVAChats"):
    """
    Delete the DynamoDB table (use with caution!)
    """
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-2')
        )
        
        table = dynamodb.Table(table_name)
        table.delete()
        
        print(f"⏳ Deleting table '{table_name}'...")
        table.wait_until_not_exists()
        print(f"✅ Table '{table_name}' deleted successfully")
        
        return True
    except ClientError as e:
        print(f"❌ Error deleting table: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("DynamoDB Table Creation Script")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--delete":
        confirm = input("\n⚠️  Are you sure you want to DELETE the table? (yes/no): ")
        if confirm.lower() == "yes":
            delete_table()
        else:
            print("Deletion cancelled")
    else:
        create_securiva_table()
