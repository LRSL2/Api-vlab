#!/bin/bash
set -e

echo "Waiting for database..."
sleep 5

echo "Running database migrations..."
alembic upgrade head

echo "Migrations completed successfully!"

