#!/bin/sh
set -e

PORT="${PORT:-80}"
BACKEND_URL="${BACKEND_URL:-http://backend:8080}"
echo "Listening on port: $PORT"
echo "Using backend: $BACKEND_URL"

sed -i "s|__BACKEND_URL__|$BACKEND_URL|g" /etc/nginx/conf.d/default.conf
sed -i "s|__PORT__|$PORT|g" /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
