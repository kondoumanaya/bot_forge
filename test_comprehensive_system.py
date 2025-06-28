#!/usr/bin/env python3

"""
Bot Forge 包括的システムテスト
全機能の動作確認を行います
"""

import asyncio
import logging
import sys
import os
import subprocess
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "backend"))

from backend.app.topgun_integration import TopgunDataCollector
from backend.app.backtest_engine import BacktestEngine
from backend.app.database import get_db, init_db
from backend.app.models import TickData, OrderBookData, OHLCData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_all_exchanges():
    """全15取引所のサポート状況をテストします"""
    print("🌐 全15取引所サポートテスト")
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
            result = await collector.start_collection(exchange, "BTC_USDT", ["tick"])
            if result:
                await asyncio.sleep(0.5)  # 0.5秒だけテスト
                await collector.stop_collection(exchange, "BTC_USDT")
                print(f"✅ {exchange.upper()}: サポート済み")
                supported_count += 1
            else:
                print(f"❌ {exchange.upper()}: 接続失敗")
        except Exception as e:
            print(f"❌ {exchange.upper()}: {str(e)[:50]}...")

    print(f"\n📊 サポート状況: {supported_count}/{len(exchanges)} 取引所")
    return supported_count

async def test_backtest_functionality():
    """バックテスト機能をテストします"""
    print("\n🔄 バックテスト機能テスト")
    print("=" * 50)

    try:
        engine = BacktestEngine()

        result = await engine.run_backtest(
            strategy_name="Simple MA Crossover",
            exchange="binance",
            symbol="BTC_USDT",
            start_date="2024-01-01",
            end_date="2024-01-07",
            initial_balance=10000.0,
            parameters={"risk_per_trade": 0.02}
        )

        print(f"✅ バックテスト実行成功")
        print(f"📊 戦略: {result['strategy_name']}")
        print(f"💰 初期残高: ${result['initial_balance']:,.2f}")
        print(f"💰 最終残高: ${result['final_balance']:,.2f}")
        print(f"📈 総リターン: {result['total_return']:.2f}%")
        print(f"📉 最大ドローダウン: {result['max_drawdown']:.2f}%")
        print(f"🎯 勝率: {result['win_rate']:.2f}")
        print(f"📊 総取引数: {result['total_trades']}")

        return True

    except Exception as e:
        print(f"❌ バックテストエラー: {e}")
        logger.exception("Backtest test failed")
        return False

def test_cli_tools_comprehensive():
    """CLI ツールの包括的テストを実行します"""
    print("\n🛠️ CLI ツール包括的テスト")
    print("=" * 50)

    cli_tests = [
        ("export.py", ["--help"]),
        ("o3_analysis.py", ["--help"]),
    ]

    success_count = 0

    for tool, args in cli_tests:
        try:
            result = subprocess.run([
                sys.executable, f"cli/{tool}"
            ] + args, capture_output=True, text=True, cwd=project_root)

            if result.returncode == 0:
                print(f"✅ {tool}: 正常動作")
                success_count += 1
            else:
                print(f"❌ {tool}: エラー {result.stderr[:100]}...")
        except Exception as e:
            print(f"❌ {tool}: {e}")

    print(f"\n📊 CLI ツール: {success_count}/{len(cli_tests)} 成功")
    return success_count

def test_documentation():
    """ドキュメント完成度をテストします"""
    print("\n📚 ドキュメント完成度テスト")
    print("=" * 50)

    required_files = [
        "README.md",
        "docs/SETUP.md",
        "scripts/setup.sh",
        "scripts/update_dependencies.sh"
    ]

    found_count = 0

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}: 存在")
            found_count += 1
        else:
            print(f"❌ {file_path}: 未作成")

    print(f"\n📊 ドキュメント: {found_count}/{len(required_files)} 完成")
    return found_count

async def main():
    """包括的システムテスト実行"""
    print("🤖 Bot Forge 包括的システムテスト")
    print("=" * 60)

    try:
        init_db()
        print("✅ データベース初期化完了")
    except Exception as e:
        print(f"❌ データベース初期化失敗: {e}")
        return False

    exchange_support = await test_all_exchanges()
    backtest_ok = await test_backtest_functionality()
    cli_tools_ok = test_cli_tools_comprehensive()
    docs_ok = test_documentation()

    print("\n" + "=" * 60)
    print("📋 包括的テスト結果")
    print("=" * 60)
    print(f"🌐 取引所サポート: {exchange_support}/15 取引所")
    print(f"🔄 バックテスト機能: {'✅ OK' if backtest_ok else '❌ NG'}")
    print(f"🛠️ CLI ツール: {cli_tools_ok}/2 成功")
    print(f"📚 ドキュメント: {docs_ok}/4 完成")

    success_criteria = (
        exchange_support >= 10,  # 15取引所中10以上サポート
        backtest_ok,             # バックテスト機能動作
        cli_tools_ok >= 2,       # CLI ツール全て動作
        docs_ok >= 3             # 主要ドキュメント存在
    )

    if all(success_criteria):
        print("\n🎉 Bot Forge システムは包括的に動作しています！")
        print("✨ 全ての主要機能が正常に実装されています")
        return True
    else:
        print("\n⚠️ システムに改善が必要な箇所があります")
        print("🔧 不足している機能の実装が必要です")
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
        logger.exception("Unexpected error in comprehensive test")
        sys.exit(1)