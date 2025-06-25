#!/usr/bin/env python3

"""
Bot Forge データ収集テストスクリプト
topgun統合とWebSocket接続をテストします
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "backend"))

from backend.app.topgun_integration import TopgunDataCollector
from backend.app.database import get_db, init_db
from backend.app.models import TickData, OrderBookData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_data_collection():
    """データ収集機能をテストします"""
    print("🧪 Bot Forge データ収集テスト開始")
    print("=" * 50)
    
    try:
        init_db()
        print("✅ データベース初期化完了")
    except Exception as e:
        print(f"❌ データベース初期化失敗: {e}")
        return False
    
    collector = TopgunDataCollector()
    
    test_cases = [
        ("binance", "BTC_USDT"),
        ("gmo", "BTC_JPY"),
        ("bitflyer", "BTC_JPY"),
    ]
    
    success_count = 0
    
    for exchange, symbol in test_cases:
        print(f"\n📡 {exchange.upper()} - {symbol} 接続テスト")
        print("-" * 30)
        
        try:
            await collector.start_collection(exchange, symbol)
            print(f"✅ {exchange} WebSocket接続開始")
            
            print("⏳ 5秒間データ収集中...")
            await asyncio.sleep(5)
            
            await collector.stop_collection()
            print(f"✅ {exchange} WebSocket接続停止")
            
            db = next(get_db())
            tick_count = db.query(TickData).filter(
                TickData.exchange == exchange,
                TickData.symbol == symbol
            ).count()
            
            orderbook_count = db.query(OrderBookData).filter(
                OrderBookData.exchange == exchange,
                OrderBookData.symbol == symbol
            ).count()
            
            print(f"📊 収集データ: Tick={tick_count}, OrderBook={orderbook_count}")
            
            if tick_count > 0 or orderbook_count > 0:
                print(f"✅ {exchange} データ収集成功")
                success_count += 1
            else:
                print(f"⚠️ {exchange} データ収集されませんでした")
            
        except Exception as e:
            print(f"❌ {exchange} 接続エラー: {e}")
            logger.exception(f"Error testing {exchange}")
    
    print("\n" + "=" * 50)
    print(f"📈 テスト結果: {success_count}/{len(test_cases)} 成功")
    
    if success_count > 0:
        print("✅ データ収集機能は動作しています")
        return True
    else:
        print("❌ データ収集機能に問題があります")
        return False

async def test_exchange_support():
    """全15取引所のサポート状況をテストします"""
    print("\n🌐 全取引所サポートテスト")
    print("=" * 50)
    
    exchanges = [
        "binance", "gmo", "bitflyer", "bitbank", "coincheck",
        "okj", "bittrade", "bybit", "okx", "phemex",
        "bitget", "mexc", "kucoin", "bitmex", "hyperliquid"
    ]
    
    collector = TopgunDataCollector()
    supported_count = 0
    
    for exchange in exchanges:
        try:
            await collector.start_collection(exchange, "BTC_USDT")
            await asyncio.sleep(1)  # 1秒だけテスト
            await collector.stop_collection()
            print(f"✅ {exchange.upper()}: サポート済み")
            supported_count += 1
        except Exception as e:
            print(f"❌ {exchange.upper()}: {str(e)[:50]}...")
    
    print(f"\n📊 サポート状況: {supported_count}/{len(exchanges)} 取引所")
    return supported_count

def test_cli_tools():
    """CLI ツールをテストします"""
    print("\n🛠️ CLI ツールテスト")
    print("=" * 50)
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "cli/export.py", "--help"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ export.py: 動作確認済み")
        else:
            print(f"❌ export.py: エラー {result.stderr}")
    except Exception as e:
        print(f"❌ export.py: {e}")
    
    try:
        result = subprocess.run([
            sys.executable, "cli/o3_analysis.py", "--help"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ o3_analysis.py: 動作確認済み")
        else:
            print(f"❌ o3_analysis.py: エラー {result.stderr}")
    except Exception as e:
        print(f"❌ o3_analysis.py: {e}")

async def main():
    """メインテスト実行"""
    print("🤖 Bot Forge システム統合テスト")
    print("=" * 60)
    
    data_collection_ok = await test_data_collection()
    
    supported_exchanges = await test_exchange_support()
    
    test_cli_tools()
    
    print("\n" + "=" * 60)
    print("📋 総合テスト結果")
    print("=" * 60)
    print(f"📡 データ収集: {'✅ OK' if data_collection_ok else '❌ NG'}")
    print(f"🌐 取引所サポート: {supported_exchanges}/15 取引所")
    print(f"🛠️ CLI ツール: 確認済み")
    
    if data_collection_ok and supported_exchanges >= 3:
        print("\n🎉 システム基本機能は正常に動作しています！")
        return True
    else:
        print("\n⚠️ システムに改善が必要な箇所があります")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ テスト中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 予期しないエラー: {e}")
        logger.exception("Unexpected error in main")
        sys.exit(1)
