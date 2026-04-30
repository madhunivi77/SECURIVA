#!/usr/bin/env bash
# Build the combined frontend+backend image, push to ECR, trigger an
# AWS App Runner deployment, wait for it to finish, smoke-test, print URL.
#
# Works from a developer laptop or from CI. Reads AWS credentials from:
#   1. existing env vars (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)
#   2. else, backend/.env (auto-sourced; teammates: get this file from a
#      teammate and put it at backend/.env before running)
#   3. else, ~/.aws/credentials profile
#
# Prerequisites: docker (running), aws cli, curl. That's it.
#
# Usage:
#   ./scripts/deploy.sh                   # build + push + deploy + wait + smoke-test
#   SKIP_BUILD=1 ./scripts/deploy.sh      # only trigger a redeploy (e.g. env-var change)
#   SKIP_DEPLOY=1 ./scripts/deploy.sh     # only build + push, don't redeploy
#   SKIP_WAIT=1 ./scripts/deploy.sh       # don't poll for completion
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$(pwd)"

log() { printf "\n\033[1;36m==>\033[0m %s\n" "$*"; }
err() { printf "\n\033[1;31m!!\033[0m %s\n" "$*" >&2; exit 1; }

# Auto-source AWS creds from backend/.env if not already in the environment.
# Reads just the AWS_* lines so we don't pollute the shell with other vars.
if [[ -z "${AWS_ACCESS_KEY_ID:-}" && -f "${ROOT}/backend/.env" ]]; then
  while IFS='=' read -r key value; do
    [[ "$key" =~ ^AWS_(ACCESS_KEY_ID|SECRET_ACCESS_KEY|REGION)$ ]] || continue
    value="${value%\"}"; value="${value#\"}"   # strip surrounding double quotes
    value="${value%\'}"; value="${value#\'}"   # strip surrounding single quotes
    export "$key=$value"
  done < "${ROOT}/backend/.env"
  log "Loaded AWS creds from backend/.env"
fi

AWS_REGION="${AWS_REGION:-us-east-2}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-281505305629}"
ECR_REPO="${ECR_REPO:-securiva-backend}"
SERVICE_ARN="${SERVICE_ARN:-arn:aws:apprunner:us-east-2:281505305629:service/securiva-backend/27d257db40ec46d1a43adf3d29b1c74d}"
PLATFORM="${PLATFORM:-linux/amd64}"
DOCKERFILE="${DOCKERFILE:-Dockerfile.combined}"
IMAGE="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest"

# Pre-flight checks
command -v docker >/dev/null   || err "docker not installed"
command -v aws >/dev/null      || err "aws CLI not installed"
command -v curl >/dev/null     || err "curl not installed"
docker info >/dev/null 2>&1    || err "docker daemon not running (open Docker Desktop)"
aws sts get-caller-identity --region "${AWS_REGION}" >/dev/null 2>&1 \
  || err "AWS credentials not working — set AWS_ACCESS_KEY_ID/SECRET in env or backend/.env"

if [[ "${SKIP_BUILD:-0}" != "1" ]]; then
  log "Logging in to ECR ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
  aws ecr get-login-password --region "${AWS_REGION}" \
    | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

  log "Building ${IMAGE} for ${PLATFORM}"
  docker buildx build \
    --platform "${PLATFORM}" \
    --provenance=false \
    -f "${ROOT}/${DOCKERFILE}" \
    -t "${IMAGE}" \
    --push \
    "${ROOT}"
fi

if [[ "${SKIP_DEPLOY:-0}" == "1" ]]; then
  log "SKIP_DEPLOY=1, exiting after push"
  exit 0
fi

log "Triggering App Runner deployment"
OP_ID=$(aws apprunner start-deployment \
  --service-arn "${SERVICE_ARN}" \
  --region "${AWS_REGION}" \
  --query 'OperationId' \
  --output text)
echo "  operation id: ${OP_ID}"

if [[ "${SKIP_WAIT:-0}" == "1" ]]; then
  log "SKIP_WAIT=1, exiting after start-deployment"
  exit 0
fi

log "Waiting for deployment ${OP_ID} to finish (poll 20s)"
while :; do
  STATUS=$(aws apprunner list-operations \
    --service-arn "${SERVICE_ARN}" \
    --region "${AWS_REGION}" \
    --query "OperationSummaryList[?Id=='${OP_ID}'].Status | [0]" \
    --output text 2>/dev/null || echo "")
  case "${STATUS}" in
    SUCCEEDED) log "Deployment SUCCEEDED"; break ;;
    FAILED|ROLLBACK_FAILED|ROLLBACK_SUCCEEDED)
      log "Deployment ended with status: ${STATUS}"; exit 1 ;;
    IN_PROGRESS|PENDING|"") sleep 20 ;;
    *) sleep 20 ;;
  esac
done

URL=$(aws apprunner describe-service \
  --service-arn "${SERVICE_ARN}" \
  --region "${AWS_REGION}" \
  --query 'Service.ServiceUrl' \
  --output text)

log "Smoke-testing https://${URL}"
ROOT_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://${URL}/" || echo "000")
API_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://${URL}/api/status" || echo "000")
SPA_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://${URL}/dashboard" || echo "000")
echo "  /             HTTP ${ROOT_CODE}"
echo "  /api/status   HTTP ${API_CODE}"
echo "  /dashboard    HTTP ${SPA_CODE}"

if [[ "${ROOT_CODE}" != "200" || "${API_CODE}" != "200" || "${SPA_CODE}" != "200" ]]; then
  log "Smoke test FAILED"
  exit 1
fi

log "Deployment complete: https://${URL}"
