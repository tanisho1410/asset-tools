#!/usr/bin/env python3
"""
投資分析Webアプリケーション - Investment Analysis Web App
CSVアップロード・リアルタイム分析・可視化ダッシュボード
"""

from flask import Flask, render_template, request, jsonify, send_file, session, flash, redirect, url_for
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils
import json
import os
import uuid
from datetime import datetime, timedelta
import yfinance as yf
from werkzeug.utils import secure_filename
import io
import base64
from tools.csv_importer import CSVImporter
from tools.securities_analyzer import SecuritiesAnalyzer

app = Flask(__name__)
app.secret_key = 'investment-analysis-secret-key-2025'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# アップロードフォルダ作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('temp_data', exist_ok=True)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class WebPortfolioAnalyzer:
    def __init__(self, session_id):
        self.session_id = session_id
        self.temp_dir = f"temp_data/{session_id}"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.importer = CSVImporter(data_dir=self.temp_dir)
        self.analyzer = SecuritiesAnalyzer(data_dir=self.temp_dir)
    
    def process_uploaded_csv(self, file_path):
        """アップロードされたCSVファイルを処理"""
        try:
            result = self.importer.standardize_csv(file_path)
            if result is None:
                return None, "CSVファイルの形式が認識できません"
            
            df_standard, format_name = result
            
            # 保有銘柄データとして保存
            holdings_file = os.path.join(self.temp_dir, "holdings.csv")
            df_standard['import_date'] = datetime.now().strftime('%Y-%m-%d')
            df_standard.to_csv(holdings_file, index=False, encoding='utf-8')
            
            return df_standard, None
            
        except Exception as e:
            return None, f"処理エラー: {str(e)}"
    
    def get_portfolio_overview(self):
        """ポートフォリオ概要を取得"""
        holdings_file = os.path.join(self.temp_dir, "holdings.csv")
        
        if not os.path.exists(holdings_file):
            return None
        
        df = pd.read_csv(holdings_file)
        latest_date = df['import_date'].max()
        df_latest = df[df['import_date'] == latest_date]
        
        total_value = df_latest.get('market_value', df_latest.get('評価額', pd.Series([0]))).sum()
        total_gain_loss = df_latest.get('gain_loss', df_latest.get('評価損益', pd.Series([0]))).sum()
        
        if total_value > 0:
            avg_return = (total_gain_loss / (total_value - total_gain_loss)) * 100
        else:
            avg_return = 0
        
        return {
            'total_value': total_value,
            'total_gain_loss': total_gain_loss,
            'avg_return': avg_return,
            'holdings_count': len(df_latest),
            'data': df_latest.to_dict('records')
        }
    
    def create_portfolio_pie_chart(self):
        """資産配分円グラフを作成"""
        overview = self.get_portfolio_overview()
        if not overview:
            return None
        
        df_data = pd.DataFrame(overview['data'])
        
        # 銘柄名と評価額を取得
        names = df_data.get('name', df_data.get('ファンド', df_data.get('銘柄名', 'N/A')))
        values = df_data.get('market_value', df_data.get('評価額', df_data.get('時価評価額', 0)))
        
        # NaN値を除外
        mask = ~pd.isna(values) & (values > 0)
        names = names[mask]
        values = values[mask]
        
        if len(values) == 0:
            return None
        
        # 上位10銘柄のみ表示
        top_10_idx = values.nlargest(10).index
        names_top = names[top_10_idx]
        values_top = values[top_10_idx]
        
        # 銘柄名を短縮
        names_short = [str(name)[:20] + "..." if len(str(name)) > 20 else str(name) for name in names_top]
        
        fig = go.Figure(data=[go.Pie(
            labels=names_short,
            values=values_top,
            hole=0.4,
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title="資産配分",
            font=dict(size=12),
            showlegend=True,
            height=500
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_performance_chart(self):
        """パフォーマンスチャートを作成"""
        overview = self.get_portfolio_overview()
        if not overview:
            return None
        
        df_data = pd.DataFrame(overview['data'])
        
        # 損益率を取得
        names = df_data.get('name', df_data.get('ファンド', df_data.get('銘柄名', 'N/A')))
        gains = df_data.get('gain_loss', df_data.get('評価損益', 0))
        values = df_data.get('market_value', df_data.get('評価額', df_data.get('時価評価額', 0)))
        
        # リターン率計算
        returns = []
        for i in range(len(gains)):
            if pd.notna(values.iloc[i]) and values.iloc[i] > 0 and pd.notna(gains.iloc[i]):
                cost_basis = values.iloc[i] - gains.iloc[i]
                if cost_basis > 0:
                    return_rate = (gains.iloc[i] / cost_basis) * 100
                else:
                    return_rate = 0
            else:
                return_rate = 0
            returns.append(return_rate)
        
        # 上位/下位銘柄をソート
        df_chart = pd.DataFrame({
            'name': [str(name)[:15] + "..." if len(str(name)) > 15 else str(name) for name in names],
            'return': returns
        }).sort_values('return', ascending=True)
        
        colors = ['red' if x < 0 else 'green' for x in df_chart['return']]
        
        fig = go.Figure(data=[go.Bar(
            y=df_chart['name'],
            x=df_chart['return'],
            orientation='h',
            marker_color=colors,
            text=[f"{x:+.1f}%" for x in df_chart['return']],
            textposition='outside'
        )])
        
        fig.update_layout(
            title="銘柄別リターン率",
            xaxis_title="リターン率 (%)",
            yaxis_title="",
            height=max(400, len(df_chart) * 30),
            margin=dict(l=200)
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_securities_analysis(self, limit=5):
        """主要銘柄の詳細分析"""
        overview = self.get_portfolio_overview()
        if not overview:
            return []
        
        df_data = pd.DataFrame(overview['data'])
        
        # 上位銘柄を取得
        values = df_data.get('market_value', df_data.get('評価額', 0))
        top_securities = df_data.nlargest(limit, values.name if hasattr(values, 'name') else 'market_value')
        
        analyses = []
        for _, security in top_securities.iterrows():
            try:
                # シンボル推定（簡易版）
                name = str(security.get('name', security.get('ファンド', 'N/A')))
                symbol = self._estimate_symbol(name)
                
                if symbol:
                    # 簡易分析
                    analysis = self._get_simple_security_analysis(symbol, name, security)
                    if analysis:
                        analyses.append(analysis)
            except Exception as e:
                continue
        
        return analyses
    
    def _estimate_symbol(self, fund_name):
        """ファンド名からシンボル推定"""
        name_lower = fund_name.lower()
        
        # 主要なファンド・ETFのマッピング
        symbol_mapping = {
            's&p500': 'SPY',
            'sp500': 'SPY',
            'vti': 'VTI',
            'topix': '1306.T',
            'nikkei': '1321.T',
            'nasdaq': 'QQQ',
            'ビットコイン': 'BTC-USD',
            'gold': 'GLD',
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL',
            'amazon': 'AMZN',
            'tesla': 'TSLA'
        }
        
        for keyword, symbol in symbol_mapping.items():
            if keyword in name_lower:
                return symbol
        
        return None
    
    def _get_simple_security_analysis(self, symbol, name, holding_data):
        """簡易証券分析"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="3mo")
            
            if len(hist) == 0:
                return None
            
            current_price = hist['Close'].iloc[-1]
            price_change_1m = ((current_price - hist['Close'].iloc[-21]) / hist['Close'].iloc[-21] * 100) if len(hist) >= 21 else 0
            
            # 保有状況
            market_value = holding_data.get('market_value', holding_data.get('評価額', 0))
            gain_loss = holding_data.get('gain_loss', holding_data.get('評価損益', 0))
            
            return {
                'symbol': symbol,
                'name': name[:30],
                'current_price': current_price,
                'price_change_1m': price_change_1m,
                'market_value': market_value,
                'gain_loss': gain_loss,
                'sector': info.get('sector', 'N/A'),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            }
            
        except Exception:
            return None

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """CSVファイルアップロード処理"""
    if 'file' not in request.files:
        flash('ファイルが選択されていません')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('ファイルが選択されていません')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # セッションIDを生成
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        # ファイル保存
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(file_path)
        
        # 処理
        analyzer = WebPortfolioAnalyzer(session_id)
        df_result, error = analyzer.process_uploaded_csv(file_path)
        
        if error:
            flash(f'エラー: {error}')
            return redirect(url_for('index'))
        
        flash('CSVファイルが正常にアップロードされました！')
        return redirect(url_for('dashboard'))
    
    flash('無効なファイル形式です。CSVファイルをアップロードしてください。')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """分析ダッシュボード"""
    if 'session_id' not in session:
        flash('先にCSVファイルをアップロードしてください')
        return redirect(url_for('index'))
    
    analyzer = WebPortfolioAnalyzer(session['session_id'])
    overview = analyzer.get_portfolio_overview()
    
    if not overview:
        flash('データの処理中にエラーが発生しました')
        return redirect(url_for('index'))
    
    return render_template('dashboard.html', overview=overview)

@app.route('/api/portfolio/pie')
def api_portfolio_pie():
    """資産配分円グラフAPI"""
    if 'session_id' not in session:
        return jsonify({'error': 'セッションが無効です'})
    
    analyzer = WebPortfolioAnalyzer(session['session_id'])
    chart_json = analyzer.create_portfolio_pie_chart()
    
    if chart_json:
        return chart_json
    else:
        return jsonify({'error': 'チャートを生成できませんでした'})

@app.route('/api/portfolio/performance')
def api_portfolio_performance():
    """パフォーマンスチャートAPI"""
    if 'session_id' not in session:
        return jsonify({'error': 'セッションが無効です'})
    
    analyzer = WebPortfolioAnalyzer(session['session_id'])
    chart_json = analyzer.create_performance_chart()
    
    if chart_json:
        return chart_json
    else:
        return jsonify({'error': 'チャートを生成できませんでした'})

@app.route('/api/securities/analysis')
def api_securities_analysis():
    """証券分析API"""
    if 'session_id' not in session:
        return jsonify({'error': 'セッションが無効です'})
    
    analyzer = WebPortfolioAnalyzer(session['session_id'])
    analyses = analyzer.get_securities_analysis()
    
    return jsonify(analyses)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)