#!/bin/bash

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting Daphne server..."
daphne -b 0.0.0.0 -p 8000 Floor_Bot.asgi:application
