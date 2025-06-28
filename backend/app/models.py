from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import json

Base = declarative_base()

class TickData(Base):
    __tablename__ = "tick_data"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String(50), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    side = Column(String(10), nullable=False)  # buy/sell
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_exchange_symbol_timestamp', 'exchange', 'symbol', 'timestamp'),
    )

class OrderBookData(Base):
    __tablename__ = "orderbook_data"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String(50), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    bids = Column(Text, nullable=False)  # JSON string
    asks = Column(Text, nullable=False)  # JSON string
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_orderbook_exchange_symbol_timestamp', 'exchange', 'symbol', 'timestamp'),
    )

class OHLCData(Base):
    __tablename__ = "ohlc_data"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String(50), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_ohlc_exchange_symbol_timeframe_timestamp', 'exchange', 'symbol', 'timeframe', 'timestamp'),
    )

class TradeHistory(Base):
    __tablename__ = "trade_history"

    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String(100), nullable=False, index=True)
    exchange = Column(String(50), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # buy/sell
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True)
    entry_time = Column(DateTime, nullable=False, index=True)
    exit_time = Column(DateTime, nullable=True)
    strategy = Column(String(100), nullable=True)
    trade_metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_trade_bot_exchange_symbol', 'bot_name', 'exchange', 'symbol'),
    )

class ExchangeApiKey(Base):
    __tablename__ = "exchange_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String(50), nullable=False, unique=True, index=True)
    api_key = Column(String(500), nullable=False)
    api_secret = Column(String(500), nullable=False)
    passphrase = Column(String(200), nullable=True)  # For exchanges that require passphrase
    sandbox_mode = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class TickDataResponse(BaseModel):
    id: int
    exchange: str
    symbol: str
    price: float
    volume: float
    side: str
    timestamp: datetime

    class Config:
        from_attributes = True

class OrderBookResponse(BaseModel):
    id: int
    exchange: str
    symbol: str
    bids: list
    asks: list
    timestamp: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            exchange=obj.exchange,
            symbol=obj.symbol,
            bids=json.loads(obj.bids),
            asks=json.loads(obj.asks),
            timestamp=obj.timestamp
        )

class OHLCResponse(BaseModel):
    id: int
    exchange: str
    symbol: str
    timeframe: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    timestamp: datetime

    class Config:
        from_attributes = True

class TradeHistoryResponse(BaseModel):
    id: int
    bot_name: str
    exchange: str
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    pnl: Optional[float]
    entry_time: datetime
    exit_time: Optional[datetime]
    strategy: Optional[str]
    trade_metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        trade_metadata = None
        if obj.trade_metadata:
            try:
                trade_metadata = json.loads(obj.trade_metadata)
            except json.JSONDecodeError:
                trade_metadata = None

        return cls(
            id=obj.id,
            bot_name=obj.bot_name,
            exchange=obj.exchange,
            symbol=obj.symbol,
            side=obj.side,
            entry_price=obj.entry_price,
            exit_price=obj.exit_price,
            quantity=obj.quantity,
            pnl=obj.pnl,
            entry_time=obj.entry_time,
            exit_time=obj.exit_time,
            strategy=obj.strategy,
            trade_metadata=trade_metadata
        )

class WSMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()

class DataCollectionRequest(BaseModel):
    exchange: str
    symbol: str
    data_types: List[str]  # ["tick", "orderbook", "ohlc"]
    timeframes: Optional[List[str]] = None

class BacktestRequest(BaseModel):
    strategy_name: str
    exchange: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_balance: float = 10000.0
    parameters: Optional[Dict[str, Any]] = None

class ExchangeApiKeyRequest(BaseModel):
    exchange: str
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None
    sandbox_mode: bool = False
    is_active: bool = True

class ExchangeApiKeyResponse(BaseModel):
    id: int
    exchange: str
    api_key: str  # In production, this should be masked
    api_secret: str  # In production, this should be masked
    passphrase: Optional[str] = None
    sandbox_mode: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True