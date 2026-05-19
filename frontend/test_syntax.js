const notifs = [];
const el = {};
function fmtTime() {}
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
      `).join('') : "<div class=\"empty-state\"><i class=\"fa fa-bell-slash\"></i><h3>No Notifications</h3><p>You're all caught up!</p></div>"}
    </div>
  `;
