#!/bin/bash

echo "🚀 Setting up Crypto Predictor Backend..."
echo "=========================================="

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "📁 Running both servers..."
echo "1. 🌐 WebSocket Server (ws://localhost:8765)"
echo "2. 🚀 API Server (http://localhost:8000)"
echo ""
echo "📋 Open new terminal windows to run:"
echo "   Terminal 1: python websocket_server.py"
echo "   Terminal 2: python main.py"
echo ""
echo "Or run both in background:"
echo "   python websocket_server.py &"
echo "   python main.py"
echo ""
echo "🔗 Quick test commands:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/payment-address"