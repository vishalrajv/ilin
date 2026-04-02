/* ILIN User Chat Interface */

requireAuth();

let currentTopicId = null;
let currentSessionId = null;

// Navigation
document.querySelectorAll('.sidebar-nav a[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.sidebar-nav a').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        const section = link.dataset.section;
        document.getElementById('chat-topics-section').classList.toggle('hidden', section !== 'topics');
        document.getElementById('chat-area-section').classList.toggle('hidden', section !== 'topics');
        document.getElementById('history-section').classList.toggle('hidden', section !== 'history');
        if (section === 'history') loadHistory();
    });
});

// Load available topics
async function loadChatTopics() {
    const resp = await apiCall("/api/topics");
    const topics = await resp.json();
    const grid = document.getElementById('chat-topics-grid');
    if (topics.length === 0) {
        grid.innerHTML = '<p class="text-muted">No topics available.</p>';
        return;
    }
    grid.innerHTML = topics.map(t => `
        <div class="card topic-card" onclick="openTopic(${t.id}, '${t.name.replace(/'/g, "\\'")}')">
            <h3>${t.name}</h3>
            <p>${t.description || 'No description'}</p>
            <div class="topic-meta">
                <span>${t.document_count} documents</span>
            </div>
        </div>
    `).join('');
}

function openTopic(topicId, topicName) {
    currentTopicId = topicId;
    currentSessionId = null;
    document.getElementById('chat-topic-name').textContent = topicName;
    document.getElementById('chat-messages').innerHTML = '';
    document.getElementById('chat-topics-section').classList.add('hidden');
    document.getElementById('chat-area-section').classList.remove('hidden');
}

function backToTopics() {
    document.getElementById('chat-topics-section').classList.remove('hidden');
    document.getElementById('chat-area-section').classList.add('hidden');
}

// Send message with SSE streaming
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    appendMessage('user', message);

    const messagesEl = document.getElementById('chat-messages');
    const assistantEl = appendMessage('assistant', '');
    const contentEl = assistantEl.querySelector('.message-content');

    const url = `/api/chat?topic_id=${currentTopicId}&message=${encodeURIComponent(message)}${currentSessionId ? `&session_id=${currentSessionId}` : ''}`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getToken()}` },
        });
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.content) {
                            contentEl.textContent += parsed.content;
                            messagesEl.scrollTop = messagesEl.scrollHeight;
                        }
                        if (parsed.done && parsed.sources) {
                            renderSources(assistantEl, parsed.sources);
                        }
                        if (parsed.error) {
                            contentEl.textContent += `\n[Error: ${parsed.error}]`;
                        }
                    } catch (e) {}
                }
            }
        }
    } catch (err) {
        contentEl.textContent = `Error: ${err.message}`;
    }
}

function appendMessage(role, content) {
    const messagesEl = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.innerHTML = `
        <div class="message-bubble">
            <div class="message-content">${content}</div>
        </div>
    `;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
}

function renderSources(messageEl, sources) {
    if (!sources.length) return;
    const sourcesDiv = document.createElement('div');
    sourcesDiv.className = 'sources';
    sourcesDiv.innerHTML = `
        <details>
            <summary>${sources.length} source(s)</summary>
            ${sources.map(s => `
                <div class="source-item">
                    <strong>${s.source_file}${s.page_number ? ` (p.${s.page_number})` : ''}</strong>
                    <p>${s.text}</p>
                </div>
            `).join('')}
        </details>
    `;
    messageEl.querySelector('.message-bubble').appendChild(sourcesDiv);
}

// Chat history
async function loadHistory() {
    const resp = await apiCall("/api/chat/history");
    const sessions = await resp.json();
    const list = document.getElementById('history-list');
    if (sessions.length === 0) {
        list.innerHTML = '<p class="text-muted">No chat history.</p>';
        return;
    }
    list.innerHTML = sessions.map(s => `
        <div class="card mb-2" style="cursor: pointer;" onclick="loadSession(${s.id})">
            <div class="flex-between">
                <div>
                    <strong>${s.topic_name}</strong>
                    <p class="text-muted" style="font-size: 12px;">${s.message_count} messages - ${new Date(s.updated_at).toLocaleString()}</p>
                </div>
                <button class="btn btn-outline" onclick="event.stopPropagation(); exportSession(${s.id})" style="padding: 6px 12px; font-size: 12px;">Export</button>
            </div>
        </div>
    `).join('');
}

async function loadSession(sessionId) {
    const resp = await apiCall(`/api/chat/history/${sessionId}`);
    const messages = await resp.json();
    document.getElementById('chat-topics-section').classList.add('hidden');
    document.getElementById('chat-area-section').classList.remove('hidden');
    document.getElementById('chat-messages').innerHTML = '';
    currentSessionId = sessionId;

    for (const m of messages) {
        const el = appendMessage(m.role, m.content);
        if (m.sources && m.sources.length) {
            renderSources(el, m.sources);
        }
    }
}

async function exportSession(sessionId) {
    const resp = await apiCall(`/api/chat/history/${sessionId}/export?format=txt`);
    const data = await resp.json();
    const blob = new Blob([data.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-session-${sessionId}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// Enter to send
document.getElementById('chat-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Init
loadChatTopics();
