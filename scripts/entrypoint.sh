#!/bin/bash

# Wait for the database to be ready
echo "_Waiting for postgres..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "_PostgreSQL started..."

# Initialize migrations if not present, otherwise upgrade
if [ ! -d "migrations" ]; then
  echo "_Initializing database migrations..."
  flask db init || { echo "_Failed to initialize migrations..."; exit 1; }
fi

# Run migrations if migrations folder is present
flask db migrate -m "Auto migration" || { echo "_Failed to create migration..."; exit 1; }
flask db upgrade || { echo "_Failed to run migrations..."; exit 1; }

# Start the flask app
exec "$@"
