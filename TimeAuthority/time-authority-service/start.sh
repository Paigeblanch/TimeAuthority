#!/bin/bash

# Time Authority - Quick Start Script
# This script helps you set up and run the timestamping service

echo "=============================================="
echo "⏰ Time Authority - Quick Start"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python $(python3 --version) found"
echo ""

# Check if wallet address is configured
if grep -q "YOUR_COINBASE_WALLET_ADDRESS_HERE" timestamp_service.py; then
    echo "⚠️  WARNING: Wallet address not configured!"
    echo ""
    echo "Please edit timestamp_service.py and replace:"
    echo "  RECIPIENT_ADDRESS = \"YOUR_COINBASE_WALLET_ADDRESS_HERE\""
    echo "with your actual Coinbase wallet address"
    echo ""
    read -p "Continue anyway for testing? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Run the service
echo "🚀 Starting Time Authority service..."
echo ""
echo "   Service will be available at:"
echo "   - API: http://localhost:8000"
echo "   - Dashboard: http://localhost:8000/dashboard"
echo "   - Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the service"
echo "=============================================="
echo ""

python3 timestamp_service.py
