# 投資開示ツール - Investment Disclosure Tools

完全透明性の投資実践を支援するツールセット

[![Charts Update](https://github.com/tanisho1410/investment-disclosure-tools/actions/workflows/update-charts.yml/badge.svg)](https://github.com/tanisho1410/investment-disclosure-tools/actions/workflows/update-charts.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📊 現在の統計 (Last Updated: 2025-09-06)

- **総資産額**: ¥2,261,361 (13銘柄)
- **評価損益**: +¥617,189 (+27.29%)
- **主力銘柄**: eMAXIS Slim米国株式(S&P500) 49.3%
- **感情記録**: 1エントリー (平均スコア: 3.0/5)

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

### 4. GitHub連携
- 自動データ更新
- 透明性レポート生成
- 検証可能な記録保持

## 🚀 使用方法

### セットアップ
```bash
pip install -r requirements.txt
python setup.py
```

### 基本操作
```bash
# 資産データ記録
python tools/portfolio_tracker.py --add-entry

# 感情指数記録
python tools/emotion_logger.py --daily-entry

# チャート生成
python tools/chart_generator.py --generate-all

# 月次レポート作成
python tools/report_builder.py --monthly
```

## 📁 ディレクトリ構造

```
investment-disclosure-tools/
├── data/                    # データファイル
│   ├── portfolio.csv       # 資産推移データ
│   ├── emotions.csv        # 感情指数データ
│   └── trades.csv          # 取引履歴
├── charts/                  # 生成チャート
├── reports/                 # 月次レポート
├── tools/                   # ツールスクリプト
└── templates/               # テンプレート
```

## 🔒 プライバシー・免責事項

- 投資成果は過去実績であり将来を保証するものではありません
- 個人的な投資判断の参考程度にとどめてください
- API キーや機密情報は含まれていません