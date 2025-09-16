#!/bin/sh
# Use shell's exec to replace the script process with the last command,
# ensuring signals (like SIGTERM from 'docker stop') are passed correctly.

# Exit immediately if a command exits with a non-zero status.
set -e

# Start nginx in the background
nginx

# Start the backend application in the foreground
echo "Starting Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
