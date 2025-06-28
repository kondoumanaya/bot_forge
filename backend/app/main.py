from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import structlog
import asyncio
from datetime import datetime, timedelta

from .config import settings
from .database import init_db, get_db
from .models import (
    TickDataResponse, OrderBookResponse, OHLCResponse, TradeHistoryResponse,
    DataCollectionRequest, BacktestRequest, TickData, OrderBookData, OHLCData, TradeHistory,
    ExchangeApiKey, ExchangeApiKeyRequest, ExchangeApiKeyResponse
)
from .websocket_manager import manager, data_stream_manager
from .topgun_integration import topgun_collector
from .backtest_engine import backtest_engine
from .routes.settings import router as settings_router
from .routes.analysis import router as analysis_router
from .routes.data import router as data_router

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title=settings.app_name,
    description="Cryptocurrency Trading Bot Forge System",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(settings_router)
app.include_router(analysis_router)
app.include_router(data_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks"""
    init_db()
    logger.info("Bot Forge System started", version="1.0.0")

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "timestamp": datetime.utcnow()}

@app.get("/api/config")
async def get_config():
    """Get system configuration"""
    return {
        "supported_exchanges": settings.supported_exchanges,
        "supported_timeframes": settings.supported_timeframes,
        "default_exchange": settings.default_exchange,
        "default_timeframe": settings.default_timeframe
    }

@app.post("/api/data/start-collection")
async def start_data_collection(request: DataCollectionRequest):
    """Start data collection for specified exchange and symbol"""
    try:
        success = await topgun_collector.start_collection(
            request.exchange, 
            request.symbol, 
            request.data_types
        )

        if success:
            await data_stream_manager.start_data_stream(
                request.exchange,
                request.symbol,
                request.data_types
            )

            return {
                "status": "success",
                "message": f"Started data collection for {request.exchange}:{request.symbol}",
                "data_types": request.data_types
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start data collection")

    except Exception as e:
        logger.error("Failed to start data collection", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/stop-collection")
async def stop_data_collection(exchange: str, symbol: str):
    """Stop data collection for specified exchange and symbol"""
    try:
        await topgun_collector.stop_collection(exchange, symbol)
        await data_stream_manager.stop_data_stream(exchange, symbol)

        return {
            "status": "success",
            "message": f"Stopped data collection for {exchange}:{symbol}"
        }
    except Exception as e:
        logger.error("Failed to stop data collection", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/tick", response_model=List[TickDataResponse])
async def get_tick_data(
    exchange: str,
    symbol: str,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get recent tick data"""
    try:
        ticks = db.query(TickData).filter(
            TickData.exchange == exchange,
            TickData.symbol == symbol
        ).order_by(TickData.timestamp.desc()).limit(limit).all()

        return ticks
    except Exception as e:
        logger.error("Failed to get tick data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/orderbook", response_model=List[OrderBookResponse])
async def get_orderbook_data(
    exchange: str,
    symbol: str,
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db)
):
    """Get recent orderbook data"""
    try:
        orderbooks = db.query(OrderBookData).filter(
            OrderBookData.exchange == exchange,
            OrderBookData.symbol == symbol
        ).order_by(OrderBookData.timestamp.desc()).limit(limit).all()

        return [OrderBookResponse.from_orm(ob) for ob in orderbooks]
    except Exception as e:
        logger.error("Failed to get orderbook data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/ohlc", response_model=List[OHLCResponse])
async def get_ohlc_data(
    exchange: str,
    symbol: str,
    timeframe: str,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get OHLC data"""
    try:
        ohlc_data = db.query(OHLCData).filter(
            OHLCData.exchange == exchange,
            OHLCData.symbol == symbol,
            OHLCData.timeframe == timeframe
        ).order_by(OHLCData.timestamp.desc()).limit(limit).all()

        return ohlc_data
    except Exception as e:
        logger.error("Failed to get OHLC data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    """Run backtest for trading strategy"""
    try:
        result = await backtest_engine.run_backtest(
            strategy_name=request.strategy_name,
            exchange=request.exchange,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_balance=request.initial_balance,
            parameters=getattr(request, 'parameters', {})
        )

        return result
    except Exception as e:
        logger.error("Failed to run backtest", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{exchange}/{symbol}")
async def websocket_endpoint(websocket: WebSocket, exchange: str, symbol: str):
    """WebSocket endpoint for real-time data streaming"""
    await manager.connect(websocket, exchange, symbol)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info("Received WebSocket message", data=data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected", exchange=exchange, symbol=symbol)

@app.websocket("/ws/general")
async def general_websocket_endpoint(websocket: WebSocket):
    """General WebSocket endpoint for system-wide updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info("Received general WebSocket message", data=data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("General WebSocket disconnected")
