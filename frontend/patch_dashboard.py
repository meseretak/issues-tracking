import re

file_path = "c:/Users/meseretak/Desktop/devops execrices/issues tracking/frontend/app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_html = """  el.innerHTML = `
    <div style="margin-bottom: 24px;">
      <h2 style="font-size: 24px; color: #172B4D; margin-bottom: 4px;">Dashboard</h2>
      <p style="color: #6B778C; font-size: 14px;">Welcome back, ${currentUser.full_name.split(' ')[0]}! Here's what's happening with your projects.</p>
    </div>

    <!-- ═══ PREMIUM METRICS ROW ═══ -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
      <div class="metric-card" onclick="filterAndNav('status', '')" style="background: #fff; border: 1px solid #dfe1e6; border-radius: 8px; padding: 20px; cursor: pointer; border-top: 3px solid #0052CC; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)'" onmouseout="this.style.transform='none';this.style.boxShadow='0 1px 3px rgba(0,0,0,0.05)'">
        <div style="color: #6B778C; font-size: 13px; font-weight: 600; text-transform: uppercase;">Total Issues</div>
        <div style="font-size: 28px; font-weight: 700; color: #172B4D; margin-top: 8px;">${stats.total_issues}</div>
      </div>
      <div class="metric-card" onclick="filterAndNav('status', 'todo')" style="background: #fff; border: 1px solid #dfe1e6; border-radius: 8px; padding: 20px; cursor: pointer; border-top: 3px solid #FF991F; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)'" onmouseout="this.style.transform='none';this.style.boxShadow='0 1px 3px rgba(0,0,0,0.05)'">
        <div style="color: #6B778C; font-size: 13px; font-weight: 600; text-transform: uppercase;">Open Issues</div>
        <div style="font-size: 28px; font-weight: 700; color: #172B4D; margin-top: 8px;">${stats.open_issues}</div>
      </div>
      <div class="metric-card" onclick="filterAndNav('status', 'in_progress')" style="background: #fff; border: 1px solid #dfe1e6; border-radius: 8px; padding: 20px; cursor: pointer; border-top: 3px solid #36B37E; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)'" onmouseout="this.style.transform='none';this.style.boxShadow='0 1px 3px rgba(0,0,0,0.05)'">
        <div style="color: #6B778C; font-size: 13px; font-weight: 600; text-transform: uppercase;">In Progress</div>
        <div style="font-size: 28px; font-weight: 700; color: #172B4D; margin-top: 8px;">${stats.in_progress}</div>
      </div>
      <div class="metric-card" onclick="filterAndNav('status', '')" style="background: #fff; border: 1px solid #dfe1e6; border-radius: 8px; padding: 20px; cursor: pointer; border-top: 3px solid #FF5630; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)'" onmouseout="this.style.transform='none';this.style.boxShadow='0 1px 3px rgba(0,0,0,0.05)'">
        <div style="color: #6B778C; font-size: 13px; font-weight: 600; text-transform: uppercase;">Overdue</div>
        <div style="font-size: 28px; font-weight: 700; color: #172B4D; margin-top: 8px;">${stats.overdue}</div>
      </div>
    </div>

    <!-- ═══ GRAPHS & CHARTS ROW ═══ -->
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 24px;">
      <div style="background: #fff; border: 1px solid #dfe1e6; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="font-size: 14px; color: #172B4D; margin: 0 0 16px 0; font-weight: 600;">Issues by Status</h3>
        <div class="chart-wrap" style="height: 200px;"><canvas id="chart-status"></canvas></div>
      </div>
      <div style="background: #fff; border: 1px solid #dfe1e6; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="font-size: 14px; color: #172B4D; margin: 0 0 16px 0; font-weight: 600;">Issues by Priority</h3>
        <div class="chart-wrap" style="height: 200px;"><canvas id="chart-priority"></canvas></div>
      </div>
      <div style="background: #fff; border: 1px solid #dfe1e6; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="font-size: 14px; color: #172B4D; margin: 0 0 16px 0; font-weight: 600;">14-Day Trend</h3>
        <div class="chart-wrap" style="height: 200px;"><canvas id="chart-daily"></canvas></div>
      </div>
    </div>

    <!-- ═══ JIRA GADGETS ROW ═══ -->
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px;">
      
      <!-- Left Column: Assigned to Me & Intro -->
      <div>
        <!-- Introduction -->
        <div style="background:#fff; border:1px solid #dfe1e6; border-radius:3px; margin-bottom:16px;">
          <div style="background:#FF991F; color:#fff; padding:6px 16px; font-size:14px; font-weight:600; border-radius:3px 3px 0 0; display:flex; justify-content:space-between;">
            <span>Introduction</span>
            <div style="display:flex;gap:4px;"><i class="fa fa-arrows-alt"></i><i class="fa fa-minus"></i></div>
          </div>
          <div style="padding:16px; display:flex; gap:16px;">
            <img src="https://ui-avatars.com/api/?name=Awash+Bank&background=1B1F6B&color=fff&rounded=true" style="width:48px;height:48px;border-radius:50%;">
            <div>
              <h2 style="margin:0 0 8px 0;font-size:18px;color:#172B4D;font-weight:500;">Welcome to Awash Bank</h2>
              <p style="margin:0 0 8px 0;font-size:14px;color:#172B4D;">Here is your customized dashboard with both high-level metrics and your daily Jira tasks.</p>
            </div>
          </div>
        </div>

        <!-- Assigned to Me Gadget -->
        <div style="background:#fff; border:1px solid #dfe1e6; border-radius:3px; margin-bottom:16px;">
          <div style="background:#0052CC; color:#fff; padding:6px 16px; font-size:14px; font-weight:600; border-radius:3px 3px 0 0; display:flex; justify-content:space-between;">
            <span>Assigned to Me</span>
            <div style="display:flex;gap:4px;"><i class="fa fa-arrows-alt"></i><i class="fa fa-minus"></i></div>
          </div>
          <table style="width:100%; border-collapse:collapse; font-size:14px; color:#172B4D;">
            <thead>
              <tr style="border-bottom:1px solid #dfe1e6;">
                <th style="padding:8px 12px;text-align:left;font-weight:600;color:#5E6C84;width:30px;">T</th>
                <th style="padding:8px 12px;text-align:left;font-weight:600;color:#5E6C84;width:90px;">Key</th>
                <th style="padding:8px 12px;text-align:left;font-weight:600;color:#5E6C84;">Summary</th>
                <th style="padding:8px 12px;text-align:left;font-weight:600;color:#5E6C84;width:80px;">P</th>
              </tr>
            </thead>
            <tbody>
              ${myIssues.slice(0, 10).map(i => `
                <tr style="border-bottom:1px solid #f4f5f7; cursor:pointer;" onmouseover="this.style.background='#f4f5f7'" onmouseout="this.style.background=''" onclick="openIssueDetail(${i.id})">
                  <td style="padding:8px 12px;">${getTypeIcon(i.issue_type)}</td>
                  <td style="padding:8px 12px;"><a href="#" style="color:#0052CC;text-decoration:none;">${i.key}</a></td>
                  <td style="padding:8px 12px;">${i.title}</td>
                  <td style="padding:8px 12px;">${getPriorityBadge(i.priority)}</td>
                </tr>
              `).join('')}
              ${myIssues.length === 0 ? '<tr><td colspan="4" style="padding:16px;text-align:center;color:#6B778C;">No issues assigned to you.</td></tr>' : ''}
            </tbody>
          </table>
          ${myIssues.length > 0 ? `<div style="padding:8px 16px;font-size:12px;color:#5E6C84;border-top:1px solid #dfe1e6;display:flex;justify-content:space-between;"><span>1-${Math.min(10, myIssues.length)} of ${myIssues.length}</span><a href="#" style="color:#0052CC;" onclick="nav('myissues');return false;">View all</a></div>` : ''}
        </div>
      </div>

      <!-- Right Column: Activity Stream -->
      <div>
        <div style="background:#fff; border:1px solid #dfe1e6; border-radius:3px;">
          <div style="background:#0052CC; color:#fff; padding:6px 16px; font-size:14px; font-weight:600; border-radius:3px 3px 0 0; display:flex; justify-content:space-between;">
            <span>Activity Stream</span>
            <div style="display:flex;gap:4px;"><i class="fa fa-arrows-alt"></i><i class="fa fa-minus"></i></div>
          </div>
          <div style="padding:16px; max-height: 400px; overflow-y: auto;">
            <div style="font-size:12px;color:#5E6C84;margin-bottom:12px;">Recent Updates</div>
            ${stats.recent_activity.slice(0, 10).map(a => `
              <div style="display:flex;gap:12px;margin-bottom:16px;border-bottom:1px solid #f4f5f7;padding-bottom:12px;">
                <div class="avatar" style="background:${a.user.avatar_color || '#1B1F6B'};width:32px;height:32px;font-size:12px;border-radius:3px;display:flex;align-items:center;justify-content:center;color:#fff;flex-shrink:0;">${getInitials(a.user.full_name)}</div>
                <div>
                  <div style="font-size:13px;color:#172B4D;margin-bottom:4px;line-height:1.4;">
                    <strong>${a.user.full_name}</strong> ${a.action.replace(/_/g, ' ')} ${a.field_changed ? `<em style="color:#0052CC">${a.field_changed}</em>` : ''}
                  </div>
                  <div style="font-size:11px;color:#5E6C84;display:flex;gap:8px;">
                    <span>${fmtTime(a.created_at)}</span>
                  </div>
                </div>
              </div>
            `).join('')}
            ${stats.recent_activity.length === 0 ? '<div style="color:#6B778C;font-size:13px;text-align:center;">No recent activity</div>' : ''}
          </div>
        </div>
      </div>

    </div>
  `;"""

pattern = re.compile(r"el\.innerHTML = `[\s\S]*?</div>\s*`;")
new_content = pattern.sub(new_html.replace("\\", "\\\\"), content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)
print("Dashboard HTML replaced successfully.")
