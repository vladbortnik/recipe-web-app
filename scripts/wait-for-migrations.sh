#!/bin/bash
# =============================================================================
# Database Migration Script - Standalone Migration Service
# =============================================================================
#
# PURPOSE:
#   This script runs database migrations as a one-time job. It's designed to
#   be used as a separate Docker service that runs, performs migrations, and
#   then exits. This allows the main application containers to wait for
#   migrations to complete before starting.
#
# EXECUTION ORDER:
#   1. Wait for PostgreSQL to accept connections
#   2. Initialize Flask-Migrate if not already done
#   3. Create/apply database migrations
#   4. Exit successfully (allowing dependent services to start)
#
# ENVIRONMENT VARIABLES REQUIRED:
#   - DB_HOST: PostgreSQL hostname (usually 'db' for Docker networks)
#   - DB_PORT: PostgreSQL port (usually 5432)
#
# USAGE:
#   Used as the command for the 'migration' service in docker-compose.yaml:
#   
#   migration:
#     build: .
#     command: ./scripts/wait-for-migrations.sh
#     depends_on:
#       - db
#     restart: "no"
#
# DIFFERENCE FROM entrypoint.sh:
#   - entrypoint.sh: Runs migrations AND starts the app (stays running)
#   - wait-for-migrations.sh: Runs migrations only, then exits (one-time job)
#
# RELATED FILES:
#   - scripts/entrypoint.sh (full entrypoint with app startup)
#   - docker-compose-examples/compose-simple-w-auto-migration.yaml
#
# =============================================================================

set -e  # Exit immediately if a command exits with a non-zero status

# -----------------------------------------------------------------------------
# Step 1: Wait for PostgreSQL Database
# -----------------------------------------------------------------------------
echo "Waiting for postgres..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL started..."

# -----------------------------------------------------------------------------
# Step 2: Initialize Flask-Migrate (if first run)
# -----------------------------------------------------------------------------
if [ ! -d "migrations" ]; then
  echo "Initializing database migrations..."
  flask db init || { echo "ERROR: Failed to initialize migrations"; exit 1; }
fi

# -----------------------------------------------------------------------------
# Step 3: Create and Apply Migrations
# -----------------------------------------------------------------------------
# Create a new migration if there are model changes
flask db migrate -m "Auto migration" || { echo "WARNING: Migration creation skipped (no changes or already exists)"; }

# Apply all pending migrations
flask db upgrade head || { echo "ERROR: Failed to apply migrations"; exit 1; }

# -----------------------------------------------------------------------------
# Step 4: Exit Successfully
# -----------------------------------------------------------------------------
# Exit with success code so dependent services know migrations are complete
echo "Database migrations completed successfully!"
exit 0
