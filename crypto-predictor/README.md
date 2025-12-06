# Crypto Predictor Backend

A powerful backend system for cryptocurrency prediction featuring real-time data streaming, Solana payment verification, and AI-powered prediction generation. This project includes two main components:

* **FastAPI REST API Server** – primary backend handling authentication, payments, predictions, and database operations.
* **WebSocket Server** – delivers real-time crypto candlestick data.

---

## 🚀 Quick Start

### **Prerequisites**

* Python 3.8+
* MongoDB (local or cloud)
* Internet connection

---

## 1. Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd crypto-predictor-backend

# Make scripts executable
chmod +x run.sh test_all.sh
```

---

## 2. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn motor pydantic python-dotenv requests websockets
```

---

## 3. Environment Configuration

Create a `.env` file in the project root:

```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
YOUR_WALLET=Your_Solana_Wallet_Address_Here
GEMINI_KEY=your_gemini_api_key_here
```

---

## 🏗️ Architecture

```
crypto-predictor-backend/
├── main.py              # FastAPI Server
├── websocket_server.py  # Live price WebSocket
├── test.py              # WebSocket test client
├── run.sh               # Setup and run script
├── test_all.sh          # Test suite📌 Overview

A comprehensive cryptocurrency prediction system with real-time data streaming, Solana payment verification, and AI-powered predictions. This backend consists of two main components:

FastAPI REST API Server - Main application server

WebSocket Server - Real-time crypto data streaming

🚀 Quick Start
Prerequisites
Python 3.8+

MongoDB (local or cloud)

Internet connection for API calls

1. Clone and Setup
bash
# Clone repository
git clone <your-repo-url>
cd crypto-predictor-backend

# Make scripts executable
chmod +x run.sh test_all.sh
2. Environment Setup
bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn motor pydantic python-dotenv requests websockets
3. Environment Configuration
Create a .env file in the root directory:

env
# MongoDB Connection
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/

# Solana Wallet (For receiving payments)
YOUR_WALLET=Your_Solana_Wallet_Address_Here

# Gemini AI Key (Optional - for AI explanations)
GEMINI_KEY=your_gemini_api_key_here
🏗️ Architecture
System Components
text
crypto-predictor-backend/
├── main.py              # FastAPI REST API Server
├── websocket_server.py  # WebSocket Server for real-time data
├── test.py              # WebSocket client test
├── run.sh               # Setup and run script
├── test_all.sh          # Complete API testing script
├── requirements.txt     # Python dependencies
└── .env                # Environment variables
🚀 Running the Servers
Option A: Using the Run Script (Recommended)
bash
./run.sh
This will:

Setup virtual environment

Install dependencies

Provide instructions to run both servers

Option B: Manual Start
Terminal 1 - WebSocket Server
bash
# Activate virtual environment
source venv/bin/activate

# Start WebSocket Server
python websocket_server.py
Expected Output:

text
🚀 Live Crypto WebSocket Server Starting...
============================================================
📊 Supported Coins:
   • BTC: Bitcoin
   • ETH: Ethereum
   • SOL: Solana
   • BNB: Binance Coin
   • XRP: Ripple
   • DOGE: Dogecoin
   • ADA: Cardano
   • MATIC: Polygon

📈 Supported Timeframes: 4h, 1d, 1w
🌐 Server: ws://localhost:8765
⏰ Updates: Every 4 hours
📊 Data: Last 1000 candles per coin/interval
============================================================
✅ WebSocket server started!
⏳ Waiting for client connections...
Terminal 2 - API Server
bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI Server
python main.py
Expected Output:

text
============================================================
🚀 CRYPTO PREDICTOR PRO - REAL SOLANA VERIFICATION
============================================================
💰 Payment Address: Your_Wallet_Address
🌐 Solana Devnet RPC: https://api.devnet.solana.com
🔍 Using direct RPC calls for verification
============================================================
📡 API Endpoints
Base URL: http://localhost:8000
1. Health Check
bash
GET /health
Checks if the server and MongoDB are running.

2. Application Info
bash
GET /
Returns application information and payment details.

3. User Management
Signup
bash
POST /signup
Content-Type: application/json

{
    "name": "username",
    "password": "password123"
}
Login
bash
POST /login?name=username&password=password123
Get User Status
bash
GET /user/{user_id}/status
4. Payment System
Check Transaction
bash
GET /check-transaction/{tx_hash}
Verify Payment
bash
POST /verify-payment
Content-Type: application/json

{
    "user_id": "user123",
    "tx_hash": "solana_transaction_hash"
}
5. Predictions
Get Prediction
bash
POST /predict
Content-Type: application/json

{
    "user_id": "user123",
    "coin": "BTC"
}
Note: This takes 10-15 seconds to simulate real analysis.

Get Prediction History
bash
GET /predictions/{user_id}?limit=20
6. Market Data
Get Coin Prices
bash
GET /prices/{coin}?limit=100
🌐 WebSocket Server
Connection Details
URL: ws://localhost:8765

Protocol: WebSocket

Data: Real-time cryptocurrency candlestick data

Subscription
json
{
    "action": "subscribe",
    "coin": "BTC",
    "interval": "4h"
}
Supported Coins
BTC (Bitcoin)

ETH (Ethereum)

SOL (Solana)

BNB (Binance Coin)

XRP (Ripple)

DOGE (Dogecoin)

ADA (Cardano)

MATIC (Polygon)

Supported Intervals
4h (4 hours)

1d (1 day)

1w (1 week)

💳 Payment System
How It Works
User signs up and gets a user ID

User sends 1 SOL to the provided Solana wallet address

User submits their transaction hash via /verify-payment

System verifies the transaction on Solana Devnet

If verified, user receives 50 credits for predictions

Testing Payments
For testing on Solana Devnet:

Get SOL from a Devnet faucet

Send 1 SOL to the wallet address shown in the API

Use the transaction hash for verification

🧪 Testing
Run Complete Test Suite
bash
./test_all.sh
Test WebSocket Server
bash
python test.py
Manual API Testing Examples
Check Health
bash
curl http://localhost:8000/health
Create User
bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"testuser","password":"testpass"}'
Test WebSocket Connection
python
# Use test.py or create your own WebSocket client
import asyncio
import websockets
import json

async def test_ws():
    async with websockets.connect("ws://localhost:8765") as ws:
        await ws.send(json.dumps({
            "action": "subscribe",
            "coin": "BTC",
            "interval": "4h"
        }))
        response = await ws.recv()
        print(json.loads(response))
🛠️ Configuration
MongoDB Setup
Create a MongoDB database (local or cloud)

Update MONGODB_URL in .env

Collections will be created automatically:

users - User accounts

payments - Payment records

predictions - Prediction history

coin_history - Price history

Solana Configuration
Default RPC: Solana Devnet

For production: Change to Mainnet

Update YOUR_WALLET in .env

📊 Data Flow
text
User Request → API Server → Payment Verification → Data Analysis → AI Explanation → Response
                    │              │                    │               │
                    ↓              ↓                    ↓               ↓
              MongoDB Check  Solana RPC        Binance API       Gemini AI
🔒 Security Notes
Never commit .env file to version control

Use strong passwords for MongoDB

For production:

Enable HTTPS

Implement rate limiting

Add authentication middleware

Use environment-specific configurations

Solana wallet private keys should never be stored in code

🐛 Troubleshooting
Common Issues
MongoDB Connection Failed

Check MongoDB URL in .env

Ensure MongoDB service is running

Verify network connectivity

Solana RPC Timeout

Check internet connection

Try different RPC endpoint

Increase timeout in code if needed

WebSocket Connection Failed

Ensure WebSocket server is running

Check port 8765 is available

Verify firewall settings

Payment Verification Fails

Ensure using Solana Devnet

Verify transaction has enough confirmations

Check wallet address matches

Logs
Check server logs for detailed error messages:

API Server: Terminal running main.py

WebSocket Server: Terminal running websocket_server.py

📈 Monitoring
Health Endpoints
bash
# API Health
curl http://localhost:8000/health

# MongoDB Status
# Check the health endpoint response
Log Files
Consider implementing logging to files for production:

python
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
🚀 Production Deployment
Recommended Changes
Use Environment Variables for all secrets

Implement CORS properly - restrict origins

Add API rate limiting

Use production MongoDB (Atlas recommended)

Switch to Solana Mainnet for real payments

Add SSL certificates for HTTPS

Implement proper logging

Use process manager (PM2, systemd, etc.)

Deployment Options
Docker (Recommended for containerization)

Cloud Platforms: AWS, GCP, Azure, Heroku

VPS: DigitalOcean, Linode, Vultr

📝 License
This project is for educational purposes. Commercial use may require additional licensing.

🤝 Support
For issues, questions, or contributions:

Check the troubleshooting section

Review server logs

Create an issue in the repository

Contact the development team

📁 Project Structure Details
main.py - FastAPI Server
This is the main API server that handles:

User authentication and management

Solana payment verification

Cryptocurrency predictions

MongoDB data storage

websocket_server.py - Real-time Data Server
Provides real-time cryptocurrency data via WebSocket:

Fetches data from Binance API

Supports multiple coins and timeframes

Automatic updates every 4 hours

Sends 1000 candlestick data points

test.py - WebSocket Client Test
Example client for testing WebSocket connections and data reception.

run.sh - Setup Script
Bash script to easily setup and run the application.

test_all.sh - Comprehensive Test Suite
Tests all API endpoints to ensure system is working correctly.

🔧 Customization Guide
Adding New Cryptocurrencies
Edit websocket_server.py:

python
self.supported_coins = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    # Add new coin here
    "NEWCOIN": "New Coin Name",
}
Edit main.py in get_binance_prices() function if needed for special cases.

Changing Prediction Logic
Modify the predict() function in main.py:

Adjust RSI calculation parameters

Change signal generation logic

Modify confidence scoring

Update AI prompt for explanations

Changing Payment Amount
Edit the payment verification logic in verify_solana_transaction():

python
# Change from 0.99 to desired amount
if sol_received >= 0.99:  # Current: 1 SOL minimum
Database Schema Changes
To add new fields to user documents:

python
# In signup endpoint
await users.insert_one({
    "_id": user_id,
    "name": user.name,
    "password": user.password,
    "has_paid": False,
    "credits": 0,
    "created": datetime.now().isoformat(),
    # Add new fields here
    "new_field": "default_value",
})
🎯 Use Cases
1. Educational Platform
Students can learn about crypto trading

Practice with real market data

Understand technical analysis

2. Trading Bot Integration
Use predictions to inform trading decisions

Connect via API to execute trades

Backtest strategies with historical data

3. Market Analysis Tool
Monitor multiple cryptocurrencies

Get AI-powered insights

Track prediction accuracy over time

📊 Performance Tips
For high traffic:

Implement Redis caching

Use connection pooling for MongoDB

Consider load balancing

For real-time data:

Optimize WebSocket message size

Implement data compression

Use binary protocols instead of JSON

Database optimization:

Add indexes on frequently queried fields

Implement data archiving for old records

Use read replicas for heavy read loads

🔄 Updates and Maintenance
Regular Maintenance Tasks
Update API keys and secrets regularly

Monitor server logs for errors

Update dependencies for security patches

Backup MongoDB database regularly

Monitor Solana RPC endpoint health

Version Updates
When updating the application:

Backup current database

Test updates in staging environment

Update dependencies incrementally

Document API changes

Notify users of breaking changes
├── requirements.txt
└── .env
```

---

## 🚀 Running the Servers

### **Option A — Recommended (using run.sh)**

```bash
./run.sh
```

This script prepares the environment and guides you through running both servers.

---

### **Option B — Manual Start**

#### **Terminal 1 — WebSocket Server**

```bash
source venv/bin/activate
python websocket_server.py
```

You will see startup logs including supported coins, timeframes, and server address.

#### **Terminal 2 — API Server**

```bash
source venv/bin/activate
python main.py
```

Displays server info, RPC details, and endpoint summary.

---

## 📡 API Endpoints

Base URL: `http://localhost:8000`

### **1. Health Check**

```bash
GET /health
```

### **2. App Info**

```bash
GET /
```

### **3. User Management**

#### Signup

```bash
POST /signup
{
  "name": "username",
  "password": "password123"
}
```

#### Login

```bash
POST /login?name=username&password=password123
```

#### User Status

```bash
GET /user/{user_id}/status
```

---

### **4. Payment System**

#### Check Transaction

```bash
GET /check-transaction/{tx_hash}
```

#### Verify Payment

```bash
POST /verify-payment
{
  "user_id": "user123",
  "tx_hash": "solana_transaction_hash"
}
```

---

### **5. Predictions**

#### Get Prediction

```bash
POST /predict
{
  "user_id": "user123",
  "coin": "BTC"
}
```

#### Prediction History

```bash
GET /predictions/{user_id}?limit=20
```

---

### **6. Market Data**

```bash
GET /prices/{coin}?limit=100
```

---

## 🌐 WebSocket Server

* **URL:** `ws://localhost:8765`
* Supports real-time crypto candlestick streaming

### Subscribe Example

```json
{
  "action": "subscribe",
  "coin": "BTC",
  "interval": "4h"
}
```

### Supported Coins

BTC, ETH, SOL, BNB, XRP, DOGE, ADA, MATIC

### Supported Intervals

4h, 1d, 1w

---

## 💳 Payment System Overview

* User sends **1 SOL** to the configured wallet
* User submits transaction hash
* System verifies payment via Solana Devnet
* Upon successful verification → **50 credits added**

---

## 🧪 Testing

### Run full test suite

```bash
./test_all.sh
```

### Test WebSocket

```bash
python test.py
```

### Manual API Tests

```bash
curl http://localhost:8000/health
```

---

## 🛠️ Configuration

### MongoDB Collections

* `users`
* `payments`
* `predictions`
* `coin_history`

### Solana Configuration

* Default: Solana Devnet RPC
* Replace with Mainnet RPC for production

---

## 📊 Data Flow

```
User → API → Payment Check → Analysis → AI → Response
```

---

## 🔒 Security Guidelines

* Never commit `.env` files
* Use strong MongoDB credentials
* Enable HTTPS in production
* Add rate limiting and authentication middleware
* Never store Solana private keys in code

---

## 🐛 Troubleshooting

### MongoDB Issues

* Confirm URL & connectivity

### Solana RPC Fails

* Try alternate RPC node

### WebSocket Issues

* Ensure port 8765 is free

### Payment Verification Fails

* Ensure Devnet transaction
* Ensure sufficient confirmations

---

## 📈 Monitoring

* Check `/health` endpoint
* Review logs from both servers

---

## 🚀 Production Deployment

**Recommended:** Docker, AWS, GCP, Azure, or VPS

Production best practices:

* Use SSL certificates
* Add caching (Redis)
* Implement logging & monitoring
* Switch to Solana Mainnet

---

## 📁 Project File Details

* `main.py` – FastAPI backend
* `websocket_server.py` – real-time data
* `test.py` – test client
* `run.sh` – setup script
* `test_all.sh` – test suite

---

## 🔧 Customization

* Add new cryptocurrencies
* Adjust prediction logic
* Change SOL payment amount
* Modify database schema

---

## 🎯 Use Cases

* Educational crypto learning
* Trading bot integration
* Market analytics dashboard

---

## 📊 Performance Tips

* Use Redis caching
* Enable MongoDB indexing
* Compress WebSocket data
* Load balance for high traffic

---

## 🔄 Maintenance

* Rotate API keys
* Monitor RPC performance
* Update dependencies
* Backup database regularly

---

## 📝 License

For educational use. Commercial deployment may require licensing.

---

## 🤝 Support

* Refer to Troubleshooting
* Check logs
* Open issues on repository
