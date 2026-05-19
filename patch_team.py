import re

NEW_TEAM = """async function renderTeam(el) {
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
      
      return \`<tr style="border-bottom:1px solid #f1f5f9;transition:background 0.1s;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
        <td style="padding:12px 14px;vertical-align:middle;display:flex;align-items:center;gap:8px;">
          <div style="background:\${u.avatar_color || '#1B1F6B'};width:24px;height:24px;border-radius:50%;color:#fff;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;">
            \${getInitials(u.full_name)}
          </div>
          <span style="color:#0052CC;font-weight:600;cursor:pointer;" onclick="toast('User profile loaded','info')">\${u.full_name}</span>
        </td>
        <td style="padding:12px 14px;vertical-align:middle;">
          <div style="color:#1e293b;font-weight:500;font-size:12.5px;">\${u.username}</div>
          <div style="color:#64748b;font-size:11.5px;">\${u.email}</div>
        </td>
        <td style="padding:12px 14px;vertical-align:middle;font-size:12px;color:#334155;line-height:1.4;">
          <strong>Count:</strong> \${loginCount}<br/>
          <span style="color:#64748b;"><strong>Last:</strong> \${lastLogin}</span>
        </td>
        <td style="padding:12px 14px;vertical-align:middle;max-width:240px;line-height:1.5;">
          <span style="color:#0052CC;font-size:11.5px;cursor:pointer;display:inline-block;margin-right:6px;" onclick="toast('Group page loaded','info')">\${groupName}</span>
        </td>
        <td style="padding:12px 14px;vertical-align:middle;color:#475569;font-size:12.5px;">Jira Software</td>
        <td style="padding:12px 14px;vertical-align:middle;color:#475569;font-size:12.5px;">Jira Internal Directory</td>
        <td style="padding:12px 14px;vertical-align:middle;white-space:nowrap;">
          <span style="color:#0052CC;cursor:pointer;font-weight:600;font-size:12.5px;margin-right:8px;" onclick="toast('User edit modal opened','info')">Edit</span>
          <i class="fa fa-ellipsis-h" style="color:#64748b;cursor:pointer;" onclick="toast('Actions menu opened','info')"></i>
        </td>
      </tr>\`;
    }).join('');

    if (pag && totalPages > 1) {
      let btns = \`<button class="page-btn" onclick="teamPage=Math.max(1,teamPage-1);renderUserTable(window._teamFiltered||allUsers,teamPage)" \${page === 1 ? 'disabled' : ''}>&lt; Prev</button>\`;
      for (let p = 1; p <= totalPages; p++) {
        btns += \`<button class="page-btn \${p === page ? 'active' : ''}" onclick="teamPage=\${p};renderUserTable(window._teamFiltered||allUsers,teamPage)">\${p}</button>\`;
      }
      btns += \`<button class="page-btn" onclick="teamPage=Math.min(\${totalPages},teamPage+1);renderUserTable(window._teamFiltered||allUsers,teamPage)" \${page === totalPages ? 'disabled' : ''}>Next &gt;</button>\`;
      pag.innerHTML = \`<div style="display:flex;justify-content:end;margin-top:10px;">\${btns}</div>\`;
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
"""

with open(r'frontend\app.js', encoding='utf-8') as f:
    content = f.read()

start = content.find('async function renderTeam')
end = content.find('\n// ── Reports', start)

if start != -1 and end != -1:
    new_content = content[:start] + NEW_TEAM + content[end:]
    with open(r'frontend\app.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Successfully patched renderTeam')
else:
    print('Failed to find boundaries')
