// VWAP Trade Validator - Frontend JavaScript

let currentAnalysis = null;
let priceChart = null;

// DOM Elements
const symbolInput = document.getElementById('symbol');
const entryPriceInput = document.getElementById('entryPrice');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const results = document.getElementById('results');

// Event Listeners
analyzeBtn.addEventListener('click', handleAnalyze);
clearBtn.addEventListener('click', handleClear);
symbolInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleAnalyze();
});

// Initialize
loadStatistics();

// Handle Analyze Button
async function handleAnalyze() {
    const symbol = symbolInput.value.trim().toUpperCase();

    if (!symbol) {
        showError('Please enter a stock symbol');
        return;
    }

    // Show loading, hide results and errors
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    hideError();

    try {
        const entryPrice = entryPriceInput.value ? parseFloat(entryPriceInput.value) : null;

        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symbol: symbol,
                entry_price: entryPrice
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }

        currentAnalysis = data;
        displayResults(data);

    } catch (err) {
        showError(err.message);
    } finally {
        loading.classList.add('hidden');
    }
}

// Display Results
function displayResults(data) {
    // Price Header
    displayPriceHeader(data);

    // VWAP Levels
    displayVWAPLevels(data.vwaps, data.current_price, data.deviations);

    // Top Levels
    displayTopLevels(data.top_levels);

    // Patterns
    displayPatterns(data.patterns);

    // Entry Analysis
    if (data.entry_analysis) {
        displayEntryAnalysis(data.entry_analysis);
    }

    // Chart
    displayChart(data);

    // Show results
    results.classList.remove('hidden');
}

// Display Price Header
function displayPriceHeader(data) {
    const header = document.getElementById('priceHeader');

    const change = data.quote.change;
    const changePct = data.quote.change_percent;
    const changeClass = change >= 0 ? 'positive' : 'negative';
    const changeSymbol = change >= 0 ? '+' : '';

    header.innerHTML = `
        <h2>${data.symbol}</h2>
        <div class="price-info">
            <div class="price-stat">
                <label>Current Price</label>
                <div class="value">$${data.current_price.toFixed(2)}</div>
            </div>
            <div class="price-stat">
                <label>Change</label>
                <div class="value ${changeClass}">
                    ${changeSymbol}$${change.toFixed(2)} (${changePct})
                </div>
            </div>
            <div class="price-stat">
                <label>Volume</label>
                <div class="value">${formatVolume(data.quote.volume)}</div>
            </div>
        </div>
    `;
}

// Display VWAP Levels
function displayVWAPLevels(vwaps, currentPrice, deviations) {
    const container = document.getElementById('vwapLevels');

    const timeframeOrder = ['yearly', 'quarterly', 'three_month', 'daily'];
    const timeframeLabels = {
        'yearly': 'Yearly',
        'quarterly': 'Quarterly',
        'three_month': '3-Month',
        'daily': 'Daily'
    };

    let html = '';

    timeframeOrder.forEach(tf => {
        const vwap = vwaps[tf];
        const deviation = deviations[tf];

        if (!vwap || vwap === 0) return;

        const isAbove = deviation ? deviation.is_above : currentPrice > vwap;
        const devPct = deviation ? deviation.deviation_pct : 0;
        const devDollars = deviation ? deviation.deviation_dollars : 0;
        const directionClass = isAbove ? 'above' : 'below';
        const directionSymbol = isAbove ? '+' : '';

        html += `
            <div class="level-card">
                <div class="timeframe">${timeframeLabels[tf]} VWAP</div>
                <div class="price">$${vwap.toFixed(2)}</div>
                <div class="deviation ${directionClass}">
                    <span>${directionSymbol}${devPct}%</span>
                    <span>${directionSymbol}$${devDollars.toFixed(2)}</span>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Display Top Levels
function displayTopLevels(levels) {
    const container = document.getElementById('topLevels');

    if (!levels || levels.length === 0) {
        container.innerHTML = '<p>No significant levels detected</p>';
        return;
    }

    let html = '';

    levels.forEach(level => {
        const rankEmoji = level.rank === 1 ? '🥇' : level.rank === 2 ? '🥈' : level.rank === 3 ? '🥉' : '•';

        html += `
            <div class="top-level-item">
                <div class="level-rank">${rankEmoji}</div>
                <div class="level-details">
                    <div class="label">${level.label || level.type.toUpperCase()}</div>
                    <div class="price">$${level.level.toFixed(2)}</div>
                </div>
                <div class="level-score">
                    <div class="score">${level.score}</div>
                    <div class="label">Score</div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Display Patterns
function displayPatterns(patterns) {
    const container = document.getElementById('patterns');

    let html = '';

    // Unbroken Priors
    if (patterns.unbroken_priors && patterns.unbroken_priors.length > 0) {
        html += `
            <div class="pattern-card">
                <h4>
                    Unbroken Priors
                    <span class="badge">${patterns.unbroken_priors.length}</span>
                </h4>
                <ul class="pattern-list">
                    ${patterns.unbroken_priors.map(p => `
                        <li>${p.timeframe.toUpperCase()} VWAP: $${p.level.toFixed(2)} (${p.type})</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    // Confluences
    if (patterns.confluences && patterns.confluences.length > 0) {
        html += `
            <div class="pattern-card">
                <h4>
                    Confluence Zones
                    <span class="badge">${patterns.confluences.length}</span>
                </h4>
                <ul class="pattern-list">
                    ${patterns.confluences.map(c => `
                        <li>$${c.level.toFixed(2)} - ${c.count} levels (${c.timeframes.join(', ')})</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    // Recent Reclaims
    if (patterns.reclaims && patterns.reclaims.length > 0) {
        const recentReclaims = patterns.reclaims.slice(0, 5);
        html += `
            <div class="pattern-card">
                <h4>
                    Recent Reclaims
                    <span class="badge">${recentReclaims.length}</span>
                </h4>
                <ul class="pattern-list">
                    ${recentReclaims.map(r => `
                        <li>${r.timeframe.toUpperCase()}: ${r.type} (${r.days_ago} days ago)</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    // Magnet Interactions
    if (patterns.magnet_interactions && patterns.magnet_interactions.length > 0) {
        const topMagnets = patterns.magnet_interactions.slice(0, 5);
        html += `
            <div class="pattern-card">
                <h4>
                    Magnet Interactions
                    <span class="badge">${topMagnets.length}</span>
                </h4>
                <ul class="pattern-list">
                    ${topMagnets.map(m => `
                        <li>$${m.magnet_level.toFixed(2)} (${m.magnet_pct}) - ${m.touches} touches</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    if (html === '') {
        html = '<p>No significant patterns detected in recent price action.</p>';
    }

    container.innerHTML = html;
}

// Display Entry Analysis
function displayEntryAnalysis(analysis) {
    const container = document.getElementById('entryAnalysis');

    container.className = `entry-analysis ${analysis.quality}`;

    let confirmationsHtml = '';
    if (analysis.confirmations && analysis.confirmations.length > 0) {
        confirmationsHtml = `
            <div style="margin-top: 10px;">
                <strong>Confirmations:</strong>
                <ul style="margin-left: 20px; margin-top: 5px;">
                    ${analysis.confirmations.map(c => `<li>${c}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    container.innerHTML = `
        <h3>Entry Quality: ${analysis.quality.toUpperCase()}</h3>
        <p>${analysis.reason}</p>
        <p>Distance from nearest VWAP: ${analysis.distance_pct}%</p>
        ${confirmationsHtml}
    `;

    container.classList.remove('hidden');
}

// Display Chart
function displayChart(data) {
    const ctx = document.getElementById('priceChart').getContext('2d');

    // Destroy existing chart
    if (priceChart) {
        priceChart.destroy();
    }

    // Prepare data (last 30 days for visibility)
    const chartData = prepareChartData(data);

    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Price',
                    data: chartData.prices,
                    borderColor: '#1f6feb',
                    backgroundColor: 'rgba(31, 111, 235, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1
                },
                ...chartData.vwapLines
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#c9d1d9'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#8b949e'
                    },
                    grid: {
                        color: '#30363d'
                    }
                },
                y: {
                    ticks: {
                        color: '#8b949e',
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    },
                    grid: {
                        color: '#30363d'
                    }
                }
            }
        }
    });
}

// Prepare Chart Data
function prepareChartData(data) {
    // This is simplified - in production you'd fetch historical data
    const labels = ['30d ago', '25d ago', '20d ago', '15d ago', '10d ago', '5d ago', 'Today'];
    const prices = [
        data.current_price * 0.95,
        data.current_price * 0.97,
        data.current_price * 0.96,
        data.current_price * 0.98,
        data.current_price * 0.99,
        data.current_price * 1.01,
        data.current_price
    ];

    const vwapLines = [];
    const colors = {
        'yearly': '#238636',
        'quarterly': '#d29922',
        'three_month': '#8957e5',
        'daily': '#da3633'
    };

    Object.entries(data.vwaps).forEach(([tf, vwap]) => {
        if (vwap > 0) {
            vwapLines.push({
                label: `${tf.toUpperCase()} VWAP`,
                data: Array(labels.length).fill(vwap),
                borderColor: colors[tf],
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0
            });
        }
    });

    return { labels, prices, vwapLines };
}

// Rating Functions
let selectedRating = null;

function rateTrade(rating) {
    selectedRating = rating;

    // Update button styles
    document.querySelectorAll('.rating-buttons button').forEach(btn => {
        btn.style.opacity = '0.5';
    });
    event.target.style.opacity = '1';
}

// Save Trade
async function saveTrade() {
    if (!currentAnalysis) {
        showError('No analysis to save');
        return;
    }

    const notes = document.getElementById('tradeNotes').value;

    try {
        const response = await fetch('/api/save-trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symbol: currentAnalysis.symbol,
                entry_price: currentAnalysis.entry_price || currentAnalysis.current_price,
                current_price: currentAnalysis.current_price,
                rating: selectedRating,
                notes: notes,
                vwap_data: currentAnalysis.vwaps,
                patterns: currentAnalysis.patterns
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert('Trade saved successfully!');
            loadStatistics();

            // Reset rating
            selectedRating = null;
            document.querySelectorAll('.rating-buttons button').forEach(btn => {
                btn.style.opacity = '1';
            });
            document.getElementById('tradeNotes').value = '';
        } else {
            throw new Error(data.error);
        }

    } catch (err) {
        showError('Failed to save trade: ' + err.message);
    }
}

// Load Statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const stats = await response.json();

        const container = document.getElementById('statistics');

        let html = `
            <div class="stat-item">
                <span>Total Trades Analyzed:</span>
                <strong>${stats.total_trades || 0}</strong>
            </div>
        `;

        if (stats.ratings) {
            Object.entries(stats.ratings).forEach(([rating, count]) => {
                html += `
                    <div class="stat-item">
                        <span>${rating.charAt(0).toUpperCase() + rating.slice(1)} Setups:</span>
                        <strong>${count}</strong>
                    </div>
                `;
            });
        }

        container.innerHTML = html;

    } catch (err) {
        console.error('Failed to load statistics:', err);
    }
}

// Export Trades
async function exportTrades() {
    try {
        const response = await fetch('/api/export');
        const data = await response.json();

        if (response.ok) {
            alert(data.message);
        } else {
            throw new Error(data.error);
        }

    } catch (err) {
        showError('Failed to export: ' + err.message);
    }
}

// Clear Form
function handleClear() {
    symbolInput.value = '';
    entryPriceInput.value = '';
    results.classList.add('hidden');
    hideError();
    currentAnalysis = null;
    selectedRating = null;
    document.getElementById('tradeNotes').value = '';
}

// Error Handling
function showError(message) {
    error.textContent = message;
    error.classList.remove('hidden');
}

function hideError() {
    error.classList.add('hidden');
}

// Utility Functions
function formatVolume(volume) {
    if (volume >= 1000000) {
        return (volume / 1000000).toFixed(2) + 'M';
    } else if (volume >= 1000) {
        return (volume / 1000).toFixed(2) + 'K';
    }
    return volume.toString();
}
