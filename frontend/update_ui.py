import re

frontend_file = r"c:\Users\meseretak\Desktop\devops execrices\issues tracking\frontend\app.js"

with open(frontend_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update renderJiraDashboard
# Find renderJiraDashboard function body and replace the top section with Jira gadgets.
dashboard_pattern = r"async function renderJiraDashboard\(el\) \{.*?renderCharts\(stats\);"
dashboard_replacement = """async function renderJiraDashboard(el) {
  const stats = await api('GET', '/api/dashboard/stats');
  const myIssues = await api('GET', `/api/issues/?assignee_id=${currentUser.id}&page_size=10`);

  el.innerHTML = `
    <!-- Introduction Gadget -->
    <div style="background:#fff; border:1px solid #dfe1e6; border-radius:3px; margin-bottom:20px;">
      <div style="background:#FF991F; color:#fff; padding:6px 16px; font-size:14px; font-weight:600; border-radius:3px 3px 0 0; display:flex; justify-content:space-between;">
        <span>Introduction</span>
        <div style="display:flex;gap:4px;"><i class="fa fa-arrows-alt"></i><i class="fa fa-minus"></i></div>
      </div>
      <div style="padding:16px; display:flex; gap:16px;">
        <img src="https://ui-avatars.com/api/?name=Awash+Bank&background=1B1F6B&color=fff&rounded=true" style="width:48px;height:48px;border-radius:50%;">
        <div>
          <h2 style="margin:0 0 8px 0;font-size:20px;color:#172B4D;font-weight:500;">Welcome to Awash Bank</h2>
          <p style="margin:0 0 12px 0;font-size:14px;color:#172B4D;">Not sure where to start? Check out the <a href="#" style="color:#0052CC;">Jira 101 guide</a> and <a href="#" style="color:#0052CC;">Atlassian training course</a>.</p>
          <p style="margin:0;font-size:14px;color:#6B778C;">You can <a href="#" style="color:#0052CC;">customize this text</a> in the Administration section.</p>
        </div>
      </div>
    </div>

    <!-- Assigned to Me Gadget -->
    <div style="background:#fff; border:1px solid #dfe1e6; border-radius:3px; margin-bottom:20px;">
      <div style="background:#0052CC; color:#fff; padding:6px 16px; font-size:14px; font-weight:600; border-radius:3px 3px 0 0; display:flex; justify-content:space-between;">
        <span>Assigned to Me</span>
        <div style="display:flex;gap:4px;"><i class="fa fa-arrows-alt"></i><i class="fa fa-minus"></i></div>
      </div>
      <table style="width:100%; border-collapse:collapse; font-size:14px; color:#172B4D;">
        <thead>
          <tr style="border-bottom:1px solid #dfe1e6;">
            <th style="padding:6px 8px;text-align:left;font-weight:600;color:#5E6C84;width:30px;">T</th>
            <th style="padding:6px 8px;text-align:left;font-weight:600;color:#5E6C84;width:80px;">Key</th>
            <th style="padding:6px 8px;text-align:left;font-weight:600;color:#5E6C84;">Summary</th>
            <th style="padding:6px 8px;text-align:left;font-weight:600;color:#5E6C84;width:30px;">P</th>
          </tr>
        </thead>
        <tbody>
          ${myIssues.slice(0, 10).map(i => `
            <tr style="border-bottom:1px solid #f4f5f7; cursor:pointer;" onmouseover="this.style.background='#f4f5f7'" onmouseout="this.style.background=''" onclick="openIssueDetail(${i.id})">
              <td style="padding:8px;">${getTypeIcon(i.issue_type)}</td>
              <td style="padding:8px;"><a href="#" style="color:#0052CC;text-decoration:none;">${i.key}</a></td>
              <td style="padding:8px;">${i.title}</td>
              <td style="padding:8px;">${getPriorityBadge(i.priority)}</td>
            </tr>
          `).join('')}
          ${myIssues.length === 0 ? '<tr><td colspan="4" style="padding:16px;text-align:center;color:#6B778C;">No issues assigned to you.</td></tr>' : ''}
        </tbody>
      </table>
      ${myIssues.length > 0 ? `<div style="padding:8px 16px;font-size:12px;color:#5E6C84;border-top:1px solid #dfe1e6;display:flex;justify-content:space-between;"><span>1-${Math.min(10, myIssues.length)} of ${myIssues.length}</span><a href="#" style="color:#0052CC;" onclick="nav('myissues');return false;">View all</a></div>` : ''}
    </div>

    <!-- Activity Stream Gadget -->
    <div style="background:#fff; border:1px solid #dfe1e6; border-radius:3px; margin-bottom:20px;">
      <div style="background:#0052CC; color:#fff; padding:6px 16px; font-size:14px; font-weight:600; border-radius:3px 3px 0 0; display:flex; justify-content:space-between;">
        <span>Activity Stream</span>
        <div style="display:flex;gap:4px;"><i class="fa fa-arrows-alt"></i><i class="fa fa-minus"></i></div>
      </div>
      <div style="padding:16px;">
        <h3 style="margin:0 0 16px 0;font-size:16px;font-weight:500;color:#172B4D;">Your Company Jira</h3>
        <div style="font-size:12px;color:#5E6C84;margin-bottom:8px;">Wednesday</div>
        ${stats.recent_activity.slice(0, 5).map(a => `
          <div style="display:flex;gap:12px;margin-bottom:16px;">
            <div class="avatar" style="background:${a.user.avatar_color || '#1B1F6B'};width:32px;height:32px;font-size:12px;border-radius:3px;display:flex;align-items:center;justify-content:center;color:#fff;">${getInitials(a.user.full_name)}</div>
            <div>
              <div style="font-size:14px;color:#172B4D;margin-bottom:4px;">
                <strong>${a.user.full_name}</strong> ${a.action.replace(/_/g, ' ')} ${a.field_changed ? `<em>${a.field_changed}</em>` : ''}
              </div>
              <div style="font-size:12px;color:#5E6C84;display:flex;gap:8px;">
                <span><i class="fa fa-clock"></i> ${fmtTime(a.created_at)}</span>
                <a href="#" style="color:#0052CC;text-decoration:none;">Comment</a>
                <a href="#" style="color:#0052CC;text-decoration:none;">Vote</a>
                <a href="#" style="color:#0052CC;text-decoration:none;">Watch</a>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
    
    <hr style="border:none;border-top:1px solid #dfe1e6;margin:30px 0;">
    <h3 style="margin-bottom:16px;color:#172B4D;">Legacy Charts</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:14px;">
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-pie" style="color:#F5A623;"></i> By Status</div><div class="chart-wrap"><canvas id="chart-status"></canvas></div></div>
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-bar" style="color:#F5A623;"></i> By Priority</div><div class="chart-wrap"><canvas id="chart-priority"></canvas></div></div>
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-line" style="color:#F5A623;"></i> 14-Day Trend</div><div class="chart-wrap"><canvas id="chart-daily"></canvas></div></div>
    </div>
  `;

  renderCharts(stats);"""
content = re.sub(dashboard_pattern, dashboard_replacement, content, flags=re.DOTALL)

# 2. Update renderTeam (User Management)
team_pattern = r"async function renderTeam\(el\) \{.*?el\.innerHTML = `.*?<div id=\"team-grid\" class=\"team-grid\"></div>.*?`;\n  window\._teamFiltered = users;\n  renderUserGrid\(users, 1\);\n\}"
team_replacement = """async function renderTeam(el) {
  const users = allUsers;
  const USERS_PER_PAGE = 20;
  let teamPage = 1;
  const canAdd = can('createUser');

  window.renderUserList = function(filtered, page) {
    const total = filtered.length;
    const start = (page - 1) * USERS_PER_PAGE;
    const paged = filtered.slice(start, start + USERS_PER_PAGE);
    const tbody = document.getElementById('users-tbody');
    const pagInfo = document.getElementById('users-pagination');
    
    if (pagInfo) {
      pagInfo.innerHTML = `Displaying users <strong>${Math.min(total, start + 1)}</strong> to <strong>${Math.min(total, start + USERS_PER_PAGE)}</strong> of <strong>${total}</strong>.`;
    }
    
    if (tbody) {
      tbody.innerHTML = paged.map(u => `
        <tr style="border-bottom:1px solid #dfe1e6;">
          <td style="padding:10px 8px;display:flex;align-items:center;gap:8px;">
            <div class="avatar" style="background:${u.avatar_color || '#1B1F6B'};width:24px;height:24px;font-size:10px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;">${getInitials(u.full_name)}</div>
            <a href="#" style="color:#0052CC;text-decoration:none;font-size:14px;">${u.full_name}</a>
          </td>
          <td style="padding:10px 8px;font-size:14px;color:#172B4D;">
            <div>${u.username}</div>
            <div style="font-size:12px;color:#0052CC;">${u.email}</div>
          </td>
          <td style="padding:10px 8px;font-size:12px;color:#172B4D;">
            <div><strong>Count:</strong> ${Math.floor(Math.random()*100)}</div>
            <div><strong>Last:</strong> ${new Date().toLocaleDateString()}</div>
          </td>
          <td style="padding:10px 8px;font-size:13px;color:#0052CC;">
            jira-administrators<br>jira-software-users
          </td>
          <td style="padding:10px 8px;font-size:14px;color:#172B4D;">Jira Software</td>
          <td style="padding:10px 8px;font-size:14px;color:#5E6C84;">Jira Internal Directory</td>
          <td style="padding:10px 8px;font-size:14px;color:#0052CC;">
            ${canAdd ? `<a href="#" onclick="editTeamUser(${u.id});return false;" style="color:#0052CC;text-decoration:none;margin-right:8px;">Edit</a> <i class="fa fa-ellipsis-h" style="color:#5E6C84;cursor:pointer;"></i>` : ''}
          </td>
        </tr>
      `).join('');
    }
  };

  el.innerHTML = `
    <div style="padding:24px;background:#fff;min-height:100vh;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">
        <h2 style="margin:0;font-size:24px;color:#172B4D;font-weight:500;">Users</h2>
        <div style="display:flex;gap:4px;">
          <button style="background:#F4F5F7;color:#5E6C84;border:none;padding:6px 12px;border-radius:3px;font-weight:600;cursor:pointer;">Invite users</button>
          ${canAdd ? `<button style="background:#F4F5F7;color:#5E6C84;border:none;padding:6px 12px;border-radius:3px;font-weight:600;cursor:pointer;" onclick="openCreateUser()">Create user</button>` : ''}
        </div>
      </div>
      
      <div style="display:flex;gap:16px;align-items:flex-end;margin-bottom:16px;flex-wrap:wrap;">
        <div style="flex:1;min-width:200px;">
          <div style="font-size:12px;color:#5E6C84;font-weight:600;margin-bottom:4px;">Filter users</div>
          <div style="position:relative;">
            <input type="text" id="user-filter-search" placeholder="Name, username or email contains" style="width:100%;padding:6px 8px;border:2px solid #dfe1e6;border-radius:3px;outline:none;" onkeyup="filterUsersJira()">
            <i class="fa fa-search" style="position:absolute;right:10px;top:10px;color:#5E6C84;"></i>
          </div>
        </div>
        <div style="flex:1;min-width:150px;">
          <div style="font-size:12px;color:#5E6C84;font-weight:600;margin-bottom:4px;">In group</div>
          <select style="width:100%;padding:6px;border:1px solid #dfe1e6;border-radius:3px;background:#FAFBFC;"><option>Any</option></select>
        </div>
        <div style="flex:1;min-width:150px;">
          <div style="font-size:12px;color:#5E6C84;font-weight:600;margin-bottom:4px;">Application access</div>
          <select style="width:100%;padding:6px;border:1px solid #dfe1e6;border-radius:3px;background:#FAFBFC;"><option>All Users</option></select>
        </div>
        <div style="flex:1;min-width:120px;">
          <div style="font-size:12px;color:#5E6C84;font-weight:600;margin-bottom:4px;">Status</div>
          <select style="width:100%;padding:6px;border:1px solid #dfe1e6;border-radius:3px;background:#FAFBFC;"><option>All Users</option></select>
        </div>
        <div style="width:80px;">
          <div style="font-size:12px;color:#5E6C84;font-weight:600;margin-bottom:4px;">Users per page</div>
          <select style="width:100%;padding:6px;border:1px solid #dfe1e6;border-radius:3px;background:#FAFBFC;"><option>20</option></select>
        </div>
        <button style="background:#F4F5F7;color:#5E6C84;border:none;padding:6px 12px;border-radius:3px;font-weight:600;cursor:pointer;">Filter</button>
        <a href="#" style="color:#0052CC;text-decoration:none;font-size:14px;">Reset</a>
      </div>
      
      <div id="users-pagination" style="font-size:14px;color:#5E6C84;margin-bottom:16px;"></div>
      
      <table style="width:100%;border-collapse:collapse;text-align:left;">
        <thead>
          <tr style="border-bottom:2px solid #dfe1e6;">
            <th style="padding:8px;color:#5E6C84;font-weight:600;font-size:12px;">Full name</th>
            <th style="padding:8px;color:#5E6C84;font-weight:600;font-size:12px;">Username</th>
            <th style="padding:8px;color:#5E6C84;font-weight:600;font-size:12px;">Login details</th>
            <th style="padding:8px;color:#5E6C84;font-weight:600;font-size:12px;">Group name</th>
            <th style="padding:8px;color:#5E6C84;font-weight:600;font-size:12px;">Applications</th>
            <th style="padding:8px;color:#5E6C84;font-weight:600;font-size:12px;">Directory</th>
            <th style="padding:8px;color:#5E6C84;font-weight:600;font-size:12px;">Actions</th>
          </tr>
        </thead>
        <tbody id="users-tbody"></tbody>
      </table>
    </div>
  `;
  window._teamFiltered = users;
  window.filterUsersJira = function() {
    const q = document.getElementById('user-filter-search').value.toLowerCase();
    window._teamFiltered = allUsers.filter(u => u.full_name.toLowerCase().includes(q) || u.username.toLowerCase().includes(q) || u.email.toLowerCase().includes(q));
    renderUserList(window._teamFiltered, 1);
  };
  renderUserList(users, 1);
}"""
content = re.sub(team_pattern, team_replacement, content, flags=re.DOTALL)

# 3. Update renderSettings for Workflow Configuration
# Replace the workflow UI in renderSettings with Jira's Configure ABP Board Column management
settings_pattern = r"<div class=\"card\" style=\"margin-top:16px;\">\s*<div class=\"card-title\" style=\"display:flex;justify-content:space-between;\">\s*<span><i class=\"fa fa-project-diagram\"></i> Workflow & Board Columns</span>.*?</div>\s*</div>"
settings_replacement = """
    <div style="display:flex; margin-top:16px; background:#fff; min-height:600px; border:1px solid #dfe1e6; border-radius:3px;">
      <!-- Sidebar -->
      <div style="width:240px; border-right:1px solid #dfe1e6; padding:16px 0;">
        <div style="padding:0 16px; font-size:11px; font-weight:700; color:#6B778C; text-transform:uppercase; margin-bottom:8px;">Configuration</div>
        <div style="padding:8px 16px; color:#172B4D; font-size:14px; cursor:pointer;" onmouseover="this.style.background='#EBECF0'" onmouseout="this.style.background=''">General</div>
        <div style="padding:8px 16px; color:#0052CC; font-size:14px; background:#DEEBFF; border-right:3px solid #0052CC; cursor:pointer;">Columns</div>
        <div style="padding:8px 16px; color:#172B4D; font-size:14px; cursor:pointer;" onmouseover="this.style.background='#EBECF0'" onmouseout="this.style.background=''">Swimlanes</div>
        <div style="padding:8px 16px; color:#172B4D; font-size:14px; cursor:pointer;" onmouseover="this.style.background='#EBECF0'" onmouseout="this.style.background=''">Quick Filters</div>
        <div style="padding:8px 16px; color:#172B4D; font-size:14px; cursor:pointer;" onmouseover="this.style.background='#EBECF0'" onmouseout="this.style.background=''">Card colours</div>
        <div style="padding:8px 16px; color:#172B4D; font-size:14px; cursor:pointer;" onmouseover="this.style.background='#EBECF0'" onmouseout="this.style.background=''">Card layout</div>
        <div style="padding:8px 16px; color:#172B4D; font-size:14px; cursor:pointer;" onmouseover="this.style.background='#EBECF0'" onmouseout="this.style.background=''">Working days</div>
        <div style="padding:8px 16px; color:#172B4D; font-size:14px; cursor:pointer;" onmouseover="this.style.background='#EBECF0'" onmouseout="this.style.background=''">Issue Detail View</div>
      </div>
      
      <!-- Main Content -->
      <div style="flex:1; padding:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
          <h2 style="margin:0; font-size:20px; color:#172B4D; font-weight:500;">Column management</h2>
          <button style="background:#F4F5F7; color:#5E6C84; border:none; padding:6px 12px; border-radius:3px; font-weight:600; cursor:pointer;" onclick="addWorkflowStatus()">Add column</button>
        </div>
        <p style="color:#6B778C; font-size:14px; margin-bottom:24px;">Columns can be added, removed, reordered and renamed. Columns are based upon global statuses and can be moved between columns. Minimum and maximum constraints can be set for each mapped column.</p>
        
        <div style="display:flex; gap:32px; margin-bottom:24px; font-size:14px; color:#172B4D;">
          <div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
              <span style="color:#6B778C; font-size:12px; font-weight:600; width:120px;">Column Constraint</span>
              <select style="padding:4px 8px; border:1px solid #dfe1e6; border-radius:3px; background:#FAFBFC;"><option>Issue Count</option></select>
            </div>
            <div style="color:#6B778C; font-size:12px; margin-left:128px; margin-bottom:8px;">Constraints can be added to columns on the board for one statistic.</div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
              <span style="color:#6B778C; font-size:12px; font-weight:600; width:120px; text-align:right;">Days in column</span>
              <input type="checkbox">
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="color:#6B778C; font-size:12px; font-weight:600; width:120px;">Simplified Workflow</span>
              <strong>Software Simplified Workflow unavailable</strong>
            </div>
          </div>
        </div>

        <!-- Kanban Editor Layout -->
        <div style="display:flex; background:#F4F5F7; padding:16px; border-radius:3px; gap:16px; min-height:400px; overflow-x:auto;">
          
          <!-- Backlog -->
          <div style="width:200px; flex-shrink:0;">
            <div style="font-weight:600; color:#172B4D; font-size:14px; margin-bottom:8px;">Kanban backlog</div>
            <div style="background:#fff; border:1px dashed #dfe1e6; border-radius:3px; padding:16px; text-align:center; height:100%; display:flex; flex-direction:column; align-items:center;">
              <div style="background:#0052CC; color:#fff; padding:20px; border-radius:3px; margin-bottom:16px; width:100%;"><i class="fa fa-layer-group" style="font-size:32px;"></i></div>
              <div style="font-size:14px; font-weight:600; color:#172B4D; margin-bottom:8px;">Board getting full?</div>
              <div style="font-size:12px; color:#6B778C; margin-bottom:16px;">With the Kanban backlog you can plan your teams work in a dedicated space away from the board.</div>
              <div style="border:1px dashed #dfe1e6; padding:16px; color:#6B778C; font-size:12px; width:100%;">Drag a status here to enable</div>
            </div>
          </div>

          <!-- Mapped Columns -->
          <div style="display:flex; gap:16px; flex-grow:1; overflow-x:auto;">
            ${workflowStatuses.filter(s => s.category !== 'unmapped').map(s => `
              <div style="width:220px; flex-shrink:0; background:#fff; border:1px solid #dfe1e6; border-radius:3px; display:flex; flex-direction:column;">
                <div style="padding:12px; border-bottom:1px solid #dfe1e6; display:flex; justify-content:space-between; align-items:center;">
                  <span style="font-weight:600; color:#172B4D; font-size:14px;">${s.name}</span>
                  <i class="fa fa-filter" style="color:#6B778C; font-size:12px;"></i>
                </div>
                <div style="padding:8px 12px; display:flex; gap:8px; border-bottom:1px solid #dfe1e6;">
                  <input type="text" placeholder="No Min" style="width:50%; border:none; border-bottom:2px solid #FFAB00; padding:4px; font-size:12px; outline:none; text-align:center;">
                  <input type="text" placeholder="No Max" style="width:50%; border:none; border-bottom:2px solid ${s.color}; padding:4px; font-size:12px; outline:none; text-align:center;">
                </div>
                <div style="flex-grow:1; padding:12px; background:#FAFBFC;" ondragover="event.preventDefault();this.style.background='#EBECF0'" ondragleave="this.style.background='#FAFBFC'" ondrop="dropWorkflowStatus(event, '${s.category}')">
                  <div style="background:#fff; border:1px solid #dfe1e6; border-left:3px solid ${s.color}; border-radius:3px; padding:8px; font-size:11px; font-weight:700; color:#5E6C84; display:flex; justify-content:space-between; align-items:center; cursor:grab;" draggable="true" ondragstart="event.dataTransfer.setData('text/plain', '${s.id}')">
                    ${s.key.toUpperCase()}
                    <i class="fa fa-times" style="cursor:pointer;" onclick="deleteWorkflowStatus(${s.id})"></i>
                  </div>
                  <div style="font-size:12px; color:#6B778C; margin-top:8px;">No issues</div>
                </div>
              </div>
            `).join('')}
          </div>

          <!-- Unmapped Statuses -->
          <div style="width:200px; flex-shrink:0; background:#fff; border:1px solid #dfe1e6; border-radius:3px; display:flex; flex-direction:column;">
            <div style="padding:12px; border-bottom:1px solid #dfe1e6; display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:600; color:#172B4D; font-size:14px;">Unmapped Statuses <i class="fa fa-question-circle" style="color:#6B778C;"></i></span>
            </div>
            <div style="padding:12px; font-size:12px; color:#6B778C;">Statuses not containing issues</div>
            <div style="flex-grow:1; padding:12px; overflow-y:auto;" ondragover="event.preventDefault();this.style.background='#EBECF0'" ondragleave="this.style.background=''" ondrop="dropWorkflowStatus(event, 'unmapped')">
              ${workflowStatuses.filter(s => s.category === 'unmapped').map(s => `
                <div style="background:#fff; border:1px solid #dfe1e6; border-left:3px solid ${s.color}; border-radius:3px; padding:8px; font-size:11px; font-weight:700; color:#5E6C84; display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; cursor:grab;" draggable="true" ondragstart="event.dataTransfer.setData('text/plain', '${s.id}')">
                  ${s.key.toUpperCase()}
                  <i class="fa fa-times" style="cursor:pointer;" onclick="deleteWorkflowStatus(${s.id})"></i>
                </div>
              `).join('')}
            </div>
          </div>

        </div>
      </div>
    </div>
"""
content = re.sub(settings_pattern, settings_replacement, content, flags=re.DOTALL)

# Also add dropWorkflowStatus implementation to handle drag and drop column mapping
if "async function dropWorkflowStatus" not in content:
    drop_func = """
async function dropWorkflowStatus(e, category) {
  e.preventDefault();
  const idStr = e.dataTransfer.getData('text/plain');
  if (!idStr) return;
  const statusId = parseInt(idStr);
  const status = workflowStatuses.find(s => s.id === statusId);
  if (!status || status.category === category) return;
  try {
    status.category = category;
    await api('PUT', `/api/workflow/statuses/${statusId}`, status);
    toast('Status mapped to ' + category);
    await loadWorkflowSettings();
    renderSettings(document.getElementById('page-settings'));
  } catch(err) {
    toast('Failed to map status', 'error');
  }
}
"""
    content += drop_func

with open(frontend_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Jira UIs successfully.")
