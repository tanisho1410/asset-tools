#!/usr/bin/env python3
"""
レポート生成システム - Report Generation System
月次透明性レポートの自動生成
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import click
from rich.console import Console
from pathlib import Path
import json

console = Console()

class ReportBuilder:
    def __init__(self, data_dir="data", reports_dir="reports", charts_dir="charts"):
        self.data_dir = data_dir
        self.reports_dir = reports_dir
        self.charts_dir = charts_dir
        self.ensure_reports_dir()
        
    def ensure_reports_dir(self):
        os.makedirs(self.reports_dir, exist_ok=True)
        
    def load_portfolio_data(self):
        portfolio_file = os.path.join(self.data_dir, "portfolio.csv")
        if os.path.exists(portfolio_file):
            return pd.read_csv(portfolio_file, parse_dates=['date'])
        return pd.DataFrame()
    
    def load_emotion_data(self):
        emotion_file = os.path.join(self.data_dir, "emotions.csv")
        if os.path.exists(emotion_file):
            return pd.read_csv(emotion_file, parse_dates=['date'])
        return pd.DataFrame()
    
    def generate_monthly_report(self, year=None, month=None):
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
            
        report_date = datetime(year, month, 1)
        next_month = report_date.replace(month=month+1) if month < 12 else report_date.replace(year=year+1, month=1)
        
        # データ読み込み
        portfolio_df = self.load_portfolio_data()
        emotion_df = self.load_emotion_data()
        
        if portfolio_df.empty:
            console.print("⚠️ ポートフォリオデータが見つかりません")
            return
            
        # 月次データフィルタ
        month_portfolio = portfolio_df[
            (portfolio_df['date'] >= report_date) & 
            (portfolio_df['date'] < next_month)
        ]
        
        month_emotion = emotion_df[
            (emotion_df['date'] >= report_date) & 
            (emotion_df['date'] < next_month)
        ] if not emotion_df.empty else pd.DataFrame()
        
        # レポート生成
        report_content = self._build_report_content(
            year, month, month_portfolio, month_emotion, portfolio_df
        )
        
        # ファイル保存
        report_filename = f"{year}-{month:02d}-monthly-report.md"
        report_path = os.path.join(self.reports_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        console.print(f"✅ 月次レポート生成完了: {report_path}")
        return report_path
    
    def _build_report_content(self, year, month, month_portfolio, month_emotion, full_portfolio):
        month_str = f"{year}年{month}月"
        
        # ポートフォリオ分析
        if not month_portfolio.empty:
            start_value = month_portfolio.iloc[0]['total_value']
            end_value = month_portfolio.iloc[-1]['total_value']
            total_deposits = month_portfolio['deposit'].sum()
            total_withdrawals = month_portfolio['withdrawal'].sum()
            net_flow = total_deposits - total_withdrawals
            
            # 実質リターン（入出金を除く）
            actual_return = end_value - start_value - net_flow
            return_rate = (actual_return / start_value * 100) if start_value > 0 else 0
            
            # 累計統計
            if len(full_portfolio) > 1:
                total_invested = full_portfolio['deposit'].sum() - full_portfolio['withdrawal'].sum()
                total_gain = end_value - total_invested
                total_return_rate = (total_gain / total_invested * 100) if total_invested > 0 else 0
            else:
                total_return_rate = 0
                total_gain = 0
        else:
            return_rate = 0
            net_flow = 0
            end_value = 0
            total_return_rate = 0
            total_gain = 0
        
        # 感情分析
        if not month_emotion.empty:
            avg_emotion = month_emotion['emotion_score'].mean()
            avg_stress = month_emotion['stress_level'].mean()
            avg_confidence = month_emotion['confidence_level'].mean()
            avg_sleep = month_emotion['sleep_hours'].mean()
            exercise_days = month_emotion['exercise_done'].sum()
            
            emotion_emoji = self._emotion_to_emoji(avg_emotion)
            stress_emoji = self._stress_to_emoji(avg_stress)
            
            # 主要市場イベントと取引行動
            top_events = month_emotion['market_event'].value_counts().head(3)
            top_actions = month_emotion['trading_action'].value_counts().head(3)
        else:
            avg_emotion = avg_stress = avg_confidence = avg_sleep = 0
            exercise_days = 0
            emotion_emoji = stress_emoji = "😐"
            top_events = top_actions = pd.Series()
        
        # Markdownレポート作成
        report = f"""# {month_str} 投資透明性レポート

> **完全開示主義** - すべての数字と感情を公開

## 📊 財務サマリー

| 指標 | 値 |
|------|-----|
| **月末資産評価額** | ¥{end_value:,.0f} |
| **月次実質リターン** | {return_rate:+.1f}% |
| **純入出金** | ¥{net_flow:+,.0f} |
| **累計総利益** | ¥{total_gain:+,.0f} |
| **累計リターン率** | {total_return_rate:+.1f}% |

## 🧠 メンタル分析

### 感情指標
- **平均感情スコア**: {avg_emotion:.1f}/5 {emotion_emoji}
- **平均ストレスレベル**: {avg_stress:.1f}/5 {stress_emoji}  
- **平均自信レベル**: {avg_confidence:.1f}/5
- **平均睡眠時間**: {avg_sleep:.1f}時間
- **運動実施日数**: {exercise_days}日

### 主要市場イベント
"""
        
        if not top_events.empty:
            for event, count in top_events.items():
                report += f"- {event}: {count}回\n"
        else:
            report += "- データなし\n"
            
        report += "\n### 主要取引行動\n"
        if not top_actions.empty:
            for action, count in top_actions.items():
                report += f"- {action}: {count}回\n"
        else:
            report += "- データなし\n"

        report += f"""
## 📈 チャート・可視化

![資産推移](../charts/portfolio_static.png)
![感情分析](../charts/emotion_static.png)
![相関分析](../charts/correlation_analysis.png)

## 🔍 振り返りと学び

### 今月のハイライト
- **最も成功した判断**: [手動記入]
- **最大の失敗**: [手動記入]
- **重要な気づき**: [手動記入]

### 来月の改善ルール
- [ ] [ルール1を記入]
- [ ] [ルール2を記入]  
- [ ] [ルール3を記入]

## ⚖️ 免責事項

この情報は個人的な投資記録であり、投資助言ではありません。すべての投資はリスクを伴います。

---
**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**データソース**: [GitHub Repository](https://github.com/tanisho1410/investment-disclosure-tools)
"""
        
        return report
    
    def _emotion_to_emoji(self, score):
        if score >= 4.5: return "😍"
        elif score >= 3.5: return "😊"
        elif score >= 2.5: return "😐"
        elif score >= 1.5: return "😟"
        else: return "😰"
    
    def _stress_to_emoji(self, score):
        if score >= 4.5: return "🔥"
        elif score >= 3.5: return "😤"
        elif score >= 2.5: return "😕"
        elif score >= 1.5: return "🙂"
        else: return "😌"
    
    def generate_readme_summary(self):
        """READMEの統計部分を更新"""
        portfolio_df = self.load_portfolio_data()
        emotion_df = self.load_emotion_data()
        
        if portfolio_df.empty:
            return
            
        latest_portfolio = portfolio_df.iloc[-1]
        total_invested = portfolio_df['deposit'].sum() - portfolio_df['withdrawal'].sum()
        total_return = latest_portfolio['total_value'] - total_invested
        total_return_rate = (total_return / total_invested * 100) if total_invested > 0 else 0
        
        days_tracked = (pd.to_datetime(latest_portfolio['date']) - pd.to_datetime(portfolio_df.iloc[0]['date'])).days
        
        # 感情統計
        if not emotion_df.empty:
            avg_emotion = emotion_df['emotion_score'].mean()
            entries_count = len(emotion_df)
        else:
            avg_emotion = 0
            entries_count = 0
        
        summary = f"""
## 📊 現在の統計 (Last Updated: {datetime.now().strftime('%Y-%m-%d')})

- **現在資産額**: ¥{latest_portfolio['total_value']:,.0f}
- **累計リターン**: {total_return_rate:+.1f}% (¥{total_return:+,.0f})
- **追跡期間**: {days_tracked}日間
- **感情記録**: {entries_count}エントリー (平均スコア: {avg_emotion:.1f}/5)

[![Charts Update](https://github.com/tanisho1410/investment-disclosure-tools/actions/workflows/update-charts.yml/badge.svg)](https://github.com/tanisho1410/investment-disclosure-tools/actions/workflows/update-charts.yml)
"""
        
        return summary

@click.command()
@click.option('--monthly', is_flag=True, help='月次レポート生成')
@click.option('--year', type=int, help='年を指定')
@click.option('--month', type=int, help='月を指定 (1-12)')
@click.option('--auto-generate', is_flag=True, help='自動生成 (前月のレポート)')
def main(monthly, year, month, auto_generate):
    builder = ReportBuilder()
    
    if auto_generate:
        # 前月のレポートを自動生成
        last_month = datetime.now().replace(day=1) - timedelta(days=1)
        builder.generate_monthly_report(last_month.year, last_month.month)
    elif monthly:
        builder.generate_monthly_report(year, month)
    else:
        console.print("オプションを指定してください (--help で詳細確認)")

if __name__ == "__main__":
    main()