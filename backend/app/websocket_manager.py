import asyncio
import json
import structlog
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
from .models import WSMessage
from .config import settings

logger = structlog.get_logger()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.exchange_connections: Dict[str, Set[WebSocket]] = {}
        self.symbol_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, exchange: Optional[str] = None, symbol: Optional[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if exchange:
            if exchange not in self.exchange_connections:
                self.exchange_connections[exchange] = set()
            self.exchange_connections[exchange].add(websocket)
            
        if symbol:
            if symbol not in self.symbol_connections:
                self.symbol_connections[symbol] = set()
            self.symbol_connections[symbol].add(websocket)
            
        logger.info("WebSocket connected", 
                   exchange=exchange, 
                   symbol=symbol, 
                   total_connections=len(self.active_connections))
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        for exchange, connections in self.exchange_connections.items():
            connections.discard(websocket)
            
        for symbol, connections in self.symbol_connections.items():
            connections.discard(websocket)
            
        logger.info("WebSocket disconnected", total_connections=len(self.active_connections))
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error("Failed to send personal message", error=str(e))
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error("Failed to broadcast message", error=str(e))
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_exchange(self, exchange: str, message: str):
        if exchange not in self.exchange_connections:
            return
            
        disconnected = []
        for connection in self.exchange_connections[exchange]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error("Failed to broadcast to exchange", exchange=exchange, error=str(e))
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_symbol(self, symbol: str, message: str):
        if symbol not in self.symbol_connections:
            return
            
        disconnected = []
        for connection in self.symbol_connections[symbol]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error("Failed to broadcast to symbol", symbol=symbol, error=str(e))
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

class DataStreamManager:
    def __init__(self):
        self.active_streams: Dict[str, asyncio.Task] = {}
        self.stream_data: Dict[str, Any] = {}
        
    async def start_data_stream(self, exchange: str, symbol: str, data_types: List[str]):
        stream_key = f"{exchange}_{symbol}"
        
        if stream_key in self.active_streams:
            logger.info("Data stream already active", stream_key=stream_key)
            return
        
        task = asyncio.create_task(
            self._collect_data(exchange, symbol, data_types)
        )
        self.active_streams[stream_key] = task
        
        logger.info("Started data stream", 
                   exchange=exchange, 
                   symbol=symbol, 
                   data_types=data_types)
    
    async def stop_data_stream(self, exchange: str, symbol: str):
        stream_key = f"{exchange}_{symbol}"
        
        if stream_key in self.active_streams:
            task = self.active_streams[stream_key]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            del self.active_streams[stream_key]
            logger.info("Stopped data stream", stream_key=stream_key)
    
    async def _collect_data(self, exchange: str, symbol: str, data_types: List[str]):
        """Collect data from exchange and broadcast to WebSocket clients"""
        try:
            while True:
                if "tick" in data_types:
                    tick_data = {
                        "type": "tick",
                        "exchange": exchange,
                        "symbol": symbol,
                        "price": 50000.0 + (asyncio.get_event_loop().time() % 1000),
                        "volume": 0.1,
                        "side": "buy",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    message = WSMessage(type="tick_data", data=tick_data)
                    await manager.broadcast_to_symbol(
                        symbol, 
                        json.dumps(message.dict(), default=str)
                    )
                
                if "orderbook" in data_types:
                    orderbook_data = {
                        "type": "orderbook",
                        "exchange": exchange,
                        "symbol": symbol,
                        "bids": [[49990.0, 0.5], [49980.0, 1.0]],
                        "asks": [[50010.0, 0.3], [50020.0, 0.8]],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    message = WSMessage(type="orderbook_data", data=orderbook_data)
                    await manager.broadcast_to_symbol(
                        symbol,
                        json.dumps(message.dict(), default=str)
                    )
                
                await asyncio.sleep(1)  # Update every second
                
        except asyncio.CancelledError:
            logger.info("Data collection cancelled", exchange=exchange, symbol=symbol)
        except Exception as e:
            logger.error("Error in data collection", 
                        exchange=exchange, 
                        symbol=symbol, 
                        error=str(e))

data_stream_manager = DataStreamManager()
