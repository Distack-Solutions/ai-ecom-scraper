#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files in production
python manage.py collectstatic --noinput

# Execute the CMD provided in the Dockerfile or docker-compose
exec "$@"
