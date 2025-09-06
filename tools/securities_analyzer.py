#!/usr/bin/env python3
"""
証券分析システム - Securities Analysis System
保有銘柄・投資信託の詳細分析と解説
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import os
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import track
import requests
import json
from pathlib import Path

console = Console()

class SecuritiesAnalyzer:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        
        # 日本の投資信託・ETF情報
        self.fund_info = {
            # 人気ETF
            '1306': {'name': 'TOPIX連動型上場投資信託', 'category': '国内株式ETF', 'expense_ratio': 0.11},
            '1321': {'name': '日経225連動型上場投資信託', 'category': '国内株式ETF', 'expense_ratio': 0.12},
            '1557': {'name': 'SPDR S&P500 ETF', 'category': '米国株式ETF', 'expense_ratio': 0.10},
            '2558': {'name': 'MAXIS米国株式(S&P500)上場投信', 'category': '米国株式ETF', 'expense_ratio': 0.078},
            
            # 人気投資信託（架空コード）
            'EMX001': {'name': 'eMAXIS Slim 全世界株式', 'category': '全世界株式', 'expense_ratio': 0.1144},
            'EMX002': {'name': 'eMAXIS Slim 米国株式S&P500', 'category': '米国株式', 'expense_ratio': 0.09372},
            'EMX003': {'name': 'eMAXIS Slim 先進国株式', 'category': '先進国株式', 'expense_ratio': 0.1023},
        }
        
        # セクター分類
        self.sector_mapping = {
            'Technology': 'テクノロジー',
            'Healthcare': 'ヘルスケア', 
            'Financial Services': '金融',
            'Consumer Cyclical': '一般消費財',
            'Communication Services': '通信サービス',
            'Industrials': '資本財',
            'Consumer Defensive': '生活必需品',
            'Energy': 'エネルギー',
            'Real Estate': '不動産',
            'Materials': '素材',
            'Utilities': '公益事業'
        }
    
    def analyze_single_security(self, symbol, quantity=None, avg_cost=None):
        """個別銘柄の詳細分析"""
        console.print(f"\n🔍 [bold cyan]{symbol}[/bold cyan] の分析中...")
        
        try:
            # 基本情報取得
            ticker = yf.Ticker(self._format_yahoo_symbol(symbol))
            info = ticker.info
            hist = ticker.history(period="1y")
            
            if info is None or len(hist) == 0:
                console.print(f"❌ {symbol}: データを取得できません")
                return None
            
            # 基本情報パネル
            basic_info = self._create_basic_info_panel(symbol, info, quantity, avg_cost)
            
            # パフォーマンス分析
            performance_info = self._create_performance_panel(hist, info)
            
            # リスク分析
            risk_info = self._create_risk_panel(hist)
            
            # 投資判断サマリー
            summary_info = self._create_investment_summary(symbol, info, hist, avg_cost)
            
            # 表示
            console.print(Columns([basic_info, performance_info]))
            console.print(Columns([risk_info, summary_info]))
            
            return {
                'symbol': symbol,
                'info': info,
                'history': hist,
                'analysis': self._calculate_metrics(hist, info, avg_cost)
            }
            
        except Exception as e:
            console.print(f"❌ {symbol} 分析エラー: {e}")
            return None
    
    def analyze_portfolio_securities(self):
        """ポートフォリオ全銘柄の分析"""
        holdings_file = os.path.join(self.data_dir, "holdings.csv")
        
        if not os.path.exists(holdings_file):
            console.print("❌ 保有銘柄データが見つかりません")
            return
        
        df = pd.read_csv(holdings_file)
        
        # 最新データ抽出
        latest_date = df['import_date'].max()
        df_latest = df[df['import_date'] == latest_date]
        
        console.print(f"\n📊 [bold blue]ポートフォリオ分析レポート[/bold blue] ({latest_date})")
        
        analyses = []
        total_value = df_latest['market_value'].sum()
        
        for _, holding in track(df_latest.iterrows(), description="分析中...", total=len(df_latest)):
            symbol = str(holding.get('symbol', ''))
            quantity = holding.get('quantity', 0)
            avg_cost = holding.get('avg_price', 0)
            weight = holding['market_value'] / total_value * 100
            
            if weight >= 1.0:  # 1%以上の銘柄のみ詳細分析
                analysis = self.analyze_single_security(symbol, quantity, avg_cost)
                if analysis:
                    analysis['weight'] = weight
                    analyses.append(analysis)
        
        # ポートフォリオサマリー
        self._create_portfolio_summary(analyses, df_latest)
        
        return analyses
    
    def _format_yahoo_symbol(self, symbol):
        """Yahoo Finance用のシンボル形式に変換"""
        symbol = str(symbol).strip()
        
        # 日本株式の場合
        if symbol.isdigit() and len(symbol) == 4:
            return f"{symbol}.T"
        
        # 投資信託の場合（仮想的な処理）
        if symbol.startswith('EMX'):
            # 実際のAPIがあれば置き換え
            return "SPY"  # 代替として使用
        
        return symbol
    
    def _create_basic_info_panel(self, symbol, info, quantity, avg_cost):
        """基本情報パネル作成"""
        name = info.get('longName', info.get('shortName', symbol))
        sector = self.sector_mapping.get(info.get('sector', ''), info.get('sector', 'N/A'))
        industry = info.get('industry', 'N/A')
        market_cap = info.get('marketCap', 0)
        current_price = info.get('regularMarketPrice', info.get('previousClose', 0))
        
        content = f"""[bold]{name}[/bold]
        
📍 基本情報:
  セクター: {sector}
  業界: {industry}
  時価総額: {market_cap/1e9:.1f}B USD (約{market_cap/1e9*150:.0f}億円)
  
💰 価格情報:
  現在価格: ${current_price:.2f}"""
        
        if quantity and avg_cost:
            total_cost = quantity * avg_cost
            current_value = quantity * current_price
            gain_loss = current_value - total_cost
            gain_rate = (gain_loss / total_cost * 100) if total_cost > 0 else 0
            
            color = "green" if gain_loss >= 0 else "red"
            content += f"""
            
🎯 保有状況:
  保有数: {quantity}株
  平均取得価格: ${avg_cost:.2f}
  評価損益: [{color}]${gain_loss:+.2f} ({gain_rate:+.1f}%)[/{color}]"""
        
        return Panel(content, title=f"🏢 {symbol}", border_style="cyan")
    
    def _create_performance_panel(self, hist, info):
        """パフォーマンス分析パネル"""
        if len(hist) == 0:
            return Panel("データ不足", title="📈 パフォーマンス")
        
        current_price = hist['Close'][-1]
        
        # 期間別リターン計算
        returns = {}
        periods = {
            '1週間': 5,
            '1ヶ月': 21,
            '3ヶ月': 63,
            '6ヶ月': 126,
            '1年間': 252
        }
        
        for period_name, days in periods.items():
            if len(hist) >= days:
                past_price = hist['Close'].iloc[-days]
                return_rate = (current_price - past_price) / past_price * 100
                returns[period_name] = return_rate
        
        # 52週高値・安値
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        from_high = (current_price - high_52w) / high_52w * 100
        from_low = (current_price - low_52w) / low_52w * 100
        
        content = "📊 期間別リターン:\n"
        for period, ret in returns.items():
            color = "green" if ret >= 0 else "red"
            content += f"  {period}: [{color}]{ret:+.1f}%[/{color}]\n"
        
        content += f"""
📏 52週レンジ:
  高値: ${high_52w:.2f} ({from_high:+.1f}%)
  安値: ${low_52w:.2f} ({from_low:+.1f}%)
  
📈 配当利回り: {info.get('dividendYield', 0)*100:.2f}%"""
        
        return Panel(content, title="📈 パフォーマンス", border_style="green")
    
    def _create_risk_panel(self, hist):
        """リスク分析パネル"""
        if len(hist) < 30:
            return Panel("データ不足", title="⚠️ リスク分析")
        
        # ボラティリティ計算
        returns = hist['Close'].pct_change().dropna()
        volatility_daily = returns.std()
        volatility_annual = volatility_daily * np.sqrt(252) * 100
        
        # 最大ドローダウン
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # VaR (5%リスク)
        var_5 = np.percentile(returns, 5) * 100
        
        # シャープレシオ（概算、リスクフリーレートを2%と仮定）
        risk_free_rate = 0.02
        excess_return = returns.mean() * 252 - risk_free_rate
        sharpe_ratio = excess_return / (volatility_daily * np.sqrt(252)) if volatility_daily > 0 else 0
        
        # リスク評価
        risk_level = "低" if volatility_annual < 15 else "中" if volatility_annual < 25 else "高"
        risk_color = "green" if risk_level == "低" else "yellow" if risk_level == "中" else "red"
        
        content = f"""📊 リスク指標:
  年間ボラティリティ: [{risk_color}]{volatility_annual:.1f}%[/{risk_color}] ({risk_level}リスク)
  最大ドローダウン: {max_drawdown:.1f}%
  VaR(5%): {var_5:.1f}%
  シャープレシオ: {sharpe_ratio:.2f}
  
⚠️ リスク評価:
  • ボラティリティが{volatility_annual:.0f}%で{risk_level}リスク銘柄
  • 過去1年で最大{abs(max_drawdown):.1f}%下落"""
        
        return Panel(content, title="⚠️ リスク分析", border_style=risk_color)
    
    def _create_investment_summary(self, symbol, info, hist, avg_cost):
        """投資判断サマリー"""
        # 簡易スコアリング
        score = 0
        reasons = []
        
        # P/E ratio チェック
        pe_ratio = info.get('trailingPE', 0)
        if 0 < pe_ratio < 15:
            score += 1
            reasons.append("✅ P/E比が割安水準")
        elif pe_ratio > 30:
            score -= 1
            reasons.append("⚠️ P/E比が割高水準")
        
        # ROE チェック
        roe = info.get('returnOnEquity', 0)
        if roe and roe > 0.15:
            score += 1
            reasons.append("✅ ROEが良好")
        
        # 売上成長率チェック  
        revenue_growth = info.get('revenueGrowth', 0)
        if revenue_growth and revenue_growth > 0.1:
            score += 1
            reasons.append("✅ 売上成長率が良好")
        
        # テクニカル分析（移動平均）
        if len(hist) >= 50:
            ma_20 = hist['Close'].rolling(20).mean().iloc[-1]
            ma_50 = hist['Close'].rolling(50).mean().iloc[-1]
            current_price = hist['Close'].iloc[-1]
            
            if current_price > ma_20 > ma_50:
                score += 1
                reasons.append("✅ 上昇トレンド継続")
            elif current_price < ma_20 < ma_50:
                score -= 1
                reasons.append("⚠️ 下降トレンド")
        
        # 総合評価
        if score >= 3:
            rating = "🌟 強い買い"
            color = "bright_green"
        elif score >= 1:
            rating = "👍 買い"
            color = "green"
        elif score >= -1:
            rating = "😐 中立"
            color = "yellow"
        else:
            rating = "👎 弱気"
            color = "red"
        
        content = f"""[{color}]{rating}[/{color}] (スコア: {score}/4)

💡 主な理由:"""
        
        for reason in reasons[:4]:  # 最大4つまで
            content += f"\n  {reason}"
        
        if not reasons:
            content += "\n  データ不足により評価困難"
        
        # 投資アドバイス
        content += f"""
        
🎯 投資アドバイス:
  • 基本情報とリスク指標を確認
  • 分散投資の一環として検討
  • 定期的なモニタリングを推奨"""
        
        return Panel(content, title="🎯 投資判断", border_style=color)
    
    def _calculate_metrics(self, hist, info, avg_cost):
        """各種指標計算"""
        if len(hist) == 0:
            return {}
        
        current_price = hist['Close'][-1]
        returns = hist['Close'].pct_change().dropna()
        
        return {
            'current_price': current_price,
            'volatility': returns.std() * np.sqrt(252) * 100,
            'max_drawdown': ((hist['Close'] / hist['Close'].expanding().max() - 1).min() * 100),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0) * 100,
            'market_cap': info.get('marketCap', 0)
        }
    
    def _create_portfolio_summary(self, analyses, holdings_df):
        """ポートフォリオサマリー作成"""
        if not analyses:
            return
        
        console.print(f"\n📋 [bold blue]ポートフォリオ構成分析[/bold blue]")
        
        # セクター分散
        sector_weights = {}
        risk_levels = {'低': 0, '中': 0, '高': 0}
        
        for analysis in analyses:
            info = analysis['info']
            weight = analysis['weight']
            sector = self.sector_mapping.get(info.get('sector', ''), 'その他')
            
            sector_weights[sector] = sector_weights.get(sector, 0) + weight
            
            # リスクレベル集計
            vol = analysis['analysis'].get('volatility', 0)
            if vol < 15:
                risk_levels['低'] += weight
            elif vol < 25:
                risk_levels['中'] += weight
            else:
                risk_levels['高'] += weight
        
        # セクター分散表示
        console.print("\n🏭 セクター構成:")
        for sector, weight in sorted(sector_weights.items(), key=lambda x: x[1], reverse=True):
            console.print(f"  {sector}: {weight:.1f}%")
        
        # リスク分散表示
        console.print("\n⚠️ リスク分散:")
        for risk, weight in risk_levels.items():
            color = "green" if risk == "低" else "yellow" if risk == "中" else "red"
            console.print(f"  [{color}]{risk}リスク: {weight:.1f}%[/{color}]")
        
        # 推奨事項
        recommendations = []
        if max(sector_weights.values()) > 50:
            recommendations.append("⚠️ 特定セクターの比率が高すぎます")
        if risk_levels['高'] > 30:
            recommendations.append("⚠️ 高リスク銘柄の比率が高いです")
        if len(sector_weights) < 3:
            recommendations.append("💡 セクター分散を検討してください")
        
        if recommendations:
            console.print("\n💡 推奨事項:")
            for rec in recommendations:
                console.print(f"  {rec}")

@click.command()
@click.option('--symbol', type=str, help='個別銘柄分析')
@click.option('--analyze-all', is_flag=True, help='ポートフォリオ全体分析')
@click.option('--quantity', type=float, help='保有数量')
@click.option('--avg-cost', type=float, help='平均取得価格')
def main(symbol, analyze_all, quantity, avg_cost):
    analyzer = SecuritiesAnalyzer()
    
    if symbol:
        analyzer.analyze_single_security(symbol, quantity, avg_cost)
    elif analyze_all:
        analyzer.analyze_portfolio_securities()
    else:
        console.print("オプションを指定してください (--help で詳細確認)")

if __name__ == "__main__":
    main()