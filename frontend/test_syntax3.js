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
      `).join('') : '<div class="empty-state"><i class="fa fa-bell-slash"></i><h3>No Notifications</h3><p>You\'re all caught up!</p></div>'}
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
