/**
 * VALORANT Scouting Tool
 * Professional Match Preparation Frontend
 */

const API_BASE = '';

let currentReport = null;
let chatHistory = [];
let jsonExpanded = false;

/* =========================
   INIT
========================= */
document.addEventListener('DOMContentLoaded', async () => {
    await loadTeams();
});

/* =========================
   LOAD TEAMS
========================= */
async function loadTeams() {
    try {
        const res = await fetch(`${API_BASE}/api/teams`);
        const teams = await res.json();

        const teamA = document.getElementById('teamA');
        const teamB = document.getElementById('teamB');

        teamA.innerHTML = `<option value="">Choose team...</option>`;
        teamB.innerHTML = `<option value="">Choose opponent...</option>`;

        teams.forEach(t => {
            const label = `${t.name} [${t.region || 'INT'}]`;
            teamA.add(new Option(label, t.id));
            teamB.add(new Option(label, t.id));
        });
    } catch {
        document.getElementById('teamA').innerHTML = `<option>Error loading teams</option>`;
        document.getElementById('teamB').innerHTML = `<option>Error loading teams</option>`;
    }
}

/* =========================
   GENERATE REPORT
========================= */
async function generateReport() {
    const teamAEl = document.getElementById('teamA');
    const teamBEl = document.getElementById('teamB');
    const timeWindowEl = document.getElementById('timeWindow');

    const teamAId = teamAEl?.value;
    const teamBId = teamBEl?.value;
    const days = parseInt(timeWindowEl?.value || '90');

    if (!teamAId || !teamBId) return alert('Select both teams');
    if (teamAId === teamBId) return alert('Teams must be different');

    showLoading(true);
    hideResults();

    try {
        const res = await fetch(`${API_BASE}/api/scout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                team_a_id: teamAId,
                team_b_id: teamBId,
                time_window_days: days
            })
        });

        currentReport = await res.json();
        renderReport(currentReport);
        showResults();
    } catch (e) {
        console.error('Generate report failed', e);
        alert('Failed to generate report');
    } finally {
        showLoading(false);
    }
}

/* =========================
   RENDER REPORT
========================= */
function renderReport(data) {
    const core = data.layer1_report;
    const insights = data.layer2_insights;

    reportMeta.textContent =
        `Report ${data.report_id} • ${new Date(data.generated_at).toLocaleString()}`;

    renderAssistant(data.executive_insight, core.match_overview);
    renderRecommendations(core.coach_recommendations);
    renderSummary(core);
    renderInsights(insights);
    renderRawJSON(data);
}

/* =========================
   MATCH ASSISTANT
========================= */
function renderAssistant(insight, overview) {
    const box = chatMessages;
    box.innerHTML = '';
    chatHistory = [];

    const intro = insight?.success
        ? insight.insight
        : `Opponent profile loaded for ${overview.team_b_name}. Ask about maps, agents, or strategy.`;

    addChatMessage('bot', intro);

    chatHistory.push(
        { role: 'user', content: `Give me a strategic breakdown of ${overview.team_b_name}` },
        { role: 'assistant', content: intro }
    );
}

async function sendChatMessage() {
    const msg = chatInput.value.trim();
    if (!msg || !currentReport) return;

    chatInput.value = '';
    addChatMessage('user', msg);
    showTypingIndicator();

    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: msg,
                report_data: currentReport,
                chat_history: chatHistory.slice(-6)
            })
        });

        const { answer } = await res.json();
        hideTypingIndicator();
        addChatMessage('bot', answer);

        chatHistory.push(
            { role: 'user', content: msg },
            { role: 'assistant', content: answer }
        );
    } catch {
        hideTypingIndicator();
        addChatMessage('bot', 'Try asking about maps, agents, or key players.');
    }
}

function addChatMessage(role, text) {
    const msg = document.createElement('div');
    msg.className = `chat-message ${role}`;
    msg.innerHTML = `
        <div class="message-avatar">${role === 'user' ? '👤' : '🎯'}</div>
        <div class="message-content">
            <div class="message-text">${text}</div>
            <div class="message-time">${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</div>
        </div>
    `;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* =========================
   RECOMMENDATIONS
========================= */
function renderRecommendations(list) {
    const box = recommendationsContent;

    if (!list?.length) {
        box.innerHTML = `<div class="no-data-card">No strong recommendations detected yet.</div>`;
        return;
    }

    box.innerHTML = list.map(r => `
        <div class="rec-card">
            <div class="rec-header">
                <span class="rec-action">${r.action}</span>
                <span class="rec-confidence ${r.confidence}">${r.confidence}</span>
            </div>
            <div class="rec-body">
                <p>${r.reasoning}</p>
                <p><strong>Expected Impact:</strong> ${r.expected_impact}</p>
            </div>
        </div>
    `).join('');
}

/* =========================
   SUMMARY
========================= */
function renderSummary(r) {
    renderTeamMap(r.match_overview, r.opponent_snapshot);
    renderAgentPlayers(r.opponent_snapshot);
    renderStrengths(r.key_strengths);
    renderWeaknesses(r.exploitable_weaknesses);
}

/* =========================
   INSIGHTS
========================= */
function renderInsights(i) {
    allInsightsContent.innerHTML = i?.success
        ? `<div class="insights-full">${marked.parse(i.insights)}</div>`
        : `<div class="alert">Additional insights will appear as more data becomes available.</div>`;
}

/* =========================
   RAW DATA
========================= */
function renderRawJSON(data) {
    jsonPre.textContent = JSON.stringify(data, null, 2);
}

/* =========================
   UI HELPERS
========================= */
function showLoading(v) {
    loadingSection.classList.toggle('d-none', !v);
    generateBtn.disabled = v;
}
function showResults() { resultsSection.classList.remove('d-none'); }
function hideResults() { resultsSection.classList.add('d-none'); }

function toggleJSON() {
    const content = document.getElementById('rawJSONContent');
    const icon = document.getElementById('jsonToggleIcon');
    const text = document.getElementById('jsonToggleText');

    if (!content || !icon || !text) return;

    jsonExpanded = !jsonExpanded;
    if (jsonExpanded) {
        content.classList.remove('collapsed');
        icon.className = 'bi bi-chevron-up';
        text.textContent = 'Collapse Data';
    } else {
        content.classList.add('collapsed');
        icon.className = 'bi bi-chevron-down';
        text.textContent = 'Expand Data';
    }
}

function renderStrengths(strengths) {
    const container = document.getElementById('strengthsContent');
    if (!container) {
        console.warn('Strengths container not found; skipping renderStrengths');
        return;
    }

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
    if (!container) {
        console.warn('Weaknesses container not found; skipping renderWeaknesses');
        return;
    }

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
