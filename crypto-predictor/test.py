# test_client.py
import asyncio
import websockets
import json

async def test_full_candles():
    """Test that we receive ALL candle data"""
    try:
        async with websockets.connect("ws://localhost:8765") as ws:
            print("🔗 Connected to server")
            
            # Subscribe to BTC 4h
            subscribe_msg = {
                "action": "subscribe",
                "coin": "BTC",
                "interval": "4h"
            }
            
            await ws.send(json.dumps(subscribe_msg))
            print("📤 Subscribed to BTC 4h")
            
            # Get response
            response = await ws.recv()
            data = json.loads(response)
            
            print(f"\n📊 Response received:")
            print(f"   Type: {data['type']}")
            print(f"   Coin: {data['coin']} ({data['coin_name']})")
            print(f"   Interval: {data['interval']}")
            print(f"   Total candles: {data['count']}")
            
            # Verify we have all candles
            candles = data['candles']
            print(f"\n✅ Candle data details:")
            print(f"   First candle index 0: Time={candles[0]['time']}, Open=${candles[0]['open']:.2f}")
            print(f"   Candle index 100: Time={candles[100]['time']}, Open=${candles[100]['open']:.2f}")
            print(f"   Candle index 500: Time={candles[500]['time']}, Open=${candles[500]['open']:.2f}")
            print(f"   Last candle index 999: Time={candles[-1]['time']}, Close=${candles[-1]['close']:.2f}")
            
            # Print first few candles for verification
            print(f"\n📈 First 5 candles:")
            for i in range(5):
                c = candles[i]
                print(f"   [{i}] Time: {c['time']}, O:{c['open']:.2f} H:{c['high']:.2f} L:{c['low']:.2f} C:{c['close']:.2f}")
            
            print(f"\n📉 Last 5 candles:")
            for i in range(-5, 0):
                c = candles[i]
                print(f"   [{len(candles)+i}] Time: {c['time']}, O:{c['open']:.2f} H:{c['high']:.2f} L:{c['low']:.2f} C:{c['close']:.2f}")
            
            # Wait for update
            print(f"\n⏳ Waiting for next update (every 4 hours)...")
            update_response = await ws.recv()
            update_data = json.loads(update_response)
            
            print(f"\n🔄 Update received:")
            print(f"   Type: {update_data['type']}")
            print(f"   Candles in update: {len(update_data['candles'])}")
            print(f"   Latest close: ${update_data['candles'][-1]['close']:.2f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_candles())