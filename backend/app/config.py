from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    app_name: str = "Bot Forge System"
    debug: bool = True

    database_url: str = "sqlite:///./bot_forge.db"

    ws_heartbeat_interval: int = 30
    ws_reconnect_delay: int = 5
    ws_max_reconnect_attempts: int = 10

    sqlite_retention_months: int = 12
    parquet_retention_years: int = 2

    supported_exchanges: List[str] = [
        "bitflyer", "gmocoin", "bitbank", "coincheck", "okj", "bittrade",
        "bybit", "binance", "okx", "phemex", "bitget", "mexc", "kucoin", "bitmex", "hyperliquid"
    ]
    default_exchange: str = "binance"

    binance_api_key: Optional[str] = None
    binance_secret_key: Optional[str] = None
    gmo_api_key: Optional[str] = None
    gmo_secret_key: Optional[str] = None

    supported_timeframes: List[str] = ["1s", "1m", "5m", "1h", "1d", "1w", "1M"]
    default_timeframe: str = "1m"

    max_tick_buffer_size: int = 10000
    max_orderbook_depth: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()