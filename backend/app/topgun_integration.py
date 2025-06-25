import sys
import os
import asyncio
import structlog
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import aiohttp

topgun_path = "/home/ubuntu/repos/bot_forge/libs/root-bot/topgun"
sys.path.insert(0, topgun_path)

try:
    from topgun.ws import WebSocketApp
    from topgun.store import DataStore, DataStoreCollection
    TOPGUN_AVAILABLE = True
except ImportError as e:
    TOPGUN_AVAILABLE = False
    print(f"Warning: topgun library not available: {e}")
    print(f"Topgun path: {topgun_path}")
    print(f"Path exists: {os.path.exists(topgun_path)}")
    if os.path.exists(topgun_path):
        print(f"Contents: {os.listdir(topgun_path)}")

from .models import TickData, OrderBookData, OHLCData
from .database import SessionLocal
from .websocket_manager import manager
from .config import settings

logger = structlog.get_logger()

class TopgunDataCollector:
    def __init__(self):
        self.active_connections: Dict[str, WebSocketApp] = {}
        self.data_stores: Dict[str, DataStore] = {}
        self.is_collecting = False
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def start_collection(self, exchange: str, symbol: str, data_types: List[str]):
        """Start data collection from exchange using topgun"""
        if not TOPGUN_AVAILABLE:
            logger.error("Topgun library not available")
            return False
            
        connection_key = f"{exchange}_{symbol}"
        
        if connection_key in self.active_connections:
            logger.info("Collection already active", connection_key=connection_key)
            return True
        
        try:
            if exchange.lower() == "gmo":
                ws_url = "wss://api.coin.z.com/ws/public/v1"
            elif exchange.lower() == "binance":
                binance_symbol = symbol.replace("_", "").lower()
                if "jpy" in binance_symbol:
                    binance_symbol = binance_symbol.replace("jpy", "usdt")
                ws_url = f"wss://stream.binance.com:9443/ws/{binance_symbol}@ticker"
            else:
                logger.error("Unsupported exchange", exchange=exchange)
                return False
            
            logger.info("Creating WebSocket connection", url=ws_url)
            
            if self.session is None:
                self.session = aiohttp.ClientSession()
            
            async def message_handler(data: dict):
                await self._handle_message(exchange, symbol, data, data_types)
            
            ws_app = WebSocketApp(
                session=self.session,
                url=ws_url,
                hdlr_json=[message_handler]
            )
            
            self.active_connections[connection_key] = ws_app
            logger.info("Started topgun data collection", 
                       exchange=exchange, 
                       symbol=symbol, 
                       data_types=data_types)
            
            return True
            
        except Exception as e:
            import traceback
            logger.error("Failed to start topgun collection", 
                        exchange=exchange, 
                        symbol=symbol, 
                        error=str(e),
                        traceback=traceback.format_exc())
            return False
    
    async def stop_collection(self, exchange: str, symbol: str):
        """Stop data collection for exchange/symbol"""
        connection_key = f"{exchange}_{symbol}"
        
        if connection_key in self.active_connections:
            ws_app = self.active_connections[connection_key]
            if hasattr(ws_app, '_task') and ws_app._task:
                ws_app._task.cancel()
            del self.active_connections[connection_key]
            
            logger.info("Stopped topgun data collection", connection_key=connection_key)
    
    async def _handle_message(self, exchange: str, symbol: str, data: Dict[str, Any], data_types: List[str]):
        """Handle incoming WebSocket message from topgun"""
        try:
            logger.info("Received message from topgun", 
                       exchange=exchange, 
                       symbol=symbol, 
                       data_keys=list(data.keys()) if isinstance(data, dict) else type(data))
            
            if "tick" in data_types:
                await self._process_tick_data(exchange, symbol, data)
            
            if "orderbook" in data_types:
                await self._process_orderbook_data(exchange, symbol, data)
                
            if "ohlc" in data_types:
                await self._process_ohlc_data(exchange, symbol, data)
                
        except Exception as e:
            logger.error("Error processing topgun message", 
                        exchange=exchange, 
                        symbol=symbol, 
                        error=str(e))
    
    async def _process_tick_data(self, exchange: str, symbol: str, data: Dict[str, Any]):
        """Process and store tick data"""
        try:
            if exchange.lower() == "gmo":
                if data.get("channel") == "trades":
                    for trade in data.get("trades", []):
                        tick = TickData(
                            exchange=exchange,
                            symbol=symbol,
                            price=float(trade["price"]),
                            volume=float(trade["size"]),
                            side=trade["side"],
                            timestamp=datetime.fromisoformat(trade["timestamp"].replace("Z", "+00:00"))
                        )
                        await self._save_tick_data(tick)
                        
            elif exchange.lower() == "binance":
                if "c" in data:  # Current price
                    tick = TickData(
                        exchange=exchange,
                        symbol=symbol,
                        price=float(data["c"]),
                        volume=float(data.get("v", 0)),
                        side="unknown",
                        timestamp=datetime.utcnow()
                    )
                    await self._save_tick_data(tick)
                    
        except Exception as e:
            logger.error("Error processing tick data", error=str(e))
    
    async def _process_orderbook_data(self, exchange: str, symbol: str, data: Dict[str, Any]):
        """Process and store orderbook data"""
        try:
            bids = []
            asks = []
            
            if exchange.lower() == "gmo":
                if data.get("channel") == "orderbooks":
                    bids = data.get("bids", [])
                    asks = data.get("asks", [])
                    
            elif exchange.lower() == "binance":
                bids = data.get("bids", [])
                asks = data.get("asks", [])
            
            if bids or asks:
                orderbook = OrderBookData(
                    exchange=exchange,
                    symbol=symbol,
                    bids=json.dumps(bids[:settings.max_orderbook_depth]),
                    asks=json.dumps(asks[:settings.max_orderbook_depth]),
                    timestamp=datetime.utcnow()
                )
                await self._save_orderbook_data(orderbook)
                
        except Exception as e:
            logger.error("Error processing orderbook data", error=str(e))
    
    async def _process_ohlc_data(self, exchange: str, symbol: str, data: Dict[str, Any]):
        """Process and store OHLC data"""
        try:
            pass
        except Exception as e:
            logger.error("Error processing OHLC data", error=str(e))
    
    async def _save_tick_data(self, tick: TickData):
        """Save tick data to database and broadcast to WebSocket clients"""
        try:
            db = SessionLocal()
            try:
                db.add(tick)
                db.commit()
                db.refresh(tick)
            finally:
                db.close()
            
            message_data = {
                "type": "tick",
                "exchange": tick.exchange,
                "symbol": tick.symbol,
                "price": tick.price,
                "volume": tick.volume,
                "side": tick.side,
                "timestamp": tick.timestamp.isoformat()
            }
            
            await manager.broadcast_to_symbol(
                tick.symbol,
                json.dumps({"type": "tick_data", "data": message_data})
            )
            
        except Exception as e:
            logger.error("Error saving tick data", error=str(e))
    
    async def _save_orderbook_data(self, orderbook: OrderBookData):
        """Save orderbook data to database and broadcast to WebSocket clients"""
        try:
            db = SessionLocal()
            try:
                db.add(orderbook)
                db.commit()
                db.refresh(orderbook)
            finally:
                db.close()
            
            message_data = {
                "type": "orderbook",
                "exchange": orderbook.exchange,
                "symbol": orderbook.symbol,
                "bids": json.loads(orderbook.bids),
                "asks": json.loads(orderbook.asks),
                "timestamp": orderbook.timestamp.isoformat()
            }
            
            await manager.broadcast_to_symbol(
                orderbook.symbol,
                json.dumps({"type": "orderbook_data", "data": message_data})
            )
            
        except Exception as e:
            logger.error("Error saving orderbook data", error=str(e))

topgun_collector = TopgunDataCollector()
