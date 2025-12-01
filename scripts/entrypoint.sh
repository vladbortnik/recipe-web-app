#!/bin/bash
# =============================================================================
# Docker Entrypoint Script - Flask Application Startup
# =============================================================================
#
# PURPOSE:
#   This script serves as the Docker container entrypoint. It ensures the
#   PostgreSQL database is ready before initializing Flask migrations and
#   starting the application.
#
# EXECUTION ORDER:
#   1. Wait for PostgreSQL to accept connections
#   2. Initialize Flask-Migrate if not already done
#   3. Create/apply database migrations
#   4. Start the Flask application (via exec "$@")
#
# ENVIRONMENT VARIABLES REQUIRED:
#   - DB_HOST: PostgreSQL hostname (usually 'db' for Docker networks)
#   - DB_PORT: PostgreSQL port (usually 5432)
#
# USAGE:
#   This script is called automatically by Docker via the Dockerfile ENTRYPOINT.
#   The CMD from docker-compose.yaml is passed as arguments ("$@").
#
# RELATED FILES:
#   - Dockerfile (sets this as ENTRYPOINT)
#   - docker-compose.yaml (provides CMD arguments)
#   - scripts/wait-for-migrations.sh (similar script for migration-only service)
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
# Step 4: Start the Application
# -----------------------------------------------------------------------------
# Execute the command passed to this script (from docker-compose CMD)
# This replaces the shell with the application process
exec "$@"
