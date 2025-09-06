#!/usr/bin/env python3
"""
資産追跡システム - Portfolio Tracking System
毎月の資産推移、入出金、パフォーマンスを記録・管理
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt, Confirm

console = Console()

class PortfolioTracker:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.portfolio_file = os.path.join(data_dir, "portfolio.csv")
        self.ensure_data_dir()
        self.df = self.load_data()
    
    def ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_data(self):
        if os.path.exists(self.portfolio_file):
            return pd.read_csv(self.portfolio_file, parse_dates=['date'])
        else:
            return pd.DataFrame(columns=[
                'date', 'total_value', 'deposit', 'withdrawal', 
                'net_flow', 'return_rate', 'notes'
            ])
    
    def save_data(self):
        self.df.to_csv(self.portfolio_file, index=False)
        console.print(f"✅ データ保存完了: {self.portfolio_file}")
    
    def add_entry(self, date=None, total_value=None, deposit=0, withdrawal=0, notes=""):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if total_value is None:
            total_value = FloatPrompt.ask("現在の総資産額を入力")
        
        net_flow = deposit - withdrawal
        
        # 前回との比較でリターン率計算
        if len(self.df) > 0:
            last_entry = self.df.iloc[-1]
            prev_value = last_entry['total_value']
            prev_net_flow = last_entry.get('net_flow', 0)
            
            # 実質的なリターン = (現在価値 - 前回価値 - 今回入出金) / 前回価値
            actual_return = (total_value - prev_value - net_flow) / prev_value * 100
        else:
            actual_return = 0
        
        new_entry = {
            'date': date,
            'total_value': total_value,
            'deposit': deposit,
            'withdrawal': withdrawal,
            'net_flow': net_flow,
            'return_rate': round(actual_return, 2),
            'notes': notes
        }
        
        self.df = pd.concat([self.df, pd.DataFrame([new_entry])], ignore_index=True)
        self.save_data()
        
        console.print("✅ エントリー追加完了")
        self.display_latest()
    
    def display_latest(self, n=5):
        table = Table(title="最新の資産記録")
        table.add_column("日付")
        table.add_column("資産額", justify="right")
        table.add_column("入金", justify="right")
        table.add_column("出金", justify="right")
        table.add_column("リターン率", justify="right")
        table.add_column("備考")
        
        recent = self.df.tail(n)
        for _, row in recent.iterrows():
            table.add_row(
                row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']),
                f"¥{row['total_value']:,.0f}",
                f"¥{row['deposit']:,.0f}" if row['deposit'] > 0 else "-",
                f"¥{row['withdrawal']:,.0f}" if row['withdrawal'] > 0 else "-",
                f"{row['return_rate']:+.1f}%" if pd.notna(row['return_rate']) else "-",
                str(row['notes'])[:20]
            )
        
        console.print(table)
    
    def get_summary(self):
        if len(self.df) == 0:
            return {}
        
        latest = self.df.iloc[-1]
        total_deposits = self.df['deposit'].sum()
        total_withdrawals = self.df['withdrawal'].sum()
        net_invested = total_deposits - total_withdrawals
        total_return = latest['total_value'] - net_invested
        total_return_rate = (total_return / net_invested * 100) if net_invested > 0 else 0
        
        return {
            'current_value': latest['total_value'],
            'net_invested': net_invested,
            'total_return': total_return,
            'total_return_rate': total_return_rate,
            'period_days': (pd.to_datetime(latest['date']) - pd.to_datetime(self.df.iloc[0]['date'])).days
        }

@click.command()
@click.option('--add-entry', is_flag=True, help='新しい資産記録を追加')
@click.option('--show-summary', is_flag=True, help='サマリーを表示')
@click.option('--value', type=float, help='資産額')
@click.option('--deposit', type=float, default=0, help='入金額')
@click.option('--withdrawal', type=float, default=0, help='出金額')
@click.option('--notes', type=str, default="", help='備考')
def main(add_entry, show_summary, value, deposit, withdrawal, notes):
    tracker = PortfolioTracker()
    
    if add_entry:
        tracker.add_entry(total_value=value, deposit=deposit, withdrawal=withdrawal, notes=notes)
    elif show_summary:
        summary = tracker.get_summary()
        if summary:
            console.print("\n📊 [bold blue]ポートフォリオサマリー[/bold blue]")
            console.print(f"現在価値: ¥{summary['current_value']:,.0f}")
            console.print(f"純投資額: ¥{summary['net_invested']:,.0f}")
            console.print(f"総リターン: ¥{summary['total_return']:,.0f} ({summary['total_return_rate']:+.1f}%)")
            console.print(f"運用期間: {summary['period_days']}日")
    else:
        tracker.display_latest()

if __name__ == "__main__":
    main()