/**
 * VALORANT Scouting Tool - Frontend Application
 * Simplified, elegant frontend without explicit layer labels or data-source chatter
 */

// API Base URL
const API_BASE = '';

// Store current report data for download and chat
let currentReport = null;
let jsonExpanded = false;
let chatHistory = [];

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
        updateLoadingText('Fetching matchup data...');

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

        updateLoadingText('Preparing insights...');

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
 * Render the complete report (simplified)
 */
function renderReport(data) {
    // Minimal meta info
    const genDate = new Date(data.generated_at).toLocaleString();
    document.getElementById('reportMeta').textContent = `Report ${data.report_id} • ${genDate}`;

    // Executive insight + chat area
    renderExecutiveChat(data.executive_insight, data.layer1_report.match_overview);

    // Actionable recommendations
    renderRecommendations(data.layer1_report.coach_recommendations);

    // Structured summary
    renderSummary(data.layer1_report);

    // All insights
    renderAllInsights(data.layer2_insights);

    // Raw JSON
    renderRawJSON(data);
}

/**
 * Executive Chatbot (clean, no data-source chatter)
 */
function renderExecutiveChat(insight, overview) {
    const container = document.getElementById('chatMessages');

    // Clear chat history for new report
    chatHistory = [];

    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (!insight || !insight.success) {
        container.innerHTML = `
            <div class="chat-message bot">
                <div class="message-avatar"><i class="bi bi-robot"></i></div>
                <div class="message-content">
                    <div class="message-text">
                        I've loaded the opponent profile for <strong>${overview.team_b_name}</strong>. Ask me about maps, agents, players, or strategy.
                    </div>
                    <div class="message-time">
                        <i class="bi bi-clock"></i> ${currentTime}
                    </div>
                </div>
            </div>
        `;
        return;
    }

    const generatedTime = new Date(insight.generated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Store initial exchange in chat history
    chatHistory.push({
        role: 'user',
        content: `Give me a strategic breakdown of ${overview.team_b_name}.`
    });
    chatHistory.push({
        role: 'assistant',
        content: insight.insight
    });

    const html = `
        <div class="chat-message bot">
            <div class="message-avatar"><i class="bi bi-robot"></i></div>
            <div class="message-content">
                <div class="message-text">
                    ${insight.insight}
                </div>
                <div class="message-time">
                    <i class="bi bi-clock"></i> ${generatedTime}
                </div>
            </div>
        </div>
        <div class="chat-message bot">
            <div class="message-avatar"><i class="bi bi-robot"></i></div>
            <div class="message-content">
                <div class="message-text">
                    Ask follow-ups like:
                    <ul style="margin: 0.5rem 0 0 1rem; padding: 0;">
                        <li>Which maps favor them?</li>
                        <li>Any agent dependencies?</li>
                        <li>Who is their primary carry?</li>
                    </ul>
                </div>
                <div class="message-time">
                    <i class="bi bi-clock"></i> ${generatedTime}
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function handleChatKeypress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

function askQuestion(question) {
    document.getElementById('chatInput').value = question;
    sendChatMessage();
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message || !currentReport) return;

    input.value = '';

    addChatMessage('user', message);
    showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: message,
                report_data: currentReport,
                chat_history: chatHistory.slice(-6)
            })
        });

        hideTypingIndicator();

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        addChatMessage('bot', data.answer);
        chatHistory.push({ role: 'user', content: message });
        chatHistory.push({ role: 'assistant', content: data.answer });
    } catch (error) {
        hideTypingIndicator();
        console.error('Chat error:', error);
        addChatMessage('bot', "I'm having trouble with that. Try asking about maps, agents, players, or strategies.", 'error');
    }
}

function addChatMessage(role, content, model = null) {
    const container = document.getElementById('chatMessages');
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;

    if (role === 'user') {
        messageDiv.innerHTML = `
            <div class="message-avatar"><i class="bi bi-person-fill"></i></div>
            <div class="message-content">
                <div class="message-text">${escapeHtml(content)}</div>
                <div class="message-time"><i class="bi bi-clock"></i> ${time}</div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-avatar"><i class="bi bi-robot"></i></div>
            <div class="message-content">
                <div class="message-text">${content}</div>
                <div class="message-time"><i class="bi bi-clock"></i> ${time}</div>
            </div>
        `;
    }

    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const indicator = document.createElement('div');
    indicator.id = 'typingIndicator';
    indicator.className = 'chat-message bot';
    indicator.innerHTML = `
        <div class="message-avatar"><i class="bi bi-robot"></i></div>
        <div class="message-content">
            <div class="chat-typing">
                <div class="typing-dots"><span></span><span></span><span></span></div>
                <span>Analyzing...</span>
            </div>
        </div>
    `;
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Recommendations (cleaned)
 */
function renderRecommendations(recommendations) {
    const container = document.getElementById('recommendationsContent');

    const typeIcons = {
        'map_pick': 'bi-map-fill',
        'map_ban': 'bi-x-circle-fill',
        'agent_strategy': 'bi-person-fill',
        'tactical': 'bi-crosshair',
        'player_focus': 'bi-person-bounding-box'
    };

    let html = '';

    if (!recommendations || recommendations.length === 0) {
        html += `
            <div class="no-data-card">
                <i class="bi bi-info-circle"></i>
                <p>No specific recommendations available. More match data needed.</p>
            </div>
        `;
    } else {
        recommendations.forEach(rec => {
            const icon = typeIcons[rec.type] || 'bi-lightning-fill';
            html += `
                <div class="rec-card">
                    <div class="rec-header">
                        <span class="rec-action"><i class="bi ${icon}"></i> ${rec.action}</span>
                        <span class="rec-confidence ${rec.confidence}">${rec.confidence}</span>
                    </div>
                    <div class="rec-body">
                        <p class="rec-reasoning">${rec.reasoning}</p>
                        <p class="rec-impact"><strong>Expected Impact:</strong> ${rec.expected_impact}</p>
                        <div class="rec-data"><strong>Source:</strong> ${rec.grid_data}</div>
                    </div>
                </div>
            `;
        });
    }

    container.innerHTML = html;
}

/**
 * Structured Summary (cleaned)
 */
function renderSummary(report) {
    const overview = report.match_overview;
    const snapshot = report.opponent_snapshot;

    renderTeamMap(overview, snapshot);
    renderAgentPlayers(snapshot);
    renderStrengths(report.key_strengths);
    renderWeaknesses(report.exploitable_weaknesses);
}

function renderTeamMap(overview, snapshot) {
    const container = document.getElementById('teamMapContent');

    const formBadges = overview.opponent_recent_form.map(r =>
        `<span class="form-badge ${r === 'W' ? 'win' : 'loss'}">${r}</span>`
    ).join(' ');

    const html = `
        <div class="stat-section">
            <table class="data-table">
                <tr><td class="label">Your Team</td><td class="value">${overview.team_a_name}</td></tr>
                <tr><td class="label">Opponent</td><td class="value highlight">${overview.team_b_name}</td></tr>
                <tr><td class="label">Matches Analyzed</td><td class="value">${overview.matches_analyzed_team_b}</td></tr>
                <tr><td class="label">Games Analyzed</td><td class="value">${overview.games_analyzed || 'N/A'}</td></tr>
                <tr><td class="label">Time Window</td><td class="value">${overview.analysis_time_window_days} days</td></tr>
                <tr>
                    <td class="label">Opponent Win Rate</td>
                    <td class="value ${overview.opponent_overall_win_rate >= 50 ? 'negative' : 'positive'}">${overview.opponent_overall_win_rate.toFixed(1)}%</td>
                </tr>
                <tr><td class="label">Recent Form</td><td class="value">${formBadges}</td></tr>
            </table>
        </div>
        <div class="stat-section">
            <table class="data-table full-width">
                <thead>
                    <tr><th>Map</th><th>Win Rate</th><th>Record</th><th>Status</th></tr>
                </thead>
                <tbody>
                    ${snapshot.best_maps.map(m => `
                        <tr class="best-map"><td>${m.map}</td><td class="negative">${m.win_rate}%</td><td>${m.record}</td><td><span class="status-badge danger">Strong</span></td></tr>
                    `).join('')}
                    ${snapshot.worst_maps.map(m => `
                        <tr class="worst-map"><td>${m.map}</td><td class="positive">${m.win_rate}%</td><td>${m.record}</td><td><span class="status-badge success">Weak</span></td></tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

function renderAgentPlayers(snapshot) {
    const container = document.getElementById('agentPlayerContent');

    const html = `
        <div class="stat-section">
            <table class="data-table full-width">
                <thead>
                    <tr><th>Agent</th><th>Pick Rate</th><th>Win Rate</th></tr>
                </thead>
                <tbody>
                    ${snapshot.most_played_agents.map(a => `
                        <tr><td>${a.agent}</td><td>${a.pick_rate}%</td><td class="${a.win_rate >= 50 ? 'negative' : 'positive'}">${a.win_rate || 'N/A'}%</td></tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        <div class="stat-section">
            <table class="data-table full-width">
                <thead>
                    <tr><th>Player</th><th>ACS</th><th>K/D</th><th>Role</th></tr>
                </thead>
                <tbody>
                    ${snapshot.star_players.map(p => `
                        <tr><td class="player-name">${p.name}</td><td>${p.avg_acs.toFixed(0)}</td><td class="${p.kd_ratio >= 1.0 ? 'negative' : 'positive'}">${p.kd_ratio.toFixed(2)}</td><td><span class="role-badge">${p.role || 'Flex'}</span></td></tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

function renderStrengths(strengths) {
    const container = document.getElementById('strengthsContent');

    let html = '';
    if (!strengths || strengths.length === 0) {
        html += `<div class="no-data">No specific strengths detected</div>`;
    } else {
        strengths.forEach(s => {
            html += `
                <div class="strength-item">
                    <div class="item-category">${s.category}</div>
                    <div class="item-desc">${s.description}</div>
                    <div class="item-metric"><i class="bi bi-graph-up"></i> ${s.metric}</div>
                </div>
            `;
        });
    }
    container.innerHTML = html;
}

function renderWeaknesses(weaknesses) {
    const container = document.getElementById('weaknessesContent');

    let html = '';
    if (!weaknesses || weaknesses.length === 0) {
        html += `<div class="no-data">No specific weaknesses detected</div>`;
    } else {
        weaknesses.forEach(w => {
            html += `
                <div class="weakness-item">
                    <div class="item-category">${w.category}</div>
                    <div class="item-desc">${w.description}</div>
                    <div class="item-metric"><i class="bi bi-graph-down"></i> ${w.metric}</div>
                </div>
            `;
        });
    }
    container.innerHTML = html;
}

/**
 * All insights (cleaned)
 */
function renderAllInsights(insights) {
    const container = document.getElementById('allInsightsContent');

    let html = '';
    if (!insights || !insights.success) {
        html += `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Insights unavailable right now.
            </div>
        `;
    } else {
        const insightHtml = marked.parse(insights.insights);
        html += `
            <div class="ai-insights-full">${insightHtml}</div>
            <div class="insight-footer">
                <span><i class="bi bi-clock me-1"></i> ${new Date(insights.generated_at).toLocaleString()}</span>
            </div>
        `;
    }

    container.innerHTML = html;
}

/**
 * Raw JSON (unchanged for transparency)
 */
function renderRawJSON(data) {
    const container = document.getElementById('jsonPre');
    container.textContent = JSON.stringify(data, null, 2);
}

function toggleJSON() {
    const content = document.getElementById('rawJSONContent');
    const icon = document.getElementById('jsonToggleIcon');
    const text = document.getElementById('jsonToggleText');

    jsonExpanded = !jsonExpanded;

    if (jsonExpanded) {
        content.classList.remove('collapsed');
        icon.className = 'bi bi-chevron-up';
        text.textContent = 'Collapse Raw JSON';
    } else {
        content.classList.add('collapsed');
        icon.className = 'bi bi-chevron-down';
        text.textContent = 'Expand Raw JSON';
    }
}

function downloadJSON() {
    if (!currentReport) {
        alert('No report data available');
        return;
    }

    const dataStr = JSON.stringify(currentReport, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `scouting_report_${currentReport.report_id}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

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
