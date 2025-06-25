from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import json
from datetime import datetime, timedelta
import structlog

from ..database import get_db
from ..models import TickData, OrderBookData, OHLCData, TickDataResponse, OrderBookResponse, OHLCResponse
from ..config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/api/data", tags=["data"])

@router.get("/export/csv")
async def export_data_csv(
    exchange: str,
    symbol: str,
    data_type: str = Query(..., regex="^(tick|orderbook|ohlc)$"),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    db: Session = Depends(get_db)
):
    """Export data as CSV"""
    try:
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        if data_type == "tick":
            query = db.query(TickData).filter(
                TickData.exchange == exchange,
                TickData.symbol == symbol,
                TickData.timestamp >= start_date,
                TickData.timestamp <= end_date
            )
            data = query.all()
            
            df = pd.DataFrame([{
                'timestamp': item.timestamp,
                'price': item.price,
                'volume': item.volume,
                'side': item.side
            } for item in data])
            
        elif data_type == "orderbook":
            query = db.query(OrderBookData).filter(
                OrderBookData.exchange == exchange,
                OrderBookData.symbol == symbol,
                OrderBookData.timestamp >= start_date,
                OrderBookData.timestamp <= end_date
            )
            data = query.all()
            
            df = pd.DataFrame([{
                'timestamp': item.timestamp,
                'bids': item.bids,
                'asks': item.asks
            } for item in data])
            
        elif data_type == "ohlc":
            query = db.query(OHLCData).filter(
                OHLCData.exchange == exchange,
                OHLCData.symbol == symbol,
                OHLCData.timestamp >= start_date,
                OHLCData.timestamp <= end_date
            )
            data = query.all()
            
            df = pd.DataFrame([{
                'timestamp': item.timestamp,
                'open': item.open_price,
                'high': item.high_price,
                'low': item.low_price,
                'close': item.close_price,
                'volume': item.volume,
                'timeframe': item.timeframe
            } for item in data])
        
        csv_data = df.to_csv(index=False)
        
        return {
            "status": "success",
            "data": csv_data,
            "rows": len(df),
            "format": "csv"
        }
        
    except Exception as e:
        logger.error("Failed to export CSV data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/json")
async def export_data_json(
    exchange: str,
    symbol: str,
    data_type: str = Query(..., regex="^(tick|orderbook|ohlc)$"),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    db: Session = Depends(get_db)
):
    """Export data as JSON for o3 integration"""
    try:
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        if data_type == "tick":
            query = db.query(TickData).filter(
                TickData.exchange == exchange,
                TickData.symbol == symbol,
                TickData.timestamp >= start_date,
                TickData.timestamp <= end_date
            )
            data = query.all()
            
            json_data = {
                "metadata": {
                    "exchange": exchange,
                    "symbol": symbol,
                    "data_type": data_type,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "count": len(data)
                },
                "data": [{
                    "timestamp": item.timestamp.isoformat(),
                    "price": item.price,
                    "volume": item.volume,
                    "side": item.side
                } for item in data]
            }
            
        elif data_type == "orderbook":
            query = db.query(OrderBookData).filter(
                OrderBookData.exchange == exchange,
                OrderBookData.symbol == symbol,
                OrderBookData.timestamp >= start_date,
                OrderBookData.timestamp <= end_date
            )
            data = query.all()
            
            json_data = {
                "metadata": {
                    "exchange": exchange,
                    "symbol": symbol,
                    "data_type": data_type,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "count": len(data)
                },
                "data": [{
                    "timestamp": item.timestamp.isoformat(),
                    "bids": json.loads(item.bids),
                    "asks": json.loads(item.asks)
                } for item in data]
            }
        
        return {
            "status": "success",
            "data": json_data,
            "format": "json"
        }
        
    except Exception as e:
        logger.error("Failed to export JSON data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_data_stats(
    exchange: str = Query(None),
    symbol: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get data collection statistics"""
    try:
        stats = {}
        
        tick_query = db.query(TickData)
        if exchange:
            tick_query = tick_query.filter(TickData.exchange == exchange)
        if symbol:
            tick_query = tick_query.filter(TickData.symbol == symbol)
        
        stats["tick_data"] = {
            "total_records": tick_query.count(),
            "latest_timestamp": tick_query.order_by(TickData.timestamp.desc()).first().timestamp if tick_query.first() else None
        }
        
        ob_query = db.query(OrderBookData)
        if exchange:
            ob_query = ob_query.filter(OrderBookData.exchange == exchange)
        if symbol:
            ob_query = ob_query.filter(OrderBookData.symbol == symbol)
        
        stats["orderbook_data"] = {
            "total_records": ob_query.count(),
            "latest_timestamp": ob_query.order_by(OrderBookData.timestamp.desc()).first().timestamp if ob_query.first() else None
        }
        
        ohlc_query = db.query(OHLCData)
        if exchange:
            ohlc_query = ohlc_query.filter(OHLCData.exchange == exchange)
        if symbol:
            ohlc_query = ohlc_query.filter(OHLCData.symbol == symbol)
        
        stats["ohlc_data"] = {
            "total_records": ohlc_query.count(),
            "latest_timestamp": ohlc_query.order_by(OHLCData.timestamp.desc()).first().timestamp if ohlc_query.first() else None
        }
        
        return stats
        
    except Exception as e:
        logger.error("Failed to get data stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
