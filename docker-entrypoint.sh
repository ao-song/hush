#!/bin/sh
# Use shell's exec to replace the script process with the last command,
# ensuring signals (like SIGTERM from 'docker stop') are passed correctly.

# Exit immediately if a command exits with a non-zero status.
set -e

# If APP_SUB_PATH is set, create a prefix with a leading slash.
if [ -n "$APP_SUB_PATH" ] && [ "$APP_SUB_PATH" != "/" ]; then
    # remove leading/trailing slashes
    CLEAN_SUB_PATH=$(printf '%s' "$APP_SUB_PATH" | sed 's#^/*##; s#/*$##')
    APP_SUB_PATH_PREFIX="/$CLEAN_SUB_PATH"
else
    APP_SUB_PATH_PREFIX=""
fi

# Replace placeholders in Nginx config and frontend files
sed -i "s|##APP_SUB_PATH_PREFIX##|$APP_SUB_PATH_PREFIX|g" /etc/nginx/conf.d/default.conf
sed -i "s|##APP_SUB_PATH_PREFIX##|$APP_SUB_PATH_PREFIX|g" /app/frontend/index.html
sed -i "s|##APP_SUB_PATH_PREFIX##|$APP_SUB_PATH_PREFIX|g" /app/frontend/script.js
chown appuser:appuser /app/frontend/script.js /app/frontend/index.html

# Start nginx in the background
nginx

# Start the backend application in the foreground
echo "Starting Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
