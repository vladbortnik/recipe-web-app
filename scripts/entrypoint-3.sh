#!/bin/sh

# Wait for the database to be ready
echo "_Waiting for postgres..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "_PostgreSQL started..."

# Function to reset the database schema
reset_database() {
  echo "_Resetting database schema for development..."

  # Drop the database
  PGPASSWORD="$POSTGRES_PASSWORD" psql -d "$POSTGRES_DB" -h "$DB_HOST" -U "$POSTGRES_USER" -c "DROP DATABASE IF EXISTS $POSTGRES_DB;" || { echo "_Failed to drop database..."; exit 1; }
  echo "_Drop the database failed......."

  # Recreate the database
  PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -U "$POSTGRES_USER" -c "CREATE DATABASE $POSTGRES_DB;" || { echo "_Failed to create database..."; exit 1; }
  echo "_Recreate the database failed......."

  # Apply migrations
  flask db init || { echo "_Failed to initialize migrations..."; exit 1; }
  flask db migrate || { echo "_Failed to create migration..."; exit 1; }
  flask db upgrade || { echo "_Failed to upgrade database..."; exit 1; }

  echo "_Apply migrations failed......."
}

# Check if the environment is development
if [ "$FLASK_ENV" = "development" ]; then
  # Ensure to export the password to avoid prompt for password
  # export PGPASSWORD="$POSTGRES_PASSWORD"
  reset_database
  echo "_reset_database failed......."
fi

# Start the flask app
exec "$@"
