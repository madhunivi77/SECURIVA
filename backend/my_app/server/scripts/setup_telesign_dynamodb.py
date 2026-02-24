"""
Setup DynamoDB table for Telesign logging

Run this script once to create the DynamoDB table:
    python -m my_app.server.scripts.setup_telesign_dynamodb
"""

import boto3
import os
from botocore.exceptions import ClientError

def create_telesign_table(table_name="TelesignLogs", region="us-east-2"):
    """
    Create DynamoDB table for Telesign logs
    
    Args:
        table_name: Name of the DynamoDB table
        region: AWS region
    """
    dynamodb = boto3.client('dynamodb', region_name=region)
    
    try:
        print(f"Creating DynamoDB table: {table_name} in {region}...")
        
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'log_type',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'log_type',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand pricing
            Tags=[
                {
                    'Key': 'Application',
                    'Value': 'Securiva'
                },
                {
                    'Key': 'Purpose',
                    'Value': 'Telesign API Logging'
                }
            ]
        )
        
        print(f"✅ Table '{table_name}' is being created...")
        print(f"   ARN: {response['TableDescription']['TableArn']}")
        print(f"   Status: {response['TableDescription']['TableStatus']}")
        
        # Wait for table to be created
        print("⏳ Waiting for table to become active...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
        # Enable TTL for automatic log deletion
        print("🔧 Enabling TTL for automatic log expiration...")
        dynamodb.update_time_to_live(
            TableName=table_name,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'expiration_time'
            }
        )
        
        print(f"✅ Table '{table_name}' is ready!")
        print(f"\n📝 Next steps:")
        print(f"1. Set TELESIGN_USE_DYNAMODB=true in your .env file")
        print(f"2. Ensure AWS credentials are configured")
        print(f"3. Restart your backend server")
        
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️ Table '{table_name}' already exists")
            return True
        else:
            print(f"❌ Error creating table: {e}")
            return False


def delete_telesign_table(table_name="TelesignLogs", region="us-east-2"):
    """
    Delete DynamoDB table (use with caution!)
    
    Args:
        table_name: Name of the DynamoDB table
        region: AWS region
    """
    dynamodb = boto3.client('dynamodb', region_name=region)
    
    try:
        print(f"⚠️ Deleting DynamoDB table: {table_name}...")
        confirm = input("Are you sure? Type 'DELETE' to confirm: ")
        
        if confirm != 'DELETE':
            print("❌ Deletion cancelled")
            return False
        
        dynamodb.delete_table(TableName=table_name)
        print(f"✅ Table '{table_name}' deleted")
        return True
        
    except ClientError as e:
        print(f"❌ Error deleting table: {e}")
        return False


def main():
    """Main setup function"""
    import sys
    
    # Get AWS region from env or use default
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
    table_name = os.getenv("TELESIGN_DYNAMODB_TABLE", "TelesignLogs")
    
    print("=" * 60)
    print("TELESIGN DYNAMODB SETUP")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "delete":
        delete_telesign_table(table_name, region)
    else:
        create_telesign_table(table_name, region)


if __name__ == "__main__":
    main()