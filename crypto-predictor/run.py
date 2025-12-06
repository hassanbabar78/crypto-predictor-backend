#!/usr/bin/env python3
"""
Combined server runner for Render deployment
Runs both FastAPI and WebSocket servers in one process
"""

import asyncio
import os
import signal
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

# Import our modules
from main import app as fastapi_app
from websocket_server import LiveCryptoWebSocketServer

# Global variable to store servers
websocket_server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print("=" * 60)
    print("🚀 CRYPTO PREDICTOR PRO - PRODUCTION DEPLOYMENT")
    print("=" * 60)
    
    # Start WebSocket server in background
    print("🌐 Starting WebSocket server...")
    global websocket_server
    websocket_server = LiveCryptoWebSocketServer()
    
    # Start WebSocket server as background task
    ws_port = int(os.getenv("WS_PORT", 8765))
    ws_task = asyncio.create_task(start_websocket(websocket_server, ws_port))
    
    print(f"✅ FastAPI server starting on port {os.getenv('PORT', 8000)}")
    print(f"✅ WebSocket server starting on port {ws_port}")
    print(f"💰 Payment Address: {os.getenv('YOUR_WALLET', 'Not set')}")
    print("=" * 60)
    
    yield
    
    # Shutdown
    print("\n🛑 Shutting down servers...")
    if websocket_server:
        # Clean up WebSocket connections
        for client in list(websocket_server.connected_clients):
            try:
                await client.close()
            except:
                pass
    
    # Cancel WebSocket task
    if ws_task:
        ws_task.cancel()
        try:
            await ws_task
        except asyncio.CancelledError:
            pass
    
    print("✅ Servers shut down cleanly")

async def start_websocket(server, port):
    """Start WebSocket server"""
    import websockets
    
    async with websockets.serve(server.handle_client, "0.0.0.0", port):
        print(f"   WebSocket: Listening on ws://0.0.0.0:{port}")
        await asyncio.Future()  # Run forever

async def run_fastapi():
    """Run FastAPI with uvicorn"""
    port = int(os.getenv("PORT", 8000))
    
    config = uvicorn.Config(
        app=fastapi_app,
        host="0.0.0.0",
        port=port,
        lifespan="on",
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Main async entry point"""
    # Set up signal handlers
    loop = asyncio.get_running_loop()
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))
    
    try:
        # Run both servers
        await asyncio.gather(
            run_fastapi(),
        )
    except asyncio.CancelledError:
        print("\n📡 Server shutdown requested")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

async def shutdown():
    """Graceful shutdown"""
    print("\n⏳ Graceful shutdown initiated...")
    
    # Get all running tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    
    # Cancel all tasks
    for task in tasks:
        task.cancel()
    
    # Wait for tasks to complete
    await asyncio.gather(*tasks, return_exceptions=True)
    
    print("✅ All tasks stopped")

if __name__ == "__main__":
    # Add lifespan to FastAPI app
    fastapi_app.router.lifespan_context = lifespan
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)