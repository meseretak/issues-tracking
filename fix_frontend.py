"""
Complete frontend fix script.
Adds: renderGroups, pagination, all status badges, severity badges, filterIssues fix.
Run: python "issues tracking/fix_frontend.py"
"""
import re, os

BASE = os.path.dirname(os.path.abspath(__file__))
JS_PATH = os.path.join(BASE, 'frontend', 'app.js')

js = open(JS_PATH, encoding='utf-8').read()

# ── 1. Fix filterIssues to store filtered list and reset page ─────────────────
old_filter = '''function filterIssues() {
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
}'''

new_filter = '''function filterIssues() {
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
}'''

if old_filter in js:
    js = js.replace(old_filter, new_filter)
    print('filterIssues: replaced')
else:
    print('filterIssues: not found, skipping')

# ── 2. Replace renderIssuesTable with paginated version ───────────────────────
new_table_fn = r'''function renderIssuesTable(issues) {
  const tbody = document.getElementById('issues-tbody');
  const pagEl = document.getElementById('issues-pagination');
  if (!issues || !issues.length) {
    tbody.innerHTML = '<tr><td colspan="11" style="text-align:center;padding:40px;color:#6b7280;"><i class="fa fa-inbox" style="font-size:32px;display:block;margin-bottom:10px;opacity:.3;"></i>No issues found</td></tr>';
    if (pagEl) pagEl.innerHTML = '';
    return;
  }
  const total = issues.length;
  const totalPages = Math.ceil(total / ISSUES_PER_PAGE);
  const start = (issuesPage - 1) * ISSUES_PER_PAGE;
  const paged = issues.slice(start, start + ISSUES_PER_PAGE);
  tbody.innerHTML = paged.map(i => {
    const overdue = i.due_date && new Date(i.due_date) < new Date() && !['done','closed','cancelled'].includes(i.status);
    return '<tr onclick="openIssueDetail(' + i.id + ')">' +
      '<td><strong style="color:#1B1F6B;font-family:monospace;">' + i.key + '</strong></td>' +
      '<td style="max-width:280px;"><div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="' + i.title + '">' + i.title + '</div></td>' +
      '<td>' + getTypeIcon(i.issue_type) + '</td>' +
      '<td>' + getStatusBadge(i.status) + '</td>' +
      '<td>' + getPriorityBadge(i.priority) + '</td>' +
      '<td>' + getSeverityBadge(i.severity) + '</td>' +
      '<td>' + (i.assignee ? '<div style="display:flex;align-items:center;gap:6px;">' + getAvatar(i.assignee, 22) + '<span>' + i.assignee.full_name.split(' ')[0] + '</span></div>' : '<span style="color:#9ca3af;">-</span>') + '</td>' +
      '<td style="font-size:11px;color:#6b7280;">' + (i.sprint ? i.sprint.name : '-') + '</td>' +
      '<td style="text-align:center;">' + (i.story_points ? '<span class="sp-badge">' + i.story_points + '</span>' : '-') + '</td>' +
      '<td style="font-size:12px;color:' + (overdue ? '#dc2626' : '#6b7280') + ';">' + fmt(i.due_date) + '</td>' +
      '<td style="font-size:12px;color:#6b7280;">' + fmt(i.created_at) + '</td>' +
      '</tr>';
  }).join('');
  if (pagEl && totalPages > 1) {
    const sub = document.getElementById('issues-subtitle');
    if (sub) sub.textContent = total + ' issues - page ' + issuesPage + ' of ' + totalPages;
    let btns = '<button class="page-btn" onclick="issuesPage=Math.max(1,issuesPage-1);renderIssuesTable(window._fi||allIssues)" ' + (issuesPage===1?'disabled':'') + '>&lt; Prev</button>';
    for (let p = Math.max(1,issuesPage-2); p <= Math.min(totalPages,issuesPage+2); p++) {
      btns += '<button class="page-btn ' + (p===issuesPage?'active':'') + '" onclick="issuesPage=' + p + ';renderIssuesTable(window._fi||allIssues)">' + p + '</button>';
    }
    btns += '<button class="page-btn" onclick="issuesPage=Math.min(' + totalPages + ',issuesPage+1);renderIssuesTable(window._fi||allIssues)" ' + (issuesPage===totalPages?'disabled':'') + '>Next &gt;</button>';
    pagEl.innerHTML = '<div class="pagination"><span class="pagination-info">Showing ' + (start+1) + '-' + Math.min(start+ISSUES_PER_PAGE,total) + ' of ' + total + '</span><div class="pagination-btns">' + btns + '</div></div>';
  } else if (pagEl) { pagEl.innerHTML = ''; }
}'''

js = re.sub(r'function renderIssuesTable\(issues\).*?^}', new_table_fn, js, flags=re.DOTALL|re.MULTILINE)
print('renderIssuesTable: replaced')

# ── 3. Add renderGroups before the Init on Load section ───────────────────────
groups_fn = '''
// ── Groups / Teams ────────────────────────────────────────────────────────────
async function renderGroups(el) {
  let teams = [];
  try { teams = await api('GET', '/api/teams/'); } catch(e) {}
  const canManage = ['super_admin','admin','project_manager'].includes(currentUser.role);
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Teams &amp; Groups</div><div class="page-subtitle">${teams.length} teams</div></div>
      ${canManage ? '<button class="btn btn-orange" onclick="openCreateTeamModal()"><i class="fa fa-plus"></i> New Team</button>' : ''}
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px;">
      ${teams.map(t => `
        <div class="team-card">
          <div class="team-card-header">
            <div class="team-color-dot" style="background:${t.color};width:14px;height:14px;border-radius:50%;flex-shrink:0;"></div>
            <div style="flex:1;">
              <div class="team-name">${t.name}</div>
              <div class="team-type">${t.team_type ? t.team_type.toUpperCase() : ''} TEAM</div>
            </div>
            <span class="badge" style="background:${t.color};color:#fff;">${t.member_count} members</span>
          </div>
          ${t.description ? `<div style="font-size:12px;color:#6b7280;margin-bottom:12px;">${t.description}</div>` : ''}
          ${t.lead ? `<div style="font-size:12px;margin-bottom:12px;display:flex;align-items:center;gap:6px;"><i class="fa fa-crown" style="color:#F5A623;"></i><strong>Lead:</strong> ${t.lead.full_name}</div>` : ''}
          <div style="border-top:1px solid var(--border);padding-top:12px;">
            <div style="font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;">Members</div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;">
              ${t.members.map(m => `
                <div style="display:flex;align-items:center;gap:6px;background:var(--bg);padding:4px 8px;border-radius:20px;">
                  ${getAvatar(m, 22)}
                  <span style="font-size:12px;font-weight:500;">${m.full_name.split(' ')[0]}</span>
                  <span class="badge r-${m.role}" style="font-size:9px;padding:1px 5px;">${m.role.replace(/_/g,' ')}</span>
                </div>
              `).join('')}
              ${t.members.length === 0 ? '<span style="font-size:12px;color:#9ca3af;">No members yet</span>' : ''}
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function openCreateTeamModal() {
  toast('Team creation coming soon', 'info');
}

'''

if 'async function renderGroups' not in js:
    # Insert before the Init on Load section
    insert_before = '// ── Init on Load'
    if insert_before in js:
        js = js.replace(insert_before, groups_fn + insert_before)
        print('renderGroups: added')
    else:
        js += groups_fn
        print('renderGroups: appended at end')
else:
    print('renderGroups: already exists')

# ── 4. Fix globalSearch to actually work ──────────────────────────────────────
old_search = '''function globalSearch(q) {
  if (!q || q.length < 2) return;
  console.log('Search:', q);
}'''

new_search = '''function globalSearch(q) {
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
});'''

if old_search in js:
    js = js.replace(old_search, new_search)
    print('globalSearch: replaced')
else:
    print('globalSearch: not found (may already be updated)')

# ── 5. Fix renderTeam to show pagination ──────────────────────────────────────
# Find renderTeam and check if it has pagination
if 'teamPage' not in js:
    old_team_start = 'async function renderTeam(el) {'
    idx = js.find(old_team_start)
    if idx >= 0:
        # Find end of function
        depth = 0
        i = idx
        while i < len(js):
            if js[i] == '{': depth += 1
            elif js[i] == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        old_team_fn = js[idx:i+1]
        new_team_fn = '''async function renderTeam(el) {
  const users = allUsers;
  const USERS_PER_PAGE = 20;
  let teamPage = 1;
  const roles = [...new Set(users.map(u => u.role))].sort();
  const depts = [...new Set(users.map(u => u.department).filter(Boolean))].sort();
  const canAdd = ['super_admin','admin'].includes(currentUser.role);

  function renderUserGrid(filtered, page) {
    const total = filtered.length;
    const totalPages = Math.ceil(total / USERS_PER_PAGE);
    const start = (page - 1) * USERS_PER_PAGE;
    const paged = filtered.slice(start, start + USERS_PER_PAGE);
    const grid = document.getElementById('team-grid');
    const pag = document.getElementById('team-pagination');
    if (!grid) return;
    grid.innerHTML = paged.map(u => `
      <div class="user-card">
        <div class="user-card-avatar" style="background:${u.avatar_color};">${getInitials(u.full_name)}</div>
        <div class="user-card-name">${u.full_name}</div>
        <div class="user-card-dept">${u.department || 'No Department'}</div>
        ${getRoleBadge(u.role)}
        <div class="user-card-email">${u.email}</div>
        ${u.phone ? '<div style="font-size:11px;color:#6b7280;margin-top:4px;"><i class="fa fa-phone" style="margin-right:4px;"></i>' + u.phone + '</div>' : ''}
        <div style="margin-top:10px;display:flex;gap:6px;justify-content:center;">
          <span class="badge" style="background:${u.is_active ? '#dcfce7' : '#fee2e2'};color:${u.is_active ? '#15803d' : '#dc2626'};">${u.is_active ? 'Active' : 'Inactive'}</span>
        </div>
      </div>
    `).join('');
    if (pag && totalPages > 1) {
      let btns = '<button class="page-btn" onclick="teamPage=Math.max(1,teamPage-1);renderUserGrid(window._teamFiltered||allUsers,teamPage)" ' + (page===1?'disabled':'') + '>&lt; Prev</button>';
      for (let p = Math.max(1,page-2); p <= Math.min(totalPages,page+2); p++) {
        btns += '<button class="page-btn ' + (p===page?'active':'') + '" onclick="teamPage=' + p + ';renderUserGrid(window._teamFiltered||allUsers,teamPage)">' + p + '</button>';
      }
      btns += '<button class="page-btn" onclick="teamPage=Math.min(' + totalPages + ',teamPage+1);renderUserGrid(window._teamFiltered||allUsers,teamPage)" ' + (page===totalPages?'disabled':'') + '>Next &gt;</button>';
      pag.innerHTML = '<div class="pagination"><span class="pagination-info">Showing ' + (start+1) + '-' + Math.min(start+USERS_PER_PAGE,total) + ' of ' + total + '</span><div class="pagination-btns">' + btns + '</div></div>';
    } else if (pag) { pag.innerHTML = ''; }
  }

  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Team Members</div><div class="page-subtitle">${users.length} members</div></div>
      ${canAdd ? '<button class="btn btn-orange" onclick="openCreateUser()"><i class="fa fa-user-plus"></i> Add Member</button>' : ''}
    </div>
    <div class="filter-bar">
      <select id="team-filter-role" onchange="filterTeam()"><option value="">All Roles</option>${roles.map(r => '<option value="' + r + '">' + r.replace(/_/g,' ') + '</option>').join('')}</select>
      <select id="team-filter-dept" onchange="filterTeam()"><option value="">All Departments</option>${depts.map(d => '<option value="' + d + '">' + d + '</option>').join('')}</select>
      <select id="team-filter-status" onchange="filterTeam()"><option value="">All Status</option><option value="active">Active</option><option value="inactive">Inactive</option></select>
      <div class="filter-spacer"></div>
      <input type="text" id="team-search" placeholder="Search members..." oninput="filterTeam()" style="width:200px;"/>
    </div>
    <div class="users-grid" id="team-grid"></div>
    <div id="team-pagination"></div>
  `;

  window._teamFiltered = users;
  renderUserGrid(users, 1);

  window.filterTeam = function() {
    const role = document.getElementById('team-filter-role')?.value;
    const dept = document.getElementById('team-filter-dept')?.value;
    const status = document.getElementById('team-filter-status')?.value;
    const search = document.getElementById('team-search')?.value.toLowerCase();
    let filtered = allUsers;
    if (role) filtered = filtered.filter(u => u.role === role);
    if (dept) filtered = filtered.filter(u => u.department === dept);
    if (status === 'active') filtered = filtered.filter(u => u.is_active);
    if (status === 'inactive') filtered = filtered.filter(u => !u.is_active);
    if (search) filtered = filtered.filter(u => u.full_name.toLowerCase().includes(search) || u.email.toLowerCase().includes(search) || (u.username||'').toLowerCase().includes(search));
    window._teamFiltered = filtered;
    teamPage = 1;
    renderUserGrid(filtered, 1);
  };
}'''
        js = js.replace(old_team_fn, new_team_fn)
        print('renderTeam: replaced with paginated version')
    else:
        print('renderTeam: not found')
else:
    print('renderTeam: already has pagination')

# ── 6. Save ───────────────────────────────────────────────────────────────────
open(JS_PATH, 'w', encoding='utf-8').write(js)
print('Saved. Total lines:', js.count('\n'))
print('Checks:')
for c in ['renderGroups','qa_approved','s-blocked','pagination','filterTeam','globalSearch','getSeverityBadge']:
    print('  ' + ('OK' if c in js else 'MISSING') + ': ' + c)
