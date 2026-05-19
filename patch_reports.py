import re

NEW_REPORTS = """async function renderReports(el) {
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
              
              return \`<tr style="border-bottom:1px solid #f1f5f9;">
                <td style="padding:12px 16px;">
                  <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:24px;height:24px;border-radius:4px;background:\${p.color||'#1B1F6B'};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:10px;">\${p.name.charAt(0)}</div>
                    <div>
                      <div style="font-weight:600;color:#1e293b;font-size:13.5px;">\${p.name}</div>
                      <div style="font-size:11.5px;color:#64748b;margin-top:2px;font-family:monospace;">\${p.key}</div>
                    </div>
                  </div>
                </td>
                <td style="padding:12px 16px;">
                  <div style="display:flex;align-items:center;gap:6px;color:\${typeColor};font-size:12px;text-transform:capitalize;">
                    <i class="fa \${typeIcon}"></i> \${typeName}
                  </div>
                </td>
                <td style="padding:12px 16px;text-align:center;font-weight:600;color:#334155;">\${total}</td>
                <td style="padding:12px 16px;">
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div style="flex:1;display:flex;height:8px;border-radius:4px;overflow:hidden;background:#e2e8f0;">
                      \${wTodo>0 ? \`<div style="width:\${wTodo}%;background:#64748b;" title="\${todo} To Do"></div>\` : ''}
                      \${wProg>0 ? \`<div style="width:\${wProg}%;background:#f59e0b;" title="\${prog} In Progress"></div>\` : ''}
                      \${wDone>0 ? \`<div style="width:\${wDone}%;background:#10b981;" title="\${done} Done"></div>\` : ''}
                    </div>
                    <div style="font-size:11.5px;color:#475569;white-space:nowrap;width:70px;text-align:right;">
                      \${todo} / \${prog} / \${done}
                    </div>
                  </div>
                </td>
                <td style="padding:12px 16px;">
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div style="flex:1;height:6px;border-radius:3px;background:#e2e8f0;overflow:hidden;">
                      <div style="height:100%;width:\${pct}%;background:\${pct===100 ? '#10b981' : '#0ea5e9'};"></div>
                    </div>
                    <span style="font-size:12px;font-weight:600;color:#334155;width:32px;text-align:right;">\${pct}%</span>
                  </div>
                </td>
              </tr>\`;
            }).join('') : '<tr><td colspan="5" style="padding:30px;text-align:center;color:#64748b;">No active projects found.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>
  `;
}
"""

with open(r'frontend\app.js', encoding='utf-8') as f:
    content = f.read()

start = content.find('async function renderReports')
end = content.find('\n// ── SLA Monitor', start)

if start != -1 and end != -1:
    new_content = content[:start] + NEW_REPORTS + content[end:]
    with open(r'frontend\app.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Successfully patched renderReports')
else:
    print('Failed to find boundaries')
