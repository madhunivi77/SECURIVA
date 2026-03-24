# Compliance Reports DynamoDB Testing

This guide contains the exact commands to create the DynamoDB table, enable compliance report persistence, generate a report, and verify that the write succeeded.

## Prerequisites

Ensure these environment variables are set in `backend/.env` or exported in your shell:

```bash
AWS_ACCESS_KEY_ID="your_access_key_id"
AWS_SECRET_ACCESS_KEY="your_secret_access_key"
AWS_REGION="us-east-2"
USE_DYNAMODB_COMPLIANCE_REPORTS="true"
COMPLIANCE_REPORTS_DYNAMODB_TABLE="SecuriVAComplianceReports"
```

## 1. Create the Compliance Reports Table

```bash
cd /workspaces/SECURIVA/backend
/workspaces/SECURIVA/.venv/bin/python tests/create_compliance_reports_table.py
```

If you want a custom table name:

```bash
cd /workspaces/SECURIVA/backend
/workspaces/SECURIVA/.venv/bin/python tests/create_compliance_reports_table.py --table YourCustomReportsTable
```

## 2. Enable Persistence for the Current Shell

```bash
cd /workspaces/SECURIVA/backend
export USE_DYNAMODB_COMPLIANCE_REPORTS=true
export COMPLIANCE_REPORTS_DYNAMODB_TABLE=SecuriVAComplianceReports
```

## 3. Generate a Compliance Report

Use the existing compliance tool test script:

```bash
cd /workspaces/SECURIVA/backend
/workspaces/SECURIVA/.venv/bin/python tests/test_compliance_tools.py
```

## 4. Verify the Save Was Attempted

Check tool logs for the persistence event:

```bash
cd /workspaces/SECURIVA/backend
grep -n "save_compliance_report" logs/tool_calls.json | tail -n 5
```

Expected result:

- A `save_compliance_report` entry appears
- The entry contains `"success": true`
- The entry includes a generated `report_id`

## 5. Verify the Report Exists in DynamoDB

Using AWS CLI:

```bash
aws dynamodb scan \
  --table-name SecuriVAComplianceReports \
  --region us-east-2 \
  --max-items 5
```

If you used a custom table name:

```bash
aws dynamodb scan \
  --table-name YourCustomReportsTable \
  --region us-east-2 \
  --max-items 5
```

Expected fields in each item:

- `report_id`
- `generated_at`
- `saved_at`
- `standards`
- `options`
- `report`

## 6. One-Pass Command Sequence

```bash
cd /workspaces/SECURIVA/backend
/workspaces/SECURIVA/.venv/bin/python tests/create_compliance_reports_table.py
export USE_DYNAMODB_COMPLIANCE_REPORTS=true
export COMPLIANCE_REPORTS_DYNAMODB_TABLE=SecuriVAComplianceReports
/workspaces/SECURIVA/.venv/bin/python tests/test_compliance_tools.py
grep -n "save_compliance_report" logs/tool_calls.json | tail -n 5
aws dynamodb scan --table-name SecuriVAComplianceReports --region us-east-2 --max-items 5
```

## Troubleshooting

If `save_compliance_report` does not appear in the logs:

- Verify `USE_DYNAMODB_COMPLIANCE_REPORTS=true`
- Verify AWS credentials are loaded in the shell that runs the test
- Verify the table exists in the same region as `AWS_REGION`

If the report generates but no DynamoDB item appears:

- Check `logs/tool_calls.json` for a failed `save_compliance_report` event
- Confirm the table name matches `COMPLIANCE_REPORTS_DYNAMODB_TABLE`
- Confirm the AWS CLI is pointed at the same account and region