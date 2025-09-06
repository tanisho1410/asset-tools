#!/usr/bin/env python3
"""
CSVインポートシステム - CSV Import System  
証券会社からダウンロードしたCSVファイルの統合・分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from pathlib import Path
import re

console = Console()

class CSVImporter:
    def __init__(self, data_dir="data", import_dir="imports"):
        self.data_dir = data_dir
        self.import_dir = import_dir
        self.ensure_dirs()
        
        # 既知のCSVフォーマット定義
        self.csv_formats = {
            'sbi_portfolio': {
                'pattern': r'(assetbalance|資産残高)',
                'columns': {
                    'date': ['評価日', 'Date', '日付'],
                    'symbol': ['銘柄コード', 'Symbol', 'Code'],
                    'name': ['銘柄名', 'Name', '商品名'],
                    'quantity': ['保有数量', 'Quantity', '数量'],
                    'unit_price': ['基準価格', 'Price', '単価'],
                    'market_value': ['評価額', 'Market Value', '時価評価額'],
                    'gain_loss': ['評価損益', 'Gain/Loss', '損益'],
                    'gain_loss_rate': ['評価損益率', 'Return Rate', '損益率']
                }
            },
            'sbi_trading': {
                'pattern': r'(trading|取引履歴)',
                'columns': {
                    'date': ['約定日', 'Settlement Date', '取引日'],
                    'type': ['売買', 'Transaction Type', '取引種別'],
                    'symbol': ['銘柄コード', 'Symbol'],
                    'name': ['銘柄名', 'Security Name'],
                    'quantity': ['数量', 'Quantity'],
                    'price': ['単価', 'Unit Price'],
                    'amount': ['金額', 'Amount', '約定代金']
                }
            },
            'rakuten_portfolio': {
                'pattern': r'(保有商品|portfolio)',
                'columns': {
                    'symbol': ['商品コード', 'Product Code'],
                    'name': ['商品名', 'Product Name'],
                    'quantity': ['保有口数', 'Units Held'],
                    'avg_price': ['平均取得価額', 'Average Cost'],
                    'current_price': ['基準価額', 'Current Price'],
                    'market_value': ['評価金額', 'Market Value'],
                    'gain_loss': ['評価損益', 'Unrealized P&L']
                }
            }
        }
    
    def ensure_dirs(self):
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.import_dir, exist_ok=True)
    
    def detect_csv_format(self, csv_path):
        """CSVファイルの形式を自動判定"""
        try:
            # ファイル名から判定
            filename = Path(csv_path).name.lower()
            for format_name, format_info in self.csv_formats.items():
                if re.search(format_info['pattern'], filename):
                    console.print(f"🔍 ファイル名から形式判定: {format_name}")
                    return format_name
            
            # ヘッダーから判定
            df_sample = pd.read_csv(csv_path, nrows=0, encoding='utf-8')
            columns = df_sample.columns.tolist()
            
            for format_name, format_info in self.csv_formats.items():
                match_count = 0
                for col_type, possible_names in format_info['columns'].items():
                    for col in columns:
                        if any(name in col for name in possible_names):
                            match_count += 1
                            break
                
                if match_count >= 3:  # 3つ以上一致で判定
                    console.print(f"🔍 ヘッダーから形式判定: {format_name} (一致: {match_count})")
                    return format_name
            
            console.print("⚠️ 未知の形式です。手動で設定が必要です。")
            return None
            
        except Exception as e:
            console.print(f"❌ ファイル読み込みエラー: {e}")
            return None
    
    def standardize_csv(self, csv_path, format_name=None):
        """CSVファイルを標準形式に変換"""
        if format_name is None:
            format_name = self.detect_csv_format(csv_path)
        
        if format_name not in self.csv_formats:
            console.print(f"❌ 未対応形式: {format_name}")
            return None
        
        try:
            # CSVファイル読み込み（文字エンコーディング自動判定）
            encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    console.print(f"✅ エンコーディング: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                console.print("❌ ファイルを読み込めません")
                return None
            
            # 列名のマッピング
            format_info = self.csv_formats[format_name]
            column_mapping = {}
            
            for standard_col, possible_names in format_info['columns'].items():
                for col in df.columns:
                    if any(name in str(col) for name in possible_names):
                        column_mapping[col] = standard_col
                        break
            
            # データ変換
            df_standard = df.rename(columns=column_mapping)
            
            # 日付列の標準化
            if 'date' in df_standard.columns:
                df_standard['date'] = pd.to_datetime(df_standard['date'], errors='coerce')
            
            # 数値列のクリーニング
            numeric_columns = ['quantity', 'unit_price', 'market_value', 'gain_loss', 'gain_loss_rate', 'price', 'amount', 'avg_price', 'current_price']
            for col in numeric_columns:
                if col in df_standard.columns:
                    # カンマ、円マーク、%記号を除去
                    df_standard[col] = df_standard[col].astype(str).str.replace(r'[¥,,%]', '', regex=True)
                    df_standard[col] = pd.to_numeric(df_standard[col], errors='coerce')
            
            console.print(f"✅ 標準化完了: {len(df_standard)}行のデータ")
            return df_standard, format_name
            
        except Exception as e:
            console.print(f"❌ データ変換エラー: {e}")
            return None
    
    def import_portfolio_data(self, csv_path):
        """ポートフォリオCSVをインポートして既存データと統合"""
        result = self.standardize_csv(csv_path)
        if result is None:
            return False
        
        df_new, format_name = result
        
        # ポートフォリオデータの場合の処理
        if 'portfolio' in format_name:
            return self._process_portfolio_data(df_new, format_name)
        elif 'trading' in format_name:
            return self._process_trading_data(df_new, format_name)
        else:
            console.print(f"⚠️ 未対応のデータ種別: {format_name}")
            return False
    
    def _process_portfolio_data(self, df, format_name):
        """ポートフォリオデータの処理"""
        # 保有銘柄分析用データ保存
        holdings_file = os.path.join(self.data_dir, "holdings.csv")
        
        if os.path.exists(holdings_file):
            existing_df = pd.read_csv(holdings_file)
            # 日付でマージ（同じ日付の場合は新しいデータで上書き）
            df['import_date'] = datetime.now().strftime('%Y-%m-%d')
            df_combined = pd.concat([existing_df, df], ignore_index=True)
            df_combined.drop_duplicates(subset=['symbol', 'import_date'], keep='last', inplace=True)
        else:
            df['import_date'] = datetime.now().strftime('%Y-%m-%d')
            df_combined = df
        
        df_combined.to_csv(holdings_file, index=False, encoding='utf-8')
        
        # 総資産額を計算してポートフォリオトラッカーに追加
        if 'market_value' in df.columns:
            total_value = df['market_value'].sum()
            notes = f"CSV取込 ({len(df)}銘柄)"
            
            import sys
            import os as os_path
            sys.path.append(os_path.path.dirname(os_path.path.dirname(os_path.path.abspath(__file__))))
            from tools.portfolio_tracker import PortfolioTracker
            tracker = PortfolioTracker(self.data_dir)
            tracker.add_entry(
                total_value=total_value,
                notes=notes
            )
            
            console.print(f"✅ ポートフォリオ更新: 総資産額 ¥{total_value:,.0f}")
        
        return True
    
    def _process_trading_data(self, df, format_name):
        """取引履歴データの処理"""
        trading_file = os.path.join(self.data_dir, "trades.csv")
        
        if os.path.exists(trading_file):
            existing_df = pd.read_csv(trading_file)
            df_combined = pd.concat([existing_df, df], ignore_index=True)
            df_combined.drop_duplicates(inplace=True)
        else:
            df_combined = df
        
        df_combined.to_csv(trading_file, index=False, encoding='utf-8')
        console.print(f"✅ 取引履歴更新: {len(df)}件の取引")
        
        return True
    
    def analyze_holdings(self):
        """保有銘柄の分析表示"""
        holdings_file = os.path.join(self.data_dir, "holdings.csv")
        
        if not os.path.exists(holdings_file):
            console.print("❌ 保有銘柄データが見つかりません")
            return
        
        df = pd.read_csv(holdings_file)
        
        # 最新データのみ抽出
        latest_date = df['import_date'].max()
        df_latest = df[df['import_date'] == latest_date]
        
        # 保有銘柄一覧表示
        table = Table(title=f"保有銘柄分析 ({latest_date})")
        table.add_column("銘柄", style="cyan")
        table.add_column("評価額", justify="right")
        table.add_column("損益", justify="right")
        table.add_column("損益率", justify="right", style="bold")
        table.add_column("構成比", justify="right")
        
        total_value = df_latest['market_value'].sum()
        
        # 構成比でソート
        df_sorted = df_latest.sort_values('market_value', ascending=False)
        
        for _, row in df_sorted.head(10).iterrows():  # 上位10銘柄
            name = str(row.get('name', row.get('symbol', 'N/A')))[:20]
            value = row['market_value']
            gain_loss = row.get('gain_loss', 0)
            gain_rate = row.get('gain_loss_rate', 0)
            weight = value / total_value * 100
            
            gain_color = "green" if gain_loss >= 0 else "red"
            
            table.add_row(
                name,
                f"¥{value:,.0f}",
                f"[{gain_color}]{gain_loss:+,.0f}[/{gain_color}]",
                f"[{gain_color}]{gain_rate:+.1f}%[/{gain_color}]",
                f"{weight:.1f}%"
            )
        
        console.print(table)
        
        # サマリー統計
        total_gain_loss = df_latest['gain_loss'].sum()
        avg_return = total_gain_loss / total_value * 100
        
        console.print(f"\n📊 [bold blue]ポートフォリオサマリー[/bold blue]")
        console.print(f"総評価額: ¥{total_value:,.0f}")
        console.print(f"評価損益: ¥{total_gain_loss:+,.0f}")
        console.print(f"平均リターン: {avg_return:+.2f}%")
        console.print(f"保有銘柄数: {len(df_latest)}銘柄")

@click.command()
@click.option('--import-csv', type=click.Path(exists=True), help='CSVファイルをインポート')
@click.option('--import-dir', type=click.Path(exists=True), help='ディレクトリ内のCSVを一括インポート')
@click.option('--analyze-holdings', is_flag=True, help='保有銘柄分析を表示')
@click.option('--format', type=str, help='CSVフォーマットを指定')
def main(import_csv, import_dir, analyze_holdings, format):
    importer = CSVImporter()
    
    if import_csv:
        console.print(f"📁 CSVファイルをインポート: {import_csv}")
        success = importer.import_portfolio_data(import_csv)
        if success:
            console.print("✅ インポート完了")
        else:
            console.print("❌ インポート失敗")
    
    elif import_dir:
        console.print(f"📁 ディレクトリから一括インポート: {import_dir}")
        csv_files = list(Path(import_dir).glob("*.csv"))
        
        for csv_file in csv_files:
            console.print(f"\n処理中: {csv_file.name}")
            success = importer.import_portfolio_data(str(csv_file))
            if success:
                console.print(f"✅ {csv_file.name} 完了")
            else:
                console.print(f"❌ {csv_file.name} 失敗")
    
    elif analyze_holdings:
        importer.analyze_holdings()
    
    else:
        console.print("オプションを指定してください (--help で詳細確認)")

if __name__ == "__main__":
    main()