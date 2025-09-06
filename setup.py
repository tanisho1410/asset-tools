#!/usr/bin/env python3
"""
投資開示ツール初期セットアップスクリプト
"""

import os
import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.prompt import Confirm, FloatPrompt, Prompt

console = Console()

def setup_directories():
    """必要なディレクトリを作成"""
    directories = ['data', 'charts', 'reports', 'templates']
    
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        console.print(f"✅ ディレクトリ作成: {dir_name}/")

def create_sample_data():
    """サンプルデータの作成（オプション）"""
    if Confirm.ask("サンプルデータを作成しますか？"):
        # サンプルポートフォリオデータ
        sample_portfolio = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=6, freq='M'),
            'total_value': [1000000, 1050000, 980000, 1100000, 1200000, 1150000],
            'deposit': [1000000, 50000, 0, 0, 0, 0],
            'withdrawal': [0, 0, 0, 0, 0, 50000],
            'net_flow': [1000000, 50000, 0, 0, 0, -50000],
            'return_rate': [0, 0, -6.7, 12.2, 9.1, -4.2],
            'notes': ['初期投資', '追加投資', '調整なし', '好調', '順調', '一部利確']
        })
        
        sample_portfolio.to_csv('data/portfolio.csv', index=False)
        console.print("✅ サンプルポートフォリオデータ作成")
        
        # サンプル感情データ
        sample_emotions = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'emotion_score': [3, 4, 2, 3, 4, 5, 3, 2, 3, 4, 
                             3, 2, 1, 2, 3, 4, 5, 4, 3, 2,
                             3, 4, 3, 2, 4, 5, 3, 2, 3, 4],
            'stress_level': [2, 2, 4, 3, 2, 1, 3, 4, 3, 2,
                            3, 4, 5, 4, 3, 2, 1, 2, 3, 4,
                            3, 2, 3, 4, 2, 1, 3, 4, 3, 2],
            'confidence_level': [3, 4, 2, 3, 4, 5, 3, 2, 3, 4,
                                4, 3, 2, 3, 4, 5, 4, 3, 2, 3,
                                4, 5, 4, 3, 4, 5, 3, 2, 3, 4],
            'market_event': ['横ばい'] * 30,
            'trading_action': ['ホールド'] * 30,
            'notes': [''] * 30,
            'sleep_hours': [7, 8, 6, 7, 8, 7, 6, 7, 8, 7,
                           6, 7, 5, 6, 7, 8, 7, 6, 7, 8,
                           7, 8, 7, 6, 7, 8, 7, 6, 7, 8],
            'exercise_done': [True, False, True, False, True, True, False, True, False, True] * 3,
            'info_consumption': ['普通'] * 30
        })
        
        sample_emotions.to_csv('data/emotions.csv', index=False)
        console.print("✅ サンプル感情データ作成")

def create_initial_entry():
    """初期エントリーの作成"""
    if Confirm.ask("現在の資産状況を記録しますか？"):
        from tools.portfolio_tracker import PortfolioTracker
        
        tracker = PortfolioTracker()
        
        console.print("\n[yellow]初期資産記録を作成します[/yellow]")
        current_value = FloatPrompt.ask("現在の総資産額を入力してください")
        initial_deposit = FloatPrompt.ask("初期投資額を入力してください", default=current_value)
        notes = Prompt.ask("備考があれば入力してください", default="初期セットアップ")
        
        tracker.add_entry(
            total_value=current_value,
            deposit=initial_deposit,
            notes=notes
        )
        
        console.print("✅ 初期資産記録完了")

def create_config_file():
    """設定ファイルの作成"""
    config = {
        "auto_backup": True,
        "chart_style": "seaborn",
        "default_currency": "JPY",
        "timezone": "Asia/Tokyo",
        "github_repo": "tanisho1410/investment-disclosure-tools",
        "update_frequency": "weekly"
    }
    
    import json
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    console.print("✅ 設定ファイル作成: config.json")

def create_gitignore():
    """GitIgnoreファイルの作成"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Sensitive data (uncomment if needed)
# data/portfolio.csv
# data/emotions.csv
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    console.print("✅ .gitignore作成")

def main():
    console.print("[bold blue]🚀 投資開示ツール初期セットアップ[/bold blue]\n")
    
    setup_directories()
    create_config_file()
    create_gitignore()
    create_sample_data()
    create_initial_entry()
    
    console.print("\n[bold green]✨ セットアップ完了！[/bold green]")
    console.print("\n次のステップ:")
    console.print("1. [cyan]python tools/portfolio_tracker.py --add-entry[/cyan] - 資産記録")
    console.print("2. [cyan]python tools/emotion_logger.py --daily-entry[/cyan] - 感情記録") 
    console.print("3. [cyan]python tools/chart_generator.py --generate-all[/cyan] - チャート生成")
    console.print("4. [cyan]python tools/report_builder.py --monthly[/cyan] - レポート作成")
    console.print("\n詳細は README.md をご確認ください！")

if __name__ == "__main__":
    main()