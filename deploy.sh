#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

APP_DIR="/eba-job-platform"   # Path to your app on the server
NGINX_SERVICE="nginx"             # Nginx systemd service name

echo "=== Starting deployment of Eba Job Platform ==="

# 1. Go to app directory
cd "$APP_DIR"

# 2. Pull latest changes from Git
echo "--- Pulling latest changes from Git ---"
git fetch --all
git pull origin master   



# 4. Build & restart containers
echo "--- Rebuilding and restarting Docker containers ---"
docker compose down
docker compose up -d --build

# 5. Check container status
docker compose ps
