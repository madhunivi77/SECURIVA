# DynamoDB Management Guide for SecuriVA

## Overview

SecuriVA uses a dual-database architecture that supports both SQLite (development) and DynamoDB (production). This guide explains how to check, configure, and manage DynamoDB.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [Testing DynamoDB Connection](#testing-dynamodb-connection)
4. [Creating the DynamoDB Table](#creating-the-dynamodb-table)
5. [Switching Between SQLite and DynamoDB](#switching-between-sqlite-and-dynamodb)
6. [Monitoring and Management](#monitoring-and-management)
7. [Troubleshooting](#troubleshooting)
8. [Cost Optimization](#cost-optimization)

---

## Quick Start

### 1. Check if DynamoDB is configured
```bash
cd backend
python tests/test_dynamodb_connection.py
```

### 2. Create the table (if needed)
```bash
python tests/create_dynamodb_table.py
```

### 3. Switch to DynamoDB mode
Edit `backend/my_app/server/db.py` line 240:
```python
USE_DYNAMO = True  # Change from False to True
```

---

## Configuration

### Environment Variables

Ensure these are set in `backend/.env`:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID="your_access_key_id"
AWS_SECRET_ACCESS_KEY="your_secret_access_key"
AWS_REGION="us-east-2"
```

⚠️ **Security Note**: Never commit AWS credentials to version control. Use IAM roles when deploying to AWS.

### Table Configuration

- **Table Name**: `SecuriVAChats`
- **Region**: `us-east-2`
- **Billing Mode**: Pay-per-request (no capacity planning needed)
- **Primary Key**:
  - Partition Key: `user_id` (String)
  - Sort Key: `session_timestamp` (String)

---

## Testing DynamoDB Connection

### Basic Connection Test

```bash
cd backend
python tests/test_dynamodb_connection.py
```

This script will:
1. ✅ Verify AWS credentials are valid
2. ✅ Check if the `SecuriVAChats` table exists
3. ✅ Test read/write operations
4. ✅ Clean up test data

### Expected Output

```
============================================================
DynamoDB Connection Test
============================================================

1. Checking DynamoDB connection...
✅ DynamoDB connection successful!
Available tables: ['SecuriVAChats', 'OtherTable']

2. Checking table existence...
✅ Table 'SecuriVAChats' exists
   Status: ACTIVE
   Item count: 42
   Table ARN: arn:aws:dynamodb:us-east-2:123456789:table/SecuriVAChats

Table Schema:
   Partition Key: user_id (HASH)
   Sort Key: session_timestamp (RANGE)

3. Testing read/write operations...
✅ Write test successful
✅ Read test successful
✅ Cleanup successful

✅ All tests passed! DynamoDB is ready to use.
```

---

## Creating the DynamoDB Table

### Using the Script (Recommended)

```bash
cd backend
python tests/create_dynamodb_table.py
```

### Using AWS CLI

```bash
aws dynamodb create-table \
    --table-name SecuriVAChats \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=session_timestamp,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=session_timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-2
```

### Using AWS Console

1. Go to [DynamoDB Console](https://console.aws.amazon.com/dynamodb)
2. Click "Create table"
3. Configure:
   - **Table name**: `SecuriVAChats`
   - **Partition key**: `user_id` (String)
   - **Sort key**: `session_timestamp` (String)
   - **Billing mode**: On-demand
4. Click "Create table"

---

## Switching Between SQLite and DynamoDB

### Development → Production

Edit `backend/my_app/server/db.py`:

```python
# Line 240
USE_DYNAMO = True  # Enable DynamoDB
```

Restart your server:
```bash
cd backend
python run.py
```

### Production → Development

```python
# Line 240
USE_DYNAMO = False  # Use SQLite
```

### Environment-Based Switching (Recommended)

Modify `db.py` to use environment variables:

```python
import os

# Line 240
USE_DYNAMO = os.getenv("USE_DYNAMODB", "false").lower() == "true"
```

Then set in `.env`:
```bash
# Development
USE_DYNAMODB=false

# Production
USE_DYNAMODB=true
```

---

## Monitoring and Management

### View Table Status

```python
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('SecuriVAChats')

print(f"Status: {table.table_status}")
print(f"Item count: {table.item_count}")
print(f"Size: {table.table_size_bytes / (1024**2):.2f} MB")
```

### Query Data

```python
from boto3.dynamodb.conditions import Key

# Get all chats for a user
response = table.query(
    KeyConditionExpression=Key('user_id').eq('user_123')
)

for item in response['Items']:
    print(f"Version: {item['version']}, Title: {item['title']}")
```

### Delete Test Data

```python
# Delete a specific chat
table.delete_item(
    Key={
        'user_id': 'test_user',
        'session_timestamp': '1234567890'
    }
)
```

### Backup Table

```bash
# Create on-demand backup
aws dynamodb create-backup \
    --table-name SecuriVAChats \
    --backup-name SecuriVAChats-Backup-$(date +%Y%m%d) \
    --region us-east-2
```

---

## Troubleshooting

### Issue: "ResourceNotFoundException"

**Problem**: Table doesn't exist

**Solution**:
```bash
python backend/tests/create_dynamodb_table.py
```

---

### Issue: "UnrecognizedClientException"

**Problem**: Invalid AWS credentials

**Solution**:
1. Check your credentials in `.env`
2. Verify credentials with AWS CLI:
   ```bash
   aws sts get-caller-identity
   ```
3. Generate new credentials in [IAM Console](https://console.aws.amazon.com/iam)

---

### Issue: "AccessDeniedException"

**Problem**: Insufficient IAM permissions

**Required Permissions**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:DeleteItem",
                "dynamodb:DescribeTable",
                "dynamodb:ListTables"
            ],
            "Resource": "arn:aws:dynamodb:us-east-2:*:table/SecuriVAChats"
        }
    ]
}
```

---

### Issue: Performance/Latency

**Diagnosis**:
- Enable CloudWatch metrics in AWS Console
- Check DynamoDB metrics → "SystemErrors" and "UserErrors"

**Solutions**:
- Ensure you're using the correct region (`us-east-2`)
- Consider switching to provisioned capacity if you have predictable traffic
- Add DynamoDB connection pooling

---

### Issue: Data Inconsistency

**Problem**: Stale data or missing items

**Solution**:
- DynamoDB is eventually consistent by default
- For critical reads, use strongly consistent reads:
  ```python
  response = table.get_item(
      Key={'user_id': 'user_123', 'session_timestamp': '1234567890'},
      ConsistentRead=True  # Strong consistency
  )
  ```

---

## Cost Optimization

### Pay-Per-Request vs Provisioned Capacity

**Current Setup**: Pay-per-request (on-demand)
- **Pros**: No capacity planning, scales automatically
- **Cons**: More expensive for consistent high traffic

**When to Switch**:
- If you have >1M requests/month, consider provisioned capacity
- Calculate break-even point using [AWS Pricing Calculator](https://calculator.aws/)

### Monitor Costs

```bash
# View DynamoDB costs
aws ce get-cost-and-usage \
    --time-period Start=2026-02-01,End=2026-03-01 \
    --granularity MONTHLY \
    --metrics UnblendedCost \
    --filter file://filter.json
```

`filter.json`:
```json
{
    "Dimensions": {
        "Key": "SERVICE",
        "Values": ["Amazon DynamoDB"]
    }
}
```

### Cost-Saving Tips

1. **Enable TTL** for old chat data:
   ```python
   # Add expiration_time attribute
   import time
   expiration_time = int(time.time()) + (90 * 24 * 60 * 60)  # 90 days
   
   table.put_item(Item={
       'user_id': 'user_123',
       'session_timestamp': '1234567890',
       'expiration_time': expiration_time,  # Auto-delete after 90 days
       'version': 1,
       'title': 'Chat Title',
       'messages': [...]
   })
   ```

2. **Use projection expressions** to minimize data transfer:
   ```python
   response = table.query(
       KeyConditionExpression=Key('user_id').eq('user_123'),
       ProjectionExpression='version, title'  # Only fetch needed fields
   )
   ```

3. **Batch operations** for bulk reads/writes:
   ```python
   with table.batch_writer() as batch:
       for i in range(100):
           batch.put_item(Item={...})
   ```

---

## Production Checklist

- [ ] DynamoDB table created and active
- [ ] Connection test passes
- [ ] AWS credentials configured (use IAM roles, not hardcoded keys)
- [ ] `USE_DYNAMO = True` in production
- [ ] CloudWatch alarms configured for errors
- [ ] Backup strategy implemented
- [ ] TTL configured for data retention
- [ ] IAM permissions follow least-privilege principle

---

## Additional Resources

- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Boto3 DynamoDB Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [AWS Cost Explorer](https://console.aws.amazon.com/cost-management/)

---

## Contact

For issues or questions, refer to the main project README or contact the development team.
