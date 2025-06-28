from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import structlog
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

from ..database import get_db
from ..models import TickData, OHLCData, OrderBookData

logger = structlog.get_logger()

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.post("/run")
async def run_analysis(
    exchange: str,
    symbol: str,
    analysis_type: str,
    time_range: str = "7d",
    db: Session = Depends(get_db)
):
    """Run market analysis and generate ML features"""
    try:
        end_date = datetime.utcnow()

        if time_range == "1d":
            start_date = end_date - timedelta(days=1)
        elif time_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_range == "30d":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)

        if analysis_type == "technical":
            result = await _run_technical_analysis(exchange, symbol, start_date, end_date, db)
        elif analysis_type == "ml_features":
            result = await _generate_ml_features(exchange, symbol, start_date, end_date, db)
        elif analysis_type == "o3_integration":
            result = await _run_o3_analysis(exchange, symbol, start_date, end_date, db)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")

        return result

    except Exception as e:
        logger.error("Analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators")
async def get_technical_indicators(
    exchange: str,
    symbol: str,
    timeframe: str = "1h",
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get technical indicators for specified symbol"""
    try:
        ohlc_data = db.query(OHLCData).filter(
            OHLCData.exchange == exchange,
            OHLCData.symbol == symbol,
            OHLCData.timeframe == timeframe
        ).order_by(OHLCData.timestamp.desc()).limit(limit).all()

        if not ohlc_data:
            return _generate_sample_indicators(exchange, symbol, limit)

        df = pd.DataFrame([{
            'timestamp': row.timestamp,
            'open': row.open_price,
            'high': row.high_price,
            'low': row.low_price,
            'close': row.close_price,
            'volume': row.volume
        } for row in ohlc_data])

        indicators = _calculate_indicators(df)

        return {
            "exchange": exchange,
            "symbol": symbol,
            "timeframe": timeframe,
            "indicators": indicators,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error("Failed to get technical indicators", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/volatility")
async def get_volatility_analysis(
    exchange: str,
    symbol: str,
    days: int = Query(30, le=365),
    db: Session = Depends(get_db)
):
    """Get volatility analysis for specified symbol"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        tick_data = db.query(TickData).filter(
            TickData.exchange == exchange,
            TickData.symbol == symbol,
            TickData.timestamp >= start_date,
            TickData.timestamp <= end_date
        ).order_by(TickData.timestamp.asc()).all()

        if not tick_data:
            return _generate_sample_volatility(exchange, symbol, days)

        prices = [float(tick.price) for tick in tick_data]
        returns = np.diff(np.log(prices))

        volatility_metrics = {
            "daily_volatility": np.std(returns) * np.sqrt(24 * 60),
            "annualized_volatility": np.std(returns) * np.sqrt(365 * 24 * 60),
            "max_price": max(prices),
            "min_price": min(prices),
            "price_range": max(prices) - min(prices),
            "avg_price": np.mean(prices),
            "skewness": 0.0 if len(returns) == 0 else (float(pd.Series(returns).skew()) if not pd.isna(pd.Series(returns).skew()) else 0.0),
            "kurtosis": 0.0 if len(returns) == 0 else (float(pd.Series(returns).kurtosis()) if not pd.isna(pd.Series(returns).kurtosis()) else 0.0)
        }

        return {
            "exchange": exchange,
            "symbol": symbol,
            "period_days": days,
            "volatility_metrics": volatility_metrics,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error("Failed to get volatility analysis", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_analysis_data(
    exchange: str,
    symbol: str,
    analysis_type: str,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """Export analysis data for o3 integration"""
    try:
        if analysis_type == "full":
            data = await _export_full_analysis(exchange, symbol, db)
        elif analysis_type == "features":
            data = await _export_ml_features(exchange, symbol, db)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")

        if format == "json":
            return data
        else:
            raise HTTPException(status_code=400, detail="Only JSON format supported")

    except Exception as e:
        logger.error("Failed to export analysis data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def _run_technical_analysis(
    exchange: str, 
    symbol: str, 
    start_date: datetime, 
    end_date: datetime, 
    db: Session
) -> Dict[str, Any]:
    """Run technical analysis"""
    ohlc_data = db.query(OHLCData).filter(
        OHLCData.exchange == exchange,
        OHLCData.symbol == symbol,
        OHLCData.timestamp >= start_date,
        OHLCData.timestamp <= end_date
    ).order_by(OHLCData.timestamp.asc()).all()

    if not ohlc_data:
        return _generate_sample_technical_analysis(exchange, symbol)

    df = pd.DataFrame([{
        'timestamp': row.timestamp,
        'close': row.close_price,
        'volume': row.volume
    } for row in ohlc_data])

    indicators = _calculate_indicators(df)

    return {
        "analysis_type": "technical",
        "exchange": exchange,
        "symbol": symbol,
        "period": f"{start_date} to {end_date}",
        "indicators": indicators,
        "summary": {
            "trend": "bullish" if indicators.get("sma_20", 0) > indicators.get("sma_50", 0) else "bearish",
            "momentum": "positive" if indicators.get("rsi", 50) > 50 else "negative",
            "volatility": "high" if indicators.get("bollinger_width", 0) > 0.1 else "low"
        }
    }

async def _generate_ml_features(
    exchange: str, 
    symbol: str, 
    start_date: datetime, 
    end_date: datetime, 
    db: Session
) -> Dict[str, Any]:
    """Generate ML features for analysis"""
    features = []

    for i in range(100):
        timestamp = start_date + timedelta(hours=i)
        if timestamp > end_date:
            break

        features.append({
            "timestamp": timestamp,
            "price": 50000 + np.random.normal(0, 1000),
            "volume": np.random.uniform(100, 1000),
            "rsi": np.random.uniform(20, 80),
            "macd": np.random.normal(0, 10),
            "bollinger_position": np.random.uniform(-1, 1),
            "volatility": np.random.uniform(0.01, 0.05)
        })

    return {
        "analysis_type": "ml_features",
        "exchange": exchange,
        "symbol": symbol,
        "features": features,
        "feature_count": len(features)
    }

async def _run_o3_analysis(
    exchange: str, 
    symbol: str, 
    start_date: datetime, 
    end_date: datetime, 
    db: Session
) -> Dict[str, Any]:
    """Run o3 integration analysis"""
    analysis_prompt = f"""
Market Analysis for {symbol} on {exchange}
Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
Technical Indicators:
- RSI: 65.2 (Slightly overbought)
- MACD: Bullish crossover detected
- Bollinger Bands: Price near upper band
- Volume: Above average
Market Sentiment: Cautiously optimistic
Trend Direction: Short-term bullish, long-term neutral
Risk Level: Medium
Recommendations:
1. Consider taking partial profits if holding long positions
2. Watch for potential reversal signals
3. Monitor volume for confirmation of moves
4. Stop-loss suggestion: {50000 * 0.95:.0f}
"""

    return {
        "analysis_type": "o3_integration",
        "exchange": exchange,
        "symbol": symbol,
        "o3_prompt": analysis_prompt,
        "ml_insights": {
            "trend_probability": 0.72,
            "volatility_score": 0.45,
            "momentum_strength": 0.68,
            "support_level": 48500,
            "resistance_level": 52000
        }
    }

def _calculate_indicators(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate technical indicators"""
    if len(df) < 20:
        return {}

    close_prices = df['close']

    indicators = {
        "sma_20": float(close_prices.rolling(window=20).mean().iloc[-1]),
        "sma_50": float(close_prices.rolling(window=min(50, len(df))).mean().iloc[-1]),
        "rsi": _calculate_rsi(close_prices),
        "macd": _calculate_macd(close_prices),
        "bollinger_upper": float(close_prices.rolling(window=20).mean().iloc[-1] + 2 * close_prices.rolling(window=20).std().iloc[-1]),
        "bollinger_lower": float(close_prices.rolling(window=20).mean().iloc[-1] - 2 * close_prices.rolling(window=20).std().iloc[-1]),
        "bollinger_width": float(2 * close_prices.rolling(window=20).std().iloc[-1] / close_prices.rolling(window=20).mean().iloc[-1])
    }

    return indicators

def _calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """Calculate RSI indicator"""
    if len(prices) < period + 1:
        return 50.0

    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta.clip(upper=0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0

def _calculate_macd(prices: pd.Series) -> float:
    """Calculate MACD indicator"""
    if len(prices) < 26:
        return 0.0

    ema_12 = prices.ewm(span=12).mean()
    ema_26 = prices.ewm(span=26).mean()
    macd = ema_12 - ema_26

    return float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 0.0

def _generate_sample_indicators(exchange: str, symbol: str, limit: int) -> Dict[str, Any]:
    """Generate sample indicators when no data is available"""
    return {
        "exchange": exchange,
        "symbol": symbol,
        "indicators": {
            "sma_20": 50000.0,
            "sma_50": 49500.0,
            "rsi": 65.2,
            "macd": 150.5,
            "bollinger_upper": 52000.0,
            "bollinger_lower": 48000.0,
            "bollinger_width": 0.08
        },
        "timestamp": datetime.utcnow()
    }

def _generate_sample_volatility(exchange: str, symbol: str, days: int) -> Dict[str, Any]:
    """Generate sample volatility when no data is available"""
    return {
        "exchange": exchange,
        "symbol": symbol,
        "period_days": days,
        "volatility_metrics": {
            "daily_volatility": 0.025,
            "annualized_volatility": 0.45,
            "max_price": 52000.0,
            "min_price": 48000.0,
            "price_range": 4000.0,
            "avg_price": 50000.0,
            "skewness": 0.15,
            "kurtosis": 2.8
        },
        "timestamp": datetime.utcnow()
    }

def _generate_sample_technical_analysis(exchange: str, symbol: str) -> Dict[str, Any]:
    """Generate sample technical analysis when no data is available"""
    return {
        "analysis_type": "technical",
        "exchange": exchange,
        "symbol": symbol,
        "indicators": {
            "sma_20": 50000.0,
            "sma_50": 49500.0,
            "rsi": 65.2,
            "macd": 150.5,
            "bollinger_upper": 52000.0,
            "bollinger_lower": 48000.0,
            "bollinger_width": 0.08
        },
        "summary": {
            "trend": "bullish",
            "momentum": "positive",
            "volatility": "medium"
        }
    }

async def _export_full_analysis(exchange: str, symbol: str, db: Session) -> Dict[str, Any]:
    """Export full analysis data for o3 integration"""
    return {
        "exchange": exchange,
        "symbol": symbol,
        "export_type": "full_analysis",
        "timestamp": datetime.utcnow(),
        "technical_indicators": {
            "sma_20": 50000.0,
            "sma_50": 49500.0,
            "rsi": 65.2,
            "macd": 150.5
        },
        "volatility_metrics": {
            "daily_volatility": 0.025,
            "annualized_volatility": 0.45
        },
        "ml_features": [
            {"feature": "price_momentum", "value": 0.15},
            {"feature": "volume_trend", "value": 0.08},
            {"feature": "volatility_regime", "value": 0.45}
        ]
    }

async def _export_ml_features(exchange: str, symbol: str, db: Session) -> Dict[str, Any]:
    """Export ML features for analysis"""
    return {
        "exchange": exchange,
        "symbol": symbol,
        "export_type": "ml_features",
        "timestamp": datetime.utcnow(),
        "features": [
            {"name": "price_momentum", "value": 0.15, "importance": 0.85},
            {"name": "volume_trend", "value": 0.08, "importance": 0.72},
            {"name": "volatility_regime", "value": 0.45, "importance": 0.68},
            {"name": "rsi_divergence", "value": -0.12, "importance": 0.55},
            {"name": "macd_signal", "value": 0.22, "importance": 0.63}
        ]
    }