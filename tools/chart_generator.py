#!/usr/bin/env python3
"""
チャート生成システム - Chart Generation System
資産推移、感情指数、パフォーマンス分析の可視化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import click
from rich.console import Console

console = Console()

class ChartGenerator:
    def __init__(self, data_dir="data", charts_dir="charts"):
        self.data_dir = data_dir
        self.charts_dir = charts_dir
        self.ensure_charts_dir()
        
        # 日本語フォント設定
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'Hiragino Sans']
        sns.set_style("whitegrid")
        
    def ensure_charts_dir(self):
        os.makedirs(self.charts_dir, exist_ok=True)
    
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
    
    def generate_portfolio_chart(self, interactive=True):
        df = self.load_portfolio_data()
        if df.empty:
            console.print("⚠️ ポートフォリオデータが見つかりません")
            return
        
        if interactive:
            # Plotlyで対話的チャート
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('資産推移', '月次リターン率'),
                vertical_spacing=0.1,
                row_heights=[0.7, 0.3]
            )
            
            # 資産推移
            fig.add_trace(
                go.Scatter(
                    x=df['date'], 
                    y=df['total_value'],
                    mode='lines+markers',
                    name='資産額',
                    line=dict(color='#1f77b4', width=3),
                    hovertemplate='日付: %{x}<br>資産額: ¥%{y:,.0f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # リターン率
            fig.add_trace(
                go.Bar(
                    x=df['date'], 
                    y=df['return_rate'],
                    name='月次リターン率',
                    marker=dict(
                        color=df['return_rate'],
                        colorscale='RdYlGn',
                        showscale=True
                    ),
                    hovertemplate='日付: %{x}<br>リターン: %{y:.1f}%<extra></extra>'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title='ポートフォリオ分析ダッシュボード',
                height=700,
                showlegend=False
            )
            
            fig.update_xaxes(title_text="日付", row=2, col=1)
            fig.update_yaxes(title_text="資産額 (¥)", row=1, col=1)
            fig.update_yaxes(title_text="リターン率 (%)", row=2, col=1)
            
            output_file = os.path.join(self.charts_dir, "portfolio_interactive.html")
            fig.write_html(output_file)
            console.print(f"✅ 対話的チャート生成完了: {output_file}")
        
        # 静的チャート（GitHub用）
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 資産推移
        ax1.plot(df['date'], df['total_value'], marker='o', linewidth=2.5, markersize=6)
        ax1.set_title('Portfolio Value Over Time', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Total Value (¥)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'¥{x/1e6:.1f}M'))
        
        # リターン率
        colors = ['red' if x < 0 else 'green' for x in df['return_rate']]
        ax2.bar(df['date'], df['return_rate'], color=colors, alpha=0.7)
        ax2.set_title('Monthly Returns', fontsize=16, fontweight='bold')
        ax2.set_ylabel('Return Rate (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        static_file = os.path.join(self.charts_dir, "portfolio_static.png")
        plt.savefig(static_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"✅ 静的チャート生成完了: {static_file}")
    
    def generate_emotion_chart(self, interactive=True):
        df = self.load_emotion_data()
        if df.empty:
            console.print("⚠️ 感情データが見つかりません")
            return
        
        if interactive:
            # Plotlyで感情分析ダッシュボード
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('感情スコア推移', 'ストレス vs 自信', '睡眠時間', '取引行動分布'),
                specs=[[{}, {}], [{}, {"type": "pie"}]]
            )
            
            # 感情スコア推移
            fig.add_trace(
                go.Scatter(
                    x=df['date'], y=df['emotion_score'],
                    mode='lines+markers', name='感情',
                    line=dict(color='blue')
                ), row=1, col=1
            )
            
            # ストレス vs 自信の散布図
            fig.add_trace(
                go.Scatter(
                    x=df['stress_level'], y=df['confidence_level'],
                    mode='markers', name='ストレス-自信',
                    marker=dict(size=8, color=df['emotion_score'], colorscale='Viridis')
                ), row=1, col=2
            )
            
            # 睡眠時間
            fig.add_trace(
                go.Scatter(
                    x=df['date'], y=df['sleep_hours'],
                    mode='lines+markers', name='睡眠',
                    line=dict(color='purple')
                ), row=2, col=1
            )
            
            # 取引行動分布
            action_counts = df['trading_action'].value_counts()
            fig.add_trace(
                go.Pie(
                    labels=action_counts.index, values=action_counts.values,
                    name='取引行動'
                ), row=2, col=2
            )
            
            fig.update_layout(
                title='感情分析ダッシュボード',
                height=800
            )
            
            emotion_interactive_file = os.path.join(self.charts_dir, "emotion_interactive.html")
            fig.write_html(emotion_interactive_file)
            console.print(f"✅ 感情分析チャート生成完了: {emotion_interactive_file}")
        
        # 静的チャート
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 感情スコア推移
        ax1.plot(df['date'], df['emotion_score'], marker='o', color='blue', alpha=0.7)
        ax1.fill_between(df['date'], df['emotion_score'], alpha=0.3, color='blue')
        ax1.set_title('Emotion Score Over Time')
        ax1.set_ylabel('Emotion Score (1-5)')
        ax1.grid(True, alpha=0.3)
        
        # ストレス vs 自信
        scatter = ax2.scatter(df['stress_level'], df['confidence_level'], 
                             c=df['emotion_score'], cmap='viridis', s=60, alpha=0.7)
        ax2.set_title('Stress vs Confidence')
        ax2.set_xlabel('Stress Level')
        ax2.set_ylabel('Confidence Level')
        plt.colorbar(scatter, ax=ax2, label='Emotion Score')
        
        # 睡眠時間
        ax3.plot(df['date'], df['sleep_hours'], marker='s', color='purple', alpha=0.7)
        ax3.set_title('Sleep Hours')
        ax3.set_ylabel('Hours')
        ax3.grid(True, alpha=0.3)
        
        # 取引行動分布
        action_counts = df['trading_action'].value_counts()
        ax4.pie(action_counts.values, labels=action_counts.index, autopct='%1.1f%%')
        ax4.set_title('Trading Actions Distribution')
        
        plt.tight_layout()
        emotion_static_file = os.path.join(self.charts_dir, "emotion_static.png")
        plt.savefig(emotion_static_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"✅ 静的感情チャート生成完了: {emotion_static_file}")
    
    def generate_correlation_analysis(self):
        portfolio_df = self.load_portfolio_data()
        emotion_df = self.load_emotion_data()
        
        if portfolio_df.empty or emotion_df.empty:
            console.print("⚠️ 相関分析には両方のデータが必要です")
            return
        
        # データマージ
        merged_df = pd.merge(portfolio_df, emotion_df, on='date', how='inner')
        
        if merged_df.empty:
            console.print("⚠️ 日付が一致するデータが見つかりません")
            return
        
        # 相関行列作成
        correlation_vars = ['return_rate', 'emotion_score', 'stress_level', 'confidence_level', 'sleep_hours']
        corr_matrix = merged_df[correlation_vars].corr()
        
        # ヒートマップ生成
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu_r', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": .8})
        plt.title('Correlation Analysis: Returns vs Emotions', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        corr_file = os.path.join(self.charts_dir, "correlation_analysis.png")
        plt.savefig(corr_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"✅ 相関分析チャート生成完了: {corr_file}")
        
        # 統計サマリー
        console.print("\n📊 [bold blue]相関分析結果[/bold blue]")
        console.print(f"リターン率 vs 感情スコア: {corr_matrix.loc['return_rate', 'emotion_score']:.3f}")
        console.print(f"リターン率 vs ストレス: {corr_matrix.loc['return_rate', 'stress_level']:.3f}")
        console.print(f"リターン率 vs 自信レベル: {corr_matrix.loc['return_rate', 'confidence_level']:.3f}")
        console.print(f"リターン率 vs 睡眠時間: {corr_matrix.loc['return_rate', 'sleep_hours']:.3f}")

@click.command()
@click.option('--portfolio', is_flag=True, help='ポートフォリオチャート生成')
@click.option('--emotion', is_flag=True, help='感情チャート生成')
@click.option('--correlation', is_flag=True, help='相関分析チャート生成')
@click.option('--generate-all', is_flag=True, help='全チャート生成')
@click.option('--static-only', is_flag=True, help='静的チャートのみ生成')
def main(portfolio, emotion, correlation, generate_all, static_only):
    generator = ChartGenerator()
    
    interactive = not static_only
    
    if generate_all:
        generator.generate_portfolio_chart(interactive)
        generator.generate_emotion_chart(interactive)
        generator.generate_correlation_analysis()
    elif portfolio:
        generator.generate_portfolio_chart(interactive)
    elif emotion:
        generator.generate_emotion_chart(interactive)
    elif correlation:
        generator.generate_correlation_analysis()
    else:
        console.print("オプションを指定してください (--help で詳細確認)")

if __name__ == "__main__":
    main()