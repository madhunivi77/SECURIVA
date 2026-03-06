# Deploy SECURIVA Backend to AWS App Runner

## Architecture Overview

- **Compute:** AWS App Runner (container-based, auto-scaling)
- **Container Registry:** Amazon ECR (`securiva-backend`)
- **Storage:** S3 (`securiva-data-prod`) for OAuth data (`data/oauth.json`)
- **Region:** `us-east-2` (Ohio)
- **Service URL:** `https://buechw2rme.us-east-2.awsapprunner.com`
- **Service ARN:** `arn:aws:apprunner:us-east-2:281505305629:service/securiva-backend/27d257db40ec46d1a43adf3d29b1c74d`

## IAM Roles

| Role | Purpose | Trust Principal |
|------|---------|-----------------|
| `securiva-apprunner-ecr-role` | Allows App Runner to pull images from ECR | `build.apprunner.amazonaws.com` |
| `securiva-apprunner-instance-role` | Allows running container to access S3 | `tasks.apprunner.amazonaws.com` |

---

## Pre-Flight Checks

```bash
# Check which AWS account/user you're logged in as
aws sts get-caller-identity

# Check your region
aws configure get region

# List existing ECR repositories
aws ecr describe-repositories --query 'repositories[].repositoryName' --output table

# List existing App Runner services
aws apprunner list-services --query 'ServiceSummaryList[].{Name:ServiceName,Status:Status,URL:ServiceUrl}' --output table

# List existing S3 buckets
aws s3 ls

# List IAM roles (check for existing App Runner roles)
aws iam list-roles --query 'Roles[?contains(RoleName,`apprunner`) || contains(RoleName,`AppRunner`)].RoleName' --output table
```

---

## First-Time Setup (Steps 1-5)

### Step 1: Create ECR Repository

```bash
aws ecr create-repository --repository-name securiva-backend --region us-east-2
```

### Step 2: Build & Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 281505305629.dkr.ecr.us-east-2.amazonaws.com

# Build (from backend/ directory)
cd backend
docker build -t securiva-backend .

# Tag
docker tag securiva-backend:latest 281505305629.dkr.ecr.us-east-2.amazonaws.com/securiva-backend:latest

# Push
docker push 281505305629.dkr.ecr.us-east-2.amazonaws.com/securiva-backend:latest
```

### Step 3: Create S3 Bucket for OAuth Data

```bash
aws s3 mb s3://securiva-data-prod --region us-east-2

# Initialize with empty oauth data
echo '{"users":[]}' | aws s3 cp - s3://securiva-data-prod/data/oauth.json --content-type application/json
```

### Step 4: Create IAM Roles

#### 4a. Instance role (for S3 access at runtime)

```bash
# Trust policy
cat > /tmp/apprunner-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "tasks.apprunner.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name securiva-apprunner-instance-role \
  --assume-role-policy-document file:///tmp/apprunner-trust-policy.json

# S3 access policy
cat > /tmp/securiva-s3-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],
    "Resource": "arn:aws:s3:::securiva-data-prod/data/*"
  }]
}
EOF

aws iam put-role-policy \
  --role-name securiva-apprunner-instance-role \
  --policy-name securiva-s3-access \
  --policy-document file:///tmp/securiva-s3-policy.json
```

#### 4b. ECR access role (for App Runner to pull images)

```bash
cat > /tmp/apprunner-ecr-trust.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "build.apprunner.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name securiva-apprunner-ecr-role \
  --assume-role-policy-document file:///tmp/apprunner-ecr-trust.json

aws iam attach-role-policy \
  --role-name securiva-apprunner-ecr-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess
```

### Step 5: Create App Runner Service

```bash
aws apprunner create-service \
  --service-name securiva-backend \
  --source-configuration '{
    "AuthenticationConfiguration": {
      "AccessRoleArn": "arn:aws:iam::281505305629:role/securiva-apprunner-ecr-role"
    },
    "ImageRepository": {
      "ImageIdentifier": "281505305629.dkr.ecr.us-east-2.amazonaws.com/securiva-backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "ENVIRONMENT": "production",
          "BACKEND_URL": "https://temp.us-east-2.awsapprunner.com",
          "FRONTEND_URL": "<your-frontend-url>",
          ...other env vars...
        }
      }
    }
  }' \
  --instance-configuration '{"InstanceRoleArn":"arn:aws:iam::281505305629:role/securiva-apprunner-instance-role"}' \
  --health-check-configuration '{"Protocol":"TCP","Interval":10,"Timeout":5,"HealthyThreshold":1,"UnhealthyThreshold":5}' \
  --region us-east-2
```

> **Note:** Use TCP health check (not HTTP). After creation, get the service URL and update env vars with the real URL using `aws apprunner update-service`.

### Step 6: Update Service with Real URL

Once you have the App Runner URL, update `BACKEND_URL`, `MCP_SERVER_URL`, `AUTH_SERVER_URL`, and `SF_CALLBACK_URL` to use it.

### Step 7: Post-Deploy Checklist

1. **Google Cloud Console** — Add `https://<app-runner-url>/callback` to OAuth redirect URIs
2. **Salesforce Connected App** — Add `https://<app-runner-url>/salesforce/callback` as callback URL
3. **Verify** — `curl https://<app-runner-url>/api/status`

---

## Environment Variables

The service requires these env vars (set via App Runner configuration):

| Variable | Description |
|----------|-------------|
| `ENVIRONMENT` | `production` |
| `BACKEND_URL` | App Runner service URL |
| `FRONTEND_URL` | Frontend URL (for CORS) |
| `MCP_SERVER_URL` | `<BACKEND_URL>/mcp/` |
| `AUTH_SERVER_URL` | `<BACKEND_URL>/auth/token` |
| `JWT_SECRET_KEY` | JWT signing secret |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `OPENAI_API_KEY` | OpenAI API key |
| `GROQ_API_KEY` | Groq API key |
| `SF_CLIENT_ID` | Salesforce connected app client ID |
| `SF_CLIENT_SECRET` | Salesforce connected app client secret |
| `SF_CALLBACK_URL` | `<BACKEND_URL>/salesforce/callback` |
| `OAUTH_S3_BUCKET` | `securiva-data-prod` |
| `OAUTH_S3_KEY` | `data/oauth.json` |
| `COOKIE_SAMESITE` | `none` |
| `COOKIE_SECURE` | `true` |
| `TELESIGN_CUSTOMER_ID` | TeleSign customer ID |
| `TELESIGN_API_KEY` | TeleSign API key |

> **Important:** Never commit actual secret values to git. Use `cloudshell-command.txt` / `cloudshell-update.txt` locally only (these are gitignored).

---

## Manual Deployment (After Code Changes)

```bash
cd backend

# 1. Build image
docker build -t securiva-backend .

# 2. Tag for ECR
docker tag securiva-backend:latest 281505305629.dkr.ecr.us-east-2.amazonaws.com/securiva-backend:latest

# 3. Login to ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 281505305629.dkr.ecr.us-east-2.amazonaws.com

# 4. Push
docker push 281505305629.dkr.ecr.us-east-2.amazonaws.com/securiva-backend:latest

# 5. Trigger new deployment
aws apprunner start-deployment --service-arn arn:aws:apprunner:us-east-2:281505305629:service/securiva-backend/27d257db40ec46d1a43adf3d29b1c74d
```

---

## Troubleshooting

```bash
# Check service status
aws apprunner describe-service \
  --service-arn arn:aws:apprunner:us-east-2:281505305629:service/securiva-backend/27d257db40ec46d1a43adf3d29b1c74d \
  --query 'Service.Status'

# View operations
aws apprunner list-operations \
  --service-arn arn:aws:apprunner:us-east-2:281505305629:service/securiva-backend/27d257db40ec46d1a43adf3d29b1c74d

# Check S3 oauth data
aws s3 cp s3://securiva-data-prod/data/oauth.json -

# View App Runner logs (via CloudWatch)
# Logs are at: /aws/apprunner/securiva-backend/<service-id>/application
```

## Docker Details

- **Base image:** `python:3.12-slim`
- **Package manager:** `uv` (installed from `ghcr.io/astral-sh/uv:latest`)
- **Server:** `uvicorn` on port 8000
- **Command:** `uv run uvicorn my_app.server.main:app --host 0.0.0.0 --port 8000`
