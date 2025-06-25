#!/usr/bin/env python3
"""
CLI tool for data export in various formats
"""

import argparse
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
import zipfile

console = Console()

def create_connection():
    """Create database connection"""
    db_path = Path(__file__).parent.parent / "backend" / "bot_forge.db"
    return sqlite3.connect(str(db_path))

def export_csv(exchange: str, symbol: str, data_type: str, output_file: str, days: int = 30):
    """Export data as CSV"""
    with create_connection() as conn:
        if data_type == 'tick':
            query = """
            SELECT timestamp, price, volume, side FROM tick_data 
            WHERE exchange = ? AND symbol = ? 
            AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp
            """.format(days)
        elif data_type == 'orderbook':
            query = """
            SELECT timestamp, bids, asks FROM orderbook_data 
            WHERE exchange = ? AND symbol = ? 
            AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp
            """.format(days)
        elif data_type == 'ohlc':
            query = """
            SELECT timestamp, timeframe, open_price, high_price, low_price, close_price, volume 
            FROM ohlc_data 
            WHERE exchange = ? AND symbol = ? 
            AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp
            """.format(days)
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        
        df = pd.read_sql_query(query, conn, params=(exchange, symbol))
    
    if df.empty:
        console.print("[red]No data found for export[/red]")
        return
    
    df.to_csv(output_file, index=False)
    console.print(f"[green]Exported {len(df)} records to {output_file}[/green]")

def export_parquet(exchange: str, symbol: str, data_type: str, output_file: str, days: int = 30, compress: bool = True):
    """Export data as Parquet with optional compression"""
    with create_connection() as conn:
        if data_type == 'tick':
            query = """
            SELECT * FROM tick_data 
            WHERE exchange = ? AND symbol = ? 
            AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp
            """.format(days)
        elif data_type == 'orderbook':
            query = """
            SELECT * FROM orderbook_data 
            WHERE exchange = ? AND symbol = ? 
            AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp
            """.format(days)
        elif data_type == 'ohlc':
            query = """
            SELECT * FROM ohlc_data 
            WHERE exchange = ? AND symbol = ? 
            AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp
            """.format(days)
        
        df = pd.read_sql_query(query, conn, params=(exchange, symbol))
    
    if df.empty:
        console.print("[red]No data found for export[/red]")
        return
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    compression = 'gzip' if compress else None
    df.to_parquet(output_file, compression=compression, index=False)
    
    if compress:
        zip_file = output_file.replace('.parquet', '.zip')
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(output_file, Path(output_file).name)
        
        Path(output_file).unlink()
        output_file = zip_file
    
    console.print(f"[green]Exported {len(df)} records to {output_file}[/green]")

def main():
    parser = argparse.ArgumentParser(description="Bot Forge Data Export CLI")
    parser.add_argument("--exchange", required=True, help="Exchange name")
    parser.add_argument("--symbol", required=True, help="Trading symbol")
    parser.add_argument("--data-type", choices=['tick', 'orderbook', 'ohlc'], 
                       required=True, help="Type of data to export")
    parser.add_argument("--format", choices=['csv', 'parquet'], 
                       default='csv', help="Export format")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--days", type=int, default=30, help="Number of days to export")
    parser.add_argument("--compress", action='store_true', help="Compress output (parquet only)")
    
    args = parser.parse_args()
    
    console.print(f"[blue]Exporting {args.data_type} data for {args.symbol} on {args.exchange.upper()}[/blue]")
    
    try:
        if args.format == 'csv':
            export_csv(args.exchange, args.symbol, args.data_type, args.output, args.days)
        elif args.format == 'parquet':
            export_parquet(args.exchange, args.symbol, args.data_type, args.output, args.days, args.compress)
    
    except Exception as e:
        console.print(f"[red]Export failed: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
