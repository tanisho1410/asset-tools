#!/usr/bin/env python3
"""
感情指数トラッキングシステム - Emotion Index Tracking System
投資判断における感情状態を記録・分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import track

console = Console()

class EmotionLogger:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.emotion_file = os.path.join(data_dir, "emotions.csv")
        self.ensure_data_dir()
        self.df = self.load_data()
        
        self.emotion_categories = {
            1: "極度不安 😰",
            2: "不安 😟", 
            3: "普通 😐",
            4: "自信 😊",
            5: "極度楽観 😍"
        }
        
        self.market_events = [
            "大幅上昇", "小幅上昇", "横ばい", "小幅下落", "大幅下落", 
            "決算発表", "経済指標", "FED会合", "地政学リスク", "その他"
        ]
    
    def ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_data(self):
        if os.path.exists(self.emotion_file):
            return pd.read_csv(self.emotion_file, parse_dates=['date'])
        else:
            return pd.DataFrame(columns=[
                'date', 'emotion_score', 'stress_level', 'confidence_level',
                'market_event', 'trading_action', 'notes', 'sleep_hours',
                'exercise_done', 'info_consumption'
            ])
    
    def save_data(self):
        self.df.to_csv(self.emotion_file, index=False)
        console.print(f"✅ 感情データ保存完了: {self.emotion_file}")
    
    def daily_entry(self):
        console.print("[bold blue]📊 今日の感情状態を記録します[/bold blue]")
        
        date = datetime.now().strftime('%Y-%m-%d')
        
        # 基本感情指数
        console.print("\n[yellow]1-5で評価してください（1=極度不安, 3=普通, 5=極度楽観）[/yellow]")
        emotion_score = IntPrompt.ask("全体的な感情状態", choices=["1", "2", "3", "4", "5"])
        
        stress_level = IntPrompt.ask("ストレスレベル（1=なし, 5=極度）", choices=["1", "2", "3", "4", "5"])
        
        confidence_level = IntPrompt.ask("投資判断への自信（1=なし, 5=極度）", choices=["1", "2", "3", "4", "5"])
        
        # 市場イベント
        console.print(f"\n[yellow]今日の主な市場イベント:[/yellow]")
        for i, event in enumerate(self.market_events, 1):
            console.print(f"{i}. {event}")
        
        market_event_idx = IntPrompt.ask("該当番号を選択", choices=[str(i) for i in range(1, len(self.market_events)+1)])
        market_event = self.market_events[market_event_idx - 1]
        
        # 取引行動
        trading_actions = ["売り", "買い", "ホールド", "様子見", "ポジション調整", "なし"]
        console.print(f"\n[yellow]今日の主な取引行動:[/yellow]")
        for i, action in enumerate(trading_actions, 1):
            console.print(f"{i}. {action}")
        
        trading_idx = IntPrompt.ask("該当番号を選択", choices=[str(i) for i in range(1, len(trading_actions)+1)])
        trading_action = trading_actions[trading_idx - 1]
        
        # ライフスタイル指標
        sleep_hours = IntPrompt.ask("昨夜の睡眠時間（時間）", choices=[str(i) for i in range(0, 13)])
        
        exercise_done = Confirm.ask("今日運動をしましたか？")
        
        info_levels = ["なし", "少し", "普通", "多め", "過剰"]
        console.print(f"\n[yellow]情報摂取量:[/yellow]")
        for i, level in enumerate(info_levels, 1):
            console.print(f"{i}. {level}")
        
        info_idx = IntPrompt.ask("該当番号を選択", choices=[str(i) for i in range(1, len(info_levels)+1)])
        info_consumption = info_levels[info_idx - 1]
        
        # 備考
        notes = Prompt.ask("備考・特記事項があれば入力", default="")
        
        # エントリー追加
        new_entry = {
            'date': date,
            'emotion_score': emotion_score,
            'stress_level': stress_level,
            'confidence_level': confidence_level,
            'market_event': market_event,
            'trading_action': trading_action,
            'notes': notes,
            'sleep_hours': sleep_hours,
            'exercise_done': exercise_done,
            'info_consumption': info_consumption
        }
        
        self.df = pd.concat([self.df, pd.DataFrame([new_entry])], ignore_index=True)
        self.save_data()
        
        console.print("\n✅ [green]感情記録完了[/green]")
        self.display_latest()
    
    def display_latest(self, n=7):
        table = Table(title="最新の感情記録")
        table.add_column("日付")
        table.add_column("感情", justify="center")
        table.add_column("ストレス", justify="center")
        table.add_column("自信", justify="center")
        table.add_column("市場イベント")
        table.add_column("取引行動")
        table.add_column("睡眠", justify="center")
        
        recent = self.df.tail(n)
        for _, row in recent.iterrows():
            table.add_row(
                row['date'].strftime('%m/%d') if hasattr(row['date'], 'strftime') else str(row['date']),
                str(row['emotion_score']),
                str(row['stress_level']),
                str(row['confidence_level']),
                str(row['market_event'])[:8],
                str(row['trading_action'])[:6],
                f"{row['sleep_hours']}h"
            )
        
        console.print(table)
    
    def get_weekly_summary(self, weeks_back=1):
        if len(self.df) == 0:
            return {}
        
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        mask = pd.to_datetime(self.df['date']) >= start_date
        week_data = self.df[mask]
        
        if len(week_data) == 0:
            return {}
        
        return {
            'avg_emotion': week_data['emotion_score'].mean(),
            'avg_stress': week_data['stress_level'].mean(),
            'avg_confidence': week_data['confidence_level'].mean(),
            'avg_sleep': week_data['sleep_hours'].mean(),
            'exercise_days': week_data['exercise_done'].sum(),
            'most_common_event': week_data['market_event'].mode().iloc[0] if len(week_data['market_event'].mode()) > 0 else 'N/A',
            'most_common_action': week_data['trading_action'].mode().iloc[0] if len(week_data['trading_action'].mode()) > 0 else 'N/A'
        }

@click.command()
@click.option('--daily-entry', is_flag=True, help='今日の感情記録を追加')
@click.option('--weekly-summary', is_flag=True, help='週次サマリーを表示')
@click.option('--show-recent', type=int, default=7, help='最新N日分を表示')
def main(daily_entry, weekly_summary, show_recent):
    logger = EmotionLogger()
    
    if daily_entry:
        logger.daily_entry()
    elif weekly_summary:
        summary = logger.get_weekly_summary()
        if summary:
            console.print("\n📊 [bold blue]週次感情サマリー[/bold blue]")
            console.print(f"平均感情スコア: {summary['avg_emotion']:.1f}")
            console.print(f"平均ストレス: {summary['avg_stress']:.1f}")
            console.print(f"平均自信レベル: {summary['avg_confidence']:.1f}")
            console.print(f"平均睡眠時間: {summary['avg_sleep']:.1f}時間")
            console.print(f"運動実施日数: {summary['exercise_days']}日")
            console.print(f"主な市場イベント: {summary['most_common_event']}")
            console.print(f"主な取引行動: {summary['most_common_action']}")
    else:
        logger.display_latest(show_recent)

if __name__ == "__main__":
    main()