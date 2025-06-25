#!/bin/bash

set -e

echo "🚀 Bot Forge System Setup"
echo "========================="

echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is required but not installed"
    echo "Install with: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "✅ Prerequisites check passed"

echo "📦 Initializing git submodules..."
git submodule update --init --recursive

echo "🐍 Setting up backend dependencies..."
cd backend
poetry install
cd ..

echo "📱 Setting up frontend dependencies..."
cd frontend
if command -v pnpm &> /dev/null; then
    pnpm install
elif command -v npm &> /dev/null; then
    npm install
else
    echo "❌ Neither pnpm nor npm found"
    exit 1
fi
cd ..

echo "🔧 Setting up CLI tools..."
cd cli
pip install pandas rich typer
cd ..

echo "🗄️ Initializing database..."
cd backend
poetry run python -c "from app.database import init_db; init_db()"
cd ..

echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "1. Backend:  cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "2. Frontend: cd frontend && npm run dev"
echo "3. Access:   http://localhost:5173"
