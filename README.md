# bot_forge システム

高性能な仮想通貨取引ボットのバックテスト・分析・データ収集システム

## システム概要

bot_forgeは以下の機能を提供する包括的な取引ボットシステムです：

1. **Botのバックテスト** - 戦略の有効性を過去データで検証、エッジ抽出
2. **o3による相場分析** - 特徴量探索・MLモデル作成のための学習データ生成  
3. **戦略の可視化** - PnL, ドローダウン, エントリーポイントの分析
4. **データ収集基盤構築** - 複数取引所・時間足に対応したデータ保存/管理機構

## アーキテクチャ

```
+----------------------------+
| UI Frontend (Next.js)      |
| - shadcn/ui + Tailwind CSS |
| - 時間足切替 / 取引所選択  |
+-------------+--------------+
              ↓
+----------------------------+
| FastAPI Backend            |
| - WebSocket受信 & DataStore|
| - SQLite保存 / JSON出力    |
+-------------+--------------+
              ↓
+----------------------------+
| ストレージ層               |
| - SQLite / DuckDB          |
| - Parquet / CSV対応        |
| - bot戦略ごとに保存分離    |
+----------------------------+
```

## 技術スタック

- **フロントエンド**: Next.js + Tailwind CSS + shadcn/ui
- **バックエンド**: FastAPI + WebSocket
- **データ取得**: topgun + DataStore
- **保存**: SQLite(PoC向け)
- **可視化**: rich / seaborn / plotly
- **分析・ML**: pandas / scikit-learn / pytorch
- **ファイル出力**: JSON / Parquet / CSV 形式

## データ管理ポリシー

- **直近12ヶ月**: SQLite(常時アクセス)
- **6ヶ月~2年**: 圧縮(Parquet/CSV + zip)
- **2年以上前**: 自動削除

## 環境構築

### 前提条件

- Python 3.12+
- Node.js 18+
- Git

### 1. リポジトリのクローン

```bash
git clone https://github.com/kondoumanaya/bot_forge.git
cd bot_forge
git submodule update --init --recursive
```

### 2. バックエンドのセットアップ

```bash
cd backend
pip install -r requirements.txt
```

### 3. フロントエンドのセットアップ

```bash
cd frontend
npm install
```

### 4. 環境変数の設定

```bash
cp .env.example .env
# .envファイルを編集して必要な設定を行う
```

## アプリケーション起動

### 開発環境

```bash
# バックエンド起動
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# フロントエンド起動（別ターミナル）
cd frontend
npm run dev
```

### プロダクション環境

```bash
# バックエンド
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# フロントエンド
cd frontend
npm run build
npm start
```

## CLI使用方法

```bash
# データ分析
python cli/analyze.py --exchange binance --symbol BTC_JPY --period 1d

# データエクスポート
python cli/export.py --format parquet --output data.parquet

# o3連携
python cli/o3_analysis.py --input data.json
```

## 機能詳細

### UI要件

1. **取引所切り替え** - プルダウンまたはタブで複数取引所を選択可能
2. **時間足切り替え** - 1秒/1分/5分/1時間/日足/週足/月足などの切り替えUI
3. **データプレビュー** - 現在取得しているTickデータ・板・OHLCなどのライブビュー
4. **データ保存操作** - 条件を指定してCSV/Parquet形式で保存、ファイルDL可能
5. **分析パネル** - 特徴量の可視化、勝率・PnLグラフ表示
6. **データ管理** - 期間指定検索/取引所フィルター/データ検索表示

### 相場データ取得要件

- **Tickデータ** - 約定価格・数量 (ミリ秒)
- **板情報** - bid/ask価格とサイズのリスト(深さ10~50程度)
- **成行約定履歴** - takerの注文履歴(price/size/side)
- **時間足** - OHLC 1min, 5min, 1h, daily, week
- **ポジション/トレード履歴** - botの行動ログ(entry/exit,損益など)
- **タイムスタンプ** - JST/UTC秒単位(ローカル→UTC統一)

## 開発ガイド

### Git Submodule管理

```bash
# サブモジュール追加
git submodule add <repository_url> <path>

# サブモジュール更新
git submodule update --remote

# 全サブモジュール同期
git submodule foreach git pull origin main
```

### 依存関係更新

```bash
# Python依存関係更新
pip install -r requirements.txt

# Node.js依存関係更新
npm install

# 自動更新スクリプト
./scripts/update_dependencies.sh
```

## トラブルシューティング

### よくある問題

1. **WebSocket接続エラー**
   - ネットワーク設定を確認
   - APIキーの有効性を確認

2. **データベース接続エラー**
   - SQLiteファイルの権限を確認
   - ディスク容量を確認

3. **フロントエンド起動エラー**
   - Node.jsバージョンを確認
   - npm installを再実行

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。

## サポート

- GitHub Issues: https://github.com/kondoumanaya/bot_forge/issues
- Documentation: [docs/](./docs/)

---

**Link to Devin run**: https://app.devin.ai/sessions/4e167d0b763d4952891dcdc835abc389
**Requested by**: manaya_kondou@icloud.com
