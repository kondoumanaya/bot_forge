# Bot Forge システム

高性能な仮想通貨取引ボットのバックテスト・分析・データ収集システム

## 🎯 システム概要

Bot Forge は以下の機能を提供する包括的な取引ボットシステムです：

1. **Bot のバックテスト** - 戦略の有効性を過去データで検証、エッジ抽出
2. **o3 による相場分析** - 特徴量探索・ML モデル作成のための学習データ生成
3. **戦略の可視化** - PnL, ドローダウン, エントリーポイントの分析
4. **データ収集基盤構築** - 複数取引所・時間足に対応したデータ保存/管理機構

## 🏗️ システムアーキテクチャ

```
+----------------------------+
| UI Frontend (React + Vite) |
| - shadcn/ui + Tailwind CSS |
| - サイドバーナビゲーション |
| - 15取引所対応             |
+-------------+--------------+
              ↓
+----------------------------+
| FastAPI Backend            |
| - WebSocket受信 & DataStore|
| - SQLite保存 / JSON出力    |
| - topgun統合               |
+-------------+--------------+
              ↓
+----------------------------+
| ストレージ層               |
| - SQLite (12ヶ月)          |
| - Parquet圧縮 (2年)        |
| - 自動削除 (2年以上)       |
+----------------------------+
```

## 🛠️ 技術スタック

- **フロントエンド**: React + Vite + Tailwind CSS + shadcn/ui
- **バックエンド**: FastAPI + WebSocket + SQLAlchemy
- **データ取得**: topgun + DataStore (15 取引所対応)
- **データベース**: SQLite (開発) / PostgreSQL (本番)
- **可視化**: Recharts / rich / seaborn / plotly
- **分析・ML**: pandas / scikit-learn / pytorch
- **ファイル出力**: JSON / Parquet / CSV 形式

## 📊 対応取引所 (15 取引所)

| 取引所      | WebSocket | API | 備考             |
| ----------- | --------- | --- | ---------------- |
| Binance     | ✅        | ✅  | グローバル最大手 |
| GMO Coin    | ✅        | ✅  | 日本大手         |
| bitFlyer    | ✅        | ✅  | 日本最大手       |
| bitbank     | ✅        | ✅  | 日本取引量上位   |
| Coincheck   | ✅        | ✅  | 日本大手         |
| OKJ         | ✅        | ✅  | OKX 日本版       |
| BitTrade    | ✅        | ✅  | 日本取引所       |
| Bybit       | ✅        | ✅  | デリバティブ大手 |
| OKX         | ✅        | ✅  | グローバル大手   |
| Phemex      | ✅        | ✅  | デリバティブ     |
| Bitget      | ✅        | ✅  | コピートレード   |
| MEXC        | ✅        | ✅  | アルトコイン豊富 |
| KuCoin      | ✅        | ✅  | アルトコイン     |
| BitMEX      | ✅        | ✅  | デリバティブ老舗 |
| Hyperliquid | ✅        | ✅  | DeFi DEX         |

## 🚀 クイックスタート

### 自動セットアップ（推奨）

```bash
# リポジトリクローン
git clone https://github.com/kondoumanaya/bot_forge.git
cd bot_forge

# 自動セットアップ実行
chmod +x scripts/setup.sh
./scripts/setup.sh

# システム起動
./start_all.sh
```

### 手動セットアップ

#### 前提条件

- **Python 3.12+** (pyenv 推奨)
- **Node.js 18+** (nvm 推奨)
- **Poetry** (Python 依存関係管理)
- **Git** (サブモジュール管理)

#### 1. 環境構築

```bash
# リポジトリクローン
git clone https://github.com/kondoumanaya/bot_forge.git
cd bot_forge

# Git サブモジュール初期化
git submodule update --init --recursive

# バックエンド環境構築
cd backend
poetry install
poetry run python -c "from app.database import init_db; init_db()"

# フロントエンド環境構築
cd ../frontend
npm install
npm run build  # ビルドテスト

cd ..
```

#### 2. 環境変数設定

```bash
# バックエンド環境変数
cat > backend/.env << EOF
DATABASE_URL=sqlite:///./bot_forge.db
SECRET_KEY=your-secret-key-here
DEBUG=true
LOG_LEVEL=info
API_HOST=0.0.0.0
API_PORT=8000
EOF

# フロントエンド環境変数
cat > frontend/.env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_APP_NAME=Bot Forge
EOF
```

#### 3. アプリケーション起動

```bash
# バックエンド起動（ターミナル1）
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# フロントエンド起動（ターミナル2）
cd frontend
npm run dev
```

#### 4. アクセス確認

- **フロントエンド**: http://localhost:5173
- **バックエンド API**: http://localhost:8000
- **API 文書**: http://localhost:8000/docs

## 📱 UI 機能詳細

### サイドバーナビゲーション

1. **📊 Data Preview** - リアルタイムデータ表示

   - Live Price Data (価格データ)
   - Order Book (板情報)
   - Recent Trades (約定履歴)

2. **🔄 Backtest** - バックテスト実行

   - 戦略選択 (Simple MA Crossover 等)
   - 期間設定・初期資金設定
   - パフォーマンス分析

3. **📈 Analysis** - 市場分析・ML 特徴量

   - Technical Indicators (RSI, MACD, Bollinger Bands)
   - Price vs Volume Correlation
   - o3 分析連携

4. **💾 Data Management** - データ管理

   - データ統計表示
   - CSV/Parquet エクスポート
   - データ検索・フィルター

5. **⚙️ ルート設定** - API 設定
   - 15 取引所の API キー管理
   - セキュリティ設定
   - 接続テスト

### データ管理ポリシー

- **直近 12 ヶ月**: SQLite (常時高速アクセス)
- **6 ヶ月~2 年**: Parquet 圧縮保存
- **2 年以上前**: 自動削除 (ストレージ最適化)

## 🔧 CLI ツール使用方法

### データエクスポート

```bash
# Tick データエクスポート (CSV)
python cli/export.py \
  --exchange binance \
  --symbol BTC_JPY \
  --data-type tick \
  --format csv \
  --output /tmp/btc_tick.csv \
  --days 7

# Order Book データエクスポート (Parquet圧縮)
python cli/export.py \
  --exchange gmo \
  --symbol BTC_JPY \
  --data-type orderbook \
  --format parquet \
  --output /tmp/btc_orderbook.parquet \
  --days 30 \
  --compress

# OHLC データエクスポート
python cli/export.py \
  --exchange bitflyer \
  --symbol BTC_JPY \
  --data-type ohlc \
  --format csv \
  --output /tmp/btc_ohlc.csv \
  --days 90
```

### o3 分析連携

```bash
# JSON形式で分析結果出力
python cli/o3_analysis.py \
  --input /tmp/btc_tick.csv \
  --output /tmp/analysis_result.json \
  --format json

# プロンプト形式で出力 (o3直接連携)
python cli/o3_analysis.py \
  --input /tmp/btc_tick.csv \
  --format prompt
```

### 分析例

```bash
# 1. データエクスポート
python cli/export.py --exchange binance --symbol BTC_JPY --data-type tick --format csv --output btc_data.csv --days 30

# 2. o3分析実行
python cli/o3_analysis.py --input btc_data.csv --format json --output analysis.json

# 3. 結果確認 (Rich formatting)
python -c "
import json
from rich.console import Console
from rich.json import JSON
console = Console()
with open('analysis.json') as f:
    data = json.load(f)
console.print(JSON.from_data(data))
"
```

## 🔄 Git サブモジュール管理

### 基本操作

```bash
# サブモジュール追加
git submodule add https://github.com/user/repo.git libs/repo

# サブモジュール更新
git submodule update --remote --recursive

# 全サブモジュール最新化
git submodule foreach git pull origin main

# サブモジュール状態確認
git submodule status
```

### 自動更新

```bash
# 依存関係自動更新 (git pull後に実行)
./scripts/update_dependencies.sh

# 自動コミット付き更新
./scripts/update_dependencies.sh --auto-commit

# Git フック設定 (pull後自動実行)
echo "./scripts/update_dependencies.sh --git-hook" > .git/hooks/post-merge
chmod +x .git/hooks/post-merge
```

## 🧪 開発・テスト

### リンター・型チェック

```bash
# バックエンド
cd backend
poetry run flake8 app/
poetry run mypy app/

# フロントエンド
cd frontend
npm run lint
npm run type-check
```

### テスト実行

```bash
# バックエンドテスト
cd backend
poetry run pytest

# フロントエンドテスト
cd frontend
npm test
```

### データ収集テスト

```bash
# 特定取引所のデータ収集テスト
python -c "
from backend.app.topgun_integration import TopgunDataCollector
import asyncio
async def test_collection():
    collector = TopgunDataCollector()
    await collector.start_collection('binance', 'BTC_JPY')
    await asyncio.sleep(10)  # 10秒間データ収集
    await collector.stop_collection()
asyncio.run(test_collection())
"
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. WebSocket 接続エラー

```bash
# 症状: データ収集が開始されない
# 原因: APIキー未設定 or ネットワーク問題

# 解決方法:
# 1. ルート設定でAPIキーを確認
# 2. ネットワーク接続確認
curl -I https://api.binance.com/api/v3/ping

# 3. ログ確認
tail -f backend/logs/app.log
```

#### 2. データベース接続エラー

```bash
# 症状: SQLite接続失敗
# 解決方法:
cd backend
poetry run python -c "from app.database import init_db; init_db()"

# 権限確認
ls -la bot_forge.db
chmod 664 bot_forge.db
```

#### 3. フロントエンド起動エラー

```bash
# Node.js バージョン確認
node --version  # 18+ 必要

# 依存関係再インストール
cd frontend
rm -rf node_modules package-lock.json
npm install

# ポート競合確認
lsof -i :5173
```

#### 4. Poetry/依存関係エラー

```bash
# Poetry再インストール
curl -sSL https://install.python-poetry.org | python3 -

# 仮想環境リセット
cd backend
poetry env remove python
poetry install
```

### ログ確認

```bash
# アプリケーションログ
tail -f backend/logs/app.log

# WebSocketログ
tail -f backend/logs/websocket.log

# データ収集ログ
tail -f backend/logs/data_collection.log
```

## 📚 API リファレンス

### REST API エンドポイント

```bash
# 設定管理
GET    /api/settings/exchanges     # 取引所一覧
POST   /api/settings/api-keys      # APIキー保存
GET    /api/settings/api-keys      # APIキー取得

# データ管理
GET    /api/data/statistics        # データ統計
POST   /api/data/export           # データエクスポート
GET    /api/data/search           # データ検索

# バックテスト
POST   /api/backtest/run          # バックテスト実行
GET    /api/backtest/results      # 結果取得

# 分析
POST   /api/analysis/technical    # テクニカル分析
POST   /api/analysis/ml-features  # ML特徴量生成
POST   /api/analysis/o3          # o3分析連携
```

### WebSocket API

```bash
# データストリーム
ws://localhost:8000/ws/data/{exchange}/{symbol}

# システム状態
ws://localhost:8000/ws/status

# バックテスト進捗
ws://localhost:8000/ws/backtest/{session_id}
```

## 🔐 セキュリティ

### API キー管理

- **暗号化保存**: AES-256 で暗号化して SQLite に保存
- **メモリ保護**: 使用後即座にメモリクリア
- **アクセス制御**: ローカルアクセスのみ許可
- **監査ログ**: API 使用履歴を記録

### 推奨設定

```bash
# 本番環境では以下を設定
export SECRET_KEY="$(openssl rand -hex 32)"
export DATABASE_URL="postgresql://user:pass@localhost/botforge"
export DEBUG=false
export LOG_LEVEL=warning
```

## 🚀 デプロイメント

### Docker デプロイ

```bash
# Docker Compose起動
docker-compose up -d

# ログ確認
docker-compose logs -f
```

### 本番環境設定

```bash
# 環境変数設定
export ENVIRONMENT=production
export DATABASE_URL=postgresql://...
export REDIS_URL=redis://...

# システム起動
./scripts/production_start.sh
```

## 🤝 貢献・開発参加

### 開発フロー

1. **Issue 作成** - 機能要求・バグ報告
2. **Fork & Branch** - 開発ブランチ作成
3. **実装 & テスト** - 機能実装・テスト追加
4. **Pull Request** - レビュー依頼
5. **マージ** - main ブランチへマージ

### コーディング規約

- **Python**: PEP 8 + Black + isort
- **TypeScript**: ESLint + Prettier
- **コミット**: Conventional Commits
- **テスト**: 新機能には必ずテスト追加

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 📞 サポート

- **GitHub Issues**: https://github.com/kondoumanaya/bot_forge/issues
- **Documentation**: [docs/](./docs/)
- **Wiki**: https://github.com/kondoumanaya/bot_forge/wiki
