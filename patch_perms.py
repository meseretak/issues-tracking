import os

import re

JS_PATH = os.path.join('frontend', 'app.js')
js = open(JS_PATH, encoding='utf-8').read()

# ── 1. Update renderProjects to show Create button only for allowed roles ──────
old_proj_btn = '<button class="btn btn-orange" onclick="openCreateProject()"><i class="fa fa-plus"></i> New Project</button>'
new_proj_btn = '${can("createProject") ? \'<button class="btn btn-orange" onclick="openCreateProject()"><i class="fa fa-plus"></i> New Project</button>\' : ""}'
if old_proj_btn in js:
    js = js.replace(old_proj_btn, new_proj_btn)
    print('renderProjects button: updated')

# ── 2. Update renderTeam to show Add Member only for admin ─────────────────────
old_team_btn = '${canAdd ? \'<button class="btn btn-orange" onclick="openCreateUser()"><i class="fa fa-user-plus"></i> Add Member</button>\' : \'\'}'
# Already uses canAdd - check if it's set correctly
if 'canAdd' in js:
    old_can_add = "const canAdd = ['super_admin','admin'].includes(currentUser.role);"
    new_can_add = "const canAdd = can('createUser');"
    if old_can_add in js:
        js = js.replace(old_can_add, new_can_add)
        print('canAdd: updated to use can()')

# ── 3. Update topbar New Issue button to be role-aware ─────────────────────────
# The button in HTML is always visible - we'll hide it via JS after login
# Add a function to update UI based on role
update_ui_addition = '''
function updateRoleBasedUI() {
  // Hide/show New Issue button based on role
  const newIssueBtns = document.querySelectorAll('[onclick="openCreateIssue()"]');
  newIssueBtns.forEach(btn => {
    btn.style.display = can('createIssue') ? '' : 'none';
  });
  // Hide/show admin-only nav items
  const execNav = document.getElementById('nav-executive');
  if (execNav) execNav.style.display = ['super_admin','admin','project_manager','scrum_master'].includes(currentUser.role) ? '' : 'none';
  const intNav = document.getElementById('nav-integrations');
  if (intNav) intNav.style.display = can('manageIntegrations') ? '' : 'none';
  const auditNav = document.getElementById('nav-audit');
  if (auditNav) auditNav.style.display = can('viewAudit') ? '' : 'none';
}
'''

if 'updateRoleBasedUI' not in js:
    js = js.replace('function updateUserUI() {', update_ui_addition + 'function updateUserUI() {')
    print('updateRoleBasedUI: added')

# ── 4. Call updateRoleBasedUI after initApp loads ─────────────────────────────
old_init = "  try { nav('dashboard'); } catch(e) { console.error('nav failed:', e); }"
new_init = "  try { updateRoleBasedUI(); nav('dashboard'); } catch(e) { console.error('nav failed:', e); }"
if old_init in js:
    js = js.replace(old_init, new_init)
    print('initApp: updateRoleBasedUI call added')

# ── 5. Add Task Management page ───────────────────────────────────────────────
if 'renderTasks' not in js:
    tasks_fn = '''
// ── Task Management ───────────────────────────────────────────────────────────
async function renderTasks(el) {
  const issues = await api('GET', '/api/issues/?page_size=200');
  const tasks = issues.filter(i => i.issue_type === 'task' || i.issue_type === 'story');
  const myTasks = tasks.filter(i => i.assignee && i.assignee.id === currentUser.id);
  const unassigned = tasks.filter(i => !i.assignee);

  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Task Management</div><div class="page-subtitle">${tasks.length} tasks total</div></div>
      <div style="display:flex;gap:8px;">
        ${can('createIssue') ? '<button class="btn btn-orange" onclick="openCreateIssue()"><i class="fa fa-plus"></i> New Task</button>' : ''}
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:16px;">
      <div class="stat-card" style="border-left-color:#1B1F6B;">
        <div class="stat-icon" style="background:#e8eaf6;color:#1B1F6B;"><i class="fa fa-tasks"></i></div>
        <div><div class="stat-value">${tasks.length}</div><div class="stat-label">Total Tasks</div></div>
      </div>
      <div class="stat-card" style="border-left-color:#F5A623;">
        <div class="stat-icon" style="background:#fff7ed;color:#F5A623;"><i class="fa fa-user-check"></i></div>
        <div><div class="stat-value">${myTasks.length}</div><div class="stat-label">My Tasks</div></div>
      </div>
      <div class="stat-card" style="border-left-color:#dc2626;">
        <div class="stat-icon" style="background:#fee2e2;color:#dc2626;"><i class="fa fa-user-slash"></i></div>
        <div><div class="stat-value">${unassigned.length}</div><div class="stat-label">Unassigned</div></div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
      <!-- My Tasks -->
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fa fa-user-check" style="color:#F5A623;"></i> My Tasks</div>
          <span style="font-size:12px;color:#6b7280;">${myTasks.length} tasks</span>
        </div>
        ${myTasks.length === 0 ? '<div class="empty-state"><i class="fa fa-check-circle"></i><p>No tasks assigned to you</p></div>' :
          myTasks.map(t => renderTaskCard(t)).join('')}
      </div>

      <!-- All Tasks by Status -->
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fa fa-list-check" style="color:#F5A623;"></i> All Tasks by Status</div>
        </div>
        ${['todo','in_progress','in_review','testing','done'].map(status => {
          const statusTasks = tasks.filter(t => t.status === status);
          if (!statusTasks.length) return '';
          return '<div style="margin-bottom:12px;">' +
            '<div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;">' +
            status.replace(/_/g,' ') + ' (' + statusTasks.length + ')</div>' +
            statusTasks.slice(0,5).map(t => renderTaskCard(t)).join('') +
            (statusTasks.length > 5 ? '<div style="font-size:12px;color:#6b7280;padding:4px 0;">+' + (statusTasks.length-5) + ' more</div>' : '') +
            '</div>';
        }).join('')}
      </div>
    </div>

    <!-- Unassigned Tasks (PM/Admin only) -->
    ${can('editAnyIssue') && unassigned.length > 0 ? `
    <div class="card" style="margin-top:14px;">
      <div class="card-header">
        <div class="card-title"><i class="fa fa-user-slash" style="color:#dc2626;"></i> Unassigned Tasks</div>
        <span style="font-size:12px;color:#dc2626;font-weight:600;">${unassigned.length} need assignment</span>
      </div>
      <table style="width:100%;border-collapse:collapse;">
        <thead><tr style="background:#f8f9ff;">
          <th style="padding:8px 12px;text-align:left;font-size:11px;font-weight:700;color:#6b7280;border-bottom:2px solid var(--border);">Key</th>
          <th style="padding:8px 12px;text-align:left;font-size:11px;font-weight:700;color:#6b7280;border-bottom:2px solid var(--border);">Title</th>
          <th style="padding:8px 12px;text-align:left;font-size:11px;font-weight:700;color:#6b7280;border-bottom:2px solid var(--border);">Priority</th>
          <th style="padding:8px 12px;text-align:left;font-size:11px;font-weight:700;color:#6b7280;border-bottom:2px solid var(--border);">Assign To</th>
        </tr></thead>
        <tbody>
          ${unassigned.slice(0,10).map(t => '<tr onclick="openIssueDetail(' + t.id + ')" style="cursor:pointer;" onmouseover="this.style.background=chr(39)#f8f9ff chr(39)" onmouseout="this.style.background=chr(39)chr(39)">' +
            '<td style="padding:8px 12px;border-bottom:1px solid var(--border);"><strong style="color:#1B1F6B;font-family:monospace;font-size:11px;">' + t.key + '</strong></td>' +
            '<td style="padding:8px 12px;border-bottom:1px solid var(--border);font-size:13px;">' + t.title + '</td>' +
            '<td style="padding:8px 12px;border-bottom:1px solid var(--border);">' + getPriorityBadge(t.priority) + '</td>' +
            '<td style="padding:8px 12px;border-bottom:1px solid var(--border);" onclick="event.stopPropagation();">' +
            '<select onchange="assignTask(' + t.id + ',this.value)" style="padding:4px 8px;border:1.5px solid var(--border);border-radius:6px;font-size:12px;outline:none;">' +
            '<option value="">Assign...</option>' +
            allUsers.filter(u => u.is_active).map(u => '<option value="' + u.id + '">' + u.full_name + '</option>').join('') +
            '</select></td></tr>'
          ).join('')}
        </tbody>
      </table>
    </div>` : ''}
  `;
}

function renderTaskCard(task) {
  const overdue = task.due_date && new Date(task.due_date) < new Date() && !['done','closed'].includes(task.status);
  return '<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);cursor:pointer;" onclick="openIssueDetail(' + task.id + ')">' +
    getTypeIcon(task.issue_type) +
    '<div style="flex:1;min-width:0;">' +
    '<div style="font-size:13px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + task.title + '</div>' +
    '<div style="font-size:11px;color:#6b7280;margin-top:2px;">' + task.key + (task.due_date ? ' &bull; Due: <span style="color:' + (overdue?'#dc2626':'#6b7280') + ';">' + fmt(task.due_date) + '</span>' : '') + '</div>' +
    '</div>' +
    getStatusBadge(task.status) +
    (task.assignee ? getAvatar(task.assignee, 22) : '') +
    '</div>';
}

async function assignTask(issueId, userId) {
  if (!userId) return;
  try {
    await api('PUT', '/api/issues/' + issueId, {assignee_id: parseInt(userId)});
    toast('Task assigned!', 'success');
    loadPage('tasks');
  } catch(e) {}
}
'''
    # Insert before Init on Load
    js = js.replace('// ── Init on Load', tasks_fn + '// ── Init on Load')
    print('renderTasks: added')

# ── 6. Add tasks to nav and loadPage ─────────────────────────────────────────
if "'tasks': await renderTasks" not in js:
    js = js.replace(
        "case 'team':          await renderTeam(el); break;",
        "case 'tasks':         await renderTasks(el); break;\n      case 'team':          await renderTeam(el); break;"
    )
    print('loadPage tasks: added')

if "'tasks': 'Task Management'" not in js and "tasks: 'Task Management'" not in js:
    js = js.replace(
        "groups: 'Teams & Groups',",
        "tasks: 'Task Management', groups: 'Teams & Groups',"
    )
    print('nav titles tasks: added')

# ── Save ──────────────────────────────────────────────────────────────────────
open(JS_PATH, 'w', encoding='utf-8').write(js)
print('Saved. Lines:', js.count('\n'))
