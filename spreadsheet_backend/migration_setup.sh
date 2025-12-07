#!/bin/bash
set -e

echo "🔧 Running database migrations..."

# Initialize migrations if missing
if [ ! -d "migrations" ]; then
  echo "📁 No migrations folder found. Initializing..."
  flask db init
fi

# Generate and apply migrations
echo "🛠  Generating and applying migrations..."
flask db migrate -m "Auto migration on container start" || echo "⚠️  No new changes detected"
flask db upgrade

echo "✅ Migrations applied successfully!"