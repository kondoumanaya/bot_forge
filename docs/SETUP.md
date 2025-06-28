# Bot Forge セットアップガイド

このドキュメントでは、Bot Forge システムの詳細なセットアップ手順を説明します。

## 前提条件

### 必要なソフトウェア

- **Python 3.12+**: バックエンド API 用
- **Node.js 18+**: フロントエンド用
- **Poetry**: Python 依存関係管理
- **Git**: バージョン管理と submodule 管理

### 推奨ツール

- **pnpm**: 高速な Node.js パッケージマネージャー（npm の代替）
- **VS Code**: 開発環境（Python、TypeScript 拡張推奨）

## 詳細セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/kondoumanaya/bot_forge.git
cd bot_forge
```

### 2. git submodule の初期化

Bot Forge は`root-bot`ライブラリを submodule として使用しています：

```bash
git submodule update --init --recursive
```

### 3. バックエンドセットアップ

#### Poetry 環境の構築

```bash
cd backend
poetry install
```

#### 環境変数の設定（オプション）

`.env`ファイルを作成して設定をカスタマイズ：

```bash
# backend/.env
DEBUG=true
DATABASE_URL=sqlite:///./bot_forge.db
WS_HEARTBEAT_INTERVAL=30
SQLITE_RETENTION_MONTHS=12
PARQUET_RETENTION_YEARS=2
```

#### データベースの初期化

```bash
poetry run python -c "from app.database import init_db; init_db()"
```

### 4. フロントエンドセットアップ

#### 依存関係のインストール

```bash
cd frontend

# pnpmを使用（推奨）
pnpm install

# または npm を使用
npm install
```

### 5. CLI ツールセットアップ

```bash
cd cli
pip install pandas rich typer
```

## 開発環境の起動

### 自動セットアップスクリプト使用

```bash
./scripts/setup.sh
```

### 手動起動

#### 1. バックエンドサーバー

```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. フロントエンドサーバー

```bash
cd frontend
npm run dev
# または
pnpm dev
```

#### 3. アクセス確認

- **フロントエンド**: http://localhost:5173
- **バックエンド API**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs

## 取引所 API 設定

### 1. ルート設定ページでの設定

1. http://localhost:5173 にアクセス
2. サイドバーから「ルート設定」を選択
3. 使用する取引所のタブを選択
4. API キー情報を入力：
   - **API Key**: 取引所から発行された API キー
   - **Secret Key**: 対応するシークレットキー
   - **Passphrase**: KuCoin など一部取引所で必要

### 2. 対応取引所一覧

**日本国内取引所**

- bitFlyer
- GMO Coin
- bitbank
- Coincheck
- OKJ (OKCoin Japan)
- BitTrade

**海外取引所**

- Binance
- Bybit
- OKX
- Phemex
- Bitget
- MEXC
- KuCoin
- BitMEX
- Hyperliquid

## データ収集の開始

### 1. WebSocket データ収集

1. 「Data Preview」ページを開く
2. 取引所とシンボルを選択
3. 「Start」ボタンでデータ収集開始
4. リアルタイムデータの表示を確認

### 2. 収集されるデータタイプ

- **Tick データ**: 約定価格・数量（ミリ秒精度）
- **板情報**: bid/ask 価格とサイズ
- **OHLC データ**: 時間足データ
- **約定履歴**: 取引履歴

## バックテストの実行

### 1. 戦略設定

1. 「Backtest」ページを開く
2. 戦略を選択（SMA クロスオーバー、平均回帰、モメンタム）
3. パラメータを設定：
   - 初期資金
   - 期間（開始日・終了日）
   - リスクパラメータ

### 2. 結果の確認

- 総リターン
- 最大ドローダウン
- シャープレシオ
- 勝率
- 取引履歴

## 相場分析と o3 統合

### 1. 分析実行

1. 「Analysis」ページを開く
2. 分析タイプを選択：
   - テクニカル分析
   - ML 特徴量生成
   - o3 統合分析
3. 期間を指定して実行

### 2. 結果のエクスポート

- JSON 形式でのデータエクスポート
- o3 プロンプト生成
- ML 特徴量の可視化

## CLI ツールの使用

### データエクスポート

```bash
# CSVエクスポート
python cli/export.py --exchange binance --symbol BTC_USDT --data-type tick --format csv --output data.csv --days 7

# Parquetエクスポート（圧縮）
python cli/export.py --exchange binance --symbol BTC_USDT --data-type ohlc --format parquet --output data.parquet --compress
```

### o3 分析

```bash
# 分析実行
python cli/o3_analysis.py --input data.json --output analysis.md --format prompt
```

## git submodule 管理

### submodule の更新

```bash
git submodule update --remote --recursive
```

### 依存関係の自動更新

```bash
./scripts/update_dependencies.sh
```

### 新しい submodule の追加

```bash
git submodule add <repository-url> <path>
git submodule update --init --recursive
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. Poetry 環境の問題

```bash
# Poetry環境のリセット
cd backend
poetry env remove python
poetry install
```

#### 2. Node.js 依存関係の問題

```bash
# node_modulesのクリア
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 3. データベース接続エラー

```bash
# データベースの再初期化
cd backend
rm bot_forge.db
poetry run python -c "from app.database import init_db; init_db()"
```

#### 4. WebSocket 接続失敗

- 取引所 API キーの設定を確認
- ネットワーク接続を確認
- ファイアウォール設定を確認

#### 5. CLI ツールエラー

```bash
# 依存関係の再インストール
pip install --upgrade pandas rich typer
```

## 開発環境の設定

### VS Code 設定

推奨拡張機能：

- Python
- TypeScript and JavaScript Language Features
- Tailwind CSS IntelliSense
- ES7+ React/Redux/React-Native snippets

### デバッグ設定

`.vscode/launch.json`を作成してデバッグ環境を設定：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/app/main.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "Node: Frontend Dev",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/frontend/node_modules/.bin/vite",
      "args": ["dev"],
      "cwd": "${workspaceFolder}/frontend",
      "console": "integratedTerminal"
    }
  ]
}
```

## パフォーマンス最適化

### データベース最適化

```sql
-- インデックス作成例
CREATE INDEX idx_tick_data_exchange_symbol_timestamp
ON tick_data(exchange, symbol, timestamp);

CREATE INDEX idx_ohlc_data_exchange_symbol_timeframe_timestamp
ON ohlc_data(exchange, symbol, timeframe, timestamp);
```

### WebSocket 接続最適化

- 接続プールサイズの調整
- ハートビート間隔の最適化
- 再接続ロジックの改善

### フロントエンド最適化

- コンポーネントの遅延読み込み
- 仮想化によるリスト表示の最適化
- WebSocket データのバッファリング

## セキュリティ

### API キー管理

- 暗号化されたデータベース保存
- 環境変数による設定
- アクセス権限の制限

### ネットワークセキュリティ

- HTTPS 通信の強制
- CORS 設定の適切な管理
- レート制限の実装

## 監視・ログ

### ログ設定

```python
# backend/app/config.py
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": "bot_forge.log",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default", "file"],
    },
}
```

### メトリクス監視

- データ収集レート
- WebSocket 接続状態
- バックテスト実行時間
- API 応答時間

## 本番環境デプロイ

### Docker 設定

```dockerfile
# Dockerfile.backend
FROM python:3.12-slim

WORKDIR /app
COPY backend/pyproject.toml backend/poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY backend/ ./
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

### docker-compose.yml

```yaml
version: "3.8"
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./bot_forge.db
    volumes:
      - ./data:/app/data

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

## 高度な使用例

### カスタム戦略の実装

```python
# backend/app/strategies/custom_strategy.py
from ..backtest_engine import TradingStrategy
import pandas as pd

class CustomMomentumStrategy(TradingStrategy):
    def should_buy(self, data: pd.DataFrame) -> bool:
        if len(data) < 10:
            return False

        momentum = data['close'].pct_change(periods=5).iloc[-1]
        volume_spike = data['volume'].iloc[-1] > data['volume'].rolling(10).mean().iloc[-1] * 1.5

        return momentum > 0.02 and volume_spike and self.position is None

    def should_sell(self, data: pd.DataFrame) -> bool:
        if self.position is None:
            return False

        current_price = data['close'].iloc[-1]
        profit_pct = (current_price - self.position.entry_price) / self.position.entry_price

        return profit_pct > 0.05 or profit_pct < -0.02
```

### 高度な o3 分析プロンプト

```python
# cli/advanced_o3_analysis.py
def create_advanced_o3_prompt(data: dict) -> str:
    return f"""
# 高度な暗号通貨市場分析
## 市場データ概要
- 取引所: {data['exchange']}
- シンボル: {data['symbol']}
- 分析期間: {data['period']}
## テクニカル分析
{generate_technical_analysis(data)}
## 機械学習特徴量
{generate_ml_features(data)}
## リスク分析
{generate_risk_analysis(data)}
## 取引推奨
{generate_trading_recommendations(data)}
## 質問
1. 現在の市場状況をどう評価しますか？
2. 短期的な価格動向の予測は？
3. リスク管理の観点から注意すべき点は？
4. 最適なエントリー・エグジット戦略は？
"""
```

## FAQ

### Q: データ収集が停止してしまいます

A: 以下を確認してください：

1. 取引所 API キーの有効性
2. ネットワーク接続の安定性
3. レート制限の確認
4. ログファイルでエラーメッセージを確認

### Q: バックテストの結果が期待と異なります

A: 以下を確認してください：

1. 戦略パラメータの設定
2. 手数料の考慮
3. スリッページの設定
4. データの品質と完全性

### Q: o3 分析の精度を向上させるには？

A: 以下を試してください：

1. より多くの特徴量を追加
2. 分析期間を調整
3. 複数の時間足を組み合わせ
4. 外部データソースの統合

### Q: 本番環境での推奨設定は？

A: 以下を推奨します：

1. データベースのバックアップ設定
2. ログローテーションの設定
3. 監視・アラートの設定
4. セキュリティ設定の強化

---

このセットアップガイドに従って、Bot Forge システムを正しく構築・運用してください。追加の質問や問題がある場合は、GitHub の Issues ページで報告してください。
