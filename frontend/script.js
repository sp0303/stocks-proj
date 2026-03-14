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

let moversType = "gainers";
let moversData = [];
let isScraping = false;

let sentimentCache = JSON.parse(localStorage.getItem("sentimentCache") || "{}");

let currentPage = 1;
const itemsPerPage = 10;

async function loadNifty() {
    try {
        const res = await fetch(API + "/indices");
        const data = await res.json();
        document.getElementById("nifty-price").innerText = data.nifty50;
        
        // Also load the Nifty LSTM Chart
        renderDashboardNiftyChart("^NSEI");
    } catch (e) {
        console.error("Error loading Nifty:", e);
    }
}

async function renderDashboardNiftyChart(symbol) {
    const canvas = document.getElementById('niftyMainChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    try {
        const res = await fetch(`${API}/ai/lstm-detailed/${encodeURIComponent(symbol)}`);
        const data = await res.json();
        
        const labels = data.history.map(h => h.date).slice(-20); // Just last 20 for mini view
        const prices = data.history.map(h => h.price).slice(-20);
        
        labels.push("AI");
        const chartData = [...prices, data.predicted_price];

        const isLight = document.documentElement.getAttribute('data-theme') === 'light';
        const gridColor = isLight ? 'rgba(0, 0, 0, 0.05)' : 'rgba(255, 255, 255, 0.05)';
        const textColor = isLight ? '#475569' : '#94a3b8';

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    data: chartData,
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34, 197, 94, 0.05)',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: {
                        grid: { display: false },
                        ticks: { display: false }
                    }
                }
            }
        });
    } catch (err) {
        console.error("Nifty dashboard chart error:", err);
    }
}

loadNifty();

function changeMoversType(type) {
    moversType = type;
    currentPage = 1;

    document.querySelectorAll(".tab").forEach(tab => {
        tab.classList.toggle("active", tab.textContent.toLowerCase().includes(type));
    });

    // Instead of loading, just re-sort and render
    renderMovers();
}

function showSkeleton() {
    const tableBody = document.getElementById("movers-body");
    let html = "";

    for (let i = 0; i < 10; i++) {
        html += `
        <tr class="skeleton-row">
            <td><div class="skeleton skeleton-text"></div></td>
            <td><div class="skeleton skeleton-text"></div></td>
            <td><div class="skeleton skeleton-text"></div></td>
            <td><div class="skeleton skeleton-text"></div></td>
            <td><div class="skeleton skeleton-text"></div></td>
            <td><div class="skeleton skeleton-badge"></div></td>
            <td><div class="skeleton skeleton-badge"></div></td>
            <td><div class="skeleton skeleton-badge"></div></td>
            <td><div class="skeleton skeleton-badge"></div></td>
        </tr>`;
    }

    tableBody.innerHTML = html;
}

async function loadMovers() {
    const index = document.getElementById("index-select").value;
    const url = `${API}/movers?index=${index}`;

    showSkeleton();

    try {
        const res = await fetch(url);
        moversData = await res.json();
        console.log("Movers Data Loaded:", moversData);
        renderMovers();
    } catch (e) {
        console.error("Error loading movers:", e);
    }
}

function renderMovers() {
    // Sort locally based on moversType
    const sortedData = [...moversData].sort((a, b) => {
        if (moversType === "gainers") {
            return b.pchange - a.pchange; // High to low
        } else {
            return a.pchange - b.pchange; // Low to high (biggest losers)
        }
    });

    const start = (currentPage - 1) * itemsPerPage;
    const stocks = sortedData.slice(start, start + itemsPerPage);

    let html = "";

    stocks.forEach(stock => {
        const color = stock.pchange >= 0 ? "green" : "red";

        let volume = "N/A";
        if (stock.volume) {
            if (stock.volume >= 10000000)
                volume = (stock.volume / 10000000).toFixed(2) + " Cr";
            else if (stock.volume >= 100000)
                volume = (stock.volume / 100000).toFixed(2) + " L";
            else
                volume = stock.volume.toLocaleString();
        }

        const sentimentScore = parseFloat(stock.news_impact || 0).toFixed(2);

        let newsBadge = `<span class="badge badge-low">Low (${sentimentScore})</span>`;

        if (stock.news_impact >= 0.1 || stock.news_impact <= -0.1)
            newsBadge = `<span class="badge badge-high">🔥 High (${sentimentScore})</span>`;
        else if (stock.news_impact !== 0)
            newsBadge = `<span class="badge badge-medium">📰 Medium (${sentimentScore})</span>`;

        let fScore = stock.fundamental_score || 0;
        let fClass = "score-poor";

        if (fScore >= 8) fClass = "score-excellent";
        else if (fScore >= 5) fClass = "score-good";

        const fundBadge = `<span class="fund-score-badge ${fClass}" onclick="showFundModal('${stock.company}')">${fScore}/10</span>`;

        let tClass = "tech-neutral";
        if (stock.technical_action === "Strong Buy") tClass = "tech-strong-buy";
        if (stock.technical_action === "Buy") tClass = "tech-buy";
        if (stock.technical_action === "Sell") tClass = "tech-sell";
        if (stock.technical_action === "Strong Sell") tClass = "tech-strong-sell";

        const heatmapScore = (stock.technicals?.heatmap_score !== undefined) ? stock.technicals.heatmap_score : 'N/A';
        const techBadge = `<span class="tech-badge ${tClass}" onclick="showTechModal('${stock.company}')">${stock.technical_action} (${heatmapScore})</span>`;

        // AI VIEW (Integrated at-a-glance)
        const aiId = `ai-view-${stock.company.replace(/[^a-zA-Z0-9]/g, '-')}`;
        const aiBadge = `<div class="insight-icon" id="${aiId}" onclick="showInsightsModal('${stock.company}')" style="cursor: pointer; width: 100%;">
            <span class="badge" style="background: var(--bg-secondary); color: var(--text-secondary); opacity: 0.6; min-width: 60px; display: inline-block;">Thinking...</span>
        </div>`;

        html += `
        <tr>
            <td>${stock.company}</td>
            <td>${stock.price}</td>
            <td class="${color}">${stock.change > 0 ? "+" : ""}${stock.change}</td>
            <td class="${color}">${stock.pchange}%</td>
            <td>${volume}</td>
            <td onclick="showNewsModal('${stock.company}')">${newsBadge}</td>
            <td>${fundBadge}</td>
            <td>${techBadge}</td>
            <td style="text-align: center;">${aiBadge}</td>
            <td id="social-${stock.company}">
                ${renderSocialCell(stock.company)}
            </td>
        </tr>`;
    });

    document.getElementById("movers-body").innerHTML = html;
    updatePaginationUI();
    
    // Trigger background AI enrichment
    fetchMoversAISignals(stocks);
}

const aiCache = {}; // Cache results to prevent re-fetching on pagination
async function fetchMoversAISignals(stocks) {
    stocks.forEach(async (stock) => {
        const symbol = stock.company;
        const aiId = `ai-view-${symbol.replace(/[^a-zA-Z0-9]/g, '-')}`;
        const container = document.getElementById(aiId);
        if (!container) return;

        if (aiCache[symbol]) {
            updateAIBadge(container, aiCache[symbol]);
            return;
        }

        try {
            const res = await fetch(`${API}/ai/lstm/${encodeURIComponent(symbol)}`);
            const data = await res.json();
            if (data.signal) {
                aiCache[symbol] = data;
                updateAIBadge(container, data);
            }
        } catch (e) {
            console.error(`AI fetch error for ${symbol}:`, e);
        }
    });
}

function updateAIBadge(container, data) {
    let color = "#94a3b8";
    let bg = "rgba(148, 163, 184, 0.1)";
    
    if (data.signal === "BUY") { color = "#22c55e"; bg = "rgba(34, 197, 94, 0.1)"; }
    else if (data.signal === "SELL") { color = "#ef4444"; bg = "rgba(239, 68, 68, 0.1)"; }

    container.innerHTML = `<span class="badge" style="background: ${bg}; color: ${color}; border: 1px solid ${color}55; font-weight: bold; min-width: 65px; display: inline-block;">${data.signal}</span>`;
}

function renderSocialCell(symbol) {
    const cached = sentimentCache[symbol];

    if (!cached || cached.average_sentiment === undefined || cached.average_sentiment === null) {
        return `
        <div class="social-cell">
            <span class="badge badge-low" onclick="fetchSocialSentiment('${symbol}', false)">Check</span>
            <button class="refresh-btn" onclick="fetchSocialSentiment('${symbol}', true)">↻</button>
        </div>`;
    }

    let label = "Neutral";
    let cls = "badge-low";
    const score = parseFloat(cached.average_sentiment || 0);

    if (score > 0.15) {
        label = "Bullish";
        cls = "badge-high";
    } else if (score < -0.15) {
        label = "Bearish";
        cls = "badge-high";
    }

    return `
    <div class="social-cell">
        <span class="badge ${cls}" onclick="showTweetModal('${symbol}')">
            ${label} (${score.toFixed(3)})
        </span>
        <button class="refresh-btn" onclick="fetchSocialSentiment('${symbol}', true)">↻</button>
    </div>`;
}

async function fetchSocialSentiment(symbol, force = false) {
    if (isScraping) {
        showScraperAlert();
        return;
    }

    const cell = document.getElementById(`social-${symbol}`);
    isScraping = true;

    cell.innerHTML = `
    <div class="social-cell">
        <span class="badge badge-low">${force ? 'Scraping...' : 'Checking...'}</span>
        <button class="refresh-btn spinning">↻</button>
    </div>`;

    try {
        if (!force) {
            const cacheCheck = await fetch(`/social-results/${symbol}`);

            if (cacheCheck.ok) {
                const data = await cacheCheck.json();
                sentimentCache[symbol] = data;
                localStorage.setItem("sentimentCache", JSON.stringify(sentimentCache));
                cell.innerHTML = renderSocialCell(symbol);
                showTweetModal(symbol);
                isScraping = false;
                return;
            }
        }

        cell.innerHTML = `
        <div class="social-cell">
            <span class="badge badge-low">Scraping...</span>
            <button class="refresh-btn spinning">↻</button>
        </div>`;

        const res = await fetch(`${API}/social-sentiment/${symbol}`);
        if (!res.ok) throw new Error("Scrape failed");

        const data = await res.json();
        sentimentCache[symbol] = data;
        localStorage.setItem("sentimentCache", JSON.stringify(sentimentCache));

        cell.innerHTML = renderSocialCell(symbol);
        showTweetModal(symbol);

    } catch (e) {
        console.error(e);
        cell.innerHTML = `
        <div class="social-cell">
            <span class="badge badge-low">N/A</span>
            <button class="refresh-btn" onclick="fetchSocialSentiment('${symbol}', true)">↻</button>
        </div>`;
    } finally {
        isScraping = false;
    }
}

function showNewsModal(stockSymbol) {
    const stock = moversData.find(s => s.company === stockSymbol);
    if (!stock || !stock.articles || stock.articles.length === 0) return;

    document.getElementById("modal-title").innerText = `${stockSymbol} - Recent News`;
    const newsList = document.getElementById("news-list");
    newsList.innerHTML = stock.articles.slice(0, 5).map(article => `
        <div class="news-item">
            <a href="${article.link}" target="_blank">${article.title}</a>
            <div class="news-sentiment">Sentiment Score: ${article.score.toFixed(2)}</div>
        </div>
    `).join('');

    document.getElementById("news-modal").style.display = "flex";
}

function showFundModal(stockSymbol) {
    const stock = moversData.find(s => s.company === stockSymbol);
    if (!stock || !stock.fundamentals) return;

    const f = stock.fundamentals;
    document.getElementById("fund-modal-title").innerText = `${stockSymbol} - Fundamentals`;
    const body = document.getElementById("fund-body");
    const metrics = [
        { name: "P/E Ratio", val: f.pe, desc: "Price-to-Earnings. Target: < 25" },
        { name: "P/B Ratio", val: f.pb, desc: "Price-to-Book. Target: < 5" },
        { name: "ROE", val: f.roe ? (f.roe * 100).toFixed(2) + "%" : "N/A", desc: "Return on Equity. Target: > 15%" },
        { name: "Debt/Equity", val: f.debt_equity, desc: "Leverage. Target: < 1" },
        { name: "Profit Margin", val: f.profit_margin ? (f.profit_margin * 100).toFixed(2) + "%" : "N/A", desc: "Net Efficiency. Target: > 10%" },
        { name: "Market Cap", val: f.market_cap ? (f.market_cap / 10000000).toFixed(2) + " Cr" : "N/A", desc: "Company Size" }
    ];

    body.innerHTML = metrics.map(m => `
        <tr>
            <td><strong>${m.name}</strong></td>
            <td>${m.val || 'N/A'}</td>
            <td><small>${m.desc}</small></td>
        </tr>
    `).join('');

    document.getElementById("fund-score-val").innerText = f.score || 0;
    document.getElementById("fund-modal").style.display = "flex";
}

function showTechModal(stockSymbol) {
    const stock = moversData.find(s => s.company === stockSymbol);
    if (!stock || !stock.technicals) return;

    const t = stock.technicals;
    document.getElementById("tech-modal-title").innerText = `${stockSymbol} - Technical Indicators`;
    const body = document.getElementById("tech-body");
    const interpretRSI = (val) => {
        if (!val) return "N/A";
        if (val < 30) return "Oversold - Buy Signal";
        if (val > 70) return "Overbought - Sell Signal";
        return "Neutral range";
    };

    const metrics = [
        { name: "RSI (14)", val: t.rsi, desc: interpretRSI(t.rsi) },
        { name: "MACD", val: t.macd, desc: t.is_bullish_crossover ? "Bullish Crossover" : (t.macd > t.macd_signal ? "Bullish Range" : "Bearish Range") },
        { name: "SMA (20)", val: t.sma20, desc: stock.price > t.sma20 ? "Above Avg (Bullish)" : "Below Avg (Bearish)" },
        { name: "SMA (50)", val: t.sma50, desc: stock.price > t.sma50 ? "Above Avg (Bullish)" : "Below Avg (Bearish)" },
        { name: "Volume Spike", val: t.volume_ratio ? t.volume_ratio.toFixed(2) + "x" : "N/A", desc: t.volume_ratio > 1.5 ? "High Interest" : "Normal Volume" },
        { name: "1M Return", val: t.return_1m ? t.return_1m.toFixed(2) + "%" : "N/A", desc: t.return_1m > 0 ? "Positive Momentum" : "Negative Momentum" },
        { name: "3M Return", val: t.return_3m ? t.return_3m.toFixed(2) + "%" : "N/A", desc: t.return_3m > 0 ? "Strong Trend" : "Weak Trend" }
    ];

    body.innerHTML = metrics.map(m => `
        <tr>
            <td><strong>${m.name}</strong></td>
            <td>${m.val || 'N/A'}</td>
            <td><small>${m.desc}</small></td>
        </tr>
    `).join('');

    const score = t.heatmap_score || 0;
    document.getElementById("tech-action-val").innerHTML = `
        ${stock.technical_action} 
        <div style="margin-top: 5px; font-size: 0.9rem; color: #94a3b8;">
            Overall Score: <span style="color: #60a5fa; font-weight: bold;">${score}</span> / 10
        </div>
    `;
    document.getElementById("tech-modal").style.display = "flex";
}

function showTweetModal(symbol) {
    const data = sentimentCache[symbol];
    if (!data) return;

    document.getElementById("tweet-symbol").innerText = symbol;

    const avgScore = data.average_sentiment;
    const avgEl = document.getElementById("tweet-avg-score");
    avgEl.innerText = avgScore.toFixed(3);

    let trendLabel = "NEUTRAL";
    let trendColor = "#e2e8f0";

    if (avgScore > 0.15) {
        trendLabel = "BULLISH TREND";
        trendColor = "#10b981";
    } else if (avgScore < -0.15) {
        trendLabel = "BEARISH TREND";
        trendColor = "#ef4444";
    }

    avgEl.style.color = trendColor;

    // Add trend counts to header if container exists (we'll add it to index.html)
    const trendContainer = document.getElementById("sentiment-trend-info");
    if (trendContainer) {
        trendContainer.innerHTML = `
            <div style="font-weight:bold; color:${trendColor}; margin-bottom:10px; font-size:1.1rem">${trendLabel}</div>
            <div style="display:flex; gap:15px; font-size:0.9rem; color:#94a3b8">
                <span>🟢 Bullish: ${data.bullish_count || 0}</span>
                <span>🔴 Bearish: ${data.bearish_count || 0}</span>
                <span>⚪ Neutral: ${data.neutral_count || 0}</span>
            </div>
        `;
    }

    document.getElementById("tweet-count").innerText = data.tweets_analyzed;

    const list = document.getElementById("tweet-list");
    list.innerHTML = data.tweets.map((t, i) => {
        const score = data.scores ? data.scores[i] : 0;
        let borderColor = "rgba(255,255,255,0.1)";
        let badge = '<span class="badge badge-low" style="padding:2px 6px; font-size:0.7rem">Neutral</span>';

        if (score > 0.05) {
            borderColor = "rgba(16, 185, 129, 0.4)";
            badge = '<span class="badge badge-high" style="padding:2px 6px; font-size:0.7rem; background:#065f46">Bullish</span>';
        } else if (score < -0.05) {
            borderColor = "rgba(239, 68, 68, 0.4)";
            badge = '<span class="badge badge-high" style="padding:2px 6px; font-size:0.7rem; background:#991b1b">Bearish</span>';
        }

        return `
            <div class="tweet-card" style="border-left: 4px solid ${borderColor}; margin-bottom:10px; padding:12px; background:rgba(255,255,255,0.03); border-radius:8px">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
                    <div style="color:#60a5fa; font-weight:bold; font-size:0.8rem">Tweet #${i + 1}</div>
                    ${badge}
                </div>
                <div style="font-size:0.95rem; line-height:1.4; color:#e2e8f0">"${t}"</div>
            </div>
        `;
    }).join('');

    if (data.screenshot) {
        document.getElementById("tweet-screenshot").src = data.screenshot;
    }

    document.getElementById("tweet-modal").style.display = "flex";
}

async function showInsightsModal(symbol) {
    const modal = document.getElementById("insights-modal");
    if (modal) modal.style.display = "flex";

    // Show loading briefing
    document.getElementById("ai-briefing").innerHTML = `<i>Analyzing ${symbol} signals...</i>`;

    const stock = moversData.find(s => s.company === symbol);
    if (!stock) return;

    // Show loading state if insights are missing
    if (!stock.insights || Object.keys(stock.insights).length === 0) {
        document.getElementById("insights-modal-title").innerText = `${symbol} - Loading...`;
        try {
            const res = await fetch(`${API}/stock-insights/${symbol}`);
            const data = await res.json();
            stock.insights = data;
        } catch (e) {
            console.error("Error loading insights:", e);
            document.getElementById("insights-modal-title").innerText = `${symbol} - Data Unavailable`;
            return;
        }
    }

    const data = stock.insights;
    const titleEl = document.getElementById("insights-modal-title");
    if (titleEl) titleEl.innerText = `${symbol} - Intelligence Briefing`;

    // Volume
    const v = data.volume || { today_volume: 0, avg_volume_20: 0, volume_spike: 1.0 };
    document.getElementById("insight-today-vol").innerText = (v.today_volume || 0).toLocaleString();
    document.getElementById("insight-avg-vol").innerText = (v.avg_volume_20 || 0).toLocaleString();

    // Trigger AI prediction load (it will update briefing when done)
    loadAI(symbol, v.volume_spike || 1.0);
}

function closeModal() {
    document.querySelectorAll(".modal-overlay").forEach(m => m.style.display = "none");
}

function showScraperAlert() {
    const alert = document.getElementById("scraper-alert");
    alert.style.display = "block";
    setTimeout(() => alert.style.display = "none", 3000);
}

function updatePaginationUI() {
    const totalPages = Math.ceil(moversData.length / itemsPerPage) || 1;
    document.getElementById("page-info").innerText = `Page ${currentPage} of ${totalPages}`;
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        renderMovers();
    }
}

function nextPage() {
    const total = Math.ceil(moversData.length / itemsPerPage);
    if (currentPage < total) {
        currentPage++;
        renderMovers();
    }
}

async function loadAI(symbol, volSpike = 1.0) {
    try {
        const [resLstm, resTrans] = await Promise.all([
            fetch(API + "/ai/lstm/" + symbol),
            fetch(API + "/ai/transformer/" + symbol).catch(() => null)
        ]);
        
        const data = await resLstm.json();
        const dataTrans = resTrans && resTrans.ok ? await resTrans.json() : null;

        // LSTM Grid
        document.getElementById("aiCurrent").innerText = data.current_price.toFixed(2);
        document.getElementById("aiPredicted").innerText = data.predicted_price.toFixed(2);
        document.getElementById("aiMove").innerText = data.expected_move.toFixed(2) + "%";

        const signalEl = document.getElementById("aiSignal");
        signalEl.innerText = data.signal;
        signalEl.style.color = (data.signal === "BUY") ? "#22c55e" : (data.signal === "SELL" ? "#ef4444" : "#94a3b8");

        // Transformer Grid
        if (dataTrans && !dataTrans.error) {
            document.getElementById("aiCurrentTransformer").innerText = dataTrans.current_price.toFixed(2);
            document.getElementById("aiPredictedTransformer").innerText = dataTrans.predicted_price.toFixed(2);
            document.getElementById("aiMoveTransformer").innerText = dataTrans.expected_move.toFixed(2) + "%";

            const transSignalEl = document.getElementById("aiSignalTransformer");
            transSignalEl.innerText = dataTrans.signal;
            transSignalEl.style.color = (dataTrans.signal === "BUY") ? "#22c55e" : (dataTrans.signal === "SELL" ? "#ef4444" : "#94a3b8");
        } else {
            document.getElementById("aiCurrentTransformer").innerText = "-";
            document.getElementById("aiPredictedTransformer").innerText = "Not Trained";
            document.getElementById("aiMoveTransformer").innerText = "-";
            document.getElementById("aiSignalTransformer").innerText = "-";
        }

        // TECHNICAL INDICATORS GRID
        document.getElementById("aiRSI").innerText = data.rsi ? data.rsi.toFixed(2) : "N/A";
        document.getElementById("aiMACD").innerText = data.macd ? data.macd.toFixed(2) : "N/A";
        document.getElementById("aiSMA20").innerText = data.sma20 ? data.sma20.toFixed(2) : "N/A";
        document.getElementById("aiSMA50").innerText = data.sma50 ? data.sma50.toFixed(2) : "N/A";

        // Set detailed analysis link
        const detailedLink = document.getElementById("view-detailed-ai");
        detailedLink.href = `lstm_index.html?symbol=${encodeURIComponent(symbol)}`;

        // INTEGRATE MODAL CHART
        renderModalLstmChart(symbol);

        // GENERATE BRIEFING (using LSTM for now as baseline)
        updateAIBriefing(symbol, volSpike, data);

    } catch (err) {
        console.error("AI prediction error:", err);
        document.getElementById("aiSignal").innerText = "Unavailable";
    }
}

function updateAIBriefing(symbol, volSpike, aiData) {
    let summary = "";
    const move = aiData.expected_move.toFixed(2);
    
    // Technical Context
    let techContext = "";
    if (aiData.rsi) {
        if (aiData.rsi > 70) techContext = "RSI is <b>Overbought (>70)</b>, suggesting a possible correction. ";
        else if (aiData.rsi < 30) techContext = "RSI is <b>Oversold (<30)</b>, indicating a potential reversal. ";
        else techContext = `RSI at <b>${aiData.rsi.toFixed(1)}</b> shows balanced momentum. `;
    }

    if (volSpike > 2.0) {
        if (aiData.signal === "BUY") {
            summary = `🔥 <b>Strong Convergence:</b> ${symbol} is seeing a massive <b>${volSpike}x</b> volume spike. ${techContext}AI detects a <b>${move}%</b> breakout opportunity.`;
        } else if (aiData.signal === "SELL") {
            summary = `⚠️ <b>Warning:</b> High selling volume (<b>${volSpike}x</b>) detected. ${techContext}AI expects a <b>${Math.abs(move)}%</b> drop.`;
        } else {
            summary = `📊 <b>Volume Alert:</b> High churn detected (<b>${volSpike}x</b>). ${techContext}AI is currently <b>NEUTRAL</b>.`;
        }
    } else {
        if (aiData.signal === "BUY") {
            summary = `🚀 <b>AI Insight:</b> LSTM detects a recovery. ${techContext}Targeting a <b>${move}%</b> gain based on multivariate analysis.`;
        } else if (aiData.signal === "SELL") {
            summary = `⬇️ <b>AI Insight:</b> Model projects a <b>${Math.abs(move)}%</b> decline. ${techContext}Momentum looks weak.`;
        } else {
            summary = `☁️ <b>Stable:</b> Sideways movement predicted. ${techContext}No major volatility catalysts detected.`;
        }
    }

    document.getElementById("ai-briefing").innerHTML = summary;
}

let modalChartInstance = null;
async function renderModalLstmChart(symbol) {
    const canvas = document.getElementById('modalLstmChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Clear previous chart
    if (modalChartInstance) {
        modalChartInstance.destroy();
    }

    try {
        const [resLstm, resTrans] = await Promise.all([
            fetch(`${API}/ai/lstm-detailed/${encodeURIComponent(symbol)}`),
            fetch(`${API}/ai/transformer-detailed/${encodeURIComponent(symbol)}`).catch(() => null)
        ]);
        
        const data = await resLstm.json();
        const dataTrans = resTrans && resTrans.ok ? await resTrans.json() : null;
        
        if (data.error) throw new Error(data.error);

        const labels = data.history.map(h => h.date);
        const prices = data.history.map(h => h.price);
        
        // Add one more label for prediction
        labels.push("Prediction");
        const chartData = [...prices, data.predicted_price];

        const isLight = document.documentElement.getAttribute('data-theme') === 'light';
        const gridColor = isLight ? 'rgba(0, 0, 0, 0.05)' : 'rgba(255, 255, 255, 0.05)';
        const textColor = isLight ? '#475569' : '#94a3b8';

        let datasets = [{
            label: 'LSTM',
            data: chartData,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.3,
            fill: true,
            segment: {
                borderDash: (ctx) => ctx.p0DataIndex === prices.length - 1 ? [5, 5] : undefined,
                borderColor: (ctx) => ctx.p0DataIndex === prices.length - 1 ? '#f59e0b' : undefined,
            }
        }];

        if (dataTrans && !dataTrans.error) {
            let transData = new Array(prices.length + 1).fill(null);
            transData[prices.length - 1] = prices[prices.length - 1]; // Anchor
            transData[prices.length] = dataTrans.predicted_price;
            
            datasets.push({
                label: 'Transformer',
                data: transData,
                borderColor: '#a855f7',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: (ctx) => ctx.dataIndex === transData.length - 1 ? 6 : 0,
                pointBackgroundColor: '#a855f7',
                fill: false,
                tension: 0
            });
        }
        
        modalChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { 
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    x: { display: false },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor, font: { size: 10 } }
                    }
                }
            }
        });
    } catch (err) {
        console.error("Modal chart error:", err);
    }
}
// Event Listeners
document.addEventListener('click', (e) => {
    if (e.target.classList.contains("close-btn")) closeModal();
    if (e.target.classList.contains("modal-overlay")) closeModal();
});

// Initial load
loadMovers();