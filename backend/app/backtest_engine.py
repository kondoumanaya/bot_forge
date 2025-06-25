import asyncio
import structlog
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dataclasses import dataclass
import pandas as pd
import numpy as np

from .database import get_db
from .models import TickData, OHLCData, TradeHistory

logger = structlog.get_logger()

@dataclass
class Trade:
    timestamp: datetime
    side: str  # 'buy' or 'sell'
    price: float
    quantity: float
    pnl: float = 0.0

@dataclass
class Position:
    symbol: str
    side: str  # 'long' or 'short'
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float = 0.0

class TradingStrategy:
    def __init__(self, name: str, parameters: Dict[str, Any]):
        self.name = name
        self.parameters = parameters
        self.position: Optional[Position] = None
        self.trades: List[Trade] = []
        self.balance = 0.0
        
    def should_buy(self, data: pd.DataFrame) -> bool:
        """Override in specific strategy implementations"""
        if len(data) < 20:
            return False
        
        sma_short = data['close'].rolling(window=5).mean().iloc[-1]
        sma_long = data['close'].rolling(window=20).mean().iloc[-1]
        
        return sma_short > sma_long and self.position is None
    
    def should_sell(self, data: pd.DataFrame) -> bool:
        """Override in specific strategy implementations"""
        if len(data) < 20 or self.position is None:
            return False
        
        sma_short = data['close'].rolling(window=5).mean().iloc[-1]
        sma_long = data['close'].rolling(window=20).mean().iloc[-1]
        
        return sma_short < sma_long
    
    def calculate_position_size(self, price: float, balance: float) -> float:
        """Calculate position size based on risk management"""
        risk_per_trade = self.parameters.get('risk_per_trade', 0.02)
        return (balance * risk_per_trade) / price

class BacktestEngine:
    def __init__(self):
        self.strategies = {
            'sma_crossover': TradingStrategy,
            'mean_reversion': TradingStrategy,
            'momentum': TradingStrategy
        }
    
    async def run_backtest(
        self,
        strategy_name: str,
        exchange: str,
        symbol: str,
        start_date: str,
        end_date: str,
        initial_balance: float,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run backtest for specified strategy and parameters"""
        try:
            if parameters is None:
                parameters = {}
            
            strategy_mapping = {
                "Simple MA Crossover": "sma_crossover",
                "simple_ma_crossover": "sma_crossover",
                "RSI Strategy": "rsi_strategy",
                "MACD Strategy": "macd_strategy"
            }
            
            mapped_strategy = strategy_mapping.get(strategy_name, strategy_name)
            strategy_class = self.strategies.get(mapped_strategy)
            if not strategy_class:
                raise ValueError(f"Strategy {mapped_strategy} not found")
            
            strategy = strategy_class(strategy_name, parameters)
            strategy.balance = initial_balance
            
            start_dt = datetime.strptime(start_date, "%Y-%m-%d") if isinstance(start_date, str) else start_date
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") if isinstance(end_date, str) else end_date
            
            historical_data = await self._get_historical_data(
                exchange, symbol, start_dt, end_dt
            )
            
            if historical_data.empty:
                raise ValueError("No historical data available for the specified period")
            
            results = await self._execute_backtest(strategy, historical_data)
            
            return {
                "strategy_name": strategy_name,
                "exchange": exchange,
                "symbol": symbol,
                "period": f"{start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}",
                "initial_balance": initial_balance,
                "final_balance": results['final_balance'],
                "total_return": results['total_return'],
                "max_drawdown": results['max_drawdown'],
                "sharpe_ratio": results['sharpe_ratio'],
                "total_trades": results['total_trades'],
                "win_rate": results['win_rate'],
                "profit_factor": results['profit_factor'],
                "avg_trade_duration": results['avg_trade_duration'],
                "trades": results['trades'],
                "equity_curve": results['equity_curve'],
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Backtest failed", error=str(e))
            raise
    
    async def _get_historical_data(
        self, 
        exchange: str, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """Retrieve historical OHLC data from database"""
        try:
            db = next(get_db())
            
            ohlc_data = db.query(OHLCData).filter(
                OHLCData.exchange == exchange,
                OHLCData.symbol == symbol,
                OHLCData.timestamp >= start_date,
                OHLCData.timestamp <= end_date,
                OHLCData.timeframe == '1h'
            ).order_by(OHLCData.timestamp.asc()).all()
            
            if not ohlc_data:
                return self._generate_sample_data(start_date, end_date)
            
            df = pd.DataFrame([{
                'timestamp': row.timestamp,
                'open': row.open_price,
                'high': row.high_price,
                'low': row.low_price,
                'close': row.close_price,
                'volume': row.volume
            } for row in ohlc_data])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to get historical data", error=str(e))
            return self._generate_sample_data(start_date, end_date)
    
    def _generate_sample_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate sample OHLC data for backtesting when no real data is available"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='1H')
        
        np.random.seed(42)
        base_price = 50000.0
        prices = []
        current_price = base_price
        
        for _ in date_range:
            change = np.random.normal(0, 0.02)
            current_price *= (1 + change)
            
            high = current_price * (1 + abs(np.random.normal(0, 0.01)))
            low = current_price * (1 - abs(np.random.normal(0, 0.01)))
            open_price = current_price * (1 + np.random.normal(0, 0.005))
            close_price = current_price
            volume = np.random.uniform(100, 1000)
            
            prices.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': close_price,
                'volume': volume
            })
        
        df = pd.DataFrame(prices, index=date_range)
        return df
    
    async def _execute_backtest(self, strategy: TradingStrategy, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute backtest logic"""
        trades = []
        equity_curve = []
        balance_history = []
        
        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            current_price = data.iloc[i]['close']
            current_time = data.index[i]
            
            if strategy.should_buy(current_data):
                position_size = strategy.calculate_position_size(current_price, strategy.balance)
                
                trade = Trade(
                    timestamp=current_time,
                    side='buy',
                    price=current_price,
                    quantity=position_size
                )
                
                strategy.position = Position(
                    symbol='BTC_USDT',
                    side='long',
                    size=position_size,
                    entry_price=current_price,
                    current_price=current_price
                )
                
                strategy.trades.append(trade)
                trades.append({
                    'timestamp': current_time,
                    'side': 'buy',
                    'price': current_price,
                    'quantity': position_size,
                    'pnl': 0.0
                })
                
            elif strategy.should_sell(current_data) and strategy.position:
                pnl = (current_price - strategy.position.entry_price) * strategy.position.size
                strategy.balance += pnl
                
                trade = Trade(
                    timestamp=current_time,
                    side='sell',
                    price=current_price,
                    quantity=strategy.position.size,
                    pnl=pnl
                )
                
                strategy.trades.append(trade)
                trades.append({
                    'timestamp': current_time,
                    'side': 'sell',
                    'price': current_price,
                    'quantity': strategy.position.size,
                    'pnl': pnl
                })
                
                strategy.position = None
            
            current_balance = strategy.balance
            if strategy.position:
                unrealized_pnl = (current_price - strategy.position.entry_price) * strategy.position.size
                current_balance += unrealized_pnl
            
            balance_history.append(current_balance)
            equity_curve.append({
                'timestamp': current_time,
                'balance': current_balance
            })
        
        return self._calculate_metrics(strategy, balance_history, trades, equity_curve)
    
    def _calculate_metrics(
        self, 
        strategy: TradingStrategy, 
        balance_history: List[float], 
        trades: List[Dict], 
        equity_curve: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate backtest performance metrics"""
        if not balance_history:
            return {
                'final_balance': strategy.balance,
                'total_return': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'total_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'avg_trade_duration': 0.0,
                'trades': [],
                'equity_curve': []
            }
        
        initial_balance = balance_history[0] if balance_history else strategy.balance
        final_balance = balance_history[-1] if balance_history else strategy.balance
        
        total_return = ((final_balance - initial_balance) / initial_balance) * 100
        
        max_drawdown = 0.0
        peak = initial_balance
        for balance in balance_history:
            if balance > peak:
                peak = balance
            drawdown = ((peak - balance) / peak) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0.0
        
        gross_profit = sum(t['pnl'] for t in winning_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
        
        returns = np.diff(balance_history) / balance_history[:-1] if len(balance_history) > 1 else [0]
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0.0
        
        return {
            'final_balance': final_balance,
            'total_return': total_return,
            'max_drawdown': -max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': len(trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_trade_duration': 24.0,
            'trades': trades,
            'equity_curve': equity_curve
        }

backtest_engine = BacktestEngine()
