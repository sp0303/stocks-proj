// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeUI(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeUI(newTheme);
    
    // Refresh page to update charts with new theme colors
    location.reload();
}

function updateThemeUI(theme) {
    const icon = document.getElementById('theme-icon');
    const text = document.getElementById('theme-text');
    if (!icon || !text) return;

    if (theme === 'light') {
        icon.innerText = '☀️';
        text.innerText = 'Light Mode';
    } else {
        icon.innerText = '🌙';
        text.innerText = 'Dark Mode';
    }
}

initTheme();

const API = "";
let globalData = null;
let globalDataTrans = null;
let currentChartType = 'price';
let chartInstance = null;

async function loadDetailedData(symbol = "^NSEI") {
    const loader = document.getElementById("loader");
    try {
        const [resLstm, resTrans] = await Promise.all([
            fetch(`${API}/ai/lstm-detailed/${symbol}`),
            fetch(`${API}/ai/transformer-detailed/${symbol}`).catch(() => null)
        ]);
        
        const data = await resLstm.json();
        const dataTrans = resTrans && resTrans.ok ? await resTrans.json() : null;

        if (data.error) throw new Error(data.error);

        globalData = data;
        globalDataTrans = dataTrans;
        updateStats(data, dataTrans);
        renderActiveChart();
        renderTable(data.history);
        
        loader.style.display = "none";
    } catch (e) {
        console.error("Error loading detailed data:", e);
        alert("Failed to load AI data: " + e.message);
        window.location.href = "index.html";
    }
}

function updateStats(data, dataTrans) {
    document.getElementById("stat-current").innerText = data.current_price.toFixed(2);
    
    // LSTM Stats
    document.getElementById("stat-predicted").innerText = data.predicted_price.toFixed(2);
    const move = data.expected_move.toFixed(2);
    const moveEl = document.getElementById("stat-move");
    moveEl.innerText = (move > 0 ? "+" : "") + move + "%";
    moveEl.style.color = move > 0 ? "#22c55e" : "#ef4444";

    const signalEl = document.getElementById("stat-signal");
    signalEl.innerText = data.signal;
    if (data.signal === "BUY") signalEl.style.color = "#22c55e";
    else if (data.signal === "SELL") signalEl.style.color = "#ef4444";
    else signalEl.style.color = "#94a3b8";

    // Transformer Stats
    if (dataTrans && !dataTrans.error) {
        document.getElementById("stat-predicted-trans").innerText = dataTrans.predicted_price.toFixed(2);
        const transMove = dataTrans.expected_move.toFixed(2);
        const transMoveEl = document.getElementById("stat-move-trans");
        transMoveEl.innerText = (transMove > 0 ? "+" : "") + transMove + "%";
        transMoveEl.style.color = transMove > 0 ? "#a855f7" : "#ef4444"; // Purple for positive Transformer move

        const transSignalEl = document.getElementById("stat-signal-trans");
        transSignalEl.innerText = dataTrans.signal;
        if (dataTrans.signal === "BUY") transSignalEl.style.color = "#a855f7";
        else if (dataTrans.signal === "SELL") transSignalEl.style.color = "#ef4444";
        else transSignalEl.style.color = "#94a3b8";
    } else {
        document.getElementById("stat-predicted-trans").innerText = "Not Trained";
        document.getElementById("stat-move-trans").innerText = "--";
        document.getElementById("stat-signal-trans").innerText = "--";
    }


    // Technical Snapshot
    const latest = data.history[data.history.length - 1];
    document.getElementById("stat-rsi").innerText = latest.rsi ? latest.rsi.toFixed(2) : "--";
    document.getElementById("stat-macd").innerText = latest.macd ? latest.macd.toFixed(2) : "--";
    document.getElementById("stat-sma20").innerText = latest.sma20 ? latest.sma20.toFixed(1) : "--";
    document.getElementById("stat-sma50").innerText = latest.sma50 ? latest.sma50.toFixed(1) : "--";

    // BRIEFING
    updateAIBriefing(data.symbol, 1.0, data); // Default 1.0 vol for index if not tracked
}

function updateAIBriefing(symbol, volSpike, aiData) {
    let summary = "";
    const move = aiData.expected_move.toFixed(2);
    const latest = aiData.history[aiData.history.length - 1];
    
    let techContext = "";
    if (latest.rsi) {
        if (latest.rsi > 70) techContext = "RSI is <b>Overbought</b>. ";
        else if (latest.rsi < 30) techContext = "RSI is <b>Oversold</b>. ";
        else techContext = "Momentum is neutral. ";
    }

    if (aiData.signal === "BUY") {
        summary = `🚀 <b>Intelligence Briefing:</b> ${symbol} shows a bullish multivariate pattern. ${techContext}Model predicts a <b>${move}%</b> upward move supported by current technical indicators.`;
    } else if (aiData.signal === "SELL") {
        summary = `⬇️ <b>Intelligence Briefing:</b> Bearish outlook detected for ${symbol}. ${techContext}AI expects a <b>${Math.abs(move)}%</b> decline as indicators show weakness.`;
    } else {
        summary = `☁️ <b>Intelligence Briefing:</b> AI remains net-neutral on ${symbol}. Sideways consolidation is the most likely scenario based on current feature patterns.`;
    }

    const briefingEl = document.getElementById("ai-briefing");
    if (briefingEl) briefingEl.innerHTML = summary;
    
    // Legacy support for prediction-text if still in HTML
    const callout = document.getElementById("prediction-text");
    if (callout) {
        callout.className = "prediction-callout " + (aiData.signal === "BUY" ? "callout-buy" : (aiData.signal === "SELL" ? "callout-sell" : "callout-neutral"));
        callout.innerText = summary.replace(/<[^>]*>/g, '');
    }
}

function switchChart(type) {
    currentChartType = type;
    
    // Update tabs
    document.querySelectorAll('#chart-tabs button').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`#chart-tabs button[onclick="switchChart('${type}')"]`).classList.add('active');
    
    // Update title
    const titles = {
        'price': 'Price Trend & AI Prediction',
        'volume': 'Trading Volume Analysis',
        'technicals': 'Momentum Indicators (RSI & MACD)',
        'averages': 'Trend Analysis (SMA 20/50)'
    };
    document.getElementById('chart-title').innerText = titles[type];
    
    renderActiveChart();
}

function renderActiveChart() {
    if (!globalData) return;
    const ctx = document.getElementById('predictionChart').getContext('2d');
    if (chartInstance) chartInstance.destroy();

    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const gridColor = isLight ? 'rgba(0, 0, 0, 0.05)' : 'rgba(255, 255, 255, 0.05)';
    const textColor = isLight ? '#475569' : '#94a3b8';
    
    const labels = globalData.history.map(h => h.date);
    let datasets = [];

    if (currentChartType === 'price') {
        const historyPrices = globalData.history.map(h => h.price);
        const labelsWithPred = [...labels, "AI Prediction"];
        const dataWithPred = [...historyPrices, globalData.predicted_price];
        
        datasets = [{
            label: 'LSTM Prediction',
            data: dataWithPred,
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: (ctx) => ctx.dataIndex === dataWithPred.length - 1 ? 8 : 0,
            pointBackgroundColor: (ctx) => ctx.dataIndex === dataWithPred.length - 1 ? '#f59e0b' : '#60a5fa',
            segment: {
                borderDash: (ctx) => ctx.p0DataIndex === historyPrices.length - 1 ? [5, 5] : undefined,
                borderColor: (ctx) => ctx.p0DataIndex === historyPrices.length - 1 ? '#f59e0b' : undefined,
            }
        }];

        if (globalDataTrans && !globalDataTrans.error) {
            let transData = new Array(historyPrices.length + 1).fill(null);
            transData[historyPrices.length - 1] = historyPrices[historyPrices.length - 1]; // Anchor
            transData[historyPrices.length] = globalDataTrans.predicted_price;
            
            datasets.push({
                label: 'Transformer Prediction',
                data: transData,
                borderColor: '#a855f7',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: (ctx) => ctx.dataIndex === transData.length - 1 ? 8 : 0,
                pointBackgroundColor: '#a855f7',
                fill: false,
                tension: 0
            });
        }
        
        createChart(ctx, labelsWithPred, datasets, gridColor, textColor);
    } else if (currentChartType === 'volume') {
        datasets = [{
            label: 'Volume',
            data: globalData.history.map(h => h.volume),
            backgroundColor: isLight ? 'rgba(59, 130, 246, 0.5)' : 'rgba(59, 130, 246, 0.3)',
            borderColor: '#3b82f6',
            borderWidth: 1,
            type: 'bar'
        }];
        createChart(ctx, labels, datasets, gridColor, textColor);
    } else if (currentChartType === 'technicals') {
        datasets = [
            {
                label: 'RSI',
                data: globalData.history.map(h => h.rsi),
                borderColor: '#a855f7',
                borderWidth: 2,
                pointRadius: 0,
                yAxisID: 'y'
            },
            {
                label: 'MACD',
                data: globalData.history.map(h => h.macd),
                borderColor: '#f59e0b',
                borderWidth: 2,
                pointRadius: 0,
                yAxisID: 'y1'
            }
        ];
        createMultiAxisChart(ctx, labels, datasets, gridColor, textColor);
    } else if (currentChartType === 'averages') {
        datasets = [
            {
                label: 'Price',
                data: globalData.history.map(h => h.price),
                borderColor: '#60a5fa',
                borderWidth: 1,
                pointRadius: 0
            },
            {
                label: 'SMA 20',
                data: globalData.history.map(h => h.sma20),
                borderColor: '#22c55e',
                borderWidth: 2,
                pointRadius: 0
            },
            {
                label: 'SMA 50',
                data: globalData.history.map(h => h.sma50),
                borderColor: '#ef4444',
                borderWidth: 2,
                pointRadius: 0
            }
        ];
        createChart(ctx, labels, datasets, gridColor, textColor);
    }
}

function createChart(ctx, labels, datasets, gridColor, textColor) {
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: datasets.length > 1, labels: { color: textColor } } },
            scales: {
                y: { grid: { color: gridColor }, ticks: { color: textColor } },
                x: { grid: { display: false }, ticks: { color: textColor, maxRotation: 45, minRotation: 45 } }
            }
        }
    });
}

function createMultiAxisChart(ctx, labels, datasets, gridColor, textColor) {
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: textColor } } },
            scales: {
                y: { type: 'linear', display: true, position: 'left', grid: { color: gridColor }, ticks: { color: textColor }, title: { display: true, text: 'RSI', color: textColor } },
                y1: { type: 'linear', display: true, position: 'right', grid: { drawOnChartArea: false }, ticks: { color: textColor }, title: { display: true, text: 'MACD', color: textColor } },
                x: { grid: { display: false }, ticks: { color: textColor, maxRotation: 45, minRotation: 45 } }
            }
        }
    });
}

function renderTable(history) {
    const body = document.getElementById("history-body");
    let html = "";
    
    // Render in reverse chronological order
    const reversed = [...history].reverse();
    
    reversed.forEach((day) => {
        const volStr = day.volume >= 10000000 ? (day.volume/10000000).toFixed(2) + " Cr" : (day.volume/100000).toFixed(2) + " L";
        
        html += `
            <tr>
                <td>${day.date}</td>
                <td style="font-weight: bold;">${day.price.toFixed(2)}</td>
                <td style="font-size: 0.8rem; color: #94a3b8;">H: ${day.high.toFixed(2)}<br>L: ${day.low.toFixed(2)}</td>
                <td>${volStr}</td>
                <td>${day.rsi ? day.rsi.toFixed(2) : '--'}</td>
                <td>${day.macd ? day.macd.toFixed(2) : '--'}</td>
                <td style="font-size: 0.8rem;">20: ${day.sma20 ? day.sma20.toFixed(1) : '--'}<br>50: ${day.sma50 ? day.sma50.toFixed(1) : '--'}</td>
            </tr>
        `;
    });
    
    body.innerHTML = html;
}

// Initial load
const urlParams = new URLSearchParams(window.location.search);
const symbolParam = urlParams.get('symbol') || "^NSEI";

if (symbolParam !== "^NSEI") {
    document.getElementById("page-title").innerText = `LSTM Intelligence: ${symbolParam}`;
    document.title = `LSTM Analysis | ${symbolParam}`;
}

loadDetailedData(symbolParam);
