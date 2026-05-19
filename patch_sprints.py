import re

NEW_SPRINTS = """async function renderSprints(el) {
  const IS_DEV = ['developer','devops_engineer','security_engineer','viewer'].includes(currentUser.role);
  
  el.innerHTML = `
    <div class="page-header" style="margin-bottom:20px;">
      <div>
        <div class="page-title" style="font-size:22px;color:#1B1F6B;font-weight:700;">Sprints</div>
        <div class="page-subtitle" style="font-size:14px;color:#64748b;margin-top:2px;">${allSprints.length} sprints &middot; Timeboxed iterations</div>
      </div>
      ${!IS_DEV ? `<button class="btn btn-primary" onclick="openCreateSprint()" style="background:#1B1F6B;border:none;padding:8px 16px;font-size:13px;font-weight:600;border-radius:6px;box-shadow:0 2px 4px rgba(27,31,107,0.2);"><i class="fa fa-plus" style="margin-right:6px;"></i> New Sprint</button>` : ''}
    </div>
    
    <div class="sprint-list" style="display:grid;grid-template-columns:repeat(auto-fill, minmax(350px, 1fr));gap:16px;">
      ${allSprints.map(s => {
        const isAct = s.status === 'active';
        const isFuture = s.status === 'planned';
        const isDone = s.status === 'closed';
        
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
            daysHtml = `<span style="font-weight:700;color:\${left<=2?'#dc2626':'#F5A623'}"><i class="fa fa-clock"></i> \${left} days left</span>`;
          } else if (isFuture) {
            const startsIn = Math.max(0, Math.ceil((start - now)/(1000*60*60*24)));
            daysHtml = `<span style="color:#64748b;"><i class="fa fa-calendar"></i> Starts in \${startsIn} days</span>`;
          } else {
            daysHtml = `<span style="color:#64748b;"><i class="fa fa-check-double"></i> Completed</span>`;
          }
        }
        
        return \`<div class="sprint-item" style="\${bgStyle}border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.05);transition:transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)';this.style.transform='translateY(-2px)'" onmouseout="this.style.boxShadow='0 1px 3px rgba(0,0,0,0.05)';this.style.transform='translateY(0)'">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
            <div>
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="font-size:16px;font-weight:700;color:#1e293b;">\${s.name}</div>
                <span style="font-size:10px;font-weight:700;padding:2px 6px;border-radius:12px;background:\${isAct?'#fef3c7':isDone?'#d1fae5':'#f1f5f9'};color:\${headerColor};text-transform:uppercase;">\${s.status}</span>
              </div>
              <div style="font-size:12px;color:#64748b;margin-top:4px;">\${s.start_date ? fmt(s.start_date) : '-'} &mdash; \${s.end_date ? fmt(s.end_date) : '-'}</div>
            </div>
            <button class="btn btn-sm" onclick="viewSprintBoard(\${s.id})" style="background:#f1f5f9;color:#0052CC;border:none;padding:6px 10px;border-radius:4px;font-size:12px;font-weight:600;cursor:pointer;"><i class="fa fa-columns"></i> Board</button>
          </div>
          
          \${s.goal ? \`<div style="font-size:13px;color:#334155;background:\${isAct?'#fffbeb':'#f8fafc'};padding:8px 12px;border-radius:4px;border-left:3px solid \${headerColor};margin-bottom:14px;">"\${s.goal}"</div>\` : ''}
          
          <div style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;font-weight:600;">
              <span style="color:#475569;">Progress (\${doneC}/\${totalC})</span>
              <span style="color:\${pct===100?'#10b981':'#1e293b'};">\${pct}%</span>
            </div>
            <div style="height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;">
              <div style="height:100%;width:\${pct}%;background:\${isAct ? (pct===100?'#10b981':'#0052CC') : isDone ? '#10b981' : '#94a3b8'};"></div>
            </div>
          </div>
          
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;border-top:1px solid #e2e8f0;padding-top:12px;margin-top:auto;">
            \${daysHtml}
            \${isAct && !IS_DEV ? \`<button onclick="toast('Complete sprint dialog','info')" style="background:transparent;border:none;color:#0052CC;font-weight:600;font-size:12px;cursor:pointer;">Complete Sprint</button>\` : ''}
          </div>
        </div>\`;
      }).join('')}
    </div>
  `;
}
"""

with open(r'frontend\app.js', encoding='utf-8') as f:
    content = f.read()

start = content.find('async function renderSprints')
end = content.find('\nfunction viewSprintBoard', start)

if start != -1 and end != -1:
    new_content = content[:start] + NEW_SPRINTS + content[end:]
    with open(r'frontend\app.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Successfully patched renderSprints')
else:
    print('Failed to find boundaries')
