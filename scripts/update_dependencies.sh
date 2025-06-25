#!/bin/bash

set -e

echo "🔄 Updating Bot Forge Dependencies"
echo "=================================="

echo "📋 Updating git repository..."
git pull origin main

echo "📦 Updating git submodules..."
git submodule update --remote --recursive

echo "🐍 Updating backend dependencies..."
cd backend
poetry update
cd ..

echo "📱 Updating frontend dependencies..."
cd frontend
if command -v pnpm &> /dev/null; then
    pnpm update
elif command -v npm &> /dev/null; then
    npm update
else
    echo "❌ Neither pnpm nor npm found"
    exit 1
fi
cd ..

echo "🔧 Updating CLI tools..."
cd cli
pip install --upgrade pandas rich typer
cd ..

echo "✅ Dependencies updated successfully!"
echo ""
echo "🔄 Restart your servers to apply updates:"
echo "1. Backend:  cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "2. Frontend: cd frontend && npm run dev"
