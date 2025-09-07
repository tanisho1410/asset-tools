# 投資開示ツール - Investment Disclosure Tools

完全透明性の投資実践を支援するツールセット + Webアプリケーション

[![Charts Update](https://github.com/tanisho1410/investment-disclosure-tools/actions/workflows/update-charts.yml/badge.svg)](https://github.com/tanisho1410/investment-disclosure-tools/actions/workflows/update-charts.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📊 現在の統計 (Last Updated: 2025-09-06)

- **総資産額**: ¥2,261,361 (13銘柄)
- **評価損益**: +¥617,189 (+27.29%)
- **主力銘柄**: eMAXIS Slim米国株式(S&P500) 49.3%
- **感情記録**: 1エントリー (平均スコア: 3.0/5)

## 🚀 新機能: Webアプリケーション

### 📱 **誰でも簡単に使える Web インターフェース**

```bash
# Webアプリ起動
python app.py
# ブラウザで http://localhost:5000 にアクセス
```

#### ✨ **主要機能**
- **CSV ドラッグ&ドロップ アップロード**
- **リアルタイム資産配分円グラフ**  
- **銘柄別パフォーマンス分析**
- **Yahoo Finance API 連携**
- **レスポンシブデザイン**

#### 📊 **対応証券会社**
- SBI証券 ✅
- 楽天証券 ✅  
- マネックス証券 ✅

## 📊 機能概要

### 1. 資産追跡システム
- 毎月の資産推移記録
- 入出金履歴管理
- パフォーマンス計算

### 2. 感情指数トラッキング
- 日次/週次の感情状態記録
- 投資判断への感情的影響分析
- ストレス・不安レベルの可視化

### 3. 自動可視化
- 資産推移グラフ
- 感情曲線チャート
- 月次サマリーレポート

### 4. CSV統合・証券分析 🆕
- **SBI・楽天証券CSV自動インポート**
- **個別銘柄リアルタイム分析**
- **リスク・パフォーマンス評価**
- **投資判断アルゴリズム**

### 5. Webアプリケーション 🆕
- **ブラウザベース操作**
- **インタラクティブチャート**
- **リアルタイムデータ取得**

### 6. GitHub連携
- 自動データ更新
- 透明性レポート生成
- 検証可能な記録保持

## 🚀 使用方法

### セットアップ
```bash
pip install -r requirements.txt
python setup.py
```

### 🌐 Webアプリケーション (推奨)
```bash
python app.py
# ブラウザで http://localhost:5000 にアクセス
```

### 📊 コマンドライン版
```bash
# 資産データ記録
python tools/portfolio_tracker.py --add-entry

# 感情指数記録
python tools/emotion_logger.py --daily-entry

# CSV統合
python tools/csv_importer.py --import-csv your-file.csv
python tools/csv_importer.py --analyze-holdings

# 証券分析
python tools/securities_analyzer.py --symbol AAPL --quantity 100

# チャート生成
python tools/chart_generator.py --generate-all

# 月次レポート作成
python tools/report_builder.py --monthly
```

## 📁 ディレクトリ構造

```
investment-disclosure-tools/
├── app.py                   # Webアプリケーション
├── templates/               # HTMLテンプレート
│   ├── base.html           # ベーステンプレート
│   ├── index.html          # メインページ
│   └── dashboard.html      # 分析ダッシュボード
├── static/                  # 静的ファイル
│   ├── css/style.css       # カスタムスタイル
│   └── js/app.js          # JavaScript
├── data/                    # データファイル
│   ├── portfolio.csv       # 資産推移データ
│   ├── emotions.csv        # 感情指数データ
│   ├── holdings.csv        # 保有銘柄データ 🆕
│   └── trades.csv          # 取引履歴 🆕
├── charts/                  # 生成チャート
├── reports/                 # 月次レポート
├── tools/                   # ツールスクリプト
│   ├── portfolio_tracker.py
│   ├── emotion_logger.py
│   ├── csv_importer.py     # CSV統合 🆕
│   └── securities_analyzer.py # 証券分析 🆕
└── templates/               # テンプレート
```

## 💡 使用例

### CSV アップロード・分析
1. SBI証券・楽天証券からポートフォリオCSVをダウンロード
2. Webアプリにドラッグ&ドロップでアップロード  
3. 自動で資産配分・パフォーマンス分析
4. 保有銘柄のリアルタイム分析表示

### 個別銘柄分析
- **Apple (AAPL)**: +59.8%リターン、高リスク評価
- **SPY ETF**: +61.8%リターン、中リスク評価
- **Yahoo Finance API**でリアルタイム価格・指標取得

### ポートフォリオ構成分析
- **セクター分散**: テクノロジー・ヘルスケア・金融
- **リスク評価**: 低/中/高リスク銘柄の分散状況
- **推奨事項**: 自動的な分散投資アドバイス

## 🔧 技術仕様

### Backend
- **Python 3.10+**
- **Flask 2.3+** (Webフレームワーク)
- **pandas** (データ処理)
- **yfinance** (株価API)
- **plotly** (インタラクティブチャート)

### Frontend  
- **Bootstrap 5** (UIフレームワーク)
- **Font Awesome** (アイコン)
- **Plotly.js** (チャート)
- **レスポンシブデザイン**

### APIs
- **Yahoo Finance** (株価・企業情報)
- **自動エンコーディング検出** (CSV処理)

## 🔒 プライバシー・免責事項

- 投資成果は過去実績であり将来を保証するものではありません
- 個人的な投資判断の参考程度にとどめてください
- **アップロードされたCSVは一時処理のみ、永続保存されません**
- API キーや機密情報は含まれていません

---

**GitHubリポジトリ**: https://github.com/tanisho1410/asset-tools