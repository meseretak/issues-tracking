import os
import re

frontend_file = r"c:\Users\meseretak\Desktop\devops execrices\issues tracking\frontend\app.js"

with open(frontend_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace ALL_STATUSES and STATUS_TRANSITIONS with dynamic globals
content = re.sub(
    r"const ALL_STATUSES = \[.*?\];\nconst STATUS_TRANSITIONS = \{.*?\};\nfunction getAllowedStatuses\(\) \{ return STATUS_TRANSITIONS\[currentUser && currentUser\.role\] \|\| \[\]; \}",
    """let workflowStatuses = [];
let workflowRules = [];
function getAllowedStatuses() {
    if (!currentUser) return [];
    if (['super_admin', 'admin', 'project_manager', 'scrum_master'].includes(currentUser.role)) {
        return workflowStatuses.map(s => s.key);
    }
    const rules = workflowRules.filter(r => r.allowed_role === currentUser.role);
    const allowed = new Set();
    rules.forEach(r => allowed.add(r.to_status_key));
    return Array.from(allowed);
}
function getStatusConfig(key) {
    return workflowStatuses.find(s => s.key === key) || { name: key, color: '#6B778C' };
}""",
    content,
    flags=re.DOTALL
)

# 2. Add loadWorkflowSettings to initApp
content = content.replace(
    "try { await loadProjects(); }",
    "try { await loadWorkflowSettings(); } catch (e) { console.error('loadWorkflowSettings failed:', e); }\n  try { await loadProjects(); }"
)

# 3. Add loadWorkflowSettings implementation
if "async function loadWorkflowSettings" not in content:
    load_ws_func = """
async function loadWorkflowSettings() {
  workflowStatuses = await api('GET', '/api/workflow/statuses');
  workflowRules = await api('GET', '/api/workflow/rules');
}
"""
    content = content.replace("async function loadProjects() {", load_ws_func + "\nasync function loadProjects() {")

# 4. Replace formatStatus function
content = re.sub(
    r"function formatStatus\(s\) \{.*?\n\}",
    """function formatStatus(s) {
  if (!s) return '-';
  const conf = getStatusConfig(s);
  return `<span class="badge" style="background:${conf.color}20;color:${conf.color};">${conf.name}</span>`;
}""",
    content,
    flags=re.DOTALL
)

# 5. Fix Kanban board
content = re.sub(
    r"const cols = \['todo', 'in_progress', 'testing', 'qa_approved', 'done'\];\n\s*const colNames = \{.*?\};\n\s*const colColors = \{.*?\};",
    """const cols = workflowStatuses.filter(s => s.category !== 'closed').map(s => s.key);
  const colNames = {};
  const colColors = {};
  workflowStatuses.forEach(s => {
    colNames[s.key] = s.name;
    colColors[s.key] = s.color;
  });""",
    content,
    flags=re.DOTALL
)

# 6. Replace dropToKanban checking logic
drop_logic_pattern = r"const allowed = STATUS_TRANSITIONS\[currentUser\.role\] \|\| \[\];\n\s*if \(!allowed\.includes\(newStatus\)\) \{[^\}]+\}"
replacement_drop = """
    let canMove = false;
    if (['super_admin', 'admin', 'project_manager', 'scrum_master'].includes(currentUser.role)) {
      canMove = true;
    } else {
      const rule = workflowRules.find(r => r.from_status_key === issue.status && r.to_status_key === newStatus && r.allowed_role === currentUser.role);
      if (rule) canMove = true;
    }
    if (!canMove) {
      toast('You are not allowed to move this card to ' + colNames[newStatus], 'error');
      renderKanban(document.getElementById('page-kanban'));
      return;
    }
"""
content = re.sub(drop_logic_pattern, replacement_drop, content)

# 7. Issue Detail drop-downs
content = re.sub(
    r"ALL_STATUSES\.map\(s => `<option value=\"\$\{s\}\".*?`\)\.join\(''\)",
    r"workflowStatuses.map(s => `<option value=\"${s.key}\" ${issue.status===s.key?'selected':''}>${s.name}</option>`).join('')",
    content,
    flags=re.DOTALL
)
# For the create issue modal:
content = re.sub(
    r"ALL_STATUSES\.map\(s => `<option value=\"\$\{s\}\".*?`\)\.join\(''\)",
    r"workflowStatuses.map(s => `<option value=\"${s.key}\">${s.name}</option>`).join('')",
    content,
    flags=re.DOTALL
)
# For the edit issue modal:
content = re.sub(
    r"ALL_STATUSES\.map\(st => `<option value=\"\$\{st\}\" \$\{i\.status===st\?'selected':''\}>\$\{st\.replace\(\/_/g, ' '\)\}</option>`\)\.join\(''\)",
    r"workflowStatuses.map(st => `<option value=\"${st.key}\" ${i.status===st.key?'selected':''}>${st.name}</option>`).join('')",
    content,
    flags=re.DOTALL
)


# 8. Render Workflow Settings
render_settings_replacement = """
    </div>
    
    <div class="card" style="margin-top:16px;">
      <div class="card-title" style="display:flex;justify-content:space-between;">
        <span><i class="fa fa-project-diagram"></i> Workflow & Board Columns</span>
        <button class="btn btn-primary btn-sm" onclick="addWorkflowStatus()"><i class="fa fa-plus"></i> Add Column</button>
      </div>
      <div style="overflow-x:auto;">
        <table class="data-table">
          <thead><tr><th>Order</th><th>Name</th><th>Key</th><th>Category</th><th>Color</th><th>Actions</th></tr></thead>
          <tbody>
            ${workflowStatuses.map(s => `
              <tr>
                <td>${s.order_index}</td>
                <td><span class="badge" style="background:${s.color}20;color:${s.color};">${s.name}</span></td>
                <td><code>${s.key}</code></td>
                <td>${s.category}</td>
                <td>${s.color}</td>
                <td>
                  <button class="action-btn text-danger" onclick="deleteWorkflowStatus(${s.id})"><i class="fa fa-trash"></i></button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      
      <div class="card-title" style="display:flex;justify-content:space-between;margin-top:24px;">
        <span><i class="fa fa-exchange-alt"></i> Transition Rules</span>
        <button class="btn btn-primary btn-sm" onclick="addWorkflowRule()"><i class="fa fa-plus"></i> Add Rule</button>
      </div>
      <div style="overflow-x:auto;">
        <table class="data-table">
          <thead><tr><th>From Status</th><th>To Status</th><th>Allowed Role</th><th>Actions</th></tr></thead>
          <tbody>
            ${workflowRules.map(r => `
              <tr>
                <td><code>${r.from_status_key}</code></td>
                <td><code>${r.to_status_key}</code></td>
                <td><span class="badge" style="background:#e0e7ff;color:#4f46e5;">${r.allowed_role}</span></td>
                <td>
                  <button class="action-btn text-danger" onclick="deleteWorkflowRule(${r.id})"><i class="fa fa-trash"></i></button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
"""
content = content.replace("    <div class=\"card\" style=\"margin-top:16px;\">\n      <div class=\"card-title\"><i class=\"fa fa-shield-alt\"", render_settings_replacement + "\n    <div class=\"card\" style=\"margin-top:16px;\">\n      <div class=\"card-title\"><i class=\"fa fa-shield-alt\"")


# Add the functions for settings UI at the end of the file
workflow_ui_funcs = """
async function addWorkflowStatus() {
  const html = `
    <input id="swal-s-name" class="swal2-input" placeholder="Name (e.g. UAT)">
    <input id="swal-s-key" class="swal2-input" placeholder="Key (e.g. uat)">
    <input id="swal-s-color" class="swal2-input" type="color" value="#0052CC" style="height:40px;">
    <select id="swal-s-category" class="swal2-input">
      <option value="todo">To Do</option>
      <option value="in_progress">In Progress</option>
      <option value="done">Done</option>
    </select>
    <input id="swal-s-order" class="swal2-input" type="number" placeholder="Order (e.g. 5)" value="5">
  `;
  const r = await Swal.fire({ title: 'Add Workflow Column', html, showCancelButton: true, confirmButtonText: 'Add' });
  if (r.isConfirmed) {
    const name = document.getElementById('swal-s-name').value;
    const key = document.getElementById('swal-s-key').value;
    const color = document.getElementById('swal-s-color').value;
    const category = document.getElementById('swal-s-category').value;
    const order_index = parseInt(document.getElementById('swal-s-order').value) || 0;
    try {
      await api('POST', '/api/workflow/statuses', { name, key, color, category, order_index });
      toast('Column added');
      await loadWorkflowSettings();
      renderSettings(document.getElementById('page-settings'));
    } catch(e){}
  }
}

async function deleteWorkflowStatus(id) {
  if (!confirm('Delete this status?')) return;
  try {
    await api('DELETE', `/api/workflow/statuses/${id}`);
    await loadWorkflowSettings();
    renderSettings(document.getElementById('page-settings'));
  } catch(e){}
}

async function addWorkflowRule() {
  const options = workflowStatuses.map(s => `<option value="${s.key}">${s.name}</option>`).join('');
  const html = `
    <select id="swal-r-from" class="swal2-input">${options}</select>
    <div style="margin:10px 0;"><i class="fa fa-arrow-down"></i></div>
    <select id="swal-r-to" class="swal2-input">${options}</select>
    <input id="swal-r-role" class="swal2-input" placeholder="Allowed Role (e.g. developer)">
  `;
  const r = await Swal.fire({ title: 'Add Transition Rule', html, showCancelButton: true, confirmButtonText: 'Add' });
  if (r.isConfirmed) {
    const from_status_key = document.getElementById('swal-r-from').value;
    const to_status_key = document.getElementById('swal-r-to').value;
    const allowed_role = document.getElementById('swal-r-role').value;
    try {
      await api('POST', '/api/workflow/rules', { from_status_key, to_status_key, allowed_role });
      toast('Rule added');
      await loadWorkflowSettings();
      renderSettings(document.getElementById('page-settings'));
    } catch(e){}
  }
}

async function deleteWorkflowRule(id) {
  if (!confirm('Delete this rule?')) return;
  try {
    await api('DELETE', `/api/workflow/rules/${id}`);
    await loadWorkflowSettings();
    renderSettings(document.getElementById('page-settings'));
  } catch(e){}
}
"""
content += workflow_ui_funcs

with open(frontend_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated frontend successfully.")
