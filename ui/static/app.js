/**
 * VALORANT Scouting Tool - Frontend Application
 */

// API Base URL
const API_BASE = '';

// Store current report data
let currentReport = null;

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('VALORANT Scouting Tool initialized');
    await loadTeams();
});

/**
 * Load available teams from API
 */
async function loadTeams() {
    try {
        console.log('Loading teams...');
        const response = await fetch(`${API_BASE}/api/teams`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const teams = await response.json();
        console.log('Teams loaded:', teams);

        const teamASelect = document.getElementById('teamA');
        const teamBSelect = document.getElementById('teamB');

        // Clear existing options
        teamASelect.innerHTML = '<option value="">Choose team...</option>';
        teamBSelect.innerHTML = '<option value="">Choose opponent...</option>';

        // Populate dropdowns
        teams.forEach(team => {
            const displayText = `${team.name} [${team.region || 'INT'}]`;

            const optionA = document.createElement('option');
            optionA.value = team.id;
            optionA.textContent = displayText;
            teamASelect.appendChild(optionA);

            const optionB = document.createElement('option');
            optionB.value = team.id;
            optionB.textContent = displayText;
            teamBSelect.appendChild(optionB);
        });

        console.log(`Loaded ${teams.length} teams`);
    } catch (error) {
        console.error('Error loading teams:', error);
        // Show error in dropdown
        const teamASelect = document.getElementById('teamA');
        const teamBSelect = document.getElementById('teamB');
        teamASelect.innerHTML = '<option value="">Error loading teams</option>';
        teamBSelect.innerHTML = '<option value="">Error loading teams</option>';
    }
}

/**
 * Generate scouting report
 */
async function generateReport() {
    const teamAId = document.getElementById('teamA').value;
    const teamBId = document.getElementById('teamB').value;
    const timeWindow = document.getElementById('timeWindow').value;

    // Validation
    if (!teamAId || !teamBId) {
        alert('Please select both teams');
        return;
    }

    if (teamAId === teamBId) {
        alert('Please select different teams');
        return;
    }

    // Show loading
    showLoading(true);
    hideResults();

    try {
        updateLoadingText('Fetching match data...');

        const response = await fetch(`${API_BASE}/api/scout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                team_a_id: teamAId,
                team_b_id: teamBId,
                time_window_days: parseInt(timeWindow)
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        updateLoadingText('Analyzing patterns...');
        const data = await response.json();

        updateLoadingText('Generating insights...');

        // Store and render report
        currentReport = data;
        renderReport(data);

        showLoading(false);
        showResults();

    } catch (error) {
        console.error('Error generating report:', error);
        showLoading(false);
        alert('Failed to generate report. Please try again.');
    }
}

/**
 * Render the complete report
 */
function renderReport(data) {
    // Update meta info with GRID traceability
    const overview = data.layer1_report.match_overview;
    const genDate = new Date(data.generated_at).toLocaleString();
    document.getElementById('reportMeta').textContent =
        `Report: ${data.report_id} | Generated: ${genDate} | Data Source: ${data.data_source}`;

    // Render Executive Insight (Enhancement 1 - at the TOP)
    renderExecutiveInsight(data.executive_insight, overview);

    // Render Layer 1
    renderLayer1(data.layer1_report);

    // Render Layer 2
    renderLayer2(data.layer2_insights);

    // Render Recommendations (Enhancement 2)
    renderRecommendations(data.layer1_report.coach_recommendations, overview);
}

/**
 * Render Executive Insight (Enhancement 1)
 */
function renderExecutiveInsight(insight, overview) {
    const container = document.getElementById('executiveInsightContent');

    if (!insight || !insight.success) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Executive insight unavailable. Check Gemini API configuration.
            </div>
        `;
        return;
    }

    // GRID Traceability (Enhancement 3)
    const traceability = `Analysis based on ${overview.matches_analyzed_team_b} professional matches from GRID Esports API over the last ${overview.analysis_time_window_days} days.`;

    const html = `
        <div class="executive-insight-box">
            <div class="insight-text">${insight.insight}</div>
            <div class="insight-meta">
                <i class="bi bi-database-fill me-1"></i>
                ${traceability}
                <span class="ms-3">
                    <i class="bi bi-robot me-1"></i>
                    Generated by ${insight.model} | ${new Date(insight.generated_at).toLocaleTimeString()}
                </span>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

/**
 * Render Layer 1: Structured Report
 */
function renderLayer1(report) {
    const container = document.getElementById('layer1Content');
    const overview = report.match_overview;
    const snapshot = report.opponent_snapshot;

    // GRID Traceability (Enhancement 3)
    const gridTraceability = `Based on ${overview.matches_analyzed_team_b} matches from GRID Esports API (${overview.analysis_time_window_days}-day window)`;

    // Build form badges
    const formBadges = overview.opponent_recent_form.map(r =>
        `<span class="form-badge ${r === 'W' ? 'win' : 'loss'}">${r}</span>`
    ).join(' ');

    let html = `
        <!-- GRID Traceability Notice -->
        <div class="grid-traceability">
            <i class="bi bi-database-check-fill me-2"></i>
            ${gridTraceability}
        </div>
        
        <!-- Overview -->
        <div class="stat-section">
            <div class="stat-title">Match Overview</div>
            <div class="stat-row">
                <span class="stat-label">Your Team</span>
                <span class="stat-value">${overview.team_a_name}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Opponent</span>
                <span class="stat-value">${overview.team_b_name}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Matches Analyzed</span>
                <span class="stat-value">${overview.matches_analyzed_team_b}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Opponent Win Rate</span>
                <span class="stat-value ${overview.opponent_overall_win_rate >= 50 ? 'negative' : 'positive'}">
                    ${overview.opponent_overall_win_rate.toFixed(1)}%
                </span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Recent Form</span>
                <span class="stat-value">${formBadges}</span>
            </div>
        </div>

        <!-- Best Maps -->
        <div class="stat-section">
            <div class="stat-title">Opponent's Best Maps</div>
            <div class="map-list">
                ${snapshot.best_maps.map(m => `
                    <div class="map-item">
                        <span class="map-name">${m.map}</span>
                        <span class="map-stats">${m.win_rate}% WR (${m.record})</span>
                    </div>
                `).join('')}
            </div>
        </div>

        <!-- Worst Maps -->
        <div class="stat-section">
            <div class="stat-title">Opponent's Weak Maps</div>
            <div class="map-list">
                ${snapshot.worst_maps.map(m => `
                    <div class="map-item">
                        <span class="map-name">${m.map}</span>
                        <span class="map-stats">${m.win_rate}% WR (${m.record})</span>
                    </div>
                `).join('')}
            </div>
        </div>

        <!-- Key Agents -->
        <div class="stat-section">
            <div class="stat-title">Key Agents</div>
            <div class="agent-list">
                ${snapshot.most_played_agents.slice(0, 4).map(a => `
                    <div class="agent-item">
                        <span class="agent-name">${a.agent}</span>
                        <span class="agent-stats">${a.pick_rate}% pick rate</span>
                    </div>
                `).join('')}
            </div>
        </div>

        <!-- Star Players -->
        <div class="stat-section">
            <div class="stat-title">Star Players</div>
            <div class="player-list">
                ${snapshot.star_players.map(p => `
                    <div class="player-item">
                        <span class="player-name">${p.name}</span>
                        <span class="player-stats">${p.avg_acs.toFixed(0)} ACS | ${p.kd_ratio.toFixed(2)} K/D</span>
                    </div>
                `).join('')}
            </div>
        </div>

        <!-- Strengths -->
        <div class="stat-section">
            <div class="stat-title">Opponent Strengths</div>
            ${report.key_strengths.map(s => `
                <div class="strength-item">
                    <div class="item-category">${s.category}</div>
                    <div class="item-desc">${s.description}</div>
                    <div class="item-metric">${s.metric}</div>
                </div>
            `).join('')}
        </div>

        <!-- Weaknesses -->
        <div class="stat-section">
            <div class="stat-title">Exploitable Weaknesses</div>
            ${report.exploitable_weaknesses.map(w => `
                <div class="weakness-item">
                    <div class="item-category">${w.category}</div>
                    <div class="item-desc">${w.description}</div>
                    <div class="item-metric">${w.metric}</div>
                </div>
            `).join('')}
        </div>
    `;

    container.innerHTML = html;
}

/**
 * Render Layer 2: AI Insights
 */
function renderLayer2(insights) {
    const container = document.getElementById('layer2Content');

    if (!insights.success) {
        container.innerHTML = `
            <div style="padding: 1rem; background: rgba(255,70,85,0.1); border-radius: 6px;">
                <p style="margin: 0; color: var(--primary);">
                    AI insights unavailable. Check Gemini API configuration.
                </p>
            </div>
        `;
        return;
    }

    // Convert markdown to HTML
    const insightHtml = marked.parse(insights.insights);

    container.innerHTML = `
        <div class="ai-insights">
            ${insightHtml}
        </div>
        <hr>
        <div style="font-size: 0.75rem; color: var(--text-secondary);">
            Model: ${insights.model} | Generated: ${new Date(insights.generated_at).toLocaleTimeString()}
        </div>
    `;
}

/**
 * Render Coach Recommendations (Enhancement 2)
 */
function renderRecommendations(recommendations, overview) {
    const container = document.getElementById('recommendationsContent');

    // GRID Traceability (Enhancement 3)
    const gridTraceability = `Recommendations based on ${overview.matches_analyzed_team_b} matches from GRID Esports API (${overview.analysis_time_window_days}-day analysis window)`;

    const typeIcons = {
        'map_pick': 'bi-map-fill',
        'map_ban': 'bi-x-circle-fill',
        'agent_strategy': 'bi-person-fill',
        'tactical': 'bi-crosshair'
    };

    let html = `
        <!-- GRID Traceability for Recommendations -->
        <div class="grid-traceability mb-3">
            <i class="bi bi-database-check-fill me-2"></i>
            ${gridTraceability}
        </div>
    `;

    recommendations.forEach(rec => {
        const icon = typeIcons[rec.type] || 'bi-lightning-fill';

        html += `
            <div class="rec-card">
                <div class="rec-header">
                    <span class="rec-action">
                        <i class="bi ${icon}"></i>
                        ${rec.action}
                    </span>
                    <span class="rec-confidence ${rec.confidence}">${rec.confidence}</span>
                </div>
                <div class="rec-body">
                    <p class="rec-reasoning">${rec.reasoning}</p>
                    <p class="rec-impact"><strong>Expected Impact:</strong> ${rec.expected_impact}</p>
                    <div class="rec-data">
                        <i class="bi bi-database-fill"></i> <strong>GRID Data:</strong> ${rec.grid_data}
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

/**
 * UI Helper Functions
 */
function showLoading(show) {
    document.getElementById('loadingSection').classList.toggle('d-none', !show);
    document.getElementById('generateBtn').disabled = show;
}

function updateLoadingText(text) {
    document.getElementById('loadingText').textContent = text;
}

function showResults() {
    document.getElementById('resultsSection').classList.remove('d-none');
}

function hideResults() {
    document.getElementById('resultsSection').classList.add('d-none');
}

