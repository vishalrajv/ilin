/* ILIN Admin Dashboard */

requireAuth();
if (!isAdmin()) {
    window.location.href = "/chat";
}

let currentTopicId = null;
let allUsers = [];

// Navigation
document.querySelectorAll('.sidebar-nav a[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.sidebar-nav a').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        const section = link.dataset.section;
        document.getElementById('topics-section').classList.toggle('hidden', section !== 'topics');
        document.getElementById('users-section').classList.toggle('hidden', section !== 'users');
        if (section === 'users') loadUsers();
    });
});

// Load topics
async function loadTopics() {
    const resp = await apiCall("/api/topics");
    const topics = await resp.json();
    const grid = document.getElementById('topics-grid');
    if (topics.length === 0) {
        grid.innerHTML = '<p class="text-muted">No topics yet. Create one to get started.</p>';
        return;
    }
    grid.innerHTML = topics.map(t => `
        <div class="card topic-card" data-id="${t.id}">
            <h3>${t.name}</h3>
            <p>${t.description || 'No description'}</p>
            <div class="topic-meta">
                <span>${t.document_count} documents</span>
                <span>${t.user_count} users</span>
            </div>
            <div class="mt-2 flex gap-2">
                <button class="btn btn-outline" onclick="showUpload(${t.id})" style="padding: 6px 12px; font-size: 12px;">Upload</button>
                <button class="btn btn-outline" onclick="showAssign(${t.id})" style="padding: 6px 12px; font-size: 12px;">Assign</button>
                <button class="btn btn-danger" onclick="deleteTopic(${t.id})" style="padding: 6px 12px; font-size: 12px;">Delete</button>
            </div>
        </div>
    `).join('');
}

// Create topic
function showCreateTopic() {
    document.getElementById('modal-title').textContent = 'Create Topic';
    document.getElementById('topic-form').dataset.editId = '';
    document.getElementById('topic-name').value = '';
    document.getElementById('topic-desc').value = '';
    document.getElementById('topic-modal').classList.remove('hidden');
}

document.getElementById('topic-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('topic-name').value;
    const description = document.getElementById('topic-desc').value;
    const resp = await apiCall(`/api/topics?name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}`, { method: 'POST' });
    if (resp.ok) {
        closeModal('topic-modal');
        loadTopics();
    }
});

// Delete topic
async function deleteTopic(id) {
    if (!confirm('Delete this topic and all its documents?')) return;
    const resp = await apiCall(`/api/topics/${id}`, { method: 'DELETE' });
    if (resp.ok) loadTopics();
}

// Upload documents
function showUpload(topicId) {
    currentTopicId = topicId;
    document.getElementById('upload-files').value = '';
    document.getElementById('upload-progress').innerHTML = '';
    document.getElementById('upload-modal').classList.remove('hidden');
}

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const files = document.getElementById('upload-files').files;
    const progress = document.getElementById('upload-progress');
    progress.innerHTML = '';
    for (const file of files) {
        progress.innerHTML += `<p>Uploading: ${file.name}...</p>`;
        const formData = new FormData();
        formData.append('file', file);
        const resp = await fetch(`/api/topics/${currentTopicId}/documents`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getToken()}` },
            body: formData,
        });
        const result = await resp.json();
        if (resp.ok) {
            progress.innerHTML += `<p style="color: var(--success)">✓ ${file.name} - ${result.status}</p>`;
        } else {
            progress.innerHTML += `<p style="color: var(--danger)">✗ ${file.name} - ${result.detail}</p>`;
        }
    }
});

// Assign users
async function showAssign(topicId) {
    currentTopicId = topicId;
    const resp = await apiCall("/api/users");
    allUsers = await resp.json();
    const list = document.getElementById('assign-users-list');
    list.innerHTML = allUsers.map(u => `
        <label style="display: block; padding: 8px 0;">
            <input type="checkbox" value="${u.id}"> ${u.username} (${u.role})
        </label>
    `).join('');
    document.getElementById('assign-modal').classList.remove('hidden');
}

async function saveAssignments() {
    const checked = document.querySelectorAll('#assign-users-list input:checked');
    const userIds = Array.from(checked).map(cb => parseInt(cb.value));
    await apiCall(`/api/topics/${currentTopicId}/assign`, {
        method: 'POST',
        body: JSON.stringify({ user_ids: userIds }),
    });
    closeModal('assign-modal');
    loadTopics();
}

// Users
async function loadUsers() {
    const resp = await apiCall("/api/users");
    const users = await resp.json();
    const list = document.getElementById('users-list');
    list.innerHTML = `<table style="width:100%; border-collapse: collapse;">
        <tr style="background: var(--bg-primary);"><th style="padding: 10px; text-align: left;">Username</th><th style="padding: 10px; text-align: left;">Role</th><th style="padding: 10px; text-align: left;">Created</th></tr>
        ${users.map(u => `<tr style="border-bottom: 1px solid #e1e5eb;"><td style="padding: 10px;">${u.username}</td><td style="padding: 10px;">${u.role}</td><td style="padding: 10px;">${u.created_at || '-'}</td></tr>`).join('')}
    </table>`;
}

function showCreateUser() {
    document.getElementById('user-form').reset();
    document.getElementById('user-modal').classList.remove('hidden');
}

document.getElementById('user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resp = await apiCall("/api/users", {
        method: 'POST',
        body: JSON.stringify({
            username: document.getElementById('user-username').value,
            password: document.getElementById('user-password').value,
            role: document.getElementById('user-role').value,
        }),
    });
    if (resp.ok) {
        closeModal('user-modal');
        loadUsers();
    }
});

// Modal helpers
function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
}

// Init
loadTopics();
