import asyncio
import websockets
import json
import requests
from datetime import datetime
import time

class LiveCryptoWebSocketServer:
    def __init__(self):
        self.connected_clients = set()
        self.client_subscriptions = {}
        self.binance_url = "https://api.binance.com/api/v3/klines"
        
        # Supported coins and intervals
        self.supported_coins = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum", 
            "SOL": "Solana",
            "BNB": "Binance Coin",
            "XRP": "Ripple",
            "DOGE": "Dogecoin",
            "ADA": "Cardano",
            "MATIC": "Polygon"
        }
        
        self.supported_intervals = ["4h", "1d", "1w"]
        
        # Cache for storing fetched data
        self.data_cache = {}
        self.last_update_time = {}
    
    async def fetch_candles(self, coin: str, interval: str) -> list:
        """Fetch last 1000 candles for given coin and interval"""
        try:
            symbol = f"{coin}USDT"
            binance_interval = interval
            
            url = f"{self.binance_url}?symbol={symbol}&interval={binance_interval}&limit=1000"
            print(f"📥 Fetching {coin} {interval} data...")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            candles = []
            for candle in response.json():
                candles.append({
                    "time": int(candle[0]),      # Unix timestamp in milliseconds
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5])
                })
            
            # Cache the data
            cache_key = f"{coin}_{interval}"
            self.data_cache[cache_key] = candles
            self.last_update_time[cache_key] = datetime.now()
            
            print(f"✅ Fetched {len(candles)} {coin} {interval} candles")
            print(f"   First candle: {datetime.fromtimestamp(candles[0]['time']/1000)}")
            print(f"   Last candle: {datetime.fromtimestamp(candles[-1]['time']/1000)}")
            print(f"   Price range: ${candles[0]['open']:.2f} - ${candles[-1]['close']:.2f}")
            
            return candles
            
        except Exception as e:
            print(f"❌ Error fetching {coin} {interval}: {e}")
            return []
    
    async def handle_client(self, websocket, path):
        """Handle individual client connection"""
        client_id = id(websocket)
        self.connected_clients.add(websocket)
        
        print(f"📡 Client {client_id} connected")
        
        try:
            async for message in websocket:
                try:
                    request = json.loads(message)
                    
                    if "action" not in request:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "Missing 'action' in request"
                        }))
                        continue
                    
                    if request["action"] == "subscribe":
                        coin = request.get("coin", "").upper()
                        interval = request.get("interval", "")
                        
                        if not coin or not interval:
                            await websocket.send(json.dumps({
                                "type": "error", 
                                "message": "Missing 'coin' or 'interval' in subscribe request"
                            }))
                            continue
                        
                        # Validate
                        if coin not in self.supported_coins:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": f"Unsupported coin. Supported: {', '.join(self.supported_coins.keys())}"
                            }))
                            continue
                        
                        if interval not in self.supported_intervals:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": f"Unsupported interval. Supported: {', '.join(self.supported_intervals)}"
                            }))
                            continue
                        
                        # Store subscription
                        self.client_subscriptions[websocket] = (coin, interval)
                        
                        print(f"📊 Client {client_id} subscribed to {coin} {interval}")
                        
                        # Fetch and send data
                        cache_key = f"{coin}_{interval}"
                        
                        # Fetch fresh data
                        candles = await self.fetch_candles(coin, interval)
                        
                        if candles:
                            # Send ALL candles in response
                            response_data = {
                                "type": "candles",
                                "timestamp": datetime.now().isoformat(),
                                "coin": coin,
                                "coin_name": self.supported_coins[coin],
                                "interval": interval,
                                "candles": candles,  # Sending ALL 1000 candles
                                "count": len(candles),
                                "first_candle": {
                                    "time": candles[0]["time"],
                                    "date": datetime.fromtimestamp(candles[0]["time"]/1000).isoformat(),
                                    "price": candles[0]["open"]
                                },
                                "last_candle": {
                                    "time": candles[-1]["time"],
                                    "date": datetime.fromtimestamp(candles[-1]["time"]/1000).isoformat(),
                                    "price": candles[-1]["close"]
                                },
                                "price_range": {
                                    "lowest": min(c["low"] for c in candles),
                                    "highest": max(c["high"] for c in candles)
                                }
                            }
                            
                            # Send response
                            response_json = json.dumps(response_data)
                            print(f"📤 Sending {len(candles)} candles to client {client_id} ({len(response_json)} bytes)")
                            
                            await websocket.send(response_json)
                            print(f"✅ Data sent successfully to client {client_id}")
                        else:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": f"Could not fetch data for {coin} {interval}"
                            }))
                    
                    elif request["action"] == "unsubscribe":
                        if websocket in self.client_subscriptions:
                            coin, interval = self.client_subscriptions[websocket]
                            del self.client_subscriptions[websocket]
                            print(f"📊 Client {client_id} unsubscribed from {coin} {interval}")
                        
                        await websocket.send(json.dumps({
                            "type": "status",
                            "message": "Unsubscribed successfully"
                        }))
                    
                    else:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": f"Unknown action: {request['action']}"
                        }))
                        
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Server error: {str(e)}"
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"📡 Client {client_id} disconnected")
        finally:
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
            if websocket in self.client_subscriptions:
                del self.client_subscriptions[websocket]
    
    async def periodic_update(self):
        """Update data every 4 hours and push to subscribed clients"""
        print("🔄 Starting periodic updates (every 4 hours)...")
        
        while True:
            try:
                # Wait 4 hours
                await asyncio.sleep(14400)
                
                print(f"\n⏰ Scheduled update at {datetime.now().strftime('%H:%M:%S')}")
                
                # Get unique subscriptions
                subscriptions_to_update = set()
                for coin, interval in self.client_subscriptions.values():
                    subscriptions_to_update.add((coin, interval))
                
                if not subscriptions_to_update:
                    print("📭 No active subscriptions to update")
                    continue
                
                print(f"📊 Updating {len(subscriptions_to_update)} subscription(s)...")
                
                # Update each subscription
                for coin, interval in subscriptions_to_update:
                    candles = await self.fetch_candles(coin, interval)
                    
                    if candles:
                        # Prepare update with ALL candles
                        update_msg = {
                            "type": "update",
                            "timestamp": datetime.now().isoformat(),
                            "coin": coin,
                            "coin_name": self.supported_coins[coin],
                            "interval": interval,
                            "candles": candles,  # ALL candles
                            "count": len(candles),
                            "update_type": "full_refresh"
                        }
                        
                        update_json = json.dumps(update_msg)
                        print(f"  📤 Sending {len(candles)} {coin} {interval} candles ({len(update_json)} bytes)")
                        
                        # Send to subscribed clients
                        sent_count = 0
                        for client, (sub_coin, sub_interval) in list(self.client_subscriptions.items()):
                            if sub_coin == coin and sub_interval == interval:
                                try:
                                    await client.send(update_json)
                                    sent_count += 1
                                except:
                                    # Client disconnected
                                    pass
                        
                        print(f"  ✅ Update sent to {sent_count} client(s)")
                
                print("✅ Update cycle completed")
                
            except Exception as e:
                print(f"❌ Error in periodic update: {e}")
    
    async def run_server(self):
        """Start the WebSocket server"""
        print("🚀 Live Crypto WebSocket Server Starting...")
        print("="*60)
        print("📊 Supported Coins:")
        for symbol, name in self.supported_coins.items():
            print(f"   • {symbol}: {name}")
        print(f"\n📈 Supported Timeframes: {', '.join(self.supported_intervals)}")
        print(f"\n🌐 Server: ws://localhost:8765")
        print(f"⏰ Updates: Every 4 hours")
        print(f"📊 Data: Last 1000 candles per coin/interval")
        print("="*60)
        
        # Start periodic update
        update_task = asyncio.create_task(self.periodic_update())
        
        # Start WebSocket server
        port = int(os.getenv("PORT", 8765))  # Use Render-provided PORT
        async with websockets.serve(self.handle_client, "localhost", port):
            print("✅ WebSocket server started!")
            print("⏳ Waiting for client connections...")
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    server = LiveCryptoWebSocketServer()
    asyncio.run(server.run_server())