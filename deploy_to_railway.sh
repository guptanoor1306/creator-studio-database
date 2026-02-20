#!/bin/bash

echo "🚀 Creator Studio Data Exporter - Railway Deployment"
echo "=================================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Creator Studio Data Exporter"
    git branch -M main
    echo "✅ Git repository initialized"
    echo ""
fi

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo ""
    echo "Please install Railway CLI first:"
    echo "  npm install -g @railway/cli"
    echo "  or"
    echo "  brew install railway"
    echo ""
    exit 1
fi

echo "🔐 Logging into Railway..."
railway login

echo ""
echo "🏗️  Initializing Railway project..."
railway init

echo ""
echo "📤 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Opening your deployed app..."
railway open

echo ""
echo "=================================================="
echo "🎉 Your app is now live on Railway!"
echo ""
echo "📝 Next steps:"
echo "  1. Get your Bearer token from Creator Studio"
echo "  2. Paste it in the UI authentication field"
echo "  3. Click 'Load Channels'"
echo "  4. Start exporting data!"
echo ""
echo "=================================================="
