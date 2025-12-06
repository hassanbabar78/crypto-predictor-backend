#!/bin/bash

# ===========================================
# COMPLETE CRYPTO PREDICTOR API TESTING
# ===========================================

# Set your user ID and test transaction hash
USER_ID="7d02453cc663"
TX_HASH="3xpvnRVf9JTbmuNXRMbNEw59Q2J9gKX7F4GFo9pCVYtV2Y8SNaELjoDANVAiP5xwvHgZQcfDdd6DTZknyWqyt4JG"

echo "=================================================================="
echo "🚀 TEST 1: HEALTH CHECK"
echo "=================================================================="
curl -s http://localhost:8000/health
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 2: ROOT ENDPOINT"
echo "=================================================================="
curl -s http://localhost:8000/
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 3: USER STATUS (BEFORE PAYMENT)"
echo "=================================================================="
curl -s "http://localhost:8000/user/$USER_ID/status"
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 4: TRY PREDICTION WITHOUT PAYMENT (SHOULD FAIL)"
echo "=================================================================="
curl -s -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$USER_ID\",\"coin\":\"BTC\"}"
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 5: VERIFY PAYMENT WITH TEST HASH"
echo "=================================================================="
curl -s -X POST "http://localhost:8000/verify-payment" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$USER_ID\",\"tx_hash\":\"$TX_HASH\"}"
echo -e "\n"

echo "=================================================================="
echo "�� TEST 6: LOGIN TO CHECK PAYMENT STATUS"
echo "=================================================================="
curl -s -X POST "http://localhost:8000/login?name=crypto_pro&password=secure123"
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 7: USER STATUS (AFTER PAYMENT)"
echo "=================================================================="
curl -s "http://localhost:8000/user/$USER_ID/status"
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 8: GET PREDICTION FOR BTC (TAKES 10-15 SECONDS)"
echo "=================================================================="
echo "This will take 10-15 seconds. Starting now..."
START_TIME=$(date +%s)
RESPONSE=$(curl -s -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$USER_ID\",\"coin\":\"BTC\"}")
END_TIME=$(date +%s)
echo "$RESPONSE"
echo -e "\n⏰ Prediction took $((END_TIME - START_TIME)) seconds"

echo "=================================================================="
echo "🚀 TEST 9: GET PREDICTION FOR ETH (TAKES 10-15 SECONDS)"
echo "=================================================================="
echo "Starting ETH prediction..."
START_TIME=$(date +%s)
RESPONSE=$(curl -s -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$USER_ID\",\"coin\":\"ETH\"}")
END_TIME=$(date +%s)
echo "$RESPONSE"
echo -e "\n⏰ Prediction took $((END_TIME - START_TIME)) seconds"

echo "=================================================================="
echo "🚀 TEST 10: GET PREDICTION HISTORY"
echo "=================================================================="
curl -s "http://localhost:8000/predictions/$USER_ID"
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 11: GET BTC PRICE HISTORY"
echo "=================================================================="
curl -s "http://localhost:8000/prices/BTC"
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 12: GET ALL COIN PRICES"
echo "=================================================================="
curl -s "http://localhost:8000/all-prices"
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 13: GET CURRENT BTC PRICE"
echo "=================================================================="
curl -s "http://localhost:8000/prices/BTC?limit=1"
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 14: TRY PREDICTION WITH WRONG COIN (SHOULD FAIL)"
echo "=================================================================="
curl -s -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$USER_ID\",\"coin\":\"INVALIDCOIN\"}"
echo -e "\n"

echo "=================================================================="
echo "🚀 TEST 15: CHECK CREDITS AFTER PREDICTIONS"
echo "=================================================================="
curl -s -X POST "http://localhost:8000/login?name=crypto_pro&password=secure123"
echo -e "\n"

echo "✅ ALL TESTS COMPLETED!"
