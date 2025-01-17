#!/bin/bash
set -e

# Wait for database
python manage.py wait_for_db

# Apply database migrations
python manage.py migrate

# Collect static files if not in debug mode
if [ "$DEBUG" != "True" ]; then
    python manage.py collectstatic --noinput
fi

# Start Xvfb (virtual framebuffer)
Xvfb :99 -screen 0 1024x768x16 &
export DISPLAY=:99

# Execute the main command
exec "$@"