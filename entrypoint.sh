#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files in production
python manage.py collectstatic --noinput

# Start Xvfb (virtual framebuffer)
Xvfb :99 -screen 0 1024x768x16 &
export DISPLAY=:99

# Execute the CMD provided in the Dockerfile or docker-compose
exec "$@"
