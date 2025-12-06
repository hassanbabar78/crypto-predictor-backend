from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import requests
import hashlib
import motor.motor_asyncio
import os
import time
import asyncio
import random
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIG ==========
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyBS0x1bkjDT4AwbJm1dDoFT1gelpsBoYow")
YOUR_WALLET = os.getenv("YOUR_WALLET", "VqhmcMjsoW185gzvuQPUJXEVZiSEadCHKqSdr1YzKru")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://Hassan:hassan1339@cluster0.a1uosqr.mongodb.net/")
SOLANA_RPC_URL = "https://api.devnet.solana.com"

# ========== DATABASE ==========
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.crypto_app
users = db.users
payments = db.payments
predictions = db.predictions
coin_history = db.coin_history

# ========== MODELS ==========
class User(BaseModel):
    name: str
    password: str

class Payment(BaseModel):
    user_id: str
    tx_hash: str

class PredictRequest(BaseModel):
    user_id: str
    coin: str

# ========== APP ==========
app = FastAPI(title="Crypto Predictor Pro", version="5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== HELPER FUNCTIONS ==========
def get_binance_prices(coin, interval="4h", limit=1500):
    """Get large amount of data from Binance"""
    try:
        symbol = "MATIC" if coin == "POL" else coin
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": f"{symbol}USDT",
            "interval": interval,
            "limit": limit
        }
        response = requests.get(url, params=params, timeout=60)
        data = response.json()
        
        prices = []
        for candle in data:
            prices.append(float(candle[4]))  # Close price
        
        return prices
    except:
        return []

async def verify_solana_transaction(tx_hash: str) -> dict:
    """Verify Solana transaction using direct RPC - WORKING VERSION"""
    print(f"🔍 Checking Solana transaction: {tx_hash[:20]}...")
    
    try:
        # Direct RPC call to Solana devnet
        url = SOLANA_RPC_URL
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                tx_hash,
                {
                    "encoding": "jsonParsed",
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        
        headers = {"Content-Type": "application/json"}
        
        print(f"📡 Calling Solana RPC...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ RPC call failed: {response.status_code}")
            return {"verified": False, "reason": f"RPC call failed: {response.status_code}"}
        
        result = response.json()
        
        # Check for RPC error
        if "error" in result:
            error_msg = result["error"].get("message", "Unknown RPC error")
            print(f"❌ RPC error: {error_msg}")
            return {"verified": False, "reason": f"RPC error: {error_msg}"}
        
        # Check if transaction exists
        if not result.get("result"):
            print("❌ Transaction not found")
            return {"verified": False, "reason": "Transaction not found on Solana devnet"}
        
        tx_data = result["result"]
        
        # Check transaction status
        meta = tx_data.get("meta", {})
        
        if meta.get("err"):
            print(f"❌ Transaction failed: {meta['err']}")
            return {"verified": False, "reason": f"Transaction failed: {meta['err']}"}
        
        # Get transaction details
        message = tx_data["transaction"]["message"]
        account_keys = message["accountKeys"]
        
        # Find our wallet in the accounts
        our_wallet_index = -1
        for i, account in enumerate(account_keys):
            if account["pubkey"] == YOUR_WALLET:
                our_wallet_index = i
                break
        
        if our_wallet_index == -1:
            print(f"❌ Our wallet {YOUR_WALLET[:10]}... not found in transaction")
            print(f"   Accounts in transaction: {[acc['pubkey'][:10] + '...' for acc in account_keys[:3]]}")
            return {"verified": False, "reason": f"Transaction not sent to our wallet"}
        
        print(f"✅ Our wallet found at index: {our_wallet_index}")
        
        # Calculate SOL received
        pre_balances = meta.get("preBalances", [])
        post_balances = meta.get("postBalances", [])
        
        if len(pre_balances) > our_wallet_index and len(post_balances) > our_wallet_index:
            lamports_received = post_balances[our_wallet_index] - pre_balances[our_wallet_index]
            sol_received = lamports_received / 1_000_000_000
            
            print(f"💰 Balance change: {pre_balances[our_wallet_index]} -> {post_balances[our_wallet_index]} lamports")
            print(f"💰 SOL received: {sol_received:.6f} SOL")
            
            # Check if at least 1 SOL was received
            if sol_received >= 0.99:  # Allow small rounding
                print(f"✅ Payment verified! Received {sol_received:.6f} SOL")
                return {
                    "verified": True,
                    "amount_sol": sol_received,
                    "amount_lamports": lamports_received,
                    "transaction_data": {
                        "slot": tx_data.get("slot"),
                        "block_time": tx_data.get("blockTime"),
                        "signature": tx_hash
                    },
                    "explorer_url": f"https://explorer.solana.com/tx/{tx_hash}?cluster=devnet"
                }
            else:
                print(f"❌ Insufficient amount: {sol_received:.6f} SOL (need 1 SOL)")
                return {
                    "verified": False,
                    "reason": f"Insufficient amount: {sol_received:.6f} SOL received",
                    "amount_received": sol_received
                }
        else:
            print("❌ Could not get balance information")
            return {"verified": False, "reason": "No balance information available"}
        
    except requests.exceptions.Timeout:
        print("❌ RPC request timed out")
        return {"verified": False, "reason": "RPC request timed out"}
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"verified": False, "reason": f"Error: {str(e)}"}

# ========== ROUTES ==========
@app.get("/")
def home():
    return {
        "app": "Crypto Predictor Pro",
        "version": "5.0",
        "status": "live",
        "payment": {
            "address": YOUR_WALLET,
            "amount": "1 SOL",
            "network": "Solana Devnet",
            "explorer": f"https://explorer.solana.com/address/{YOUR_WALLET}?cluster=devnet"
        }
    }

@app.get("/health")
async def health():
    try:
        await client.admin.command('ping')
        return {"status": "healthy", "mongodb": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/signup")
async def signup(user: User):
    """Simple signup"""
    existing = await users.find_one({"name": user.name})
    if existing:
        raise HTTPException(status_code=400, detail="User exists")
    
    user_id = hashlib.md5(f"{user.name}{datetime.now()}".encode()).hexdigest()[:12]
    
    await users.insert_one({
        "_id": user_id,
        "name": user.name,
        "password": user.password,
        "has_paid": False,
        "credits": 0,
        "created": datetime.now().isoformat()
    })
    
    return {
        "user_id": user_id, 
        "message": "Signup successful. Please pay 1 SOL to unlock predictor.",
        "payment_required": True,
        "payment_amount": "1 SOL",
        "payment_address": YOUR_WALLET,
        "explorer": f"https://explorer.solana.com/address/{YOUR_WALLET}?cluster=devnet"
    }

@app.post("/login")
async def login(name: str, password: str):
    """Simple login"""
    user = await users.find_one({"name": name, "password": password})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login")
    
    return {
        "user_id": user["_id"],
        "name": user["name"],
        "has_paid": user.get("has_paid", False),
        "credits": user.get("credits", 0),
        "payment_status": "paid" if user.get("has_paid") else "pending"
    }

@app.get("/check-transaction/{tx_hash}")
async def check_transaction(tx_hash: str):
    """Check any Solana transaction on devnet"""
    result = await verify_solana_transaction(tx_hash)
    return {
        "transaction_hash": tx_hash,
        "verification": result,
        "explorer": f"https://explorer.solana.com/tx/{tx_hash}?cluster=devnet"
    }

@app.post("/verify-payment")
async def verify_payment(payment: Payment):
    """REAL Solana payment verification"""
    print(f"🔄 Verifying REAL payment for user: {payment.user_id}")
    print(f"📝 Transaction hash: {payment.tx_hash[:20]}...")
    
    user = await users.find_one({"_id": payment.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("has_paid", False):
        return {
            "success": True,
            "message": "Already verified",
            "has_paid": True,
            "credits": user.get("credits", 0)
        }
    
    # REAL Solana blockchain verification
    verification_result = await verify_solana_transaction(payment.tx_hash)
    
    if verification_result["verified"]:
        # Update user with 50 credits (for 1 SOL payment)
        credits_granted = 50
        await users.update_one(
            {"_id": payment.user_id},
            {"$set": {"has_paid": True}, "$inc": {"credits": credits_granted}}
        )
        
        # Record payment
        await payments.insert_one({
            "user_id": payment.user_id,
            "tx_hash": payment.tx_hash,
            "amount_sol": verification_result["amount_sol"],
            "amount_lamports": verification_result["amount_lamports"],
            "verified": True,
            "verification_time": datetime.now().isoformat(),
            "credits_granted": credits_granted,
            "explorer_url": verification_result.get("explorer_url"),
            "transaction_data": verification_result.get("transaction_data", {})
        })
        
        updated_user = await users.find_one({"_id": payment.user_id})
        
        return {
            "success": True,
            "message": f"🎉 Payment verified! Received {verification_result['amount_sol']:.6f} SOL.",
            "has_paid": True,
            "credits_granted": credits_granted,
            "total_credits": updated_user.get("credits", 0),
            "transaction": {
                "hash": payment.tx_hash,
                "amount_sol": verification_result["amount_sol"],
                "explorer_url": verification_result.get("explorer_url")
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # Payment not verified
    return {
        "success": False,
        "message": "Payment verification failed",
        "reason": verification_result.get("reason", "Unknown error"),
        "transaction_hash": payment.tx_hash,
        "payment_details": {
            "address": YOUR_WALLET,
            "amount": "1 SOL (1,000,000,000 lamports)",
            "network": "Solana Devnet",
            "explorer": f"https://explorer.solana.com/address/{YOUR_WALLET}?cluster=devnet"
        },
        "has_paid": False,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict")
async def predict(request: PredictRequest):
    """Get prediction with 10-15 second analysis"""
    start_time = time.time()
    
    # Check user
    user = await users.find_one({"_id": request.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.get("has_paid", False):
        raise HTTPException(
            status_code=402, 
            detail={
                "message": "Payment required",
                "payment_amount": "1 SOL",
                "payment_address": YOUR_WALLET,
                "instructions": "Send 1 SOL to unlock predictor",
                "explorer": f"https://explorer.solana.com/address/{YOUR_WALLET}?cluster=devnet"
            }
        )
    
    if user.get("credits", 0) < 1:
        raise HTTPException(
            status_code=402, 
            detail={
                "message": "No credits remaining",
                "credits_needed": 1,
                "credits_available": user.get("credits", 0)
            }
        )
    
    coin = request.coin.upper()
    
    # Get large data (simulate 10-15 second processing)
    print(f"📊 Fetching data for {coin}...")
    prices = get_binance_prices(coin, "4h", 1500)
    
    if not prices:
        raise HTTPException(status_code=400, detail="No data available for this coin")
    
    current_price = prices[-1]
    current_time = datetime.now().isoformat()
    
    # Simulate heavy processing (10-15 seconds)
    print(f"⏳ Analyzing {len(prices)} data points for {coin}...")
    await asyncio.sleep(random.randint(10, 15))
    
    # Simple RSI calculation
    if len(prices) >= 14:
        gains = sum(max(prices[i] - prices[i-1], 0) for i in range(-14, 0))
        losses = sum(abs(min(prices[i] - prices[i-1], 0)) for i in range(-14, 0))
        avg_gain = gains / 14
        avg_loss = losses / 14 if losses > 0 else 1
        rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
    else:
        rsi = 50
    
    # Generate signal
    if rsi < 30:
        signal = "BUY"
        confidence = random.randint(80, 95)
        target = round(current_price * 1.15, 2)
        stop_loss = round(current_price * 0.90, 2)
    elif rsi > 70:
        signal = "SELL"
        confidence = random.randint(75, 90)
        target = round(current_price * 0.90, 2)
        stop_loss = round(current_price * 1.10, 2)
    else:
        signal = "HOLD"
        confidence = random.randint(50, 65)
        target = round(current_price * 1.02, 2)
        stop_loss = round(current_price * 0.98, 2)
    
    # Get AI explanation
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_KEY}"
        prompt = f"Explain {signal} signal for {coin} at ${current_price} in 2 simple sentences."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            explanation = data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            explanation = f"{signal} signal for {coin} at ${current_price}."
    except:
        explanation = f"{signal} signal for {coin} at ${current_price}."
    
    # Save prediction
    pred_id = hashlib.md5(f"{request.user_id}{coin}{datetime.now()}".encode()).hexdigest()[:10]
    
    await predictions.insert_one({
        "_id": pred_id,
        "user_id": request.user_id,
        "coin": coin,
        "signal": signal,
        "confidence": confidence,
        "current_price": current_price,
        "entry_time": current_time,
        "target_price": target,
        "stop_loss": stop_loss,
        "explanation": explanation,
        "created_at": datetime.now().isoformat()
    })
    
    # Update user
    await users.update_one(
        {"_id": request.user_id},
        {"$inc": {"credits": -1}}
    )
    
    updated_user = await users.find_one({"_id": request.user_id})
    processing_time = round(time.time() - start_time, 2)
    
    return {
        "success": True,
        "prediction_id": pred_id,
        "coin": coin,
        "signal": signal,
        "confidence": f"{confidence}%",
        "current_price": round(current_price, 2),
        "target_price": target,
        "stop_loss": stop_loss,
        "entry_time": current_time,
        "analysis": {
            "rsi": round(rsi, 2),
            "processing_time": f"{processing_time} seconds",
            "data_points": len(prices)
        },
        "explanation": explanation,
        "user_info": {
            "credits_used": 1,
            "credits_remaining": updated_user.get("credits", 0)
        }
    }

@app.get("/user/{user_id}/status")
async def get_user_status(user_id: str):
    """Get user status"""
    user = await users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "name": user.get("name"),
        "has_paid": user.get("has_paid", False),
        "credits": user.get("credits", 0),
        "payment_address": YOUR_WALLET if not user.get("has_paid") else None,
        "payment_explorer": f"https://explorer.solana.com/address/{YOUR_WALLET}?cluster=devnet" if not user.get("has_paid") else None
    }


@app.get("/predictions/{user_id}")
async def get_user_predictions(user_id: str, limit: int = 20):
    """Get user's prediction history"""
    predictions_list = await predictions.find({"user_id": user_id}).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Convert ObjectId to string for JSON serialization
    for pred in predictions_list:
        pred["_id"] = str(pred["_id"])
    
    return {
        "user_id": user_id,
        "total_predictions": len(predictions_list),
        "predictions": predictions_list
    }


@app.get("/prices/{coin}")
async def get_coin_prices(coin: str, limit: int = 100):
    """Get price history for a coin"""
    # Get current price
    prices = get_binance_prices(coin, "4h", 2)
    current_price = prices[-1] if prices else 0
    
    # Store in history
    await coin_history.insert_one({
        "coin": coin.upper(),
        "price": current_price,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get history
    history = await coin_history.find({"coin": coin.upper()}).sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Convert ObjectId
    for item in history:
        item["_id"] = str(item["_id"])
    
    return {
        "coin": coin.upper(),
        "current_price": current_price,
        "history": history,
        "count": len(history)
    }



if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 CRYPTO PREDICTOR PRO - REAL SOLANA VERIFICATION")
    print("="*60)
    print(f"💰 Payment Address: {YOUR_WALLET}")
    print(f"🌐 Solana Devnet RPC: {SOLANA_RPC_URL}")
    print(f"🔍 Using direct RPC calls for verification")
    print("="*60 + "\n")
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)