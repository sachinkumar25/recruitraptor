#!/bin/bash
set -e

echo "🚀 Setting up AI Recruiter Agent development environment..."

# Check dependencies
echo "📋 Checking dependencies..."
python --version
node --version
docker --version
poetry --version

# Start infrastructure
echo "🐳 Starting infrastructure services..."
docker-compose up -d

# Setup resume parser service
echo "📄 Setting up Resume Parser service..."
cd services/resume-parser
poetry install
poetry run python -m spacy download en_core_web_sm
cd ../..

echo "✅ Setup complete! You're ready to start development."
echo ""
echo "Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Run 'make dev' to start all services"
echo "3. Begin implementing Resume Parser service"
