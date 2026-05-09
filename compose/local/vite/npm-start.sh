#!/bin/sh
set -e

echo "Installing npm dependencies..."
npm ci

echo "Starting Vite development server..."
npx vite --host 0.0.0.0 --port ${DJANGO_VITE_DEV_SERVER_PORT:-5174}
