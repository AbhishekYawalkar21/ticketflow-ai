from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import json
import logging

from app.database import init_db
from app.api import api_router
from app.config import settings
from app.middleware import RequestIDMiddleware, LoggingMiddleware, ErrorHandlerMiddleware
from app.logging_config import setup_logging

# Setup logging
setup_logging(debug=settings.DEBUG)
logger = logging.getLogger(__name__)

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
    
    async def broadcast(self, message: dict):
        """Broadcast to all connected clients"""
        for connection in self.active_connections.values():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {str(e)}")
    
    async def send_personal(self, client_id: str, message: dict):
        """Send to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending personal message: {str(e)}")

manager = ConnectionManager()

# Startup/Shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting TicketFlow AI")
    await init_db()
    logger.info("✅ Database initialized")
    
    # Check Ollama connection
    try:
        import requests
        requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=2)
        logger.info("✅ Ollama connected")
    except:
        logger.warning("⚠️  Ollama not available - classification will be disabled")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down TicketFlow AI")

# Create FastAPI app
app = FastAPI(
    title="TicketFlow AI",
    description="Intelligent Support Ticket Classification & Automation",
    version="0.5.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
)

# Add middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"] if settings.DEBUG else []
)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat()
    }

# WebSocket for real-time updates
@app.websocket("/ws/tickets/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time ticket updates"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Receive from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"WebSocket message from {client_id}: {message}")
            
            # Broadcast to all clients
            await manager.broadcast({
                "client": client_id,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast({
            "type": "user_disconnected",
            "client": client_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(client_id)

# Include API routes
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "TicketFlow AI",
        "version": "0.5.0",
        "docs": "/api/docs" if settings.DEBUG else "Not available",
        "websocket": "/ws/tickets/{client_id}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.ENVIRONMENT == "production" else "debug"
    )