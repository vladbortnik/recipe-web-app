#!/bin/sh

# Wait for the database to be ready
echo "Waiting for postgres..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL started"

# Check if the environment is development
if [ "$FLASK_ENV" = "development" ]; then
  echo "Resetting database schema for development..."

  # Drop all tables and recreate the schema
  flask db downgrade base || { echo "Failed to downgrade database"; exit 1; }
  flask db stamp head || { echo "Failed to stamp database"; exit 1; }
  flask db migrate || { echo "Failed to create migration"; exit 1; }
  flask db upgrade || { echo "Failed to upgrade database"; exit 1; }
fi

# Initialize migrations if not present, otherwise upgrade (This could be redundant with the above steps)
if [ ! -d "migrations" ]; then
  echo "Initializing database migrations..."
  flask db init || { echo "Failed to initialize migrations"; exit 1; }
fi

# Run migrations if migrations folder is present
flask db migrate -m "Auto migration" || { echo "Failed to create migration"; exit 1; }
flask db upgrade || { echo "Failed to run migrations"; exit 1; }

# Start the flask app
exec "$@"
