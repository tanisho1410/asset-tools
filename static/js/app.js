// 投資分析ツール JavaScript

// グローバル変数
let chartColors = [
    '#0d6efd', '#6f42c1', '#d63384', '#dc3545', '#fd7e14',
    '#ffc107', '#198754', '#20c997', '#0dcaf0', '#6c757d'
];

// ページ読み込み完了時の初期化
document.addEventListener('DOMContentLoaded', function() {
    // ツールチップ初期化
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // ファイルアップロードの改善
    initFileUpload();
    
    // 数値のフォーマット
    formatNumbers();
    
    // スムーススクロール
    initSmoothScroll();
});

// ファイルアップロード機能の初期化
function initFileUpload() {
    const fileInput = document.getElementById('file');
    if (!fileInput) return;

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        // ファイルサイズチェック (16MB)
        if (file.size > 16 * 1024 * 1024) {
            showAlert('ファイルサイズが大きすぎます。16MB以下のファイルをお選びください。', 'warning');
            e.target.value = '';
            return;
        }

        // ファイル形式チェック
        if (!file.name.toLowerCase().endsWith('.csv')) {
            showAlert('CSVファイルを選択してください。', 'warning');
            e.target.value = '';
            return;
        }

        // ファイル情報を表示
        const fileInfo = document.createElement('div');
        fileInfo.className = 'mt-2 text-success';
        fileInfo.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            ${file.name} (${formatFileSize(file.size)}) - 選択済み
        `;

        // 既存の情報を削除
        const existingInfo = fileInput.parentElement.querySelector('.text-success');
        if (existingInfo) {
            existingInfo.remove();
        }

        fileInput.parentElement.appendChild(fileInfo);
    });
}

// 数値フォーマット
function formatNumbers() {
    const numberElements = document.querySelectorAll('.format-number');
    numberElements.forEach(element => {
        const number = parseFloat(element.textContent);
        if (!isNaN(number)) {
            element.textContent = number.toLocaleString('ja-JP');
        }
    });
}

// スムーススクロール
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// アラート表示
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    if (!alertContainer) return;

    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show mt-3`;
    alertElement.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.insertBefore(alertElement, alertContainer.firstChild);

    // 自動削除
    setTimeout(() => {
        if (alertElement.parentElement) {
            alertElement.remove();
        }
    }, 5000);
}

// アラートアイコン取得
function getAlertIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'warning': return 'exclamation-triangle';
        case 'danger': return 'times-circle';
        default: return 'info-circle';
    }
}

// ファイルサイズフォーマット
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// チャート用ユーティリティ関数
function createChartConfig(title, type = 'responsive') {
    return {
        responsive: true,
        displayModeBar: false,
        locale: 'ja',
        config: {
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        }
    };
}

// 数値を日本円フォーマットに変換
function formatYen(amount) {
    return new Intl.NumberFormat('ja-JP', {
        style: 'currency',
        currency: 'JPY',
        minimumFractionDigits: 0
    }).format(amount);
}

// パーセンテージフォーマット
function formatPercent(value, decimals = 1) {
    return (value >= 0 ? '+' : '') + value.toFixed(decimals) + '%';
}

// エラーハンドリング
function handleApiError(error, elementId) {
    console.error('API Error:', error);
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-warning text-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                データの読み込み中にエラーが発生しました
                <br>
                <button class="btn btn-outline-primary btn-sm mt-2" onclick="location.reload()">
                    <i class="fas fa-refresh me-1"></i>再読み込み
                </button>
            </div>
        `;
    }
}

// ローディング表示
function showLoading(elementId, message = '読み込み中...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="d-flex justify-content-center align-items-center py-5">
                <div class="spinner-border text-primary me-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span>${message}</span>
            </div>
        `;
    }
}

// プログレスバー更新
function updateProgress(percentage, elementId) {
    const progressBar = document.getElementById(elementId);
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
        progressBar.textContent = Math.round(percentage) + '%';
    }
}

// 印刷最適化
function optimizePrint() {
    window.addEventListener('beforeprint', function() {
        // チャートのサイズ調整
        const charts = document.querySelectorAll('.plotly-graph-div');
        charts.forEach(chart => {
            Plotly.relayout(chart, {
                width: 800,
                height: 400
            });
        });
    });

    window.addEventListener('afterprint', function() {
        // チャートサイズを戻す
        const charts = document.querySelectorAll('.plotly-graph-div');
        charts.forEach(chart => {
            Plotly.Plots.resize(chart);
        });
    });
}

// 初期化時に印刷最適化を実行
optimizePrint();