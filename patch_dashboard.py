import re

NEW_DASHBOARD = """async function renderDashboard(el) {
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
              return \`<tr style="border-bottom:1px solid #f1f5f9;cursor:pointer;" onclick="openIssueDetail(\${i.id})" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
                <td style="padding:10px 14px;"><span style="color:#0052CC;font-weight:700;font-family:monospace;">\${i.key}</span></td>
                <td style="padding:10px 14px;font-weight:500;color:#1e293b;">\${i.title}</td>
                <td style="padding:10px 14px;color:#64748b;">\${i.project_key}</td>
                <td style="padding:10px 14px;">\${getStatusBadge(i.status)}</td>
                <td style="padding:10px 14px;">\${getPriorityBadge(i.priority)}</td>
                <td style="padding:10px 14px;color:\${over?'#dc2626':'#64748b'};">\${i.due_date ? fmt(i.due_date) : '-'}</td>
              </tr>\`;
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
  const assigned = await api('GET', \`/api/issues/?assignee_id=\${currentUser.id}&page_size=10\`);
  const displayIssues = (assigned||[]).slice(0,10);
  const sp = stats.sprint_progress;
  
  const sprintCard = sp ? (() => {
    const uc = (sp.days_remaining!==null && sp.days_remaining<=2) ? '#dc2626' : (sp.days_remaining!==null && sp.days_remaining<=5) ? '#F5A623' : '#15803d';
    return \`<div class="sprint-progress-card" style="margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;gap:16px;">
      <div style="flex:1;">
        <div class="card-title"><i class="fa fa-running" style="color:#F5A623;"></i> Active Sprint: \${sp.name}</div>
        <div class="progress-bar" style="margin-top:8px;"><div class="progress-fill" style="width:\${sp.percent}%;"></div></div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-top:6px;">
          <span>\${sp.done} / \${sp.total} completed</span>
          <span style="font-weight:700;color:#1B1F6B;">\${sp.percent}%</span>
        </div>
      </div>
      \${sp.days_remaining!==null ? \`<div style="text-align:center;background:\${uc}22;border-radius:10px;padding:12px 18px;">
        <div style="font-size:26px;font-weight:800;color:\${uc};">\${sp.days_remaining}</div>
        <div style="font-size:11px;font-weight:700;color:\${uc};">DAYS LEFT</div>
      </div>\` : ''}
    </div>\`;
  })() : '';
  
  el.innerHTML = \`
    <div class="page-header" style="margin-bottom:16px;">
      <div>
        <div class="page-title" style="font-size:22px;color:#1B1F6B;font-weight:700;">Dashboard &mdash; \${currentUser.full_name.split(' ')[0]}</div>
        <div class="page-subtitle">Awash Bank Issue Tracker</div>
      </div>
    </div>
    
    \${sprintCard}
    
    <div class="stats-grid" style="margin-bottom:16px;">
      <div class="stat-card" style="border-left-color:#1B1F6B;"><div class="stat-icon" style="background:#e8eaf6;color:#1B1F6B;"><i class="fa fa-tasks"></i></div><div><div class="stat-value">\${stats.total_issues}</div><div class="stat-label">Total Issues</div></div></div>
      <div class="stat-card" style="border-left-color:#1d4ed8;"><div class="stat-icon" style="background:#dbeafe;color:#1d4ed8;"><i class="fa fa-folder-open"></i></div><div><div class="stat-value">\${stats.open_issues}</div><div class="stat-label">Open Issues</div></div></div>
      <div class="stat-card" style="border-left-color:#c2410c;"><div class="stat-icon" style="background:#fff7ed;color:#c2410c;"><i class="fa fa-spinner"></i></div><div><div class="stat-value">\${stats.in_progress}</div><div class="stat-label">In Progress</div></div></div>
      <div class="stat-card" style="border-left-color:#15803d;"><div class="stat-icon" style="background:#dcfce7;color:#15803d;"><i class="fa fa-check-circle"></i></div><div><div class="stat-value">\${stats.resolved_today}</div><div class="stat-label">Resolved Today</div></div></div>
      <div class="stat-card" style="border-left-color:#dc2626;"><div class="stat-icon" style="background:#fee2e2;color:#dc2626;"><i class="fa fa-exclamation-triangle"></i></div><div><div class="stat-value">\${stats.overdue}</div><div class="stat-label">Overdue</div></div></div>
    </div>
    
    \${displayIssues.length ? \`<div style="background:#fff;border-left:4px solid #1B1F6B;border:1px solid #e2e8f0;border-radius:6px;margin-bottom:18px;overflow:hidden;">
      <div style="background:#1B1F6B;color:#fff;padding:8px 12px;font-size:12.5px;font-weight:700;">Assigned to Me</div>
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        <thead><tr style="background:#f8fafc;border-bottom:1px solid #e2e8f0;color:#475569;font-weight:600;"><th style="padding:10px 14px;">Key</th><th style="padding:10px 14px;">Summary</th><th style="padding:10px 14px;">Status</th><th style="padding:10px 14px;">Priority</th></tr></thead>
        <tbody>
          \${displayIssues.map(i=>\`<tr style="border-bottom:1px solid #f1f5f9;cursor:pointer;" onclick="openIssueDetail(\${i.id})" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'"><td style="padding:10px 14px;"><span style="color:#0052CC;font-weight:700;font-family:monospace;">\${i.key}</span></td><td style="padding:10px 14px;">\${i.title}</td><td style="padding:10px 14px;">\${getStatusBadge(i.status)}</td><td style="padding:10px 14px;">\${getPriorityBadge(i.priority)}</td></tr>\`).join('')}
        </tbody>
      </table>
    </div>\` : ''}
    
    <div class="charts-grid" style="margin-bottom:16px;">
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-pie"></i> Issues by Status</div><div class="chart-wrap"><canvas id="chart-status"></canvas></div></div>
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-bar"></i> Issues by Priority</div><div class="chart-wrap"><canvas id="chart-priority"></canvas></div></div>
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-line"></i> Daily Trend</div><div class="chart-wrap"><canvas id="chart-daily"></canvas></div></div>
    </div>
    <div class="bottom-grid">
      <div class="card"><div class="card-header"><div class="card-title"><i class="fa fa-history"></i> Recent Activity</div></div><div id="activity-list"></div></div>
      <div class="card"><div class="card-header"><div class="card-title"><i class="fa fa-users"></i> Top Assignees</div></div><div id="assignee-list"></div></div>
    </div>
  \`;
  renderCharts(stats);
  renderActivity(stats.recent_activity);
  renderAssignees(stats.by_assignee);
  document.getElementById('open-count').textContent = stats.open_issues;
  updateRoleBasedUI();
}
"""

with open(r'frontend\app.js', encoding='utf-8') as f:
    content = f.read()

start = content.find('async function renderDashboard')
end = content.find('\nfunction renderCharts', start)

if start != -1 and end != -1:
    new_content = content[:start] + NEW_DASHBOARD + content[end:]
    with open(r'frontend\app.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Successfully patched renderDashboard')
else:
    print('Failed to find boundaries')
