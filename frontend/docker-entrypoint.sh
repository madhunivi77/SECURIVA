#!/bin/sh
set -e

: "${BACKEND_URL:?BACKEND_URL env var is required}"

# strip any trailing slash so proxy_pass concatenates correctly
BACKEND_URL="${BACKEND_URL%/}"
export BACKEND_URL

envsubst '$BACKEND_URL' \
  < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf

echo "[render-backend-url] proxying API paths to: $BACKEND_URL"
