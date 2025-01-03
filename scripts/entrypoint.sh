#!/bin/bash

# Wait for the database to be ready
echo "Waiting for postgres..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL started..."

# Start the flask app
exec "$@"