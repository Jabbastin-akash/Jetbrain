/**
 * VALORANT Scouting Tool - Frontend Application
 * Five-Layer UI Implementation for Category 2 Hackathon
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
        updateLoadingText('Fetching match data from GRID API...');

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

        updateLoadingText('Generating AI insights...');

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
 * Render the complete five-layer report
 */
function renderReport(data) {
    // Update meta info with GRID traceability
    const overview = data.layer1_report.match_overview;
    const genDate = new Date(data.generated_at).toLocaleString();
    document.getElementById('reportMeta').textContent =
        `Report: ${data.report_id} | Generated: ${genDate} | Data Source: ${data.data_source}`;

    // LAYER 1: Executive Scouting Insight (AI)
    renderLayer1ExecutiveInsight(data.executive_insight, overview);

    // LAYER 2: Coach Recommendations
    renderLayer2Recommendations(data.layer1_report.coach_recommendations, overview);

    // LAYER 3: Structured Scouting Summary
    renderLayer3StructuredSummary(data.layer1_report);

    // LAYER 4: All Detected Insights
    renderLayer4AllInsights(data.layer2_insights, overview);

    // LAYER 5: Full Raw JSON
    renderLayer5RawJSON(data);
}

/**
 * LAYER 1: Scout Assistant Chatbot
 */
function renderLayer1ExecutiveInsight(insight, overview) {
    const container = document.getElementById('chatMessages');
    const traceability = getTraceabilityText(overview);
    const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    // Clear chat history for new report
    chatHistory = [];

    if (!insight || !insight.success) {
        container.innerHTML = `
            <div class="chat-message bot">
                <div class="message-avatar"><i class="bi bi-robot"></i></div>
                <div class="message-content">
                    <div class="chat-data-source">
                        <i class="bi bi-database-fill"></i>
                        ${traceability}
                    </div>
                    <div class="message-text">
                        I've loaded the GRID data for <strong>${overview.team_b_name}</strong>. 
                        I couldn't generate an AI analysis at the moment, but feel free to ask me questions about their stats, maps, agents, or players!
                    </div>
                    <div class="message-time">
                        <i class="bi bi-clock"></i> ${currentTime}
                    </div>
                </div>
            </div>
        `;
        return;
    }

    const generatedTime = new Date(insight.generated_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    // Store initial exchange in chat history
    chatHistory.push({
        role: 'user',
        content: `Analyze ${overview.team_b_name} and give me a strategic breakdown.`
    });
    chatHistory.push({
        role: 'assistant',
        content: insight.insight
    });

    const html = `
        <!-- Welcome Message -->
        <div class="chat-message bot">
            <div class="message-avatar"><i class="bi bi-robot"></i></div>
            <div class="message-content">
                <div class="chat-data-source">
                    <i class="bi bi-database-fill"></i>
                    ${traceability}
                </div>
                <div class="message-text">
                    👋 Hey Coach! I've analyzed <strong>${overview.team_b_name}</strong> using GRID data. Here's my strategic breakdown:
                </div>
                <div class="message-time">
                    <i class="bi bi-clock"></i> ${generatedTime}
                </div>
            </div>
        </div>

        <!-- Main Analysis Message -->
        <div class="chat-message bot">
            <div class="message-avatar"><i class="bi bi-robot"></i></div>
            <div class="message-content">
                <div class="message-text">
                    ${insight.insight}
                </div>
                <div class="message-time">
                    <i class="bi bi-cpu"></i> ${insight.model} &nbsp;•&nbsp; <i class="bi bi-clock"></i> ${generatedTime}
                </div>
            </div>
        </div>

        <!-- Follow-up prompt -->
        <div class="chat-message bot">
            <div class="message-avatar"><i class="bi bi-robot"></i></div>
            <div class="message-content">
                <div class="message-text">
                    💡 <strong>Ask me anything!</strong> For example:
                    <ul style="margin: 0.5rem 0 0 1rem; padding: 0;">
                        <li>What maps should we ban?</li>
                        <li>How do they perform on pistol rounds?</li>
                        <li>Who should we focus on shutting down?</li>
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

/**
 * Handle chat input keypress (Enter to send)
 */
function handleChatKeypress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

/**
 * Ask a predefined question
 */
function askQuestion(question) {
    document.getElementById('chatInput').value = question;
    sendChatMessage();
}

/**
 * Send chat message to AI
 */
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message || !currentReport) return;

    // Clear input
    input.value = '';

    // Add user message to chat
    addChatMessage('user', message);

    // Show typing indicator
    showTypingIndicator();

    try {
        // Send to API
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: message,
                report_data: currentReport,
                chat_history: chatHistory.slice(-6) // Last 3 exchanges for context
            })
        });

        // Hide typing indicator
        hideTypingIndicator();

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        // Add bot response
        addChatMessage('bot', data.answer, data.model);

        // Update chat history
        chatHistory.push({ role: 'user', content: message });
        chatHistory.push({ role: 'assistant', content: data.answer });

    } catch (error) {
        hideTypingIndicator();
        console.error('Chat error:', error);
        addChatMessage('bot', "I'm having trouble processing that question. Try asking about maps, agents, players, or strategies based on the GRID data.", 'error');
    }
}

/**
 * Add a message to the chat container
 */
function addChatMessage(role, content, model = null) {
    const container = document.getElementById('chatMessages');
    const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;

    if (role === 'user') {
        messageDiv.innerHTML = `
            <div class="message-avatar"><i class="bi bi-person-fill"></i></div>
            <div class="message-content">
                <div class="message-text">${escapeHtml(content)}</div>
                <div class="message-time">
                    <i class="bi bi-clock"></i> ${time}
                </div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-avatar"><i class="bi bi-robot"></i></div>
            <div class="message-content">
                <div class="message-text">${content}</div>
                <div class="message-time">
                    ${model && model !== 'error' ? `<i class="bi bi-cpu"></i> ${model} &nbsp;•&nbsp;` : ''}
                    <i class="bi bi-clock"></i> ${time}
                </div>
            </div>
        `;
    }

    container.appendChild(messageDiv);

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const indicator = document.createElement('div');
    indicator.id = 'typingIndicator';
    indicator.className = 'chat-message bot';
    indicator.innerHTML = `
        <div class="message-avatar"><i class="bi bi-robot"></i></div>
        <div class="message-content">
            <div class="chat-typing">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
                <span>Analyzing GRID data...</span>
            </div>
        </div>
    `;
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Scroll to a specific section
 */
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * LAYER 2: Coach Recommendations (Actionable)
 */
function renderLayer2Recommendations(recommendations, overview) {
    const container = document.getElementById('recommendationsContent');
    const traceability = getTraceabilityText(overview);

    const typeIcons = {
        'map_pick': 'bi-map-fill',
        'map_ban': 'bi-x-circle-fill',
        'agent_strategy': 'bi-person-fill',
        'tactical': 'bi-crosshair',
        'player_focus': 'bi-person-bounding-box'
    };

    let html = `
        <div class="grid-traceability full-width">
            <i class="bi bi-database-check-fill me-2"></i>
            ${traceability}
        </div>
    `;

    if (!recommendations || recommendations.length === 0) {
        html += `
            <div class="no-data-card">
                <i class="bi bi-info-circle"></i>
                <p>No specific recommendations available. More match data needed.</p>
            </div>
        `;
    } else {
        recommendations.forEach((rec, index) => {
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
    }

    container.innerHTML = html;
}

/**
 * LAYER 3: Structured Scouting Summary
 */
function renderLayer3StructuredSummary(report) {
    const overview = report.match_overview;
    const snapshot = report.opponent_snapshot;
    const traceability = getTraceabilityText(overview);

    // Render Team & Map section
    renderTeamMapContent(overview, snapshot, traceability);

    // Render Agents & Players section
    renderAgentPlayerContent(snapshot, traceability);

    // Render Strengths
    renderStrengths(report.key_strengths, traceability);

    // Render Weaknesses
    renderWeaknesses(report.exploitable_weaknesses, traceability);
}

function renderTeamMapContent(overview, snapshot, traceability) {
    const container = document.getElementById('teamMapContent');

    // Build form badges
    const formBadges = overview.opponent_recent_form.map(r =>
        `<span class="form-badge ${r === 'W' ? 'win' : 'loss'}">${r}</span>`
    ).join(' ');

    const html = `
        <div class="grid-traceability">
            <i class="bi bi-database-check-fill me-2"></i>
            ${traceability}
        </div>

        <!-- Team Overview Table -->
        <div class="stat-section">
            <div class="stat-title">Team Overview</div>
            <table class="data-table">
                <tr>
                    <td class="label">Your Team</td>
                    <td class="value">${overview.team_a_name}</td>
                </tr>
                <tr>
                    <td class="label">Opponent</td>
                    <td class="value highlight">${overview.team_b_name}</td>
                </tr>
                <tr>
                    <td class="label">Matches Analyzed</td>
                    <td class="value">${overview.matches_analyzed_team_b}</td>
                </tr>
                <tr>
                    <td class="label">Games Analyzed</td>
                    <td class="value">${overview.games_analyzed || 'N/A'}</td>
                </tr>
                <tr>
                    <td class="label">Analysis Window</td>
                    <td class="value">${overview.analysis_time_window_days} days</td>
                </tr>
                <tr>
                    <td class="label">Opponent Win Rate</td>
                    <td class="value ${overview.opponent_overall_win_rate >= 50 ? 'negative' : 'positive'}">
                        ${overview.opponent_overall_win_rate.toFixed(1)}%
                    </td>
                </tr>
                <tr>
                    <td class="label">Recent Form</td>
                    <td class="value">${formBadges}</td>
                </tr>
            </table>
        </div>

        <!-- Map Performance Table -->
        <div class="stat-section">
            <div class="stat-title">Map Performance</div>
            <table class="data-table full-width">
                <thead>
                    <tr>
                        <th>Map</th>
                        <th>Win Rate</th>
                        <th>Record</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${snapshot.best_maps.map(m => `
                        <tr class="best-map">
                            <td>${m.map}</td>
                            <td class="negative">${m.win_rate}%</td>
                            <td>${m.record}</td>
                            <td><span class="status-badge danger">Strong</span></td>
                        </tr>
                    `).join('')}
                    ${snapshot.worst_maps.map(m => `
                        <tr class="worst-map">
                            <td>${m.map}</td>
                            <td class="positive">${m.win_rate}%</td>
                            <td>${m.record}</td>
                            <td><span class="status-badge success">Weak</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

function renderAgentPlayerContent(snapshot, traceability) {
    const container = document.getElementById('agentPlayerContent');

    const html = `
        <div class="grid-traceability">
            <i class="bi bi-database-check-fill me-2"></i>
            ${traceability}
        </div>

        <!-- Top Agents Table -->
        <div class="stat-section">
            <div class="stat-title">Top Agents</div>
            <table class="data-table full-width">
                <thead>
                    <tr>
                        <th>Agent</th>
                        <th>Pick Rate</th>
                        <th>Win Rate</th>
                    </tr>
                </thead>
                <tbody>
                    ${snapshot.most_played_agents.map(a => `
                        <tr>
                            <td>${a.agent}</td>
                            <td>${a.pick_rate}%</td>
                            <td class="${a.win_rate >= 50 ? 'negative' : 'positive'}">${a.win_rate || 'N/A'}%</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>

        <!-- Player Stats Table -->
        <div class="stat-section">
            <div class="stat-title">Player Statistics</div>
            <table class="data-table full-width">
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>ACS</th>
                        <th>K/D</th>
                        <th>Role</th>
                    </tr>
                </thead>
                <tbody>
                    ${snapshot.star_players.map(p => `
                        <tr>
                            <td class="player-name">${p.name}</td>
                            <td>${p.avg_acs.toFixed(0)}</td>
                            <td class="${p.kd_ratio >= 1.0 ? 'negative' : 'positive'}">${p.kd_ratio.toFixed(2)}</td>
                            <td><span class="role-badge">${p.role || 'Flex'}</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

function renderStrengths(strengths, traceability) {
    const container = document.getElementById('strengthsContent');

    let html = `
        <div class="grid-traceability">
            <i class="bi bi-database-check-fill me-2"></i>
            ${traceability}
        </div>
    `;

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

function renderWeaknesses(weaknesses, traceability) {
    const container = document.getElementById('weaknessesContent');

    let html = `
        <div class="grid-traceability">
            <i class="bi bi-database-check-fill me-2"></i>
            ${traceability}
        </div>
    `;

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
 * LAYER 4: All Detected Insights (GRID-backed)
 */
function renderLayer4AllInsights(insights, overview) {
    const container = document.getElementById('allInsightsContent');
    const traceability = getTraceabilityText(overview);

    let html = `
        <div class="grid-traceability">
            <i class="bi bi-database-check-fill me-2"></i>
            ${traceability}
        </div>
    `;

    if (!insights || !insights.success) {
        html += `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle me-2"></i>
                AI-generated insights unavailable. Check Gemini API configuration.
            </div>
        `;
    } else {
        // Convert markdown to HTML
        const insightHtml = marked.parse(insights.insights);

        html += `
            <div class="ai-insights-full">
                ${insightHtml}
            </div>
            <div class="insight-footer">
                <span><i class="bi bi-robot me-1"></i> Model: ${insights.model}</span>
                <span><i class="bi bi-clock me-1"></i> Generated: ${new Date(insights.generated_at).toLocaleString()}</span>
            </div>
        `;
    }

    container.innerHTML = html;
}

/**
 * LAYER 5: Full Raw JSON Output
 */
function renderLayer5RawJSON(data) {
    const container = document.getElementById('jsonPre');
    container.textContent = JSON.stringify(data, null, 2);
}

/**
 * Toggle JSON visibility
 */
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

/**
 * Download JSON file
 */
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

/**
 * Generate GRID traceability text
 */
function getTraceabilityText(overview) {
    return `Analysis based on ${overview.matches_analyzed_team_b} professional matches and ${overview.games_analyzed || 'multiple'} games from GRID Esports API over the last ${overview.analysis_time_window_days} days.`;
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
