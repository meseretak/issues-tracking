
const API_BASE = 'http://localhost:8000';
let currentUser = null;
let currentView = 'dashboard';
let allIssues = [];
let allProjects = [];
let allUsers = [];
let allSprints = [];
let currentIssue = null;
let charts = {};

// ── API Helper ────────────────────────────────────────────────────────────────
async function api(method, path, body = null) {
  const token = localStorage.getItem('awash_token');
  const headers = {'Content-Type': 'application/json'};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const opts = {method, headers};
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(API_BASE + path, opts);
    if (res.status === 401) {
      localStorage.clear();
      location.reload();
      return;
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({detail: 'Request failed'}));
      throw new Error(err.detail || 'Request failed');
    }
    return await res.json();
  } catch (e) {
    toast(e.message, 'error');
    throw e;
  }
}

// ── Toast Notifications ───────────────────────────────────────────────────────
function toast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.innerHTML = `<i class="fa fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i><span class="toast-msg">${msg}</span>`;
  document.getElementById('toasts').appendChild(t);
  setTimeout(() => {
    t.style.animation = 'fadeOut .3s ease forwards';
    setTimeout(() => t.remove(), 300);
  }, 3000);
}

// ── Auth ──────────────────────────────────────────────────────────────────────
async function doLogin() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const btn = document.getElementById('login-btn');
  const err = document.getElementById('login-error');
  err.style.display = 'none';
  if (!username || !password) {
    err.textContent = 'Please enter username and password';
    err.style.display = 'block';
    return;
  }
  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Signing in...';
  try {
    const form = new FormData();
    form.append('username', username);
    form.append('password', password);
    const res = await fetch(API_BASE + '/api/auth/login', {method: 'POST', body: form});
    if (!res.ok) throw new Error('Invalid credentials');
    const data = await res.json();
    localStorage.setItem('awash_token', data.access_token);
    localStorage.setItem('awash_user', JSON.stringify(data.user));
    currentUser = data.user;
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('app').style.display = 'flex';
    initApp();
  } catch (e) {
    err.textContent = e.message;
    err.style.display = 'block';
    btn.disabled = false;
    btn.innerHTML = '<i class="fa fa-sign-in-alt"></i> Sign In to Awash Bank';
  }
}

function doLogout() {
  if (confirm('Are you sure you want to logout?')) {
    localStorage.clear();
    location.reload();
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
async function initApp() {
  updateUserUI();
  await Promise.all([loadProjects(), loadUsers(), loadSprints()]);
  nav('dashboard');
  loadNotifications();
  setInterval(loadNotifications, 60000);
  document.getElementById('login-password').addEventListener('keypress', e => {
    if (e.key === 'Enter') doLogin();
  });
}

function updateUserUI() {
  const initials = currentUser.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  const color = currentUser.avatar_color || '#1B1F6B';
  ['sidebar', 'topbar'].forEach(p => {
    document.getElementById(`${p}-avatar`).textContent = initials;
    document.getElementById(`${p}-avatar`).style.background = color;
    document.getElementById(`${p}-name`).textContent = currentUser.full_name;
  });
  document.getElementById('sidebar-role').textContent = currentUser.role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// ── Navigation ────────────────────────────────────────────────────────────────
function nav(page) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const navItem = document.getElementById(`nav-${page}`);
  const pageEl = document.getElementById(`page-${page}`);
  if (navItem) navItem.classList.add('active');
  if (pageEl) pageEl.classList.add('active');
  currentView = page;
  const titles = {
    dashboard: 'Dashboard', issues: 'All Issues', myissues: 'My Issues',
    kanban: 'Kanban Board', backlog: 'Backlog', projects: 'Projects',
    sprints: 'Sprints', roadmap: 'Roadmap', reports: 'Reports',
    sla: 'SLA Monitor', audit: 'Audit Log', team: 'Team',
    notifications: 'Notifications', settings: 'Settings'
  };
  document.getElementById('topbar-title').textContent = titles[page] || 'Awash Bank';
  loadPage(page);
}

async function loadPage(page) {
  const el = document.getElementById(`page-${page}`);
  if (!el) return;
  el.innerHTML = '<div style="text-align:center;padding:60px;"><div class="spinner"></div></div>';
  try {
    switch (page) {
      case 'dashboard': await renderDashboard(el); break;
      case 'issues': await renderIssues(el); break;
      case 'myissues': await renderMyIssues(el); break;
      case 'kanban': await renderKanban(el); break;
      case 'backlog': await renderBacklog(el); break;
      case 'projects': await renderProjects(el); break;
      case 'sprints': await renderSprints(el); break;
      case 'roadmap': await renderRoadmap(el); break;
      case 'reports': await renderReports(el); break;
      case 'sla': await renderSLA(el); break;
      case 'audit': await renderAudit(el); break;
      case 'team': await renderTeam(el); break;
      case 'notifications': await renderNotifications(el); break;
      case 'settings': await renderSettings(el); break;
      default: el.innerHTML = '<div class="empty-state"><i class="fa fa-construction"></i><h3>Coming Soon</h3><p>This feature is under development</p></div>';
    }
  } catch (e) {
    el.innerHTML = `<div class="empty-state"><i class="fa fa-exclamation-triangle"></i><h3>Error Loading Page</h3><p>${e.message}</p></div>`;
  }
}

// ── Data Loaders ──────────────────────────────────────────────────────────────
async function loadProjects() {
  allProjects = await api('GET', '/api/projects/');
  const sel = document.getElementById('ci-project');
  const sel2 = document.getElementById('cs-project');
  if (sel) {
    sel.innerHTML = '<option value="">Select project...</option>' + allProjects.map(p => `<option value="${p.id}">${p.key} - ${p.name}</option>`).join('');
    if (sel2) sel2.innerHTML = sel.innerHTML;
  }
}

async function loadUsers() {
  allUsers = await api('GET', '/api/users/');
  const sel = document.getElementById('ci-assignee');
  if (sel) sel.innerHTML = '<option value="">Unassigned</option>' + allUsers.filter(u => u.is_active).map(u => `<option value="${u.id}">${u.full_name} (${u.role.replace(/_/g, ' ')})</option>`).join('');
}

async function loadSprints() {
  allSprints = await api('GET', '/api/sprints/');
  const sel = document.getElementById('ci-sprint');
  if (sel) sel.innerHTML = '<option value="">No Sprint</option>' + allSprints.filter(s => s.status !== 'completed').map(s => `<option value="${s.id}">${s.name}</option>`).join('');
}

async function loadNotifications() {
  try {
    const notifs = await api('GET', '/api/notifications/?unread_only=true');
    const count = notifs.length;
    ['notif-badge', 'notif-nav-count'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.textContent = count;
        el.style.display = count > 0 ? 'flex' : 'none';
      }
    });
  } catch (e) {}
}

// ── Modals ────────────────────────────────────────────────────────────────────
function openModal(id) {
  document.getElementById(`modal-${id}`).style.display = 'flex';
}

function closeModal(id) {
  document.getElementById(`modal-${id}`).style.display = 'none';
}

function openCreateIssue() {
  openModal('create-issue');
}

async function submitCreateIssue() {
  const data = {
    title: document.getElementById('ci-title').value.trim(),
    description: document.getElementById('ci-desc').value.trim(),
    issue_type: document.getElementById('ci-type').value,
    status: document.getElementById('ci-status').value,
    priority: document.getElementById('ci-priority').value,
    project_id: parseInt(document.getElementById('ci-project').value),
    assignee_id: document.getElementById('ci-assignee').value ? parseInt(document.getElementById('ci-assignee').value) : null,
    sprint_id: document.getElementById('ci-sprint').value ? parseInt(document.getElementById('ci-sprint').value) : null,
    story_points: parseInt(document.getElementById('ci-points').value) || 0,
    due_date: document.getElementById('ci-due').value || null,
  };
  if (!data.title || !data.project_id) return toast('Title and Project are required', 'error');
  try {
    const issue = await api('POST', '/api/issues/', data);
    toast(`Issue ${issue.key} created successfully!`, 'success');
    closeModal('create-issue');
    document.getElementById('ci-title').value = '';
    document.getElementById('ci-desc').value = '';
    if (currentView === 'issues' || currentView === 'myissues' || currentView === 'backlog') loadPage(currentView);
  } catch (e) {}
}

async function openCreateProject() {
  if (!['admin', 'project_manager'].includes(currentUser.role)) return toast('Only admins and PMs can create projects', 'error');
  openModal('create-project');
}

async function submitCreateProject() {
  const data = {
    key: document.getElementById('cp-key').value.trim().toUpperCase(),
    name: document.getElementById('cp-name').value.trim(),
    description: document.getElementById('cp-desc').value.trim(),
    department: document.getElementById('cp-dept').value,
    color: document.getElementById('cp-color').value,
  };
  if (!data.key || !data.name) return toast('Key and Name are required', 'error');
  try {
    await api('POST', '/api/projects/', data);
    toast(`Project ${data.key} created!`, 'success');
    closeModal('create-project');
    await loadProjects();
    if (currentView === 'projects') loadPage('projects');
  } catch (e) {}
}

async function openCreateSprint() {
  openModal('create-sprint');
}

async function submitCreateSprint() {
  const data = {
    name: document.getElementById('cs-name').value.trim(),
    goal: document.getElementById('cs-goal').value.trim(),
    project_id: parseInt(document.getElementById('cs-project').value),
    start_date: document.getElementById('cs-start').value || null,
    end_date: document.getElementById('cs-end').value || null,
  };
  if (!data.name || !data.project_id) return toast('Name and Project are required', 'error');
  try {
    await api('POST', '/api/sprints/', data);
    toast(`Sprint created!`, 'success');
    closeModal('create-sprint');
    await loadSprints();
    if (currentView === 'sprints') loadPage('sprints');
  } catch (e) {}
}

async function openCreateUser() {
  if (currentUser.role !== 'admin') return toast('Only admins can add users', 'error');
  openModal('create-user');
}

async function submitCreateUser() {
  const data = {
    employee_id: document.getElementById('cu-empid').value.trim() || null,
    username: document.getElementById('cu-username').value.trim(),
    full_name: document.getElementById('cu-fullname').value.trim(),
    email: document.getElementById('cu-email').value.trim(),
    password: document.getElementById('cu-password').value,
    role: document.getElementById('cu-role').value,
    department: document.getElementById('cu-dept').value || null,
    branch: document.getElementById('cu-branch').value.trim(),
  };
  if (!data.username || !data.full_name || !data.email || !data.password) return toast('All required fields must be filled', 'error');
  try {
    await api('POST', '/api/auth/register', data);
    toast(`User ${data.username} created!`, 'success');
    closeModal('create-user');
    await loadUsers();
    if (currentView === 'team') loadPage('team');
  } catch (e) {}
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function fmt(date) {
  if (!date) return '-';
  const d = new Date(date);
  return d.toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'});
}

function fmtTime(date) {
  if (!date) return '-';
  const d = new Date(date);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return fmt(date);
}

function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
}

function getStatusBadge(status) {
  const icons = {backlog: 'inbox', todo: 'list', in_progress: 'spinner', in_review: 'eye', testing: 'flask', done: 'check-circle', closed: 'lock', cancelled: 'times-circle'};
  return `<span class="badge s-${status}"><i class="fa fa-${icons[status] || 'circle'}"></i> ${status.replace(/_/g, ' ')}</span>`;
}

function getPriorityBadge(priority) {
  const icons = {critical: 'exclamation-triangle', high: 'arrow-up', medium: 'minus', low: 'arrow-down'};
  return `<span class="badge p-${priority}"><i class="fa fa-${icons[priority]}"></i> ${priority}</span>`;
}

function getTypeIcon(type) {
  const icons = {bug: 'bug', feature: 'star', task: 'check-square', epic: 'bolt', story: 'bookmark', improvement: 'arrow-up', security: 'shield-alt', incident: 'fire'};
  return `<span class="type-icon t-${type}" title="${type}"><i class="fa fa-${icons[type]}"></i></span>`;
}

function getRoleBadge(role) {
  return `<span class="badge r-${role}">${role.replace(/_/g, ' ')}</span>`;
}

function getAvatar(user, size = 28) {
  if (!user) return '';
  const initials = getInitials(user.full_name || user.username);
  const color = user.avatar_color || '#1B1F6B';
  return `<div class="avatar" style="width:${size}px;height:${size}px;background:${color};font-size:${Math.floor(size / 2.8)}px;" title="${user.full_name}">${initials}</div>`;
}

function globalSearch(q) {
  if (!q || q.length < 2) return;
  console.log('Search:', q);
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
async function renderDashboard(el) {
  const stats = await api('GET', '/api/dashboard/stats');
  el.innerHTML = `
    <div class="stats-grid">
      <div class="stat-card" style="border-left-color:#1B1F6B;"><div class="stat-icon" style="background:#e8eaf6;color:#1B1F6B;"><i class="fa fa-tasks"></i></div><div><div class="stat-value">${stats.total_issues}</div><div class="stat-label">Total Issues</div></div></div>
      <div class="stat-card" style="border-left-color:#1d4ed8;"><div class="stat-icon" style="background:#dbeafe;color:#1d4ed8;"><i class="fa fa-folder-open"></i></div><div><div class="stat-value">${stats.open_issues}</div><div class="stat-label">Open Issues</div></div></div>
      <div class="stat-card" style="border-left-color:#c2410c;"><div class="stat-icon" style="background:#fff7ed;color:#c2410c;"><i class="fa fa-spinner"></i></div><div><div class="stat-value">${stats.in_progress}</div><div class="stat-label">In Progress</div></div></div>
      <div class="stat-card" style="border-left-color:#15803d;"><div class="stat-icon" style="background:#dcfce7;color:#15803d;"><i class="fa fa-check-circle"></i></div><div><div class="stat-value">${stats.resolved_today}</div><div class="stat-label">Resolved Today</div></div></div>
      <div class="stat-card" style="border-left-color:#dc2626;"><div class="stat-icon" style="background:#fee2e2;color:#dc2626;"><i class="fa fa-exclamation-triangle"></i></div><div><div class="stat-value">${stats.overdue}</div><div class="stat-label">Overdue</div></div></div>
    </div>
    ${stats.sprint_progress ? `<div class="sprint-progress-card"><div class="card-title"><i class="fa fa-running" style="color:#F5A623;"></i> Active Sprint: ${stats.sprint_progress.name}</div><div class="progress-bar"><div class="progress-fill" style="width:${stats.sprint_progress.percent}%;"></div></div><div style="display:flex;justify-content:space-between;font-size:13px;margin-top:8px;"><span>${stats.sprint_progress.done} / ${stats.sprint_progress.total} issues completed</span><span style="font-weight:700;color:#1B1F6B;">${stats.sprint_progress.percent}%</span></div></div>` : ''}
    <div class="charts-grid">
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-pie"></i> Issues by Status</div><div class="chart-wrap"><canvas id="chart-status"></canvas></div></div>
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-bar"></i> Issues by Priority</div><div class="chart-wrap"><canvas id="chart-priority"></canvas></div></div>
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-line"></i> Daily Trend</div><div class="chart-wrap"><canvas id="chart-daily"></canvas></div></div>
    </div>
    <div class="bottom-grid">
      <div class="card"><div class="card-header"><div class="card-title"><i class="fa fa-history"></i> Recent Activity</div></div><div id="activity-list"></div></div>
      <div class="card"><div class="card-header"><div class="card-title"><i class="fa fa-users"></i> Top Assignees</div></div><div id="assignee-list"></div></div>
    </div>
  `;
  renderCharts(stats);
  renderActivity(stats.recent_activity);
  renderAssignees(stats.by_assignee);
  document.getElementById('open-count').textContent = stats.open_issues;
}

function renderCharts(stats) {
  const statusLabels = Object.keys(stats.by_status).map(s => s.replace(/_/g, ' '));
  const statusData = Object.values(stats.by_status);
  const statusColors = ['#64748b', '#1d4ed8', '#c2410c', '#7c3aed', '#a16207', '#15803d', '#374151', '#dc2626'];
  if (charts.status) charts.status.destroy();
  charts.status = new Chart(document.getElementById('chart-status'), {
    type: 'doughnut',
    data: {labels: statusLabels, datasets: [{data: statusData, backgroundColor: statusColors}]},
    options: {responsive: true, maintainAspectRatio: false, plugins: {legend: {position: 'bottom'}}}
  });
  const priorityLabels = Object.keys(stats.by_priority).map(p => p.charAt(0).toUpperCase() + p.slice(1));
  const priorityData = Object.values(stats.by_priority);
  const priorityColors = ['#dc2626', '#c2410c', '#1d4ed8', '#64748b'];
  if (charts.priority) charts.priority.destroy();
  charts.priority = new Chart(document.getElementById('chart-priority'), {
    type: 'bar',
    data: {labels: priorityLabels, datasets: [{label: 'Issues', data: priorityData, backgroundColor: priorityColors}]},
    options: {responsive: true, maintainAspectRatio: false, plugins: {legend: {display: false}}}
  });
  if (stats.daily_trend && stats.daily_trend.length) {
    const dailyLabels = stats.daily_trend.map(d => d.date);
    const dailyData = stats.daily_trend.map(d => d.count);
    if (charts.daily) charts.daily.destroy();
    charts.daily = new Chart(document.getElementById('chart-daily'), {
      type: 'line',
      data: {labels: dailyLabels, datasets: [{label: 'Issues Created', data: dailyData, borderColor: '#1B1F6B', backgroundColor: 'rgba(27,31,107,0.1)', tension: 0.3, fill: true}]},
      options: {responsive: true, maintainAspectRatio: false, plugins: {legend: {display: false}}}
    });
  }
}

function renderActivity(activities) {
  const el = document.getElementById('activity-list');
  if (!activities || !activities.length) {
    el.innerHTML = '<div class="empty-state"><i class="fa fa-inbox"></i><p>No recent activity</p></div>';
    return;
  }
  el.innerHTML = activities.slice(0, 10).map(a => `
    <div class="activity-item">
      ${getAvatar(a.user, 30)}
      <div style="flex:1;">
        <div class="activity-text"><strong>${a.user.full_name}</strong> ${a.action.replace(/_/g, ' ')} ${a.field_changed ? `<em>${a.field_changed}</em>` : ''}</div>
        <div class="activity-time">${fmtTime(a.created_at)}</div>
      </div>
    </div>
  `).join('');
}

function renderAssignees(assignees) {
  const el = document.getElementById('assignee-list');
  if (!assignees || !assignees.length) {
    el.innerHTML = '<div class="empty-state"><i class="fa fa-users"></i><p>No data</p></div>';
    return;
  }
  el.innerHTML = assignees.slice(0, 8).map(a => `
    <div class="metric-row">
      <div style="display:flex;align-items:center;gap:10px;">
        <div class="avatar" style="background:${a.color};width:32px;height:32px;font-size:12px;">${getInitials(a.name)}</div>
        <span class="metric-label">${a.name}</span>
      </div>
      <span class="metric-value">${a.count}</span>
    </div>
  `).join('');
}

// ── Issues List ───────────────────────────────────────────────────────────────
async function renderIssues(el, filters = {}) {
  const params = new URLSearchParams(filters);
  const issues = await api('GET', `/api/issues/?${params}`);
  allIssues = issues;
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">All Issues</div><div class="page-subtitle">${issues.length} issues found</div></div>
      <button class="btn btn-orange" onclick="openCreateIssue()"><i class="fa fa-plus"></i> New Issue</button>
    </div>
    <div class="filter-bar">
      <select onchange="filterIssues()" id="filter-project"><option value="">All Projects</option>${allProjects.map(p => `<option value="${p.id}">${p.key}</option>`).join('')}</select>
      <select onchange="filterIssues()" id="filter-status"><option value="">All Status</option><option value="backlog">Backlog</option><option value="todo">To Do</option><option value="in_progress">In Progress</option><option value="in_review">In Review</option><option value="testing">Testing</option><option value="done">Done</option></select>
      <select onchange="filterIssues()" id="filter-priority"><option value="">All Priority</option><option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select>
      <select onchange="filterIssues()" id="filter-type"><option value="">All Types</option><option value="bug">Bug</option><option value="feature">Feature</option><option value="task">Task</option><option value="story">Story</option><option value="epic">Epic</option></select>
      <div class="filter-spacer"></div>
      <input type="text" placeholder="Search..." oninput="filterIssues()" id="filter-search" style="width:200px;"/>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Key</th><th>Title</th><th>Type</th><th>Status</th><th>Priority</th><th>Assignee</th><th>Sprint</th><th>Created</th></tr></thead>
        <tbody id="issues-tbody"></tbody>
      </table>
    </div>
  `;
  renderIssuesTable(issues);
}

function renderIssuesTable(issues) {
  const tbody = document.getElementById('issues-tbody');
  if (!issues || !issues.length) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:40px;color:#6b7280;">No issues found</td></tr>';
    return;
  }
  tbody.innerHTML = issues.map(i => `
    <tr onclick="openIssueDetail(${i.id})">
      <td><strong style="color:#1B1F6B;">${i.key}</strong></td>
      <td>${i.title}</td>
      <td>${getTypeIcon(i.issue_type)}</td>
      <td>${getStatusBadge(i.status)}</td>
      <td>${getPriorityBadge(i.priority)}</td>
      <td>${i.assignee ? getAvatar(i.assignee) + ' ' + i.assignee.full_name : '<span style="color:#6b7280;">Unassigned</span>'}</td>
      <td>${i.sprint ? i.sprint.name : '-'}</td>
      <td>${fmt(i.created_at)}</td>
    </tr>
  `).join('');
}

function filterIssues() {
  const project = document.getElementById('filter-project')?.value;
  const status = document.getElementById('filter-status')?.value;
  const priority = document.getElementById('filter-priority')?.value;
  const type = document.getElementById('filter-type')?.value;
  const search = document.getElementById('filter-search')?.value.toLowerCase();
  let filtered = allIssues;
  if (project) filtered = filtered.filter(i => i.project_id == project);
  if (status) filtered = filtered.filter(i => i.status === status);
  if (priority) filtered = filtered.filter(i => i.priority === priority);
  if (type) filtered = filtered.filter(i => i.issue_type === type);
  if (search) filtered = filtered.filter(i => i.title.toLowerCase().includes(search) || i.key.toLowerCase().includes(search));
  renderIssuesTable(filtered);
}

async function renderMyIssues(el) {
  const issues = await api('GET', `/api/issues/?assignee_id=${currentUser.id}`);
  allIssues = issues;
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">My Issues</div><div class="page-subtitle">${issues.length} issues assigned to you</div></div>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Key</th><th>Title</th><th>Type</th><th>Status</th><th>Priority</th><th>Project</th><th>Due Date</th></tr></thead>
        <tbody>${issues.map(i => `<tr onclick="openIssueDetail(${i.id})"><td><strong style="color:#1B1F6B;">${i.key}</strong></td><td>${i.title}</td><td>${getTypeIcon(i.issue_type)}</td><td>${getStatusBadge(i.status)}</td><td>${getPriorityBadge(i.priority)}</td><td>${i.project_key || '-'}</td><td>${fmt(i.due_date)}</td></tr>`).join('')}</tbody>
      </table>
    </div>
  `;
  document.getElementById('my-count').textContent = issues.filter(i => !['done', 'closed', 'cancelled'].includes(i.status)).length;
  document.getElementById('my-count').style.display = 'flex';
}

async function renderBacklog(el) {
  const issues = await api('GET', '/api/issues/?status=backlog');
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Backlog</div><div class="page-subtitle">${issues.length} issues in backlog</div></div>
      <button class="btn btn-orange" onclick="openCreateIssue()"><i class="fa fa-plus"></i> New Issue</button>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Key</th><th>Title</th><th>Type</th><th>Priority</th><th>Assignee</th><th>Story Points</th><th>Created</th></tr></thead>
        <tbody>${issues.map(i => `<tr onclick="openIssueDetail(${i.id})"><td><strong style="color:#1B1F6B;">${i.key}</strong></td><td>${i.title}</td><td>${getTypeIcon(i.issue_type)}</td><td>${getPriorityBadge(i.priority)}</td><td>${i.assignee ? getAvatar(i.assignee) + ' ' + i.assignee.full_name : '<span style="color:#6b7280;">Unassigned</span>'}</td><td>${i.story_points || '-'}</td><td>${fmt(i.created_at)}</td></tr>`).join('')}</tbody>
      </table>
    </div>
  `;
}

// ── Kanban Board ──────────────────────────────────────────────────────────────
async function renderKanban(el) {
  const sprints = allSprints.filter(s => s.status === 'active');
  if (!sprints.length) {
    el.innerHTML = '<div class="empty-state"><i class="fa fa-running"></i><h3>No Active Sprint</h3><p>Start a sprint to use the Kanban board</p><button class="btn btn-primary" onclick="nav(\'sprints\')">Go to Sprints</button></div>';
    return;
  }
  const sprint = sprints[0];
  const board = await api('GET', `/api/sprints/${sprint.id}/board`);
  const cols = ['backlog', 'todo', 'in_progress', 'in_review', 'testing', 'done'];
  const colNames = {backlog: 'Backlog', todo: 'To Do', in_progress: 'In Progress', in_review: 'In Review', testing: 'Testing', done: 'Done'};
  const colColors = {backlog: '#64748b', todo: '#1d4ed8', in_progress: '#c2410c', in_review: '#7c3aed', testing: '#a16207', done: '#15803d'};
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Kanban Board</div><div class="page-subtitle">${sprint.name}</div></div>
      <button class="btn btn-outline btn-sm" onclick="nav('sprints')"><i class="fa fa-cog"></i> Manage Sprints</button>
    </div>
    <div class="kanban-board">
      ${cols.map(col => `
        <div class="kanban-col">
          <div class="kanban-col-header" style="background:${colColors[col]};color:#fff;">
            <span>${colNames[col]}</span>
            <span class="kanban-col-count">${board[col]?.length || 0}</span>
          </div>
          <div class="kanban-col-body">
            ${(board[col] || []).map(i => `
              <div class="kanban-card" style="border-left-color:${colColors[col]};" onclick="openIssueDetail(${i.id})">
                <div class="kanban-card-key">${i.key}</div>
                <div class="kanban-card-title">${i.title}</div>
                <div class="kanban-card-footer">
                  <div style="display:flex;gap:4px;align-items:center;">
                    ${getTypeIcon(i.issue_type)}
                    ${getPriorityBadge(i.priority)}
                  </div>
                  <div style="display:flex;gap:6px;align-items:center;">
                    ${i.story_points ? `<span class="sp-badge">${i.story_points} SP</span>` : ''}
                    ${i.assignee ? getAvatar(i.assignee, 24) : ''}
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

// ── Projects ──────────────────────────────────────────────────────────────────
async function renderProjects(el) {
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Projects</div><div class="page-subtitle">${allProjects.length} active projects</div></div>
      <button class="btn btn-orange" onclick="openCreateProject()"><i class="fa fa-plus"></i> New Project</button>
    </div>
    <div class="projects-grid">
      ${allProjects.map(p => `
        <div class="project-card" onclick="filterProjectIssues(${p.id})">
          <div class="project-card-top" style="background:${p.color};"></div>
          <div class="project-card-body">
            <div class="project-key" style="background:${p.color};">${p.key}</div>
            <div class="project-name">${p.name}</div>
            <div class="project-dept">${p.department || 'No Department'}</div>
            <div class="project-stats">
              <div><div class="project-stat-val">${p.issue_count || 0}</div><div class="project-stat-lbl">Issues</div></div>
              <div><div class="project-stat-val">${p.member_count || 0}</div><div class="project-stat-lbl">Members</div></div>
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function filterProjectIssues(projectId) {
  nav('issues');
  setTimeout(() => {
    document.getElementById('filter-project').value = projectId;
    filterIssues();
  }, 100);
}

// ── Sprints ───────────────────────────────────────────────────────────────────
async function renderSprints(el) {
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Sprints</div><div class="page-subtitle">${allSprints.length} sprints</div></div>
      <button class="btn btn-orange" onclick="openCreateSprint()"><i class="fa fa-plus"></i> New Sprint</button>
    </div>
    <div class="sprint-list">
      ${allSprints.map(s => `
        <div class="sprint-item">
          <div class="sprint-item-header">
            <div class="sprint-name">${s.name}</div>
            <span class="badge s-${s.status}">${s.status}</span>
            <div class="sprint-dates">${fmt(s.start_date)} - ${fmt(s.end_date)}</div>
          </div>
          ${s.goal ? `<div class="sprint-goal">"${s.goal}"</div>` : ''}
          <div class="progress-bar"><div class="progress-fill" style="width:${s.done_count && s.issue_count ? Math.round(s.done_count / s.issue_count * 100) : 0}%;"></div></div>
          <div style="display:flex;justify-content:space-between;font-size:13px;margin-top:8px;">
            <span>${s.done_count || 0} / ${s.issue_count || 0} issues completed</span>
            <button class="btn btn-sm btn-outline" onclick="viewSprintBoard(${s.id})"><i class="fa fa-columns"></i> View Board</button>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function viewSprintBoard(sprintId) {
  nav('kanban');
}

// ── Team ──────────────────────────────────────────────────────────────────────
async function renderTeam(el) {
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Team</div><div class="page-subtitle">${allUsers.length} members</div></div>
      ${currentUser.role === 'admin' ? '<button class="btn btn-orange" onclick="openCreateUser()"><i class="fa fa-user-plus"></i> Add Member</button>' : ''}
    </div>
    <div class="users-grid">
      ${allUsers.map(u => `
        <div class="user-card">
          <div class="user-card-avatar" style="background:${u.avatar_color};">${getInitials(u.full_name)}</div>
          <div class="user-card-name">${u.full_name}</div>
          <div class="user-card-dept">${u.department || 'No Department'}</div>
          ${getRoleBadge(u.role)}
          <div style="margin-top:8px;font-size:12px;color:#6b7280;">${u.email}</div>
        </div>
      `).join('')}
    </div>
  `;
}

// ── Reports ───────────────────────────────────────────────────────────────────
async function renderReports(el) {
  const summary = await api('GET', '/api/dashboard/projects/summary');
  el.innerHTML = `
    <div class="page-header"><div class="page-title">Reports & Analytics</div></div>
    <div class="card">
      <div class="card-title"><i class="fa fa-folder-open"></i> Project Summary</div>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>Project</th><th>Key</th><th>Department</th><th>Total Issues</th><th>Open Issues</th><th>Health</th></tr></thead>
          <tbody>
            ${summary.map(p => {
              const health = p.open_issues === 0 ? 'Excellent' : p.open_issues < 10 ? 'Good' : p.open_issues < 30 ? 'Fair' : 'Needs Attention';
              const healthColor = p.open_issues === 0 ? '#15803d' : p.open_issues < 10 ? '#16a34a' : p.open_issues < 30 ? '#F5A623' : '#dc2626';
              return `<tr><td><strong>${p.name}</strong></td><td><span class="badge" style="background:${p.color};color:#fff;">${p.key}</span></td><td>${p.department || '-'}</td><td>${p.total_issues}</td><td>${p.open_issues}</td><td><span style="color:${healthColor};font-weight:600;">${health}</span></td></tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// ── SLA Monitor ───────────────────────────────────────────────────────────────
async function renderSLA(el) {
  const issues = await api('GET', '/api/issues/');
  const now = new Date();
  const slaIssues = issues.filter(i => i.due_date && !['done', 'closed', 'cancelled'].includes(i.status)).map(i => {
    const due = new Date(i.due_date);
    const diff = Math.floor((due - now) / (1000 * 60 * 60 * 24));
    const status = diff < 0 ? 'breach' : diff < 2 ? 'warn' : 'ok';
    return {...i, sla_days: diff, sla_status: status};
  }).sort((a, b) => a.sla_days - b.sla_days);
  el.innerHTML = `
    <div class="page-header"><div><div class="page-title">SLA Monitor</div><div class="page-subtitle">${slaIssues.length} issues with due dates</div></div></div>
    <div class="tbl-wrap">
      <table class="sla-table">
        <thead><tr><th>Key</th><th>Title</th><th>Priority</th><th>Assignee</th><th>Due Date</th><th>Days Remaining</th><th>SLA Status</th></tr></thead>
        <tbody>
          ${slaIssues.map(i => `
            <tr onclick="openIssueDetail(${i.id})">
              <td><strong style="color:#1B1F6B;">${i.key}</strong></td>
              <td>${i.title}</td>
              <td>${getPriorityBadge(i.priority)}</td>
              <td>${i.assignee ? getAvatar(i.assignee) + ' ' + i.assignee.full_name : '-'}</td>
              <td>${fmt(i.due_date)}</td>
              <td style="font-weight:600;color:${i.sla_status === 'breach' ? '#dc2626' : i.sla_status === 'warn' ? '#F5A623' : '#15803d'};">${i.sla_days} days</td>
              <td><div class="sla-bar"><div class="sla-fill sla-${i.sla_status}" style="width:${i.sla_status === 'breach' ? 100 : i.sla_status === 'warn' ? 60 : 30}%;"></div></div></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

// ── Audit Log ─────────────────────────────────────────────────────────────────
async function renderAudit(el) {
  const logs = await api('GET', '/api/dashboard/stats');
  const activities = logs.recent_activity || [];
  el.innerHTML = `
    <div class="page-header"><div class="page-title">Audit Log</div></div>
    <div class="card">
      ${activities.map(a => `
        <div class="audit-row">
          <div class="audit-time">${fmt(a.created_at)} ${new Date(a.created_at).toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'})}</div>
          <div class="audit-action"><span class="audit-user">${a.user.full_name}</span> ${a.action.replace(/_/g, ' ')} ${a.field_changed ? `<strong>${a.field_changed}</strong>` : ''} ${a.old_value && a.new_value ? `from <em>${a.old_value}</em> to <em>${a.new_value}</em>` : ''}</div>
        </div>
      `).join('')}
    </div>
  `;
}

// ── Notifications ─────────────────────────────────────────────────────────────
async function renderNotifications(el) {
  const notifs = await api('GET', '/api/notifications/');
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Notifications</div><div class="page-subtitle">${notifs.filter(n => !n.is_read).length} unread</div></div>
      ${notifs.some(n => !n.is_read) ? '<button class="btn btn-outline btn-sm" onclick="markAllRead()"><i class="fa fa-check-double"></i> Mark All Read</button>' : ''}
    </div>
    <div class="card">
      ${notifs.length ? notifs.map(n => `
        <div class="notif-item ${n.is_read ? '' : 'unread'}" onclick="markNotifRead(${n.id}, ${n.issue_id})">
          <div class="notif-dot ${n.is_read ? 'read' : ''}"></div>
          <div style="flex:1;">
            <div class="notif-msg">${n.message}</div>
            <div class="notif-time">${fmtTime(n.created_at)}</div>
          </div>
        </div>
      `).join('') : "<div class=\\"empty-state\\"><i class=\\"fa fa-bell-slash\\"></i><h3>No Notifications</h3><p>You're all caught up!</p></div>"}
    </div>
  `;
}

async function markAllRead() {
  await api('POST', '/api/notifications/mark-read');
