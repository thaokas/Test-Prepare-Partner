#!/bin/sh
set -e

BACKEND_URL="${BACKEND_URL:-http://backend:8080}"
echo "Using backend: $BACKEND_URL"

sed -i "s|__BACKEND_URL__|$BACKEND_URL|g" /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
