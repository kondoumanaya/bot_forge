#!/usr/bin/env python3
"""
CLI tool for o3 integration and ML analysis
"""

import argparse
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def load_data(input_file: str):
    """Load data from JSON file"""
    with open(input_file, 'r') as f:
        data = json.load(f)
    return data

def calculate_technical_indicators(df: pd.DataFrame):
    """Calculate additional technical indicators"""
    def calculate_rsi(prices, window=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def calculate_bollinger_bands(prices, window=20, num_std=2):
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band, rolling_mean
    
    if 'price' in df.columns:
        df['rsi'] = calculate_rsi(df['price'])
        df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(df['price'])
        df['bb_upper'], df['bb_lower'], df['bb_middle'] = calculate_bollinger_bands(df['price'])
        
        df['price_momentum_5'] = df['price'].pct_change(5)
        df['price_momentum_10'] = df['price'].pct_change(10)
        
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
    
    return df

def generate_ml_features(data: dict):
    """Generate ML-ready features from raw data"""
    console.print("[blue]Generating ML features...[/blue]")
    
    if 'features' not in data:
        console.print("[red]No features found in data[/red]")
        return None
    
    df = pd.DataFrame(data['features'])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    df = calculate_technical_indicators(df)
    
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    for lag in [1, 5, 10]:
        df[f'price_lag_{lag}'] = df['price'].shift(lag)
        if 'volume' in df.columns:
            df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
    
    for window in [5, 10, 20]:
        df[f'price_mean_{window}'] = df['price'].rolling(window=window).mean()
        df[f'price_std_{window}'] = df['price'].rolling(window=window).std()
        if 'volume' in df.columns:
            df[f'volume_mean_{window}'] = df['volume'].rolling(window=window).mean()
    
    df = df.dropna()
    
    return df

def analyze_patterns(df: pd.DataFrame):
    """Analyze patterns in the data"""
    console.print("\n[blue]Pattern Analysis[/blue]")
    
    patterns = {}
    
    if 'price' in df.columns:
        patterns['price_trend'] = 'bullish' if df['price'].iloc[-1] > df['price'].iloc[0] else 'bearish'
        patterns['volatility'] = df['price'].pct_change().std() * 100
        patterns['max_drawdown'] = ((df['price'] / df['price'].cummax()) - 1).min() * 100
        
        price_quantiles = df['price'].quantile([0.1, 0.25, 0.75, 0.9])
        patterns['support_levels'] = [price_quantiles[0.1], price_quantiles[0.25]]
        patterns['resistance_levels'] = [price_quantiles[0.75], price_quantiles[0.9]]
    
    if 'rsi' in df.columns:
        current_rsi = df['rsi'].iloc[-1]
        if current_rsi > 70:
            patterns['rsi_signal'] = 'overbought'
        elif current_rsi < 30:
            patterns['rsi_signal'] = 'oversold'
        else:
            patterns['rsi_signal'] = 'neutral'
    
    if 'macd' in df.columns and 'macd_signal' in df.columns:
        macd_diff = df['macd'].iloc[-1] - df['macd_signal'].iloc[-1]
        patterns['macd_signal'] = 'bullish' if macd_diff > 0 else 'bearish'
    
    return patterns

def create_o3_prompt(data: dict, df: pd.DataFrame, patterns: dict):
    """Create a prompt for o3 analysis"""
    metadata = data.get('metadata', {})
    
    prompt = f"""

- Exchange: {metadata.get('exchange', 'Unknown')}
- Symbol: {metadata.get('symbol', 'Unknown')}
- Period: {metadata.get('period_days', 'Unknown')} days
- Total Records: {len(df)}

- Latest Price: ¥{df['price'].iloc[-1]:,.2f}
- Price Trend: {patterns.get('price_trend', 'Unknown')}
- Volatility: {patterns.get('volatility', 0):.2f}%
- RSI Signal: {patterns.get('rsi_signal', 'Unknown')}
- MACD Signal: {patterns.get('macd_signal', 'Unknown')}

- Support Levels: {patterns.get('support_levels', [])}
- Resistance Levels: {patterns.get('resistance_levels', [])}

Please analyze this cryptocurrency market data and provide:

1. **Trend Analysis**: What is the overall trend and momentum?
2. **Entry/Exit Signals**: Based on technical indicators, what are the optimal entry and exit points?
3. **Risk Assessment**: What are the current risk factors and recommended position sizing?
4. **Price Prediction**: What is your short-term (24h) and medium-term (7d) price outlook?
5. **Strategy Recommendations**: What trading strategies would work best in current market conditions?

Key features for ML model training:
{list(df.select_dtypes(include=[np.number]).columns[:10])}

Please provide actionable insights for algorithmic trading strategy development.
"""
    
    return prompt

def main():
    parser = argparse.ArgumentParser(description="Bot Forge o3 Analysis CLI")
    parser.add_argument("--input", required=True, help="Input JSON file from data export")
    parser.add_argument("--output", help="Output file for analysis results")
    parser.add_argument("--format", choices=['json', 'prompt'], default='prompt', 
                       help="Output format")
    
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold]Bot Forge o3 Analysis[/bold]\n"
        f"Input: {args.input}\n"
        f"Format: {args.format}",
        border_style="green"
    ))
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading data...", total=None)
            data = load_data(args.input)
            
            progress.update(task, description="Generating features...")
            df = generate_ml_features(data)
            
            if df is None:
                return
            
            progress.update(task, description="Analyzing patterns...")
            patterns = analyze_patterns(df)
            
            progress.update(task, description="Creating analysis...")
        
        analysis_table = Table(title="Market Analysis Results")
        analysis_table.add_column("Metric", style="cyan")
        analysis_table.add_column("Value", style="green")
        
        analysis_table.add_row("Records Processed", f"{len(df):,}")
        analysis_table.add_row("Price Trend", patterns.get('price_trend', 'Unknown'))
        analysis_table.add_row("Volatility", f"{patterns.get('volatility', 0):.2f}%")
        analysis_table.add_row("RSI Signal", patterns.get('rsi_signal', 'Unknown'))
        analysis_table.add_row("MACD Signal", patterns.get('macd_signal', 'Unknown'))
        
        console.print(analysis_table)
        
        if args.format == 'prompt':
            prompt = create_o3_prompt(data, df, patterns)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(prompt)
                console.print(f"[green]o3 prompt saved to {args.output}[/green]")
            else:
                syntax = Syntax(prompt, "markdown", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title="o3 Analysis Prompt"))
        
        elif args.format == 'json':
            result = {
                'metadata': data.get('metadata', {}),
                'analysis': patterns,
                'features': df.to_dict('records'),
                'ml_ready': True,
                'feature_columns': list(df.select_dtypes(include=[np.number]).columns)
            }
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                console.print(f"[green]Analysis results saved to {args.output}[/green]")
            else:
                console.print(json.dumps(result, indent=2, default=str))
    
    except Exception as e:
        console.print(f"[red]Analysis failed: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
