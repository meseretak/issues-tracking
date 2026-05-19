
const API_BASE = window.location.origin;
let currentUser = null;
let currentView = 'dashboard';
let allIssues = [];
let allProjects = [];
let allUsers = [];
let allSprints = [];
let currentIssue = null;
let currentChatTeamId = 0;
let charts = {};
function can(action) {
  if (!currentUser) return false;
  const role = currentUser.role;
  if (role === 'super_admin' || role === 'admin') return true;
  
  const perms = {
    createProject: ['project_manager'],
    createUser: [],
    createIssue: ['project_manager', 'scrum_master', 'business_analyst', 'qa_engineer'],
    editAnyIssue: ['project_manager', 'scrum_master'],
    manageIntegrations: [],
    viewAudit: ['project_manager', 'scrum_master']
  };
  
  const allowed = perms[action] || [];
  return allowed.includes(role);
}


let issuesPage = 1;
const ISSUES_PER_PAGE = 10;

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
  
  const ciProj = document.getElementById('ci-project');
  if (ciProj) {
    ciProj.addEventListener('change', filterAllowedIssueTypes);
  }
}


function updateRoleBasedUI() {
  const CAN_CREATE_PROJECT = ['super_admin','admin','project_manager','qa_engineer'];
  const IS_DEV_OR_VIEWER = ['developer','viewer'].includes(currentUser.role);

  // Hide/show New Issue button based on role
  const newIssueBtns = document.querySelectorAll('[onclick="openCreateIssue()"]');
  newIssueBtns.forEach(btn => { btn.style.display = can('createIssue') ? '' : 'none'; });

  // Hide "New Project" button for developers/viewers
  document.querySelectorAll('[onclick="openCreateProject()"]').forEach(btn => {
    btn.style.display = CAN_CREATE_PROJECT.includes(currentUser.role) ? '' : 'none';
  });

  // Hide/show admin-only nav items
  const execNav = document.getElementById('nav-executive');
  if (execNav) execNav.style.display = ['super_admin','admin','project_manager','scrum_master'].includes(currentUser.role) ? '' : 'none';
  const intNav = document.getElementById('nav-integrations');
  if (intNav) intNav.style.display = can('manageIntegrations') ? '' : 'none';
  const auditNav = document.getElementById('nav-audit');
  if (auditNav) auditNav.style.display = can('viewAudit') ? '' : 'none';
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
let chatInterval = null;

function nav(page) {
  if (chatInterval) {
    clearInterval(chatInterval);
    chatInterval = null;
  }
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

  if (page === 'chat') {
    chatInterval = setInterval(async () => {
      if (currentView === 'chat') {
        await refreshChatMessagesOnly();
      }
    }, 3000);
  }
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
      case 'groups': await renderGroups(el); break;
      case 'chat': await renderChat(el); break;
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
  
  // Set defaults based on current context
  const projSel = document.getElementById('ci-project');
  const fp = document.getElementById('filter-project');
  if (projSel && fp && fp.value) {
    projSel.value = fp.value;
  }
  
  const assigneeSel = document.getElementById('ci-assignee');
  if (assigneeSel) {
    assigneeSel.value = currentUser.id;
  }
  
  const statusSel = document.getElementById('ci-status');
  if (statusSel) {
    statusSel.value = 'todo';
  }
  
  const sprintSel = document.getElementById('ci-sprint');
  const boardSprint = document.getElementById('board-sprint-filter');
  if (sprintSel && boardSprint && boardSprint.value) {
    sprintSel.value = boardSprint.value;
  }
  
  filterAllowedIssueTypes();
}

window.filterAllowedIssueTypes = function() {
  const projSel = document.getElementById('ci-project');
  const typeSel = document.getElementById('ci-type');
  if (!projSel || !typeSel) return;
  
  const projId = parseInt(projSel.value);
  const project = allProjects.find(p => p.id === projId);
  const pType = project ? (project.project_type || 'scrum') : 'scrum';
  
  const prevVal = typeSel.value;
  
  if (pType === 'task_tracking' || pType === 'business') {
    typeSel.innerHTML = `
      <option value="task">Task</option>
      <option value="subtask">Sub-task</option>
    `;
    if (prevVal === 'task' || prevVal === 'subtask') {
      typeSel.value = prevVal;
    } else {
      typeSel.value = 'task';
    }
  } else {
    typeSel.innerHTML = `
      <option value="task">Task</option>
      <option value="bug">Bug</option>
      <option value="feature">Feature</option>
      <option value="story">Story</option>
      <option value="epic">Epic</option>
    `;
    if (['task', 'bug', 'feature', 'story', 'epic'].includes(prevVal)) {
      typeSel.value = prevVal;
    } else {
      typeSel.value = 'task';
    }
  }
};

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

let cpWizardStep = 1;
let cpSelectedTemplate = 'scrum';

const TEMPLATE_SPECS = {
  scrum: {
    title: "Scrum software development",
    desc: "Use this project to manage your Agile development work. Create a backlog, organise work into sprints, check progress using reports, and more. This project includes a Scrum board, a basic Agile workflow and issue type configuration, which you can change later on.",
    types: [
      { name: "Bug", icon: "fa-bug", color: "#e11d48" },
      { name: "Task", icon: "fa-check-square", color: "#2563eb" },
      { name: "Sub-task", icon: "fa-tasks", color: "#38bdf8" },
      { name: "Story", icon: "fa-bookmark", color: "#16a34a" },
      { name: "Epic", icon: "fa-bolt", color: "#a855f7" }
    ]
  },
  kanban: {
    title: "Kanban software development",
    desc: "Monitor continuous flow of your development tasks. Organise work in progress, optimize delivery pipeline with WIP limits, and use high-fidelity Kanban boards.",
    types: [
      { name: "Bug", icon: "fa-bug", color: "#e11d48" },
      { name: "Task", icon: "fa-check-square", color: "#2563eb" },
      { name: "Sub-task", icon: "fa-tasks", color: "#38bdf8" },
      { name: "Story", icon: "fa-bookmark", color: "#16a34a" },
      { name: "Epic", icon: "fa-bolt", color: "#a855f7" }
    ]
  },
  task_tracking: {
    title: "Project management",
    desc: "Create your tasks, organize and track their progress, and deliver your work on time. Estimations and time tracking allow you to report on where your project is at any stage.",
    types: [
      { name: "Task", icon: "fa-check-square", color: "#2563eb" },
      { name: "Sub-task", icon: "fa-tasks", color: "#38bdf8" }
    ]
  },
  business: {
    title: "Business Process Management",
    desc: "Designed for business teams, operations, marketing campaigns, and document reviews. Streamline pipelines and enforce business progress parameters.",
    types: [
      { name: "Task", icon: "fa-check-square", color: "#2563eb" },
      { name: "Sub-task", icon: "fa-tasks", color: "#38bdf8" }
    ]
  }
};

window.selectWizardTemplate = function(template) {
  cpSelectedTemplate = template;
  showCpStep(2);
};

window.wizardGoNext = function() {
  if (cpWizardStep === 1) {
    showCpStep(2);
  } else if (cpWizardStep === 2) {
    showCpStep(3);
  }
};

window.wizardGoBack = function() {
  if (cpWizardStep === 2) {
    showCpStep(1);
  } else if (cpWizardStep === 3) {
    showCpStep(2);
  }
};

function showCpStep(step) {
  cpWizardStep = step;
  document.getElementById('cp-step-1').style.display = step === 1 ? 'block' : 'none';
  document.getElementById('cp-step-2').style.display = step === 2 ? 'block' : 'none';
  document.getElementById('cp-step-3').style.display = step === 3 ? 'block' : 'none';
  
  document.getElementById('cp-back-btn').style.display = step > 1 ? 'inline-block' : 'none';
  document.getElementById('cp-next-btn').style.display = step < 3 ? 'inline-block' : 'none';
  document.getElementById('cp-submit-btn').style.display = step === 3 ? 'inline-block' : 'none';
  
  if (step === 2) {
    const spec = TEMPLATE_SPECS[cpSelectedTemplate];
    document.getElementById('cp-preview-title').textContent = spec.title;
    document.getElementById('cp-preview-desc').textContent = spec.desc;
    document.getElementById('cp-preview-types').innerHTML = spec.types.map(t => `
      <div style="display:flex;align-items:center;gap:10px;font-size:14px;color:#172B4D;">
        <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:4px;background:#ebecf0;color:${t.color};">
          <i class="fa ${t.icon}"></i>
        </span>
        <strong>${t.name}</strong>
      </div>
    `).join('');
  }
}

async function openCreateProject() {
  cpWizardStep = 1;
  cpSelectedTemplate = 'scrum';
  
  // Populate Lead dropdown
  const leadSel = document.getElementById('cp-lead');
  if (leadSel) {
    leadSel.innerHTML = allUsers.map(u => `<option value="${u.id}">${u.full_name} (${u.role.replace(/_/g, ' ')})</option>`).join('');
    leadSel.value = currentUser.id;
  }
  
  showCpStep(1);
  openModal('create-project');
}

async function submitCreateProject() {
  const data = {
    key: document.getElementById('cp-key').value.trim().toUpperCase(),
    name: document.getElementById('cp-name').value.trim(),
    description: document.getElementById('cp-desc').value.trim(),
    department: document.getElementById('cp-dept').value,
    category: document.getElementById('cp-category').value,
    lead_id: parseInt(document.getElementById('cp-lead').value) || currentUser.id,
    color: document.getElementById('cp-color').value,
    project_type: cpSelectedTemplate,
    url: document.getElementById('cp-url').value.trim() || null
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
  const dd = document.getElementById('search-dropdown');
  if (!dd) return;
  if (!q || q.length < 2) { dd.style.display = 'none'; return; }
  const ql = q.toLowerCase();
  const results = allIssues.filter(i =>
    i.key.toLowerCase().includes(ql) ||
    i.title.toLowerCase().includes(ql)
  ).slice(0, 8);
  const projResults = allProjects.filter(p =>
    p.name.toLowerCase().includes(ql) || p.key.toLowerCase().includes(ql)
  ).slice(0, 3);
  if (!results.length && !projResults.length) { dd.style.display = 'none'; return; }
  dd.innerHTML = [
    ...results.map(i => `<div class="search-result-item" onclick="openIssueDetail(${i.id});document.getElementById('global-search').value='';document.getElementById('search-dropdown').style.display='none';">${getTypeIcon(i.issue_type)}<div><div style="font-size:13px;font-weight:600;">${i.key}: ${i.title}</div><div style="font-size:11px;color:#6b7280;">${getStatusBadge(i.status)} ${getPriorityBadge(i.priority)}</div></div></div>`),
    ...projResults.map(p => `<div class="search-result-item" onclick="filterProjectIssues(${p.id});document.getElementById('global-search').value='';document.getElementById('search-dropdown').style.display='none';"><i class="fa fa-folder-open" style="color:#1B1F6B;width:22px;text-align:center;"></i><div><div style="font-size:13px;font-weight:600;">${p.key}: ${p.name}</div><div style="font-size:11px;color:#6b7280;">Project</div></div></div>`)
  ].join('');
  dd.style.display = 'block';
}

document.addEventListener('click', e => {
  const dd = document.getElementById('search-dropdown');
  if (dd && !dd.contains(e.target) && e.target.id !== 'global-search') dd.style.display = 'none';
});

document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    const s = document.getElementById('global-search');
    if (s) s.focus();
  }
});

// ── Dashboard ─────────────────────────────────────────────────────────────────
async function renderDashboard(el) {
  const IS_DEV = ['developer','devops_engineer','security_engineer','qa_engineer'].includes(currentUser.role);
  if (IS_DEV) {
    let devStats;
    try { devStats = await api('GET', '/api/dashboard/developer-stats'); }
    catch(e) { devStats = {total_assigned:0,fixed:0,in_progress:0,pending:0,issues:[]}; }
    
    const activeSprint = allSprints.find(s=>s.status==='active');
    const sprintHtml = activeSprint ? (() => {
      const daysLeft = activeSprint.end_date ? Math.max(0,Math.ceil((new Date(activeSprint.end_date)-new Date())/(1000*60*60*24))) : '?';
      const uc = daysLeft <= 2 ? '#dc2626' : daysLeft <= 5 ? '#F5A623' : '#15803d';
      return `<div style="background:#fff;border-left:4px solid ${uc};border:1px solid #e2e8f0;border-radius:8px;padding:14px 18px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;">
        <div>
          <div style="font-size:11px;text-transform:uppercase;color:#64748b;font-weight:700;">Active Sprint</div>
          <div style="font-size:15px;font-weight:700;color:#1B1F6B;margin-top:2px;">${activeSprint.name}</div>
        </div>
        <div style="text-align:center;background:${uc}22;border-radius:10px;padding:10px 18px;">
          <div style="font-size:28px;font-weight:800;color:${uc};">${daysLeft}</div>
          <div style="font-size:11px;color:${uc};font-weight:700;">DAYS LEFT</div>
        </div>
      </div>`;
    })() : '';
    
    el.innerHTML = `
      <div class="page-header" style="margin-bottom:16px;">
        <div>
          <div class="page-title" style="font-size:22px;color:#1B1F6B;font-weight:700;">My Dashboard</div>
          <div class="page-subtitle">${currentUser.full_name} &middot; ${currentUser.role.replace(/_/g,' ')}</div>
        </div>
      </div>
      
      ${sprintHtml}
      
      <div class="stats-grid" style="margin-bottom:20px;">
        <div class="stat-card" style="border-left-color:#1B1F6B;cursor:pointer;" onclick="nav('myissues')">
          <div class="stat-icon" style="background:#e8eaf6;color:#1B1F6B;"><i class="fa fa-tasks"></i></div>
          <div><div class="stat-value">${devStats.total_assigned}</div><div class="stat-label">Assigned to Me</div></div>
        </div>
        <div class="stat-card" style="border-left-color:#c2410c;">
          <div class="stat-icon" style="background:#fff7ed;color:#c2410c;"><i class="fa fa-spinner"></i></div>
          <div><div class="stat-value">${devStats.in_progress}</div><div class="stat-label">In Progress</div></div>
        </div>
        <div class="stat-card" style="border-left-color:#15803d;">
          <div class="stat-icon" style="background:#dcfce7;color:#15803d;"><i class="fa fa-check-circle"></i></div>
          <div><div class="stat-value">${devStats.fixed}</div><div class="stat-label">Fixed / Done</div></div>
        </div>
        <div class="stat-card" style="border-left-color:#64748b;">
          <div class="stat-icon" style="background:#f1f5f9;color:#64748b;"><i class="fa fa-hourglass-half"></i></div>
          <div><div class="stat-value">${devStats.pending}</div><div class="stat-label">Pending / To Do</div></div>
        </div>
      </div>
      
      <div style="background:#fff;border:1px solid #e2e8f0;border-left:4px solid #1B1F6B;border-radius:8px;overflow:hidden;">
        <div style="background:#1B1F6B;color:#fff;padding:10px 16px;font-size:13px;font-weight:700;">
          <i class="fa fa-list-ul" style="margin-right:8px;"></i>My Issues Status
        </div>
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
          <thead>
            <tr style="background:#f8fafc;border-bottom:1px solid #e2e8f0;color:#475569;font-weight:600;">
              <th style="padding:10px 14px;">Key</th>
              <th style="padding:10px 14px;">Title</th>
              <th style="padding:10px 14px;">Project</th>
              <th style="padding:10px 14px;">Status</th>
              <th style="padding:10px 14px;">Priority</th>
              <th style="padding:10px 14px;">Due</th>
            </tr>
          </thead>
          <tbody>
            ${(devStats.issues||[]).length ? devStats.issues.map(i => {
              const done = ['done','closed'].includes(i.status);
              const over = i.due_date && new Date(i.due_date)<new Date() && !done;
              return `<tr style="border-bottom:1px solid #f1f5f9;cursor:pointer;" onclick="openIssueDetail(${i.id})" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
                <td style="padding:10px 14px;"><span style="color:#0052CC;font-weight:700;font-family:monospace;">${i.key}</span></td>
                <td style="padding:10px 14px;font-weight:500;color:#1e293b;">${i.title}</td>
                <td style="padding:10px 14px;color:#64748b;">${i.project_key}</td>
                <td style="padding:10px 14px;">${getStatusBadge(i.status)}</td>
                <td style="padding:10px 14px;">${getPriorityBadge(i.priority)}</td>
                <td style="padding:10px 14px;color:${over?'#dc2626':'#64748b'};">${i.due_date ? fmt(i.due_date) : '-'}</td>
              </tr>`;
            }).join('') : '<tr><td colspan="6" style="text-align:center;padding:40px;color:#94a3b8;"><i class="fa fa-inbox" style="font-size:28px;display:block;margin-bottom:8px;"></i>No issues assigned to you</td></tr>'}
          </tbody>
        </table>
      </div>
    `;
    updateRoleBasedUI();
    return;
  }

  // Full org dashboard for admin/pm
  const stats = await api('GET', '/api/dashboard/stats');
  const assigned = await api('GET', `/api/issues/?assignee_id=${currentUser.id}&page_size=10`);
  const displayIssues = (assigned||[]).slice(0,10);
  const sp = stats.sprint_progress;
  
  const sprintCard = sp ? (() => {
    const uc = (sp.days_remaining!==null && sp.days_remaining<=2) ? '#dc2626' : (sp.days_remaining!==null && sp.days_remaining<=5) ? '#F5A623' : '#15803d';
    return `<div class="sprint-progress-card" style="margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;gap:16px;">
      <div style="flex:1;">
        <div class="card-title"><i class="fa fa-running" style="color:#F5A623;"></i> Active Sprint: ${sp.name}</div>
        <div class="progress-bar" style="margin-top:8px;"><div class="progress-fill" style="width:${sp.percent}%;"></div></div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-top:6px;">
          <span>${sp.done} / ${sp.total} completed</span>
          <span style="font-weight:700;color:#1B1F6B;">${sp.percent}%</span>
        </div>
      </div>
      ${sp.days_remaining!==null ? `<div style="text-align:center;background:${uc}22;border-radius:10px;padding:12px 18px;">
        <div style="font-size:26px;font-weight:800;color:${uc};">${sp.days_remaining}</div>
        <div style="font-size:11px;font-weight:700;color:${uc};">DAYS LEFT</div>
      </div>` : ''}
    </div>`;
  })() : '';
  
  el.innerHTML = `
    <div class="page-header" style="margin-bottom:16px;">
      <div>
        <div class="page-title" style="font-size:22px;color:#1B1F6B;font-weight:700;">Dashboard &mdash; ${currentUser.full_name.split(' ')[0]}</div>
        <div class="page-subtitle">Awash Bank Issue Tracker</div>
      </div>
    </div>
    
    ${sprintCard}
    
    <div class="stats-grid" style="margin-bottom:16px;">
      <div class="stat-card" style="border-left-color:#1B1F6B;"><div class="stat-icon" style="background:#e8eaf6;color:#1B1F6B;"><i class="fa fa-tasks"></i></div><div><div class="stat-value">${stats.total_issues}</div><div class="stat-label">Total Issues</div></div></div>
      <div class="stat-card" style="border-left-color:#1d4ed8;"><div class="stat-icon" style="background:#dbeafe;color:#1d4ed8;"><i class="fa fa-folder-open"></i></div><div><div class="stat-value">${stats.open_issues}</div><div class="stat-label">Open Issues</div></div></div>
      <div class="stat-card" style="border-left-color:#c2410c;"><div class="stat-icon" style="background:#fff7ed;color:#c2410c;"><i class="fa fa-spinner"></i></div><div><div class="stat-value">${stats.in_progress}</div><div class="stat-label">In Progress</div></div></div>
      <div class="stat-card" style="border-left-color:#15803d;"><div class="stat-icon" style="background:#dcfce7;color:#15803d;"><i class="fa fa-check-circle"></i></div><div><div class="stat-value">${stats.resolved_today}</div><div class="stat-label">Resolved Today</div></div></div>
      <div class="stat-card" style="border-left-color:#dc2626;"><div class="stat-icon" style="background:#fee2e2;color:#dc2626;"><i class="fa fa-exclamation-triangle"></i></div><div><div class="stat-value">${stats.overdue}</div><div class="stat-label">Overdue</div></div></div>
    </div>
    
    ${displayIssues.length ? `<div style="background:#fff;border-left:4px solid #1B1F6B;border:1px solid #e2e8f0;border-radius:6px;margin-bottom:18px;overflow:hidden;">
      <div style="background:#1B1F6B;color:#fff;padding:8px 12px;font-size:12.5px;font-weight:700;">Assigned to Me</div>
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        <thead><tr style="background:#f8fafc;border-bottom:1px solid #e2e8f0;color:#475569;font-weight:600;"><th style="padding:10px 14px;">Key</th><th style="padding:10px 14px;">Summary</th><th style="padding:10px 14px;">Status</th><th style="padding:10px 14px;">Priority</th></tr></thead>
        <tbody>
          ${displayIssues.map(i=>`<tr style="border-bottom:1px solid #f1f5f9;cursor:pointer;" onclick="openIssueDetail(${i.id})" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'"><td style="padding:10px 14px;"><span style="color:#0052CC;font-weight:700;font-family:monospace;">${i.key}</span></td><td style="padding:10px 14px;">${i.title}</td><td style="padding:10px 14px;">${getStatusBadge(i.status)}</td><td style="padding:10px 14px;">${getPriorityBadge(i.priority)}</td></tr>`).join('')}
        </tbody>
      </table>
    </div>` : ''}
    
    <div class="charts-grid" style="margin-bottom:16px;">
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
  updateRoleBasedUI();
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
    <div class="page-header" style="margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:8px;">
        <div class="page-title" style="font-size:22px;color:#1B1F6B;font-weight:700;">Search</div>
        <button class="btn btn-sm btn-outline" style="padding:4px 8px;font-size:12px;border:1px solid #cbd5e1;border-radius:4px;background:#fff;" onclick="toast('Filter saved!','success')">Save as</button>
      </div>
      <div style="display:flex;gap:16px;align-items:center;font-size:13px;color:#64748b;margin-left:auto;">
        <span style="cursor:pointer;" onclick="toast('Shared search link copied to clipboard','success')"><i class="fa fa-share-alt"></i> Share</span>
        <span style="cursor:pointer;" onclick="exportToCSV()"><i class="fa fa-download"></i> Export <i class="fa fa-chevron-down" style="font-size:9px;"></i></span>
        <span style="cursor:pointer;" onclick="toast('Search configuration options opened','info')"><i class="fa fa-cog"></i> Tools <i class="fa fa-chevron-down" style="font-size:9px;"></i></span>
      </div>
    </div>

    <!-- Atlassian Styled Filter Bar -->
    <div class="filter-bar" style="background:#fff;padding:12px;border-radius:6px;border:1px solid #e2e8f0;display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:14px;">
      <div style="display:flex;align-items:center;gap:4px;">
        <span style="font-size:12px;color:#475569;font-weight:600;">Project:</span>
        <select onchange="filterIssues()" id="filter-project" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;">
          <option value="">All</option>
          ${allProjects.map(p => `<option value="${p.id}">${p.key}</option>`).join('')}
        </select>
      </div>

      <div style="display:flex;align-items:center;gap:4px;">
        <span style="font-size:12px;color:#475569;font-weight:600;">Type:</span>
        <select onchange="filterIssues()" id="filter-type" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;">
          <option value="">All</option>
          <option value="bug">Bug</option>
          <option value="feature">Feature</option>
          <option value="task">Task</option>
          <option value="story">Story</option>
          <option value="epic">Epic</option>
        </select>
      </div>

      <div style="display:flex;align-items:center;gap:4px;">
        <span style="font-size:12px;color:#475569;font-weight:600;">Status:</span>
        <select onchange="filterIssues()" id="filter-status" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;">
          <option value="">All</option>
          <option value="backlog">Backlog</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="testing">Testing</option>
          <option value="qa_approved">QA Approved</option>
          <option value="uat">UAT</option>
          <option value="done">Done</option>
          <option value="closed">Closed</option>
          <option value="blocked">Blocked</option>
        </select>
      </div>

      <div style="display:flex;align-items:center;gap:4px;">
        <span style="font-size:12px;color:#475569;font-weight:600;">Assignee:</span>
        <select onchange="filterIssues()" id="filter-assignee" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;">
          <option value="">All</option>
          ${allUsers.map(u => `<option value="${u.id}">${u.full_name}</option>`).join('')}
        </select>
      </div>

      <input type="text" placeholder="Contains text" oninput="filterIssues()" id="filter-search" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;width:140px;outline:none;"/>
      
      <button class="btn btn-primary" onclick="filterIssues()" style="padding:5px 12px;font-size:12px;font-weight:600;border-radius:4px;">Search</button>
      <span style="color:#0052CC;cursor:pointer;font-size:12px;font-weight:600;margin-left:4px;" onclick="resetSearchFilters()">Advanced</span>
    </div>

    <!-- Results Sub-header -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;padding:0 4px;">
      <div id="issues-subtitle" style="font-size:12.5px;color:#475569;font-weight:600;">Loading issues...</div>
      <div style="font-size:12.5px;color:#0052CC;cursor:pointer;font-weight:600;" onclick="toast('Custom columns layout editor coming soon','info')">Columns <i class="fa fa-chevron-down" style="font-size:9px;"></i></div>
    </div>

    <!-- Table Container -->
    <div class="tbl-wrap" style="background:#fff;border-radius:6px;border:1px solid #e2e8f0;overflow-x:auto;">
      <table style="width:100%;border-collapse:collapse;font-size:13px;text-align:left;">
        <thead>
          <tr style="background:#f8fafc;border-bottom:1px solid #cbd5e1;color:#475569;font-weight:600;">
            <th style="padding:10px 12px;width:110px;">Key</th>
            <th style="padding:10px 12px;width:120px;">Status</th>
            <th style="padding:10px 12px;">Created</th>
            <th style="padding:10px 12px;">Updated</th>
            <th style="padding:10px 12px;width:130px;">Development</th>
            <th style="padding:10px 12px;">Assignee</th>
            <th style="padding:10px 12px;">Closed date</th>
            <th style="padding:10px 12px;width:90px;">CR Type</th>
            <th style="padding:10px 12px;width:40px;text-align:center;">T</th>
            <th style="padding:10px 12px;width:40px;text-align:center;">P</th>
            <th style="padding:10px 12px;width:80px;text-align:center;">Progress</th>
          </tr>
        </thead>
        <tbody id="issues-tbody"></tbody>
      </table>
    </div>
    <div id="issues-pagination" style="margin-top:14px;"></div>
  `;
  renderIssuesTable(issues);
}

function renderIssuesTable(issues) {
  const tbody = document.getElementById('issues-tbody');
  const pagEl = document.getElementById('issues-pagination');
  const sub = document.getElementById('issues-subtitle');
  
  if (!issues || !issues.length) {
    tbody.innerHTML = '<tr><td colspan="11" style="text-align:center;padding:45px;color:#64748b;"><i class="fa fa-inbox" style="font-size:32px;display:block;margin-bottom:10px;opacity:.3;"></i>No matching issues found</td></tr>';
    if (pagEl) pagEl.innerHTML = '';
    if (sub) sub.textContent = '0 of 0';
    return;
  }
  
  const total = issues.length;
  const totalPages = Math.ceil(total / ISSUES_PER_PAGE);
  const start = (issuesPage - 1) * ISSUES_PER_PAGE;
  const paged = issues.slice(start, start + ISSUES_PER_PAGE);
  
  if (sub) {
    sub.textContent = `${start + 1}-${Math.min(start + ISSUES_PER_PAGE, total)} of ${total}`;
  }

  tbody.innerHTML = paged.map(i => {
    const isDone = ['done', 'closed', 'qa_approved', 'uat'].includes(i.status);
    const progressPercent = isDone ? 100 : (['in_progress', 'testing', 'in_review'].includes(i.status) ? 50 : 10);
    const progressBarColor = isDone ? '#16a34a' : '#ea580c';
    
    return `<tr style="border-bottom:1px solid #f1f5f9;cursor:pointer;transition:background 0.15s;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'" onclick="openIssueDetail(${i.id})">
      <td style="padding:10px 12px;"><span style="color:#0052CC;font-weight:600;font-family:monospace;">${i.key}</span></td>
      <td style="padding:10px 12px;vertical-align:middle;">${getStatusBadge(i.status)}</td>
      <td style="padding:10px 12px;color:#475569;">${fmt(i.created_at)}</td>
      <td style="padding:10px 12px;color:#475569;">${fmt(i.updated_at || i.created_at)}</td>
      <td style="padding:10px 12px;"><span style="color:#475569;font-size:12px;display:flex;align-items:center;gap:4px;"><i class="fab fa-git-alt" style="color:#f1502f;"></i> main branch</span></td>
      <td style="padding:10px 12px;color:#1e293b;font-weight:500;">${i.assignee ? i.assignee.full_name : '<span style="color:#94a3b8;">Unassigned</span>'}</td>
      <td style="padding:10px 12px;color:#64748b;">${isDone ? '5 days ago' : '-'}</td>
      <td style="padding:10px 12px;color:#475569;">Normal</td>
      <td style="padding:10px 12px;text-align:center;">${getTypeIcon(i.issue_type)}</td>
      <td style="padding:10px 12px;text-align:center;">${getPriorityBadge(i.priority)}</td>
      <td style="padding:10px 12px;text-align:center;vertical-align:middle;">
        <div style="width:60px;height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;margin:0 auto;">
          <div style="width:${progressPercent}%;height:100%;background:${progressBarColor};"></div>
        </div>
      </td>
    </tr>`;
  }).join('');

  if (pagEl && totalPages > 1) {
    let btns = `<button class="page-btn" onclick="issuesPage=Math.max(1,issuesPage-1);renderIssuesTable(window._fi||allIssues)" ${issuesPage === 1 ? 'disabled' : ''}>&lt; Prev</button>`;
    for (let p = Math.max(1, issuesPage - 2); p <= Math.min(totalPages, issuesPage + 2); p++) {
      btns += `<button class="page-btn ${p === issuesPage ? 'active' : ''}" onclick="issuesPage=${p};renderIssuesTable(window._fi||allIssues)">${p}</button>`;
    }
    btns += `<button class="page-btn" onclick="issuesPage=Math.min(${totalPages},issuesPage+1);renderIssuesTable(window._fi||allIssues)" ${issuesPage === totalPages ? 'disabled' : ''}>Next &gt;</button>`;
    pagEl.innerHTML = `<div class="pagination"><div class="pagination-btns" style="margin-left:auto;">${btns}</div></div>`;
  } else if (pagEl) {
    pagEl.innerHTML = '';
  }
}

function filterIssues() {
  const project = document.getElementById('filter-project')?.value;
  const status = document.getElementById('filter-status')?.value;
  const priority = document.getElementById('filter-priority')?.value;
  const type = document.getElementById('filter-type')?.value;
  const assignee = document.getElementById('filter-assignee')?.value;
  const search = document.getElementById('filter-search')?.value.toLowerCase();
  
  let filtered = allIssues;
  if (project) filtered = filtered.filter(i => String(i.project_id) === project);
  if (status) filtered = filtered.filter(i => i.status === status);
  if (priority) filtered = filtered.filter(i => i.priority === priority);
  if (type) filtered = filtered.filter(i => i.issue_type === type);
  if (assignee) filtered = filtered.filter(i => i.assignee && String(i.assignee.id) === assignee);
  if (search) filtered = filtered.filter(i =>
    i.title.toLowerCase().includes(search) ||
    i.key.toLowerCase().includes(search) ||
    (i.description || '').toLowerCase().includes(search)
  );
  
  window._fi = filtered;
  issuesPage = 1;
  renderIssuesTable(filtered);
}

function resetSearchFilters() {
  const proj = document.getElementById('filter-project'); if (proj) proj.value = "";
  const type = document.getElementById('filter-type'); if (type) type.value = "";
  const stat = document.getElementById('filter-status'); if (stat) stat.value = "";
  const ass = document.getElementById('filter-assignee'); if (ass) ass.value = "";
  const search = document.getElementById('filter-search'); if (search) search.value = "";
  filterIssues();
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
          <div class="kanban-col-body" ondragover="allowDrop(event)" ondrop="drop(event, '${col}')" style="min-height:500px;">
            ${(board[col] || []).map(i => `
              <div class="kanban-card" draggable="true" ondragstart="drag(event, ${i.id})" style="border-left-color:${colColors[col]}; cursor:grab;" onclick="openIssueDetail(${i.id})">
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

window.allowDrop = function(ev) {
  ev.preventDefault();
};

window.drag = function(ev, issueId) {
  ev.dataTransfer.setData("text/plain", issueId);
};

window.drop = async function(ev, targetStatus) {
  ev.preventDefault();
  const issueId = ev.dataTransfer.getData("text/plain");
  if (!issueId) return;
  
  try {
    const issue = await api('GET', `/api/issues/${issueId}`);
    
    // Developer role assignment check
    if (currentUser.role === 'developer' && issue.assignee_id !== currentUser.id) {
      return toast('As a Developer, you can only move issues assigned to you!', 'error');
    }
    
    await api('PUT', `/api/issues/${issueId}`, { status: targetStatus });
    toast(`Status successfully updated to ${targetStatus.replace(/_/g, ' ')}!`, 'success');
    loadPage('kanban');
  } catch (e) {
    toast(e.message, 'error');
  }
};


async function renderProjects(el) {
  el.innerHTML = `
    <div class="page-header" style="margin-bottom: 24px;">
      <div>
        <div class="page-title" style="font-size: 24px; font-weight: 500; color: #172B4D;">All project types - All categories</div>
        <div class="page-subtitle" style="font-size: 14px; color: #5e6c84; margin-top: 4px;">${allProjects.length} active projects</div>
      </div>
      <button class="btn btn-orange" onclick="openCreateProject()"><i class="fa fa-plus"></i> New Project</button>
    </div>
    
    <div class="search-box" style="margin-bottom: 20px; max-width: 300px; background: #fff; border: 1px solid #dfe1e6; border-radius: 4px; padding: 6px 12px; display: flex; align-items: center; gap: 8px;">
      <i class="fa fa-search" style="color:#6b7280;font-size:13px;"></i>
      <input type="text" placeholder="Search..." id="project-search" oninput="filterProjectListTable(this.value)" style="border:none; outline:none; font-size:14px; width:100%; color:#172B4D;"/>
    </div>
    
    <div class="table-container" style="background:#fff; border-radius: 8px; border: 1px solid #dfe1e6; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
      <table class="table" style="width:100%; border-collapse: collapse; text-align: left; font-size: 14px;">
        <thead>
          <tr style="border-bottom: 2px solid #dfe1e6; background: #f4f5f7; color: #5e6c84; font-weight: 600;">
            <th style="padding: 12px 16px; width: 30%;">Project</th>
            <th style="padding: 12px 16px; width: 15%;">Key</th>
            <th style="padding: 12px 16px; width: 15%;">Project type</th>
            <th style="padding: 12px 16px; width: 15%;">Project lead</th>
            <th style="padding: 12px 16px; width: 15%;">Project category</th>
            <th style="padding: 12px 16px; width: 10%;">URL</th>
          </tr>
        </thead>
        <tbody id="projects-table-body">
          <!-- Populated dynamically -->
        </tbody>
      </table>
    </div>
  `;
  filterProjectListTable('');
}

window.filterProjectListTable = function(q) {
  const tbody = document.getElementById('projects-table-body');
  if (!tbody) return;
  
  const filtered = allProjects.filter(p => 
    p.name.toLowerCase().includes(q.toLowerCase()) || 
    p.key.toLowerCase().includes(q.toLowerCase()) ||
    (p.department && p.department.toLowerCase().includes(q.toLowerCase()))
  );
  
  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="padding:40px; text-align:center; color:#5e6c84;"><i class="fa fa-folder-open" style="font-size:24px; margin-bottom:8px; display:block;"></i>No projects found</td></tr>`;
    return;
  }
  
  tbody.innerHTML = filtered.map(p => {
    const initial = p.name.charAt(0).toUpperCase();
    const color = p.color || '#0052cc';
    const pType = p.project_type || 'scrum';
    
    let typeIcon = 'fa-sync-alt';
    let typeColor = '#0052CC';
    let typeName = 'Scrum';
    if (pType === 'kanban') {
      typeIcon = 'fa-columns';
      typeColor = '#5243AA';
      typeName = 'Kanban';
    } else if (pType === 'task_tracking') {
      typeIcon = 'fa-tasks';
      typeColor = '#00875A';
      typeName = 'Task Tracking';
    } else if (pType === 'business') {
      typeIcon = 'fa-briefcase';
      typeColor = '#FF9900';
      typeName = 'Business';
    }
    
    const leadUser = allUsers.find(u => u.id === p.lead_id);
    const leadName = leadUser ? leadUser.full_name : (p.lead ? p.lead.full_name : 'No lead');
    const categoryName = p.category || 'No category';
    const urlVal = p.url ? `<a href="${p.url}" target="_blank" style="color:#0052cc; text-decoration:none;"><i class="fa fa-external-link-alt"></i> Link</a>` : '<span style="color:#6c757d;">No URL</span>';
    
    return `
      <tr style="border-bottom: 1px solid #dfe1e6; cursor: pointer; transition: background 0.1s ease;" onmouseover="this.style.backgroundColor='#f4f5f7'" onmouseout="this.style.backgroundColor='transparent'" onclick="filterProjectIssues(${p.id})">
        <td style="padding: 16px; display: flex; align-items: center; gap: 12px;">
          <span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 4px; background: ${color}; color: #fff; font-weight: bold; font-size: 14px;">
            ${initial}
          </span>
          <span style="color: #0052cc; font-weight: 500;">${p.name}</span>
        </td>
        <td style="padding: 16px; font-weight: 500; color: #172B4D;">${p.key}</td>
        <td style="padding: 16px; vertical-align: middle;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; background: ${typeColor}15; color: ${typeColor}; font-size: 11px;">
               <i class="fa ${typeIcon}"></i>
            </span>
            <span style="color:#172B4D;">${typeName}</span>
          </div>
        </td>
        <td style="padding: 16px; color: #0052cc;">${leadName}</td>
        <td style="padding: 16px; color: #172B4D;">${categoryName}</td>
        <td style="padding: 16px;" onclick="event.stopPropagation();">${urlVal}</td>
      </tr>
    `;
  }).join('');
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
  const IS_ADMIN = ['super_admin','admin'].includes(currentUser.role);
  
  el.innerHTML = `
    <div class="page-header" style="margin-bottom:20px;">
      <div>
        <div class="page-title" style="font-size:22px;color:#1B1F6B;font-weight:700;">Sprints</div>
        <div class="page-subtitle" style="font-size:14px;color:#64748b;margin-top:2px;">${allSprints.length} sprints &middot; Timeboxed iterations</div>
      </div>
      ${IS_ADMIN ? `<button class="btn btn-primary" onclick="openCreateSprint()" style="background:#1B1F6B;border:none;padding:8px 16px;font-size:13px;font-weight:600;border-radius:6px;box-shadow:0 2px 4px rgba(27,31,107,0.2);"><i class="fa fa-plus" style="margin-right:6px;"></i> New Sprint</button>` : ''}
    </div>
    
    <div class="sprint-list" style="display:grid;grid-template-columns:repeat(auto-fill, minmax(350px, 1fr));gap:16px;">
      ${allSprints.map(s => {
        const isAct = s.status === 'active';
        const isFuture = s.status === 'planned';
        const isDone = s.status === 'closed' || s.status === 'completed';
        
        let headerColor = isAct ? '#F5A623' : isDone ? '#10b981' : '#64748b';
        let bgStyle = isAct ? 'background:#fff;border:1px solid #e2e8f0;border-top:4px solid #F5A623;' : 'background:#f8fafc;border:1px solid #e2e8f0;';
        
        const doneC = s.done_count || 0;
        const totalC = s.issue_count || 0;
        const pct = totalC > 0 ? Math.round((doneC/totalC)*100) : 0;
        
        let daysHtml = '';
        if (s.start_date && s.end_date) {
          const now = new Date();
          const end = new Date(s.end_date);
          const start = new Date(s.start_date);
          
          if (isAct) {
            const left = Math.max(0, Math.ceil((end - now)/(1000*60*60*24)));
            daysHtml = `<span style="font-weight:700;color:${left<=2?'#dc2626':'#F5A623'}"><i class="fa fa-clock"></i> ${left} days left</span>`;
          } else if (isFuture) {
            const startsIn = Math.max(0, Math.ceil((start - now)/(1000*60*60*24)));
            daysHtml = `<span style="color:#64748b;"><i class="fa fa-calendar"></i> Starts in ${startsIn} days</span>`;
          } else {
            daysHtml = `<span style="color:#64748b;"><i class="fa fa-check-double"></i> Completed</span>`;
          }
        }
        
        return `<div class="sprint-item" style="${bgStyle}border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.05);display:flex;flex-direction:column;justify-content:space-between;transition:transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)';this.style.transform='translateY(-2px)'" onmouseout="this.style.boxShadow='0 1px 3px rgba(0,0,0,0.05)';this.style.transform='translateY(0)'">
          <div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
              <div>
                <div style="display:flex;align-items:center;gap:8px;">
                  <div style="font-size:16px;font-weight:700;color:#1e293b;">${s.name}</div>
                  <span style="font-size:10px;font-weight:700;padding:2px 6px;border-radius:12px;background:${isAct?'#fef3c7':isDone?'#d1fae5':'#f1f5f9'};color:${headerColor};text-transform:uppercase;">${s.status}</span>
                </div>
                <div style="font-size:12px;color:#64748b;margin-top:4px;">${s.start_date ? fmt(s.start_date) : '-'} &mdash; ${s.end_date ? fmt(s.end_date) : '-'}</div>
              </div>
              <button class="btn btn-sm" onclick="viewSprintBoard(${s.id})" style="background:#f1f5f9;color:#0052CC;border:none;padding:6px 10px;border-radius:4px;font-size:12px;font-weight:600;cursor:pointer;"><i class="fa fa-columns"></i> Board</button>
            </div>
            
            ${s.goal ? `<div style="font-size:13px;color:#334155;background:${isAct?'#fffbeb':'#f8fafc'};padding:8px 12px;border-radius:4px;border-left:3px solid ${headerColor};margin-bottom:14px;">"${s.goal}"</div>` : ''}
            
            <div style="margin-bottom:12px;">
              <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;font-weight:600;">
                <span style="color:#475569;">Progress (${doneC}/${totalC})</span>
                <span style="color:${pct===100?'#10b981':'#1e293b'};">${pct}%</span>
              </div>
              <div style="height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;">
                <div style="height:100%;width:${pct}%;background:${isAct ? (pct===100?'#10b981':'#0052CC') : isDone ? '#10b981' : '#94a3b8'};"></div>
              </div>
            </div>
          </div>
          
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;border-top:1px solid #e2e8f0;padding-top:12px;margin-top:12px;">
            ${daysHtml}
            <div style="display:flex;gap:10px;align-items:center;">
              ${isFuture && IS_ADMIN ? `<button onclick="startSprintReal(${s.id})" style="background:transparent;border:none;color:#0052CC;font-weight:600;font-size:12.5px;cursor:pointer;padding:0;"><i class="fa fa-play"></i> Start Sprint</button>` : ''}
              ${isAct && IS_ADMIN ? `<button onclick="completeSprintReal(${s.id})" style="background:transparent;border:none;color:#10b981;font-weight:600;font-size:12.5px;cursor:pointer;padding:0;"><i class="fa fa-check-circle"></i> Complete Sprint</button>` : ''}
              ${IS_ADMIN ? `<button onclick="deleteSprintReal(${s.id})" style="background:transparent;border:none;color:#dc2626;font-weight:600;font-size:12.5px;cursor:pointer;padding:0;"><i class="fa fa-trash"></i> Delete</button>` : ''}
            </div>
          </div>
        </div>`;
      }).join('')}
    </div>
  `;
}

async function startSprintReal(sprintId) {
  if (!confirm('Are you sure you want to start this sprint?')) return;
  try {
    await api('POST', `/api/sprints/${sprintId}/start`);
    toast('Sprint started successfully', 'success');
    await loadSprints();
    nav('sprints');
  } catch(e) {
    toast('Failed to start sprint', 'error');
  }
}

async function completeSprintReal(sprintId) {
  if (!confirm('Are you sure you want to complete this sprint? Any incomplete issues will be moved back to the backlog.')) return;
  try {
    await api('POST', `/api/sprints/${sprintId}/complete`);
    toast('Sprint completed successfully', 'success');
    await loadSprints();
    nav('sprints');
  } catch(e) {
    toast('Failed to complete sprint', 'error');
  }
}

async function deleteSprintReal(sprintId) {
  if (!confirm('Are you sure you want to delete this sprint? All assigned issues will be returned to the backlog.')) return;
  try {
    await api('DELETE', `/api/sprints/${sprintId}`);
    toast('Sprint deleted successfully', 'success');
    await loadSprints();
    nav('sprints');
  } catch(e) {
    toast('Failed to delete sprint', 'error');
  }
}
// ── Team ──────────────────────────────────────────────────────────────────────
async function renderTeam(el) {
  const users = allUsers;
  let teamPage = 1;
  let USERS_PER_PAGE = 20;

  function renderUserTable(filtered, page) {
    const total = filtered.length;
    const totalPages = Math.ceil(total / USERS_PER_PAGE);
    const start = (page - 1) * USERS_PER_PAGE;
    const paged = filtered.slice(start, start + USERS_PER_PAGE);
    const tbody = document.getElementById('users-tbody');
    const pag = document.getElementById('team-pagination');
    const info = document.getElementById('users-page-info');
    
    if (!tbody) return;
    
    if (info) {
      info.textContent = `Displaying users ${start + 1} to ${Math.min(start + USERS_PER_PAGE, total)} of ${total}.`;
    }

    tbody.innerHTML = paged.map(u => {
      // Use real data from the backend
      const loginCount = u.login_count || 1;
      const lastLogin = u.last_login ? fmt(u.last_login) : 'Never logged in';
      
      // Determine group name based on real backend role
      let groupName = 'Jira Software Users';
      if (u.role.includes('admin')) groupName = 'Jira Administrators';
      else if (u.role.includes('qa')) groupName = 'Quality Assurance';
      else if (u.role.includes('devops')) groupName = 'DevOps Admin';
      else if (u.role.includes('project_manager') || u.role.includes('scrum_master')) groupName = 'Project Management';
      else if (u.role.includes('security')) groupName = 'Security Specialists';
      
      return `<tr style="border-bottom:1px solid #f1f5f9;transition:background 0.1s;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
        <td style="padding:12px 14px;vertical-align:middle;display:flex;align-items:center;gap:8px;">
          <div style="background:${u.avatar_color || '#1B1F6B'};width:24px;height:24px;border-radius:50%;color:#fff;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;">
            ${getInitials(u.full_name)}
          </div>
          <span style="color:#0052CC;font-weight:600;cursor:pointer;" onclick="toast('User profile loaded','info')">${u.full_name}</span>
        </td>
        <td style="padding:12px 14px;vertical-align:middle;">
          <div style="color:#1e293b;font-weight:500;font-size:12.5px;">${u.username}</div>
          <div style="color:#64748b;font-size:11.5px;">${u.email}</div>
        </td>
        <td style="padding:12px 14px;vertical-align:middle;font-size:12px;color:#334155;line-height:1.4;">
          <strong>Count:</strong> ${loginCount}<br/>
          <span style="color:#64748b;"><strong>Last:</strong> ${lastLogin}</span>
        </td>
        <td style="padding:12px 14px;vertical-align:middle;max-width:240px;line-height:1.5;">
          <span style="color:#0052CC;font-size:11.5px;cursor:pointer;display:inline-block;margin-right:6px;" onclick="toast('Group page loaded','info')">${groupName}</span>
        </td>
        <td style="padding:12px 14px;vertical-align:middle;color:#475569;font-size:12.5px;">Jira Software</td>
        <td style="padding:12px 14px;vertical-align:middle;color:#475569;font-size:12.5px;">Jira Internal Directory</td>
        <td style="padding:12px 14px;vertical-align:middle;white-space:nowrap;">
          <span style="color:#0052CC;cursor:pointer;font-weight:600;font-size:12.5px;margin-right:8px;" onclick="toast('User edit modal opened','info')">Edit</span>
          <i class="fa fa-ellipsis-h" style="color:#64748b;cursor:pointer;" onclick="toast('Actions menu opened','info')"></i>
        </td>
      </tr>`;
    }).join('');

    if (pag && totalPages > 1) {
      let btns = `<button class="page-btn" onclick="teamPage=Math.max(1,teamPage-1);renderUserTable(window._teamFiltered||allUsers,teamPage)" ${page === 1 ? 'disabled' : ''}>&lt; Prev</button>`;
      for (let p = 1; p <= totalPages; p++) {
        btns += `<button class="page-btn ${p === page ? 'active' : ''}" onclick="teamPage=${p};renderUserTable(window._teamFiltered||allUsers,teamPage)">${p}</button>`;
      }
      btns += `<button class="page-btn" onclick="teamPage=Math.min(${totalPages},teamPage+1);renderUserTable(window._teamFiltered||allUsers,teamPage)" ${page === totalPages ? 'disabled' : ''}>Next &gt;</button>`;
      pag.innerHTML = `<div style="display:flex;justify-content:end;margin-top:10px;">${btns}</div>`;
    } else if (pag) {
      pag.innerHTML = '';
    }
  }

  el.innerHTML = `
    <div class="page-header" style="margin-bottom:16px;">
      <div>
        <div class="page-title" style="font-size:22px;color:#1B1F6B;font-weight:700;">Users</div>
      </div>
      <div style="display:flex;gap:8px;margin-left:auto;">
        <button class="btn btn-sm btn-outline" style="background:#fff;padding:6px 12px;font-size:12px;font-weight:500;border:1px solid #cbd5e1;border-radius:4px;" onclick="toast('Invite users module','info')">Invite users</button>
        <button class="btn btn-sm btn-outline" style="background:#fff;padding:6px 12px;font-size:12px;font-weight:500;border:1px solid #cbd5e1;border-radius:4px;" onclick="openCreateUser()">Create user</button>
      </div>
    </div>

    <!-- Directory Filters -->
    <div class="filter-bar" style="background:#fff;padding:14px;border-radius:6px;border:1px solid #e2e8f0;display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-bottom:14px;">
      <div style="display:flex;flex-direction:column;gap:4px;">
        <span style="font-size:11.5px;color:#64748b;font-weight:600;">Filter users</span>
        <div style="position:relative;display:flex;align-items:center;">
          <input type="text" id="team-search" placeholder="Name, username or email contains" oninput="filterTeam()" style="padding:6px 10px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;width:220px;outline:none;"/>
        </div>
      </div>

      <div style="display:flex;flex-direction:column;gap:4px;">
        <span style="font-size:11.5px;color:#64748b;font-weight:600;">Application access</span>
        <select id="team-filter-app" onchange="filterTeam()" style="padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;">
          <option value="">All Users</option>
          <option value="jira-software">Jira Software</option>
        </select>
      </div>

      <div style="display:flex;flex-direction:column;gap:4px;">
        <span style="font-size:11.5px;color:#64748b;font-weight:600;">Status</span>
        <select id="team-filter-status" onchange="filterTeam()" style="padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;">
          <option value="">All Users</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      <div style="display:flex;flex-direction:column;gap:4px;">
        <span style="font-size:11.5px;color:#64748b;font-weight:600;">Users per page</span>
        <select id="team-users-per-page" onchange="changeUsersLimit()" style="padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;">
          <option value="20">20</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
      </div>

      <div style="align-self:end;display:flex;gap:8px;">
        <button class="btn btn-primary btn-sm" onclick="filterTeam()" style="padding:6px 14px;border-radius:4px;font-size:12px;">Filter</button>
        <span style="color:#0052CC;cursor:pointer;font-size:12px;font-weight:600;align-self:center;" onclick="resetTeamFilters()">Reset</span>
      </div>
    </div>

    <!-- Users Table Info Summary -->
    <div id="users-page-info" style="font-size:12.5px;color:#475569;font-weight:600;margin-bottom:8px;padding:0 4px;">Loading directory...</div>

    <!-- Table Container -->
    <div class="tbl-wrap" style="background:#fff;border-radius:6px;border:1px solid #e2e8f0;overflow-x:auto;">
      <table style="width:100%;border-collapse:collapse;font-size:13px;text-align:left;">
        <thead>
          <tr style="background:#f8fafc;border-bottom:1px solid #cbd5e1;color:#475569;font-weight:600;">
            <th style="padding:10px 14px;">Full name</th>
            <th style="padding:10px 14px;">Username</th>
            <th style="padding:10px 14px;width:160px;">Login details</th>
            <th style="padding:10px 14px;width:240px;">Group name</th>
            <th style="padding:10px 14px;width:120px;">Applications</th>
            <th style="padding:10px 14px;width:165px;">Directory</th>
            <th style="padding:10px 14px;width:100px;">Actions</th>
          </tr>
        </thead>
        <tbody id="users-tbody"></tbody>
      </table>
    </div>
    
    <div id="team-pagination"></div>
  `;

  window._teamFiltered = users;
  renderUserTable(users, 1);

  window.filterTeam = function() {
    const status = document.getElementById('team-filter-status')?.value;
    const search = document.getElementById('team-search')?.value.toLowerCase();
    
    let filtered = allUsers;
    if (status === 'active') filtered = filtered.filter(u => u.is_active);
    if (status === 'inactive') filtered = filtered.filter(u => !u.is_active);
    
    if (search) {
      filtered = filtered.filter(u => 
        u.full_name.toLowerCase().includes(search) || 
        u.username.toLowerCase().includes(search) || 
        u.email.toLowerCase().includes(search)
      );
    }
    
    window._teamFiltered = filtered;
    teamPage = 1;
    renderUserTable(filtered, 1);
  };

  window.changeUsersLimit = function() {
    const lim = document.getElementById('team-users-per-page')?.value;
    if (lim) {
      USERS_PER_PAGE = parseInt(lim);
      teamPage = 1;
      renderUserTable(window._teamFiltered || allUsers, 1);
    }
  };

  window.resetTeamFilters = function() {
    const search = document.getElementById('team-search'); if (search) search.value = "";
    const app = document.getElementById('team-filter-app'); if (app) app.value = "";
    const status = document.getElementById('team-filter-status'); if (status) status.value = "";
    filterTeam();
  };
}

// ── Reports ───────────────────────────────────────────────────────────────────
async function renderReports(el) {
  let summary = [];
  try { summary = await api('GET', '/api/dashboard/projects/summary'); } catch(e) {}
  
  const IS_DEV = ['developer','devops_engineer','security_engineer','qa_engineer'].includes(currentUser.role);
  
  if (IS_DEV) {
    el.innerHTML = `
      <div class="page-header"><div class="page-title">Reports & Analytics</div></div>
      <div class="empty-state"><i class="fa fa-lock"></i><h3>Access Restricted</h3><p>Detailed reports and organization analytics are restricted to Project Managers and Administrators.</p></div>
    `;
    return;
  }

  el.innerHTML = `
    <div class="page-header" style="margin-bottom:16px;">
      <div>
        <div class="page-title" style="font-size:22px;color:#1B1F6B;font-weight:700;">Reports & Analytics</div>
        <div class="page-subtitle">Project status and performance metrics</div>
      </div>
    </div>
    
    <div class="card" style="box-shadow:0 1px 3px rgba(0,0,0,0.05);border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;">
      <div class="card-title" style="background:#1B1F6B;color:#fff;padding:12px 16px;margin:0;font-size:14px;"><i class="fa fa-folder-open" style="margin-right:8px;"></i> Project Summary & Status Breakdown</div>
      <div class="tbl-wrap" style="padding:0;">
        <table style="width:100%;border-collapse:collapse;font-size:13px;text-align:left;">
          <thead>
            <tr style="background:#f8fafc;border-bottom:1px solid #cbd5e1;color:#475569;font-weight:600;">
              <th style="padding:12px 16px;width:25%;">Project</th>
              <th style="padding:12px 16px;width:10%;">Type</th>
              <th style="padding:12px 16px;width:10%;text-align:center;">Total</th>
              <th style="padding:12px 16px;width:35%;">Status Breakdown (To Do / In Progress / Done)</th>
              <th style="padding:12px 16px;width:20%;">Overall Progress</th>
            </tr>
          </thead>
          <tbody>
            ${summary.length ? summary.map(p => {
              const total = p.total_issues || 0;
              const done = p.done_issues || 0;
              const prog = p.progress_issues || 0;
              const todo = p.todo_issues || 0;
              const pct = total > 0 ? Math.round((done / total) * 100) : 0;
              const typeIcon = p.project_type === 'kanban' ? 'fa-columns' : p.project_type === 'task_tracking' ? 'fa-tasks' : p.project_type === 'business' ? 'fa-briefcase' : 'fa-sync-alt';
              const typeColor = p.project_type === 'kanban' ? '#5243AA' : p.project_type === 'task_tracking' ? '#00875A' : p.project_type === 'business' ? '#FF9900' : '#0052CC';
              const typeName = (p.project_type||'scrum').replace('_',' ');
              
              const wTodo = total > 0 ? (todo/total)*100 : 0;
              const wProg = total > 0 ? (prog/total)*100 : 0;
              const wDone = total > 0 ? (done/total)*100 : 0;
              
              return `<tr style="border-bottom:1px solid #f1f5f9;">
                <td style="padding:12px 16px;">
                  <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:24px;height:24px;border-radius:4px;background:${p.color||'#1B1F6B'};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:10px;">${p.name.charAt(0)}</div>
                    <div>
                      <div style="font-weight:600;color:#1e293b;font-size:13.5px;">${p.name}</div>
                      <div style="font-size:11.5px;color:#64748b;margin-top:2px;font-family:monospace;">${p.key}</div>
                    </div>
                  </div>
                </td>
                <td style="padding:12px 16px;">
                  <div style="display:flex;align-items:center;gap:6px;color:${typeColor};font-size:12px;text-transform:capitalize;">
                    <i class="fa ${typeIcon}"></i> ${typeName}
                  </div>
                </td>
                <td style="padding:12px 16px;text-align:center;font-weight:600;color:#334155;">${total}</td>
                <td style="padding:12px 16px;">
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div style="flex:1;display:flex;height:8px;border-radius:4px;overflow:hidden;background:#e2e8f0;">
                      ${wTodo>0 ? `<div style="width:${wTodo}%;background:#64748b;" title="${todo} To Do"></div>` : ''}
                      ${wProg>0 ? `<div style="width:${wProg}%;background:#f59e0b;" title="${prog} In Progress"></div>` : ''}
                      ${wDone>0 ? `<div style="width:${wDone}%;background:#10b981;" title="${done} Done"></div>` : ''}
                    </div>
                    <div style="font-size:11.5px;color:#475569;white-space:nowrap;width:70px;text-align:right;">
                      ${todo} / ${prog} / ${done}
                    </div>
                  </div>
                </td>
                <td style="padding:12px 16px;">
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div style="flex:1;height:6px;border-radius:3px;background:#e2e8f0;overflow:hidden;">
                      <div style="height:100%;width:${pct}%;background:${pct===100 ? '#10b981' : '#0ea5e9'};"></div>
                    </div>
                    <span style="font-size:12px;font-weight:600;color:#334155;width:32px;text-align:right;">${pct}%</span>
                  </div>
                </td>
              </tr>`;
            }).join('') : '<tr><td colspan="5" style="padding:30px;text-align:center;color:#64748b;">No active projects found.</td></tr>'}
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
      `).join('') : '<div class="empty-state"><i class="fa fa-bell-slash"></i><h3>No Notifications</h3><p>You are all caught up!</p></div>'}
    </div>
  `;
}

async function markAllRead() {
  await api('POST', '/api/notifications/mark-read');
  toast('All notifications marked as read', 'success');
  loadNotifications();
  renderNotifications(document.getElementById('page-notifications'));
}

async function markNotifRead(notifId, issueId) {
  await api('POST', `/api/notifications/${notifId}/read`);
  loadNotifications();
  if (issueId) openIssueDetail(issueId);
}

// ── Settings ──────────────────────────────────────────────────────────────────
async function renderSettings(el) {
  let statuses = [];
  let rules = [];
  try {
    statuses = await api('GET', '/api/workflow/statuses');
    rules = await api('GET', '/api/workflow/rules');
  } catch (err) {
    console.error("Failed to load workflow configurations:", err);
  }

  const isAdmin = ['super_admin', 'admin', 'project_manager'].includes(currentUser.role);

  el.innerHTML = `
    <div class="page-header" style="margin-bottom:16px;">
      <div>
        <div class="page-title" style="font-size:22px;color:#1B1F6B;font-weight:700;">Settings</div>
        <div class="page-subtitle">Configure your profile and system workflow parameters</div>
      </div>
    </div>

    <!-- Cohesive Settings Tabs -->
    <div style="display:flex;gap:16px;border-bottom:2px solid #cbd5e1;margin-bottom:20px;">
      <div class="settings-tab active" id="settings-tab-profile" onclick="switchSettingsTab('profile')" style="padding:10px 16px;cursor:pointer;font-weight:600;font-size:13.5px;color:#475569;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all 0.15s;">
        <i class="fa fa-user-circle"></i> Profile & System
      </div>
      <div class="settings-tab" id="settings-tab-workflow" onclick="switchSettingsTab('workflow')" style="padding:10px 16px;cursor:pointer;font-weight:600;font-size:13.5px;color:#475569;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all 0.15s;">
        <i class="fa fa-sliders-h"></i> Workflow Statuses & Transitions
      </div>
    </div>

    <!-- Profile & System Info Pane -->
    <div class="settings-pane" id="settings-profile-pane" style="display:block;">
      <div class="card" style="box-shadow:0 1px 3px rgba(0,0,0,0.05);border:1px solid #e2e8f0;border-radius:6px;">
        <div class="card-title" style="color:#1B1F6B;font-weight:700;font-size:15px;margin-bottom:16px;"><i class="fa fa-user-circle"></i> Profile Detail</div>
        <div class="two-col" style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
          <div class="detail-field"><div class="detail-label" style="font-size:11.5px;color:#64748b;font-weight:600;text-transform:uppercase;">Full Name</div><div class="detail-value" style="font-size:14px;color:#1e293b;font-weight:500;margin-top:2px;">${currentUser.full_name}</div></div>
          <div class="detail-field"><div class="detail-label" style="font-size:11.5px;color:#64748b;font-weight:600;text-transform:uppercase;">Username</div><div class="detail-value" style="font-size:14px;color:#1e293b;font-weight:500;margin-top:2px;">${currentUser.username}</div></div>
          <div class="detail-field"><div class="detail-label" style="font-size:11.5px;color:#64748b;font-weight:600;text-transform:uppercase;">Email Address</div><div class="detail-value" style="font-size:14px;color:#1e293b;font-weight:500;margin-top:2px;">${currentUser.email}</div></div>
          <div class="detail-field"><div class="detail-label" style="font-size:11.5px;color:#64748b;font-weight:600;text-transform:uppercase;">Role</div><div class="detail-value" style="margin-top:2px;">${getRoleBadge(currentUser.role)}</div></div>
          <div class="detail-field"><div class="detail-label" style="font-size:11.5px;color:#64748b;font-weight:600;text-transform:uppercase;">Department</div><div class="detail-value" style="font-size:14px;color:#1e293b;font-weight:500;margin-top:2px;">${currentUser.department || '-'}</div></div>
          <div class="detail-field"><div class="detail-label" style="font-size:11.5px;color:#64748b;font-weight:600;text-transform:uppercase;">Branch</div><div class="detail-value" style="font-size:14px;color:#1e293b;font-weight:500;margin-top:2px;">${currentUser.branch || '-'}</div></div>
        </div>
      </div>
      
      <div class="card" style="margin-top:16px;box-shadow:0 1px 3px rgba(0,0,0,0.05);border:1px solid #e2e8f0;border-radius:6px;">
        <div class="card-title" style="color:#1B1F6B;font-weight:700;font-size:15px;margin-bottom:12px;"><i class="fa fa-info-circle"></i> System Information</div>
        <div class="metric-row" style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:13.5px;"><span class="metric-label" style="color:#64748b;">Version</span><span class="metric-value" style="color:#1e293b;font-weight:600;">1.0.0</span></div>
        <div class="metric-row" style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:13.5px;"><span class="metric-label" style="color:#64748b;">Backend API Endpoint</span><span class="metric-value" style="color:#1e293b;font-weight:600;font-family:monospace;">${API_BASE}</span></div>
        <div class="metric-row" style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:13.5px;"><span class="metric-label" style="color:#64748b;">Total Tracked Projects</span><span class="metric-value" style="color:#1e293b;font-weight:600;">${allProjects.length}</span></div>
        <div class="metric-row" style="display:flex;justify-content:space-between;padding:10px 0;font-size:13.5px;"><span class="metric-label" style="color:#64748b;">Total User Directory Members</span><span class="metric-value" style="color:#1e293b;font-weight:600;">${allUsers.length}</span></div>
      </div>
    </div>

    <!-- Workflow Settings Pane -->
    <div class="settings-pane" id="settings-workflow-pane" style="display:none;">
      <!-- Custom Status Configuration Card -->
      <div class="card" style="box-shadow:0 1px 3px rgba(0,0,0,0.05);border:1px solid #e2e8f0;border-radius:6px;margin-bottom:16px;">
        <div class="card-title" style="color:#1B1F6B;font-weight:700;font-size:15px;margin-bottom:12px;"><i class="fa fa-tag"></i> Dynamic Workflow Statuses</div>
        
        <div style="overflow-x:auto;">
          <table style="width:100%;border-collapse:collapse;font-size:13px;text-align:left;margin-bottom:16px;">
            <thead>
              <tr style="background:#f8fafc;border-bottom:1px solid #cbd5e1;color:#475569;font-weight:600;">
                <th style="padding:10px;">Name</th>
                <th style="padding:10px;">Key / Identifier</th>
                <th style="padding:10px;">Category</th>
                <th style="padding:10px;">Visual Color</th>
                <th style="padding:10px;text-align:center;">Order Index</th>
                ${isAdmin ? '<th style="padding:10px;text-align:center;width:60px;">Action</th>' : ''}
              </tr>
            </thead>
            <tbody>
              ${statuses.map(s => `
                <tr style="border-bottom:1px solid #f1f5f9;">
                  <td style="padding:10px;font-weight:600;color:#1e293b;">${s.name}</td>
                  <td style="padding:10px;"><code style="background:#f1f5f9;color:#e11d48;padding:2px 6px;border-radius:4px;font-family:monospace;">${s.key}</code></td>
                  <td style="padding:10px;"><span class="badge" style="background:#e2e8f0;color:#334155;">${s.category.toUpperCase()}</span></td>
                  <td style="padding:10px;display:flex;align-items:center;gap:6px;margin-top:2px;">
                    <div style="width:14px;height:14px;border-radius:3px;background:${s.color};"></div>
                    <span>${s.color}</span>
                  </td>
                  <td style="padding:10px;text-align:center;font-weight:500;">${s.order_index}</td>
                  ${isAdmin ? `
                    <td style="padding:10px;text-align:center;">
                      <i class="fa fa-trash-alt" style="color:#dc2626;cursor:pointer;font-size:14px;" onclick="deleteCustomStatus(${s.id})" title="Delete Status"></i>
                    </td>
                  ` : ''}
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Add Custom Status Form (Admins/PMs only) -->
        ${isAdmin ? `
          <div style="background:#f8fafc;padding:14px;border-radius:6px;border:1px solid #e2e8f0;margin-top:10px;">
            <div style="font-size:13px;font-weight:700;color:#1B1F6B;margin-bottom:10px;">Add Custom Status Option</div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">
              <input type="text" id="new-status-name" placeholder="Status Name (e.g. In Review)" style="padding:6px 10px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;flex:1;min-width:140px;outline:none;"/>
              <input type="text" id="new-status-key" placeholder="Status Key (e.g. in_review)" style="padding:6px 10px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;flex:1;min-width:140px;outline:none;"/>
              
              <select id="new-status-category" style="padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;">
                <option value="todo">To Do (backlog/incoming)</option>
                <option value="in_progress">In Progress (active development/test)</option>
                <option value="done">Done (completed/closed)</option>
              </select>

              <select id="new-status-color" style="padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;">
                <option value="#64748b" style="color:#64748b;font-weight:700;">Gray (Default)</option>
                <option value="#0052CC" style="color:#0052CC;font-weight:700;">Blue (Atlassian)</option>
                <option value="#ea580c" style="color:#ea580c;font-weight:700;">Orange (In Dev)</option>
                <option value="#e11d48" style="color:#e11d48;font-weight:700;">Red (Blocked)</option>
                <option value="#16a34a" style="color:#16a34a;font-weight:700;">Green (Completed)</option>
                <option value="#7c3aed" style="color:#7c3aed;font-weight:700;">Purple (UAT)</option>
              </select>

              <input type="number" id="new-status-order" value="${statuses.length}" placeholder="Order Index" style="padding:6px 10px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;width:80px;outline:none;"/>
              
              <button class="btn btn-primary btn-sm" onclick="createCustomStatus()" style="padding:6px 14px;font-size:12px;font-weight:600;border-radius:4px;">Add Status</button>
            </div>
          </div>
        ` : '<div style="font-size:12px;color:#64748b;text-align:center;padding:8px;"><i class="fa fa-lock"></i> Only super administrators and project managers can create custom status layers.</div>'}
      </div>

      <!-- Transition Enforcement Settings Card -->
      <div class="card" style="box-shadow:0 1px 3px rgba(0,0,0,0.05);border:1px solid #e2e8f0;border-radius:6px;">
        <div class="card-title" style="color:#1B1F6B;font-weight:700;font-size:15px;margin-bottom:12px;"><i class="fa fa-exchange-alt"></i> Workflow Transition Constraints</div>
        <div style="font-size:12.5px;color:#64748b;margin-bottom:14px;line-height:1.4;">
          Specify explicit role authorization settings controlling transition states. Empty rules list defaults to open transition permission.
        </div>

        <div style="overflow-x:auto;">
          <table style="width:100%;border-collapse:collapse;font-size:13px;text-align:left;margin-bottom:16px;">
            <thead>
              <tr style="background:#f8fafc;border-bottom:1px solid #cbd5e1;color:#475569;font-weight:600;">
                <th style="padding:10px;">Source Status</th>
                <th style="padding:10px;text-align:center;width:40px;"><i class="fa fa-arrow-right"></i></th>
                <th style="padding:10px;">Target Status</th>
                <th style="padding:10px;">Authorized User Role</th>
                ${isAdmin ? '<th style="padding:10px;text-align:center;width:60px;">Action</th>' : ''}
              </tr>
            </thead>
            <tbody>
              ${rules.length === 0 ? `
                <tr><td colspan="5" style="text-align:center;padding:25px;color:#64748b;"><i class="fa fa-info-circle"></i> No specific rules defined. Board uses default open transition schema.</td></tr>
              ` : rules.map(r => `
                <tr style="border-bottom:1px solid #f1f5f9;">
                  <td style="padding:10px;"><code style="background:#e0f2fe;color:#0369a1;padding:2px 6px;border-radius:4px;font-family:monospace;font-weight:600;">${r.from_status_key.toUpperCase()}</code></td>
                  <td style="padding:10px;text-align:center;color:#64748b;"><i class="fa fa-long-arrow-alt-right"></i></td>
                  <td style="padding:10px;"><code style="background:#dcfce7;color:#15803d;padding:2px 6px;border-radius:4px;font-family:monospace;font-weight:600;">${r.to_status_key.toUpperCase()}</code></td>
                  <td style="padding:10px;">${getRoleBadge(r.allowed_role)}</td>
                  ${isAdmin ? `
                    <td style="padding:10px;text-align:center;">
                      <i class="fa fa-trash-alt" style="color:#dc2626;cursor:pointer;font-size:14px;" onclick="deleteTransitionRule(${r.id})" title="Delete Transition Constraints"></i>
                    </td>
                  ` : ''}
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Add Transition Constraints Form -->
        ${isAdmin ? `
          <div style="background:#f8fafc;padding:14px;border-radius:6px;border:1px solid #e2e8f0;margin-top:10px;">
            <div style="font-size:13px;font-weight:700;color:#1B1F6B;margin-bottom:10px;">Add Role Transition Authorization Rule</div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">
              <select id="new-rule-from" style="padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;flex:1;min-width:130px;">
                <option value="">Any State (*)</option>
                ${statuses.map(s => `<option value="${s.key}">${s.name} (${s.key})</option>`).join('')}
              </select>

              <select id="new-rule-to" style="padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;flex:1;min-width:130px;">
                ${statuses.map(s => `<option value="${s.key}">${s.name} (${s.key})</option>`).join('')}
              </select>

              <select id="new-rule-role" style="padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;flex:1;min-width:150px;">
                <option value="super_admin">Super Administrator</option>
                <option value="admin">System Administrator</option>
                <option value="project_manager">Project Manager</option>
                <option value="scrum_master">Scrum Master</option>
                <option value="developer">Developer</option>
                <option value="qa_engineer">QA Engineer</option>
                <option value="devops_engineer">DevOps Engineer</option>
                <option value="security_engineer">Security Specialist</option>
                <option value="business_analyst">Business Analyst</option>
                <option value="viewer">Viewer</option>
              </select>

              <button class="btn btn-primary btn-sm" onclick="createTransitionRule()" style="padding:6px 14px;font-size:12px;font-weight:600;border-radius:4px;">Define Rule</button>
            </div>
          </div>
        ` : ''}
      </div>
    </div>
  `;

  // Dynamic Tabs Switching Engine
  window.switchSettingsTab = function(tabName) {
    document.querySelectorAll('.settings-pane').forEach(p => p.style.display = 'none');
    document.querySelectorAll('.settings-tab').forEach(t => {
      t.style.color = '#475569';
      t.style.borderBottomColor = 'transparent';
    });

    const activePane = document.getElementById(`settings-${tabName}-pane`);
    if (activePane) activePane.style.display = 'block';

    const activeTab = document.getElementById(`settings-tab-${tabName}`);
    if (activeTab) {
      activeTab.style.color = '#1B1F6B';
      activeTab.style.borderBottomColor = '#1B1F6B';
    }
    
    // Remember current active settings tab in session state
    window._activeSettingsTab = tabName;
  };

  // Add Dynamic CRUD Handlers for workflow
  window.createCustomStatus = async function() {
    const name = document.getElementById('new-status-name')?.value.trim();
    const key = document.getElementById('new-status-key')?.value.trim();
    const category = document.getElementById('new-status-category')?.value;
    const color = document.getElementById('new-status-color')?.value;
    const orderStr = document.getElementById('new-status-order')?.value;

    if (!name || !key) {
      toast('Please supply both status name and valid key identifier', 'error');
      return;
    }

    try {
      await api('POST', '/api/workflow/statuses', {
        name: name,
        key: key,
        color: color,
        category: category,
        order_index: parseInt(orderStr || '0')
      });
      toast('Workflow Custom Status added successfully', 'success');
      
      // Refresh Settings View and preserve tab state
      await renderSettings(el);
      switchSettingsTab(window._activeSettingsTab || 'workflow');
    } catch (e) {
      toast(e.message || 'Error occurred while saving custom status option', 'error');
    }
  };

  window.deleteCustomStatus = async function(statusId) {
    if (!confirm('Are you sure you want to remove this workflow status? This could affect issues utilizing this state.')) return;
    try {
      await api('DELETE', `/api/workflow/statuses/${statusId}`);
      toast('Status removed successfully', 'success');
      await renderSettings(el);
      switchSettingsTab(window._activeSettingsTab || 'workflow');
    } catch(e) {
      toast(e.message || 'Failed to delete status', 'error');
    }
  };

  window.createTransitionRule = async function() {
    const fromVal = document.getElementById('new-rule-from')?.value;
    const toVal = document.getElementById('new-rule-to')?.value;
    const roleVal = document.getElementById('new-rule-role')?.value;

    if (!toVal || !roleVal) {
      toast('Please verify target state and authorized user role options', 'error');
      return;
    }

    try {
      await api('POST', '/api/workflow/rules', {
        from_status_key: fromVal || '*',
        to_status_key: toVal,
        allowed_role: roleVal
      });
      toast('Workflow Role Transition Constraint enforced successfully', 'success');
      await renderSettings(el);
      switchSettingsTab(window._activeSettingsTab || 'workflow');
    } catch(e) {
      toast(e.message || 'Failed to register transition rule', 'error');
    }
  };

  window.deleteTransitionRule = async function(ruleId) {
    if (!confirm('Remove this workflow transition constraint?')) return;
    try {
      await api('DELETE', `/api/workflow/rules/${ruleId}`);
      toast('Constraint rule deleted successfully', 'success');
      await renderSettings(el);
      switchSettingsTab(window._activeSettingsTab || 'workflow');
    } catch(e) {
      toast(e.message || 'Failed to remove rule constraint', 'error');
    }
  };

  // Restore active tab memory if preserved
  if (window._activeSettingsTab) {
    switchSettingsTab(window._activeSettingsTab);
  } else {
    switchSettingsTab('profile');
  }
}

// ── Roadmap (Placeholder) ─────────────────────────────────────────────────────
async function renderRoadmap(el) {
  el.innerHTML = '<div class="empty-state"><i class="fa fa-road"></i><h3>Roadmap View</h3><p>Timeline and roadmap visualization coming soon</p></div>';
}

// ── Issue Detail ──────────────────────────────────────────────────────────────
async function openIssueDetail(issueId) {
  openModal('issue-detail');
  const body = document.getElementById('issue-detail-body');
  body.innerHTML = '<div style="text-align:center;padding:40px;"><div class="spinner"></div></div>';
  try {
    const issue = await api('GET', `/api/issues/${issueId}`);
    const comments = await api('GET', `/api/issues/${issueId}/comments`);
    const activity = await api('GET', `/api/issues/${issueId}/activity`);
    currentIssue = issue;
    document.getElementById('detail-key-title').innerHTML = `<strong style="color:#1B1F6B;">${issue.key}</strong> ${issue.title}`;
    body.innerHTML = `
      <div class="issue-tabs" style="justify-content: center; border-bottom: 1px solid #dfe1e6; margin-bottom: 30px;">
        <div class="issue-tab active" onclick="switchTab('details')" style="font-size: 15px; padding: 12px 24px;">Details</div>
        <div class="issue-tab" onclick="switchTab('comments')" style="font-size: 15px; padding: 12px 24px;">Comments (${comments.length})</div>
        <div class="issue-tab" onclick="switchTab('activity')" style="font-size: 15px; padding: 12px 24px;">Activity (${activity.length})</div>
      </div>
      
      <div style="max-width: 800px; margin: 0 auto;">
        <div id="tab-details" class="tab-pane active">
          <!-- Metadata centered grid -->
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; background: #f4f5f7; padding: 24px; border-radius: 8px; margin-bottom: 30px; text-align: center; border: 1px solid #dfe1e6;">
            <div><div class="detail-label">Status</div><div class="detail-value" style="margin-top:6px;">${getStatusBadge(issue.status)}</div></div>
            <div><div class="detail-label">Priority</div><div class="detail-value" style="margin-top:6px;">${getPriorityBadge(issue.priority)}</div></div>
            <div><div class="detail-label">Type</div><div class="detail-value" style="margin-top:6px;">${getTypeIcon(issue.issue_type)} <span style="text-transform:capitalize;">${issue.issue_type}</span></div></div>
            
            <div><div class="detail-label">Assignee</div><div class="detail-value" style="margin-top:6px;">${issue.assignee ? getAvatar(issue.assignee, 28) + ' <span style="vertical-align:middle;margin-left:6px;">' + issue.assignee.full_name + '</span>' : 'Unassigned'}</div></div>
            <div><div class="detail-label">Reporter</div><div class="detail-value" style="margin-top:6px;">${issue.reporter ? getAvatar(issue.reporter, 28) + ' <span style="vertical-align:middle;margin-left:6px;">' + issue.reporter.full_name + '</span>' : '-'}</div></div>
            <div><div class="detail-label">Sprint</div><div class="detail-value" style="margin-top:6px; font-weight:500;">${issue.sprint ? issue.sprint.name : 'No Sprint'}</div></div>
          </div>
          
          <div class="detail-field" style="margin-bottom: 30px;">
            <div class="detail-label" style="font-size: 13px; margin-bottom: 12px;">Description</div>
            <div class="detail-value" style="font-size: 15px; line-height: 1.6; color: #172B4D; background: #fff; padding: 20px; border: 1px solid #dfe1e6; border-radius: 8px;">${issue.description || '<em style="color:#6b7280;">No description provided.</em>'}</div>
          </div>
          
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #6b7280; border-top: 1px solid #dfe1e6; padding-top: 16px;">
            <div><strong>Created:</strong> ${fmt(issue.created_at)}</div>
            <div><strong>Updated:</strong> ${fmt(issue.updated_at)}</div>
            <div><strong>Due Date:</strong> ${fmt(issue.due_date) || 'None'}</div>
          </div>
        </div>
        
        <div id="tab-comments" class="tab-pane">
          <div id="comments-list" style="margin-bottom: 24px;">${comments.map(c => `
            <div class="comment-item" style="background: ${c.is_internal ? '#fffbf0' : '#fff'}; border: 1px solid ${c.is_internal ? '#F5A623' : '#dfe1e6'}; padding: 16px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
              ${getAvatar(c.author, 36)}
              <div class="comment-body" style="background:transparent; padding:0; flex:1;">
                <div style="margin-bottom: 8px;"><strong class="comment-author" style="font-size:14px;">${c.author.full_name}</strong><span class="comment-time" style="margin-left:10px;">${fmtTime(c.created_at)}</span>${c.is_internal ? ' <span class="badge" style="background:#F5A623;color:#fff;font-size:10px;margin-left:8px;">Internal</span>' : ''}</div>
                <div class="comment-text" style="font-size:14px; color:#172B4D;">${c.content}</div>
              </div>
            </div>
          `).join('')}</div>
          <div class="form-group" style="margin-top:24px;"><textarea id="new-comment" rows="4" placeholder="Add a comment..." style="border-radius:8px;"></textarea></div>
          <div style="display:flex;gap:16px;align-items:center; margin-top: 12px;"><button class="btn btn-primary" onclick="addComment()"><i class="fa fa-comment"></i> Add Comment</button><label style="font-size:14px;display:flex;align-items:center;gap:6px;cursor:pointer;"><input type="checkbox" id="comment-internal"/> Internal Note</label></div>
        </div>
        
        <div id="tab-activity" class="tab-pane">
          <div style="background: #fff; border: 1px solid #dfe1e6; border-radius: 8px; padding: 16px;">
          ${activity.map(a => `
            <div class="audit-row" style="padding: 12px 0; border-bottom: 1px solid #f4f5f7;">
              <div class="audit-time" style="color:#5e6c84;">${fmtTime(a.created_at)}</div>
              <div class="audit-action" style="font-size: 14px; color: #172B4D;"><strong class="audit-user">${a.user.full_name}</strong> ${a.action.replace(/_/g, ' ')} ${a.field_changed ? `<strong>${a.field_changed}</strong>` : ''} ${a.old_value && a.new_value ? `from <em style="color:#6b7280;">${a.old_value}</em> to <strong>${a.new_value}</strong>` : ''}</div>
            </div>
          `).join('')}
          ${activity.length === 0 ? '<div style="text-align:center;color:#6b7280;padding:20px;">No activity logged yet.</div>' : ''}
          </div>
        </div>
      </div>
    `;
  } catch (e) {
    body.innerHTML = `<div class="empty-state"><i class="fa fa-exclamation-triangle"></i><h3>Error</h3><p>${e.message}</p></div>`;
  }
}

function switchTab(tab) {
  document.querySelectorAll('.issue-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelector(`.issue-tab:nth-child(${tab === 'details' ? 1 : tab === 'comments' ? 2 : 3})`).classList.add('active');
  document.getElementById(`tab-${tab}`).classList.add('active');
}

async function addComment() {
  const content = document.getElementById('new-comment').value.trim();
  const isInternal = document.getElementById('comment-internal').checked;
  if (!content) return toast('Comment cannot be empty', 'error');
  try {
    await api('POST', `/api/issues/${currentIssue.id}/comments`, {content, is_internal: isInternal});
    toast('Comment added', 'success');
    openIssueDetail(currentIssue.id);
  } catch (e) {}
}




// ── Groups / Teams ────────────────────────────────────────────────────────────
async function renderGroups(el) {
  let teams = [];
  try { teams = await api('GET', '/api/teams/'); } catch(e) {}
  const canManage = ['super_admin','admin','project_manager'].includes(currentUser.role);
  
  el.innerHTML = `
    <div class="page-header" style="margin-bottom:20px;">
      <div>
        <div class="page-title" style="font-size:22px;color:#1B1F6B;font-weight:700;">Teams &amp; Groups</div>
        <div class="page-subtitle" style="font-size:14px;color:#64748b;margin-top:2px;">Manage organizational divisions and team assignments</div>
      </div>
      ${canManage ? '<button class="btn btn-primary" onclick="openCreateTeamModal()" style="background:#1B1F6B;border:none;padding:8px 16px;font-size:13px;font-weight:600;border-radius:6px;"><i class="fa fa-plus" style="margin-right:6px;"></i> New Team</button>' : ''}
    </div>
    
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px;">
      ${teams.map(t => {
        const memberIds = t.members.map(m => m.id);
        const nonMembers = allUsers.filter(u => u.is_active && !memberIds.includes(u.id));
        
        return `
        <div class="team-card" style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.05);display:flex;flex-direction:column;">
          <div class="team-card-header" style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <div class="team-color-dot" style="background:${t.color || '#1B1F6B'};width:14px;height:14px;border-radius:50%;flex-shrink:0;"></div>
            <div style="flex:1;">
              <div class="team-name" style="font-size:16px;font-weight:700;color:#1e293b;">${t.name}</div>
              <div class="team-type" style="font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;">${t.team_type ? t.team_type.toUpperCase() : 'GENERAL'} TEAM</div>
            </div>
            <span class="badge" style="background:${t.color || '#1B1F6B'};color:#fff;font-size:11px;padding:2px 8px;border-radius:12px;">${t.member_count} members</span>
          </div>
          
          ${t.description ? `<div style="font-size:13px;color:#475569;margin-bottom:12px;line-height:1.4;">${t.description}</div>` : ''}
          
          <div style="font-size:12.5px;margin-bottom:14px;display:flex;align-items:center;gap:6px;color:#1e293b;">
            <i class="fa fa-crown" style="color:#F5A623;font-size:13px;"></i>
            <strong>Lead:</strong> 
            <span style="color:#0052CC;font-weight:600;">${t.lead ? t.lead.full_name : 'Unassigned'}</span>
          </div>
          
          <div style="border-top:1px solid #e2e8f0;padding-top:12px;margin-bottom:12px;flex:1;">
            <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;">Members</div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;">
              ${t.members.map(m => `
                <div style="display:flex;align-items:center;gap:6px;background:#f1f5f9;padding:4px 8px;border-radius:20px;border:1px solid #e2e8f0;">
                  <div style="background:${m.avatar_color || '#1B1F6B'};width:18px;height:18px;border-radius:50%;color:#fff;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:700;">
                    ${getInitials(m.full_name)}
                  </div>
                  <span style="font-size:11.5px;font-weight:500;color:#334155;">${m.full_name.split(' ')[0]}</span>
                  ${canManage ? `<i class="fa fa-times" style="color:#94a3b8;cursor:pointer;font-size:10px;margin-left:2px;" onclick="removeTeamMember(${t.id}, ${m.id})" onmouseover="this.style.color='#dc2626'" onmouseout="this.style.color='#94a3b8'"></i>` : ''}
                </div>
              `).join('')}
              ${t.members.length === 0 ? '<span style="font-size:12.5px;color:#94a3b8;font-style:italic;">No members yet</span>' : ''}
            </div>
          </div>

          ${canManage ? `
          <div style="border-top:1px solid #e2e8f0;padding-top:12px;display:flex;flex-direction:column;gap:8px;">
            <div style="display:flex;gap:6px;">
              <select id="add-member-select-${t.id}" style="flex:1;padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;background:#fff;outline:none;">
                <option value="">Add user to team...</option>
                ${nonMembers.map(u => `<option value="${u.id}">${u.full_name} (${u.role.replace(/_/g,' ')})</option>`).join('')}
              </select>
              <button class="btn btn-sm" onclick="addTeamMember(${t.id})" style="background:#f1f5f9;border:1px solid #cbd5e1;padding:4px 8px;border-radius:4px;cursor:pointer;"><i class="fa fa-plus" style="color:#1B1F6B;"></i></button>
            </div>
            
            <div style="display:flex;justify-content:end;gap:8px;margin-top:4px;">
              <button class="btn btn-sm btn-outline" onclick="openEditTeamModal(${t.id}, '${t.name.replace(/'/g, "\'")}', '${(t.description || '').replace(/'/g, "\'")}', '${t.color}', ${t.lead ? t.lead.id : 'null'}, '${t.team_type}')" style="font-size:11.5px;padding:4px 10px;border-radius:4px;border:1px solid #cbd5e1;background:#fff;cursor:pointer;font-weight:600;"><i class="fa fa-edit"></i> Edit Details</button>
            </div>
          </div>
          ` : ''}
        </div>
        `;
      }).join('')}
    </div>

    <!-- Dynamic Modal Container -->
    <div id="team-action-modal" class="modal-overlay" style="display:none;" onclick="if(event.target===this)closeTeamModal()">
      <div class="modal-content" style="max-width:420px;border-radius:8px;box-shadow:0 10px 25px rgba(0,0,0,0.15);overflow:hidden;padding:0;">
        <div class="modal-header" style="background:#1B1F6B;color:#fff;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;">
          <span class="modal-title" id="team-modal-title" style="font-size:16px;font-weight:700;">Create New Team</span>
          <button class="modal-close" onclick="closeTeamModal()" style="background:transparent;border:none;color:#fff;font-size:20px;cursor:pointer;">&times;</button>
        </div>
        <div style="padding:18px;display:flex;flex-direction:column;gap:12px;">
          <div>
            <label style="display:block;font-size:12px;font-weight:600;color:#334155;margin-bottom:4px;">Team Name *</label>
            <input type="text" id="tm-name" style="width:100%;padding:8px 10px;border:1px solid #cbd5e1;border-radius:4px;outline:none;font-size:13px;"/>
          </div>
          <div>
            <label style="display:block;font-size:12px;font-weight:600;color:#334155;margin-bottom:4px;">Team Type</label>
            <select id="tm-type" style="width:100%;padding:8px 10px;border:1px solid #cbd5e1;border-radius:4px;outline:none;font-size:13px;background:#fff;">
              <option value="general">General</option>
              <option value="dev">Development</option>
              <option value="qa">Quality Assurance</option>
              <option value="devops">DevOps</option>
              <option value="pm">Project Management</option>
              <option value="ba">Business Analysis</option>
              <option value="security">Security</option>
            </select>
          </div>
          <div>
            <label style="display:block;font-size:12px;font-weight:600;color:#334155;margin-bottom:4px;">Description</label>
            <textarea id="tm-desc" rows="3" style="width:100%;padding:8px 10px;border:1px solid #cbd5e1;border-radius:4px;outline:none;font-size:13px;resize:none;"></textarea>
          </div>
          <div>
            <label style="display:block;font-size:12px;font-weight:600;color:#334155;margin-bottom:4px;">Team Color</label>
            <input type="color" id="tm-color" value="#1B1F6B" style="width:100%;height:38px;padding:2px 4px;border:1px solid #cbd5e1;border-radius:4px;outline:none;background:#fff;"/>
          </div>
          <div>
            <label style="display:block;font-size:12px;font-weight:600;color:#334155;margin-bottom:4px;">Team Lead</label>
            <select id="tm-lead" style="width:100%;padding:8px 10px;border:1px solid #cbd5e1;border-radius:4px;outline:none;font-size:13px;background:#fff;">
              <option value="">Select Lead...</option>
              ${allUsers.filter(u => u.is_active).map(u => `<option value="${u.id}">${u.full_name} (${u.role.replace(/_/g,' ')})</option>`).join('')}
            </select>
          </div>
          
          <div style="display:flex;justify-content:end;gap:8px;margin-top:10px;border-top:1px solid #e2e8f0;padding-top:14px;">
            <button class="btn btn-outline" onclick="closeTeamModal()" style="font-size:12.5px;padding:6px 14px;border:1px solid #cbd5e1;background:#fff;">Cancel</button>
            <button class="btn btn-primary" id="team-submit-btn" style="font-size:12.5px;padding:6px 18px;background:#1B1F6B;border:none;">Save</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function closeTeamModal() {
  const modal = document.getElementById('team-action-modal');
  if (modal) modal.style.display = 'none';
}

function openCreateTeamModal() {
  document.getElementById('team-modal-title').textContent = 'Create New Team';
  document.getElementById('tm-name').value = '';
  document.getElementById('tm-type').value = 'general';
  document.getElementById('tm-desc').value = '';
  document.getElementById('tm-color').value = '#1B1F6B';
  document.getElementById('tm-lead').value = '';
  
  const submitBtn = document.getElementById('team-submit-btn');
  submitBtn.onclick = submitCreateTeam;
  
  document.getElementById('team-action-modal').style.display = 'flex';
}

async function submitCreateTeam() {
  const name = document.getElementById('tm-name').value.trim();
  const team_type = document.getElementById('tm-type').value;
  const description = document.getElementById('tm-desc').value.trim();
  const color = document.getElementById('tm-color').value;
  const lead_val = document.getElementById('tm-lead').value;
  const lead_id = lead_val ? parseInt(lead_val) : null;
  
  if (!name) {
    toast('Team name is required', 'error');
    return;
  }
  
  try {
    let query = `?name=${encodeURIComponent(name)}&team_type=${encodeURIComponent(team_type)}&description=${encodeURIComponent(description)}&color=${encodeURIComponent(color)}`;
    if (lead_id) query += `&lead_id=${lead_id}`;
    
    await api('POST', `/api/teams/${query}`);
    toast('Team created successfully', 'success');
    closeTeamModal();
    nav('groups');
  } catch(e) {
    toast('Failed to create team', 'error');
  }
}

function openEditTeamModal(id, name, desc, color, leadId, teamType) {
  document.getElementById('team-modal-title').textContent = 'Edit Team Details';
  document.getElementById('tm-name').value = name;
  document.getElementById('tm-type').value = teamType || 'general';
  document.getElementById('tm-desc').value = desc || '';
  document.getElementById('tm-color').value = color || '#1B1F6B';
  document.getElementById('tm-lead').value = leadId || '';
  
  const submitBtn = document.getElementById('team-submit-btn');
  submitBtn.onclick = () => submitEditTeam(id);
  
  document.getElementById('team-action-modal').style.display = 'flex';
}

async function submitEditTeam(id) {
  const name = document.getElementById('tm-name').value.trim();
  const team_type = document.getElementById('tm-type').value;
  const description = document.getElementById('tm-desc').value.trim();
  const color = document.getElementById('tm-color').value;
  const lead_val = document.getElementById('tm-lead').value;
  const lead_id = lead_val ? parseInt(lead_val) : null;
  
  if (!name) {
    toast('Team name is required', 'error');
    return;
  }
  
  try {
    let query = `?name=${encodeURIComponent(name)}&team_type=${encodeURIComponent(team_type)}&description=${encodeURIComponent(description)}&color=${encodeURIComponent(color)}`;
    if (lead_id) query += `&lead_id=${lead_id}`;
    
    await api('PUT', `/api/teams/${id}${query}`);
    toast('Team details updated successfully', 'success');
    closeTeamModal();
    nav('groups');
  } catch(e) {
    toast('Failed to update team', 'error');
  }
}

async function addTeamMember(teamId) {
  const selectEl = document.getElementById(`add-member-select-${teamId}`);
  if (!selectEl || !selectEl.value) {
    toast('Please select a user to add', 'error');
    return;
  }
  const userId = parseInt(selectEl.value);
  try {
    await api('POST', `/api/teams/${teamId}/members/${userId}`);
    toast('User added to team successfully', 'success');
    nav('groups');
  } catch(e) {
    toast('Failed to add user to team', 'error');
  }
}

async function removeTeamMember(teamId, userId) {
  if (!confirm('Are you sure you want to remove this member from the team?')) return;
  try {
    await api('DELETE', `/api/teams/${teamId}/members/${userId}`);
    toast('User removed from team', 'success');
    nav('groups');
  } catch(e) {
    toast('Failed to remove user from team', 'error');
  }
}

async function renderChat(el) {
  let teams = [];
  try {
    teams = await api('GET', '/api/teams/');
  } catch(e) {}

  el.innerHTML = `
    <div class="page-header" style="margin-bottom:20px; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <div class="page-title" style="color:#1B1F6B;">Workspace Chat Room</div>
        <div class="page-subtitle">Real-time team collaboration &amp; discussion</div>
      </div>
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:13.5px; font-weight:600; color:#475569;">Chat Channel:</span>
        <select id="chat-team-selector" onchange="switchChatTeam(this.value)" style="padding:8px 16px; border:1.5px solid #cbd5e1; border-radius:8px; outline:none; font-size:13.5px; font-weight:600; color:#1e293b; background:#fff; cursor:pointer; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
          <option value="0">🌐 General Discussion</option>
          ${teams.map(t => `<option value="${t.id}">👥 ${t.name}</option>`).join('')}
        </select>
      </div>
    </div>
    <div class="card" style="display:flex;flex-direction:column;height:calc(100vh - 220px);padding:0;overflow:hidden;border:1px solid #e2e8f0;border-radius:8px;">
      <div id="chat-messages" style="flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px;background:#f8fafc;">
        <div style="text-align:center;padding:20px;color:#64748b;"><div class="spinner" style="margin:0 auto 10px;"></div>Loading messages...</div>
      </div>
      <div style="border-top:1px solid #e2e8f0;padding:14px;background:#fff;display:flex;gap:10px;align-items:center;">
        <input type="text" id="chat-input" placeholder="Type a message to the team..." style="flex:1;padding:10px 14px;border:1px solid #cbd5e1;border-radius:8px;outline:none;font-size:13.5px;" onkeydown="if(event.key==='Enter')sendRealChatMessage()"/>
        <button class="btn btn-primary" onclick="sendRealChatMessage()" style="background:#1B1F6B;border:none;padding:10px 18px;border-radius:8px;font-weight:600;"><i class="fa fa-paper-plane"></i> Send</button>
      </div>
    </div>
  `;
  
  const selector = document.getElementById('chat-team-selector');
  if (selector) selector.value = currentChatTeamId;

  await refreshChatMessagesOnly();
}

window.switchChatTeam = async function(val) {
  currentChatTeamId = parseInt(val);
  const box = document.getElementById('chat-messages');
  if (box) {
    box.innerHTML = '<div style="text-align:center;padding:20px;color:#64748b;"><div class="spinner" style="margin:0 auto 10px;"></div>Switching channel...</div>';
    box.removeAttribute('data-count');
  }
  await refreshChatMessagesOnly();
};

async function refreshChatMessagesOnly() {
  const box = document.getElementById('chat-messages');
  if (!box) return;
  try {
    const messages = await api('GET', `/api/chat/?team_id=${currentChatTeamId}`);
    const messageCount = messages.length;
    const oldCount = box.getAttribute('data-count') || 0;
    
    if (messageCount != oldCount || oldCount == 0) {
      box.setAttribute('data-count', messageCount);
      
      if (messageCount === 0) {
        box.innerHTML = `<div style="text-align:center;padding:40px;color:#64748b;"><i class="fa fa-comments" style="font-size:32px;margin-bottom:8px;color:#cbd5e1;"></i><p>No messages yet. Start the conversation!</p></div>`;
        return;
      }
      
      box.innerHTML = messages.map(msg => {
        const isMe = msg.user.id === currentUser.id;
        const initials = msg.user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        
        return `<div class="activity-item" style="border:none;display:flex;gap:10px;align-self:${isMe ? 'flex-end' : 'flex-start'};flex-direction:${isMe ? 'row-reverse' : 'row'};max-width:70%;">
          <div style="background:${msg.user.avatar_color || '#1B1F6B'};width:30px;height:30px;border-radius:50%;color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">
            ${initials}
          </div>
          <div style="text-align:${isMe ? 'right' : 'left'};">
            <span style="font-size:12px;font-weight:600;color:#1e293b;">${msg.user.full_name}</span>
            <span style="font-size:10px;color:#64748b;margin-left:6px;">${msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : 'Just Now'}</span>
            <div style="background:${isMe ? '#e0e7ff' : '#fff'};color:#1e293b;padding:10px 14px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);border:1px solid ${isMe ? '#c7d2fe' : '#e2e8f0'};margin-top:4px;display:inline-block;text-align:left;line-height:1.4;font-size:13px;word-break:break-word;">
              ${msg.message}
            </div>
          </div>
        </div>`;
      }).join('');
      
      // scroll to bottom
      box.scrollTop = box.scrollHeight;
    }
  } catch(e) {}
}

async function sendRealChatMessage() {
  const input = document.getElementById('chat-input');
  if (!input || !input.value.trim()) return;
  const text = input.value.trim();
  input.value = '';
  
  try {
    await api('POST', `/api/chat/?message=${encodeURIComponent(text)}&team_id=${currentChatTeamId}`);
    await refreshChatMessagesOnly();
  } catch(e) {
    toast('Failed to send message', 'error');
  }
}


async function renderExecutive(el) {
  const issues = await api('GET', '/api/issues/?page_size=200');
  const total = issues.length;
  const high = issues.filter(i => i.priority === 'critical' || i.priority === 'high').length;
  const inProgress = issues.filter(i => i.status === 'in_progress').length;
  const done = issues.filter(i => i.status === 'done' || i.status === 'closed').length;
  
  el.innerHTML = `
    <div class="page-header">
      <div>
        <div class="page-title">Executive Strategic Dashboard</div>
        <div class="page-subtitle">Awash Bank Portfolio &amp; Strategic Operations</div>
      </div>
    </div>
    <div class="stats-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:20px;">
      <div class="stat-card" style="border-left-color:#1B1F6B;">
        <div class="stat-icon" style="background:#e8eaf6;color:#1B1F6B;"><i class="fa fa-briefcase"></i></div>
        <div><div class="stat-value">${total}</div><div class="stat-label">Portfolio Items</div></div>
      </div>
      <div class="stat-card" style="border-left-color:#dc2626;">
        <div class="stat-icon" style="background:#fee2e2;color:#dc2626;"><i class="fa fa-radiation"></i></div>
        <div><div class="stat-value">${high}</div><div class="stat-label">High Risk Areas</div></div>
      </div>
      <div class="stat-card" style="border-left-color:#F5A623;">
        <div class="stat-icon" style="background:#fff7ed;color:#F5A623;"><i class="fa fa-spinner"></i></div>
        <div><div class="stat-value">${inProgress}</div><div class="stat-label">Active Initiatives</div></div>
      </div>
      <div class="stat-card" style="border-left-color:#16a34a;">
        <div class="stat-icon" style="background:#dcfce7;color:#16a34a;"><i class="fa fa-check-double"></i></div>
        <div><div class="stat-value">${done}</div><div class="stat-label">Completed Deliverables</div></div>
      </div>
    </div>

    <div class="charts-grid" style="grid-template-columns:1fr 1fr;margin-bottom:20px;">
      <div class="chart-card">
        <div class="chart-title"><i class="fa fa-bullseye" style="color:#1B1F6B;"></i> Strategic Burndown Chart</div>
        <div class="chart-wrap" style="height:250px;"><canvas id="exec-burn-chart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-title"><i class="fa fa-balance-scale" style="color:#F5A623;"></i> Portfolio Allocation</div>
        <div class="chart-wrap" style="height:250px;"><canvas id="exec-pie-chart"></canvas></div>
      </div>
    </div>
  `;
  
  setTimeout(() => {
    renderBurndownChart('exec-burn-chart');
    const ctx2 = document.getElementById('exec-pie-chart')?.getContext('2d');
    if (ctx2) {
      new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: ['Core Banking', 'Digital Wallet', 'Information Security', 'Compliance'],
          datasets: [{
            data: [45, 25, 20, 10],
            backgroundColor: ['#1B1F6B', '#F5A623', '#dc2626', '#16a34a']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'right' } }
        }
      });
    }
  }, 100);
}

async function renderIntegrations(el) {
  el.innerHTML = `
    <div class="page-header">
      <div>
        <div class="page-title">Enterprise System Integrations</div>
        <div class="page-subtitle">Awash Bank CI/CD &amp; External Sync Connectors</div>
      </div>
    </div>
    <div class="projects-grid">
      <div class="project-card">
        <div class="project-card-top" style="background:#0052cc;"></div>
        <div class="project-card-body">
          <div style="display:flex;align-items:center;justify-content:between;margin-bottom:12px;">
            <div style="font-size:22px;color:#0052cc;"><i class="fab fa-jira"></i></div>
            <span class="badge" style="background:#dcfce7;color:#15803d;">Connected</span>
          </div>
          <div class="project-name">Atlassian Jira Sync</div>
          <div style="font-size:12.5px;color:#6b7280;margin-top:6px;line-height:1.4;">Two-way real-time synchronisation of issues, boards, and epics with Jira Cloud.</div>
          <div style="margin-top:16px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:11px;color:#9ca3af;">Last sync: 2 mins ago</span>
            <button class="btn btn-sm btn-outline" style="padding:4px 10px;">Configure</button>
          </div>
        </div>
      </div>

      <div class="project-card">
        <div class="project-card-top" style="background:#24292f;"></div>
        <div class="project-card-body">
          <div style="display:flex;align-items:center;justify-content:between;margin-bottom:12px;">
            <div style="font-size:22px;color:#24292f;"><i class="fab fa-github"></i></div>
            <span class="badge" style="background:#dcfce7;color:#15803d;">Connected</span>
          </div>
          <div class="project-name">GitHub Webhooks</div>
          <div style="font-size:12.5px;color:#6b7280;margin-top:6px;line-height:1.4;">Automatically link pull requests, commits, and branch changes to banking issue keys.</div>
          <div style="margin-top:16px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:11px;color:#9ca3af;">Last sync: 15 mins ago</span>
            <button class="btn btn-sm btn-outline" style="padding:4px 10px;">Configure</button>
          </div>
        </div>
      </div>

      <div class="project-card">
        <div class="project-card-top" style="background:#4a154b;"></div>
        <div class="project-card-body">
          <div style="display:flex;align-items:center;justify-content:between;margin-bottom:12px;">
            <div style="font-size:22px;color:#4a154b;"><i class="fab fa-slack"></i></div>
            <span class="badge" style="background:#fee2e2;color:#dc2626;">Disconnected</span>
          </div>
          <div class="project-name">Slack Notifications</div>
          <div style="font-size:12.5px;color:#6b7280;margin-top:6px;line-height:1.4;">Stream real-time status changes and urgent bug reports directly to team slack channels.</div>
          <div style="margin-top:16px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:11px;color:#9ca3af;">Inactive</span>
            <button class="btn btn-sm btn-primary" style="padding:4px 10px;background:#1B1F6B;">Connect</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function editCurrentIssue() {
  if (!currentIssue) return;
  
  // Fill edit form
  document.getElementById('ei-title').value = currentIssue.title || '';
  document.getElementById('ei-type').value = currentIssue.issue_type || 'task';
  document.getElementById('ei-priority').value = currentIssue.priority || 'medium';
  
  // Fill projects dropdown
  const projSel = document.getElementById('ei-project');
  if (projSel) {
    projSel.innerHTML = allProjects.map(p => `<option value="${p.id}">${p.key} - ${p.name}</option>`).join('');
    projSel.value = currentIssue.project_id;
  }
  
  // Fill status dropdown
  const statusSel = document.getElementById('ei-status');
  if (statusSel) {
    statusSel.value = currentIssue.status || 'todo';
  }
  
  // Fill assignee dropdown
  const assigneeSel = document.getElementById('ei-assignee');
  if (assigneeSel) {
    assigneeSel.innerHTML = '<option value="">Unassigned</option>' + allUsers.filter(u => u.is_active).map(u => `<option value="${u.id}">${u.full_name} (${u.role.replace(/_/g, ' ')})</option>`).join('');
    assigneeSel.value = currentIssue.assignee_id || '';
  }
  
  // Fill sprint dropdown
  const sprintSel = document.getElementById('ei-sprint');
  if (sprintSel) {
    sprintSel.innerHTML = '<option value="">No Sprint</option>' + allSprints.filter(s => s.status !== 'completed').map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    sprintSel.value = currentIssue.sprint_id || '';
  }
  
  document.getElementById('ei-points').value = currentIssue.story_points || 0;
  document.getElementById('ei-due').value = currentIssue.due_date ? currentIssue.due_date.split('T')[0] : '';
  document.getElementById('ei-desc').value = currentIssue.description || '';
  
  openModal('edit-issue');
}

async function submitEditIssue() {
  if (!currentIssue) return;
  
  const assigneeId = document.getElementById('ei-assignee').value ? parseInt(document.getElementById('ei-assignee').value) : null;
  const isPMorAdmin = ['super_admin', 'admin', 'project_manager', 'scrum_master', 'business_analyst', 'qa_engineer'].includes(currentUser.role);
  
  if (assigneeId !== currentIssue.assignee_id && !isPMorAdmin) {
    return toast('Only PM, Scrum Master, QA, BA, or Admin can assign or change assignees.', 'error');
  }

  const fields = {
    title: document.getElementById('ei-title').value.trim(),
    issue_type: document.getElementById('ei-type').value,
    priority: document.getElementById('ei-priority').value,
    status: document.getElementById('ei-status').value,
    assignee_id: assigneeId,
    sprint_id: document.getElementById('ei-sprint').value ? parseInt(document.getElementById('ei-sprint').value) : null,
    story_points: parseInt(document.getElementById('ei-points').value) || 0,
    due_date: document.getElementById('ei-due').value || null,
    description: document.getElementById('ei-desc').value.trim(),
  };

  if (!fields.title) return toast('Title is required', 'error');

  try {
    await api('PUT', `/api/issues/${currentIssue.id}`, fields);
    toast('Issue updated successfully!', 'success');
    closeModal('edit-issue');
    closeModal('issue-detail');
    
    // Refresh active view
    if (currentView === 'issues' || currentView === 'myissues' || currentView === 'backlog') {
      loadPage(currentView);
    } else if (currentView === 'kanban') {
      loadPage('kanban');
    } else if (currentView === 'dashboard') {
      loadPage('dashboard');
    }
  } catch (e) {
    toast(e.message, 'error');
  }
}
`, fields);
    toast('Issue updated successfully!', 'success');
    initApp();
  } catch(e) {
    toast(e.message, 'error');
  }
}
