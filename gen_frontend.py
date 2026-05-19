import os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
FE = os.path.join(BASE, "frontend")
os.makedirs(FE, exist_ok=True)

def write(path, content):
    with open(os.path.join(FE, path), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote {path} ({len(content)} bytes)")

print("Generating Awash Bank Issue Tracker frontend...")
# ── app.css ───────────────────────────────────────────────────────────────────
CSS = """
:root{--navy:#1B1F6B;--orange:#F5A623;--navy-dark:#13175a;--bg:#f0f2f8;--sw:240px;--card:#fff;--border:#e2e6f0;--text:#1a1d2e;--muted:#6b7280;--r:10px;--sh:0 2px 12px rgba(27,31,107,.08);}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:Inter,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;}
#login-page{display:flex;align-items:center;justify-content:center;min-height:100vh;background:linear-gradient(135deg,#1B1F6B 0%,#2a3080 60%,#3a4db0 100%);}
.login-card{background:#fff;border-radius:18px;padding:48px 40px;width:420px;box-shadow:0 20px 60px rgba(0,0,0,.3);}
.login-logo{display:flex;align-items:center;gap:14px;margin-bottom:32px;}
.logo-circle{width:52px;height:52px;border-radius:50%;background:#1B1F6B;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:18px;border:3px solid #F5A623;}
.login-logo h1{font-size:20px;font-weight:700;color:#1B1F6B;line-height:1.2;}
.login-logo span{font-size:12px;color:#6b7280;}
.form-group{margin-bottom:18px;}
.form-group label{display:block;font-size:13px;font-weight:600;color:var(--text);margin-bottom:6px;}
.form-group input,.form-group select,.form-group textarea{width:100%;padding:11px 14px;border:1.5px solid var(--border);border-radius:8px;font-size:14px;font-family:Inter,sans-serif;transition:.2s;outline:none;background:#fff;color:var(--text);}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{border-color:#1B1F6B;box-shadow:0 0 0 3px rgba(27,31,107,.1);}
.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 20px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;border:none;transition:.2s;font-family:Inter,sans-serif;text-decoration:none;}
.btn-primary{background:#1B1F6B;color:#fff;}.btn-primary:hover{background:#13175a;}
.btn-orange{background:#F5A623;color:#fff;}.btn-orange:hover{background:#e09510;}
.btn-outline{background:#fff;color:#1B1F6B;border:1.5px solid #1B1F6B;}.btn-outline:hover{background:#f0f2f8;}
.btn-danger{background:#ef4444;color:#fff;}.btn-danger:hover{background:#dc2626;}
.btn-success{background:#16a34a;color:#fff;}.btn-success:hover{background:#15803d;}
.btn-sm{padding:6px 14px;font-size:12px;}
.btn-full{width:100%;justify-content:center;padding:13px;}
.btn:disabled{opacity:.5;cursor:not-allowed;}
#app{display:none;height:100vh;overflow:hidden;}
.sidebar{position:fixed;left:0;top:0;bottom:0;width:var(--sw);background:#1B1F6B;color:#fff;display:flex;flex-direction:column;z-index:100;transition:.3s;}
.sidebar-header{padding:18px 16px;border-bottom:1px solid rgba(255,255,255,.1);display:flex;align-items:center;gap:12px;}
.sidebar-logo{width:38px;height:38px;border-radius:50%;background:#F5A623;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;flex-shrink:0;color:#fff;}
.sidebar-title{font-size:13px;font-weight:700;line-height:1.2;}
.sidebar-subtitle{font-size:10px;opacity:.6;}
.sidebar-nav{flex:1;overflow-y:auto;padding:10px 0;}
.nav-section{padding:10px 16px 4px;font-size:10px;font-weight:700;opacity:.4;letter-spacing:1px;text-transform:uppercase;}
.nav-item{display:flex;align-items:center;gap:11px;padding:10px 16px;cursor:pointer;transition:.15s;font-size:13px;font-weight:500;border-left:3px solid transparent;color:rgba(255,255,255,.7);}
.nav-item:hover{background:rgba(255,255,255,.08);color:#fff;}
.nav-item.active{background:rgba(245,166,35,.15);border-left-color:#F5A623;color:#fff;}
.nav-item i{width:18px;text-align:center;font-size:14px;}
.nav-badge{margin-left:auto;background:#F5A623;color:#fff;border-radius:10px;padding:1px 7px;font-size:10px;font-weight:700;}
.sidebar-footer{padding:12px 16px;border-top:1px solid rgba(255,255,255,.1);}
.user-info{display:flex;align-items:center;gap:10px;}
.user-avatar{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;flex-shrink:0;color:#fff;}
.user-name{font-size:13px;font-weight:600;line-height:1.2;flex:1;}
.user-role-txt{font-size:10px;opacity:.6;}
.logout-btn{background:none;border:none;color:rgba(255,255,255,.5);cursor:pointer;padding:6px;border-radius:4px;transition:.2s;font-size:14px;}
.logout-btn:hover{color:#fff;background:rgba(255,255,255,.1);}
.main{margin-left:var(--sw);height:100vh;display:flex;flex-direction:column;overflow:hidden;}
.topbar{background:#fff;border-bottom:1px solid var(--border);padding:0 24px;height:60px;display:flex;align-items:center;gap:14px;flex-shrink:0;}
.topbar-title{font-size:17px;font-weight:700;color:#1B1F6B;flex:1;}
.search-box{display:flex;align-items:center;gap:8px;background:var(--bg);border:1.5px solid var(--border);border-radius:8px;padding:7px 14px;width:240px;}
.search-box input{border:none;background:none;outline:none;font-size:13px;width:100%;font-family:Inter,sans-serif;}
.notif-btn{position:relative;background:none;border:none;cursor:pointer;padding:8px;border-radius:8px;color:var(--muted);font-size:18px;transition:.2s;}
.notif-btn:hover{background:var(--bg);color:#1B1F6B;}
.notif-badge{position:absolute;top:4px;right:4px;background:#F5A623;color:#fff;border-radius:50%;width:16px;height:16px;font-size:9px;font-weight:700;display:flex;align-items:center;justify-content:center;}
.content{flex:1;overflow-y:auto;padding:24px;}
.page{display:none;}.page.active{display:block;}
.page-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;}
.page-title{font-size:20px;font-weight:700;color:#1B1F6B;}
.stats-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:24px;}
.stat-card{background:var(--card);border-radius:var(--r);padding:20px;box-shadow:var(--sh);border-left:4px solid #1B1F6B;display:flex;align-items:center;gap:16px;transition:.2s;}
.stat-card:hover{transform:translateY(-2px);}
.stat-icon{width:48px;height:48px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;}
.stat-value{font-size:28px;font-weight:700;color:#1B1F6B;line-height:1;}
.stat-label{font-size:12px;color:var(--muted);margin-top:3px;font-weight:500;}
.charts-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:24px;}
.chart-card{background:var(--card);border-radius:var(--r);padding:20px;box-shadow:var(--sh);}
.chart-card.wide{grid-column:span 2;}
.chart-card.full{grid-column:span 3;}
.chart-title{font-size:14px;font-weight:700;color:#1B1F6B;margin-bottom:16px;display:flex;align-items:center;gap:8px;}
.chart-wrap{position:relative;height:200px;}
.chart-wrap.tall{height:260px;}
.bottom-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;}
.card{background:var(--card);border-radius:var(--r);padding:20px;box-shadow:var(--sh);}
.card-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;}
.card-title{font-size:14px;font-weight:700;color:#1B1F6B;}
.activity-item{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--border);}
.activity-item:last-child{border-bottom:none;}
.activity-avatar{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;color:#fff;}
.activity-text{font-size:13px;line-height:1.5;}
.activity-time{font-size:11px;color:var(--muted);margin-top:2px;}
.progress-bar{background:var(--border);border-radius:20px;height:10px;overflow:hidden;margin:10px 0;}
.progress-fill{height:100%;background:linear-gradient(90deg,#1B1F6B,#F5A623);border-radius:20px;transition:.5s;}
.filter-bar{background:var(--card);border-radius:var(--r);padding:14px 18px;box-shadow:var(--sh);margin-bottom:16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;}
.filter-bar select,.filter-bar input{padding:7px 12px;border:1.5px solid var(--border);border-radius:7px;font-size:13px;font-family:Inter,sans-serif;outline:none;background:#fff;color:var(--text);}
.filter-bar select:focus,.filter-bar input:focus{border-color:#1B1F6B;}
.tbl-wrap{background:var(--card);border-radius:var(--r);box-shadow:var(--sh);overflow:hidden;}
table{width:100%;border-collapse:collapse;}
thead{background:#1B1F6B;color:#fff;}
th{padding:12px 16px;text-align:left;font-size:11px;font-weight:600;letter-spacing:.5px;text-transform:uppercase;white-space:nowrap;}
td{padding:11px 16px;font-size:13px;border-bottom:1px solid var(--border);vertical-align:middle;}
tr:last-child td{border-bottom:none;}
tbody tr:hover td{background:#f8f9ff;cursor:pointer;}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;white-space:nowrap;}
.s-backlog{background:#f1f5f9;color:#64748b;}.s-todo{background:#dbeafe;color:#1d4ed8;}
.s-in_progress{background:#fff7ed;color:#c2410c;}.s-in_review{background:#f3e8ff;color:#7c3aed;}
.s-testing{background:#fef9c3;color:#a16207;}.s-done{background:#dcfce7;color:#15803d;}
.s-closed{background:#f1f5f9;color:#374151;}.s-cancelled{background:#fee2e2;color:#dc2626;}
.p-critical{background:#fee2e2;color:#dc2626;}.p-high{background:#fff7ed;color:#c2410c;}
.p-medium{background:#dbeafe;color:#1d4ed8;}.p-low{background:#f1f5f9;color:#64748b;}
.r-admin{background:#1B1F6B;color:#fff;}.r-project_manager{background:#7c3aed;color:#fff;}
.r-qa_engineer{background:#15803d;color:#fff;}.r-devops_engineer{background:#0d7377;color:#fff;}
.r-developer{background:#1d4ed8;color:#fff;}.r-business_analyst{background:#c2410c;color:#fff;}
.r-security_engineer{background:#dc2626;color:#fff;}.r-viewer{background:#6b7280;color:#fff;}
.type-icon{width:22px;height:22px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;font-size:11px;}
.t-bug{background:#fee2e2;color:#dc2626;}.t-feature{background:#dcfce7;color:#15803d;}
.t-task{background:#dbeafe;color:#1d4ed8;}.t-epic{background:#f3e8ff;color:#7c3aed;}
.t-story{background:#cffafe;color:#0e7490;}.t-improvement{background:#fef9c3;color:#a16207;}
.t-security{background:#fee2e2;color:#dc2626;}.t-incident{background:#fee2e2;color:#dc2626;}
.avatar{width:28px;height:28px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff;flex-shrink:0;}
.kanban-board{display:flex;gap:14px;overflow-x:auto;padding-bottom:16px;height:calc(100vh - 180px);}
.kanban-col{min-width:230px;max-width:270px;flex-shrink:0;background:#e8eaf6;border-radius:var(--r);display:flex;flex-direction:column;max-height:100%;}
.kanban-col-header{padding:12px 14px;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:space-between;border-radius:var(--r) var(--r) 0 0;text-transform:uppercase;letter-spacing:.5px;}
.kanban-col-count{background:rgba(0,0,0,.15);border-radius:10px;padding:1px 7px;font-size:11px;}
.kanban-col-body{flex:1;padding:8px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;}
.kanban-card{background:#fff;border-radius:8px;padding:12px;box-shadow:0 1px 4px rgba(0,0,0,.08);cursor:pointer;transition:.15s;border-left:3px solid #e2e6f0;}
.kanban-card:hover{box-shadow:0 4px 12px rgba(0,0,0,.12);transform:translateY(-1px);}
.kanban-card-key{font-size:11px;color:var(--muted);font-weight:600;margin-bottom:4px;}
.kanban-card-title{font-size:13px;font-weight:500;line-height:1.4;margin-bottom:8px;}
.kanban-card-footer{display:flex;align-items:center;justify-content:space-between;}
.sp-badge{background:var(--bg);color:var(--muted);border-radius:4px;padding:2px 6px;font-size:11px;font-weight:600;}
.projects-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;}
.project-card{background:var(--card);border-radius:var(--r);overflow:hidden;box-shadow:var(--sh);cursor:pointer;transition:.2s;}
.project-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(27,31,107,.12);}
.project-card-top{height:5px;}
.project-card-body{padding:18px;}
.project-key{display:inline-block;background:#1B1F6B;color:#fff;border-radius:6px;padding:3px 10px;font-size:12px;font-weight:700;margin-bottom:10px;}
.project-name{font-size:15px;font-weight:700;color:#1B1F6B;margin-bottom:4px;}
.project-dept{font-size:12px;color:var(--muted);margin-bottom:12px;}
.project-stats{display:flex;gap:20px;}
.project-stat-val{font-size:20px;font-weight:700;color:#1B1F6B;}
.project-stat-lbl{font-size:11px;color:var(--muted);}
.users-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px;}
.user-card{background:var(--card);border-radius:var(--r);padding:20px;box-shadow:var(--sh);text-align:center;transition:.2s;}
.user-card:hover{transform:translateY(-2px);}
.user-card-avatar{width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;color:#fff;margin:0 auto 12px;}
.user-card-name{font-size:14px;font-weight:700;color:#1B1F6B;margin-bottom:4px;}
.user-card-dept{font-size:12px;color:var(--muted);margin-bottom:8px;}
.sprint-list{display:flex;flex-direction:column;gap:12px;}
.sprint-item{background:var(--card);border-radius:var(--r);padding:18px;box-shadow:var(--sh);}
.sprint-item-header{display:flex;align-items:center;gap:12px;margin-bottom:10px;}
.sprint-name{font-size:15px;font-weight:700;color:#1B1F6B;flex:1;}
.sprint-dates{font-size:12px;color:var(--muted);}
.sprint-goal{font-size:13px;color:var(--muted);margin-bottom:10px;font-style:italic;}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;}
.modal{background:#fff;border-radius:14px;width:100%;max-width:680px;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.3);}
.modal-lg{max-width:960px;}
.modal-header{padding:20px 24px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;background:#fff;z-index:1;border-radius:14px 14px 0 0;}
.modal-title{font-size:16px;font-weight:700;color:#1B1F6B;}
.modal-close{background:none;border:none;font-size:20px;cursor:pointer;color:var(--muted);padding:4px 8px;border-radius:4px;transition:.2s;}
.modal-close:hover{background:var(--bg);}
.modal-body{padding:24px;}
.modal-footer{padding:16px 24px;border-top:1px solid var(--border);display:flex;gap:10px;justify-content:flex-end;}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
.issue-detail-grid{display:grid;grid-template-columns:1fr 260px;gap:24px;}
.issue-tabs{display:flex;border-bottom:2px solid var(--border);margin-bottom:20px;}
.issue-tab{padding:10px 18px;font-size:13px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;color:var(--muted);transition:.15s;}
.issue-tab.active{color:#1B1F6B;border-bottom-color:#1B1F6B;}
.tab-pane{display:none;}.tab-pane.active{display:block;}
.detail-label{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px;}
.detail-value{font-size:13.5px;color:var(--text);}
.detail-field{margin-bottom:14px;}
.detail-sidebar .detail-field{padding:10px 0;border-bottom:1px solid var(--border);}
.comment-item{display:flex;gap:12px;margin-bottom:16px;}
.comment-body{flex:1;background:var(--bg);border-radius:8px;padding:12px;}
.comment-author{font-size:12px;font-weight:700;color:#1B1F6B;}
.comment-time{font-size:11px;color:var(--muted);margin-left:8px;}
.comment-text{font-size:13px;margin-top:6px;line-height:1.5;}
.comment-internal{border-left:3px solid #F5A623;background:#fffbf0;}
.notif-item{display:flex;gap:12px;padding:14px 0;border-bottom:1px solid var(--border);cursor:pointer;transition:.15s;}
.notif-item:hover{background:#f8f9ff;}
.notif-dot{width:8px;height:8px;border-radius:50%;background:#F5A623;flex-shrink:0;margin-top:5px;}
.notif-dot.read{background:var(--border);}
.notif-msg{font-size:13px;line-height:1.4;}
.notif-time{font-size:11px;color:var(--muted);margin-top:3px;}
.toast-container{position:fixed;top:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px;}
.toast{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 4px 20px rgba(0,0,0,.15);display:flex;align-items:center;gap:12px;min-width:280px;border-left:4px solid #1B1F6B;animation:slideIn .3s ease;}
.toast-success{border-left-color:#16a34a;}.toast-error{border-left-color:#dc2626;}.toast-warning{border-left-color:#F5A623;}
.toast-msg{font-size:13px;font-weight:500;flex:1;}
@keyframes slideIn{from{transform:translateX(110%);opacity:0;}to{transform:translateX(0);opacity:1;}}
.spinner{display:inline-block;width:18px;height:18px;border:2px solid var(--border);border-top-color:#1B1F6B;border-radius:50%;animation:spin .7s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
.empty-state{text-align:center;padding:60px 20px;color:var(--muted);}
.empty-state i{font-size:48px;margin-bottom:16px;opacity:.3;display:block;}
.empty-state h3{font-size:16px;font-weight:600;margin-bottom:8px;color:var(--text);}
.pagination{display:flex;align-items:center;gap:6px;margin-top:16px;justify-content:center;}
.page-btn{padding:6px 12px;border:1.5px solid var(--border);border-radius:6px;background:#fff;cursor:pointer;font-size:13px;transition:.15s;font-family:Inter,sans-serif;}
.page-btn:hover,.page-btn.active{background:#1B1F6B;color:#fff;border-color:#1B1F6B;}
.sla-bar{height:6px;border-radius:3px;background:var(--border);overflow:hidden;margin-top:4px;}
.sla-fill{height:100%;border-radius:3px;transition:.3s;}
.sla-ok{background:#16a34a;}.sla-warn{background:#F5A623;}.sla-breach{background:#dc2626;}
.metric-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border);}
.metric-row:last-child{border-bottom:none;}
.metric-label{font-size:13px;}.metric-value{font-size:14px;font-weight:700;color:#1B1F6B;}
.reports-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
.three-col{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;}
.audit-row{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--border);font-size:13px;}
.audit-row:last-child{border-bottom:none;}
.audit-time{color:var(--muted);font-size:11px;white-space:nowrap;min-width:130px;}
.audit-user{font-weight:600;color:#1B1F6B;}
.inline-edit{cursor:pointer;border-bottom:1px dashed var(--border);padding:2px 4px;border-radius:3px;transition:.15s;}
.inline-edit:hover{background:var(--bg);border-bottom-color:#1B1F6B;}
@media(max-width:1400px){.stats-grid{grid-template-columns:repeat(3,1fr);}}
@media(max-width:1100px){.charts-grid{grid-template-columns:1fr 1fr;}.chart-card.wide,.chart-card.full{grid-column:span 2;}}
@media(max-width:768px){:root{--sw:60px;}.sidebar-title,.sidebar-subtitle,.nav-item span,.user-name,.user-role-txt{display:none;}.main{margin-left:60px;}.stats-grid{grid-template-columns:1fr 1fr;}.issue-detail-grid{grid-template-columns:1fr;}.form-row{grid-template-columns:1fr;}}
"""
write("app.css", CSS)

# ── index.html ────────────────────────────────────────────────────────────────
INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Awash Bank Issue Tracker</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link rel="stylesheet" href="app.css"/>
</head>
<body>
<div class="toast-container" id="toasts"></div>
<div id="login-page">
  <div class="login-card">
    <div class="login-logo">
      <div class="logo-circle">AB</div>
      <div><h1>Awash Bank</h1><span>Issue Tracker &amp; Project Management</span></div>
    </div>
    <div id="login-error" style="display:none;background:#fee2e2;color:#dc2626;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:16px;"></div>
    <div class="form-group">
      <label><i class="fa fa-user" style="margin-right:6px;color:#1B1F6B;"></i>Username</label>
      <input type="text" id="login-username" placeholder="Enter your username" autocomplete="username"/>
    </div>
    <div class="form-group">
      <label><i class="fa fa-lock" style="margin-right:6px;color:#1B1F6B;"></i>Password</label>
      <input type="password" id="login-password" placeholder="Enter your password" autocomplete="current-password"/>
    </div>
    <button class="btn btn-primary btn-full" id="login-btn" onclick="doLogin()">
      <i class="fa fa-sign-in-alt"></i> Sign In to Awash Bank
    </button>
    <div style="margin-top:20px;padding:14px;background:#f0f2f8;border-radius:8px;font-size:12px;color:#6b7280;line-height:1.8;">
      <strong style="color:#1B1F6B;display:block;margin-bottom:4px;">Demo Accounts:</strong>
      admin / Admin@123 &nbsp;&bull;&nbsp; pm.sara / Pass@123<br/>
      qa.meron / Pass@123 &nbsp;&bull;&nbsp; dev.yonas / Pass@123<br/>
      devops.abel / Pass@123 &nbsp;&bull;&nbsp; sec.hana / Pass@123
    </div>
  </div>
</div>
<div id="app">
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="sidebar-logo">AB</div>
      <div><div class="sidebar-title">Awash Bank</div><div class="sidebar-subtitle">Issue Tracker</div></div>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-section">Overview</div>
      <div class="nav-item active" onclick="nav('dashboard')" id="nav-dashboard"><i class="fa fa-chart-pie"></i><span>Dashboard</span></div>
      <div class="nav-item" onclick="nav('myissues')" id="nav-myissues"><i class="fa fa-user-check"></i><span>My Issues</span><span class="nav-badge" id="my-count" style="display:none">0</span></div>
      <div class="nav-section">Tracking</div>
      <div class="nav-item" onclick="nav('issues')" id="nav-issues"><i class="fa fa-bug"></i><span>All Issues</span><span class="nav-badge" id="open-count">0</span></div>
      <div class="nav-item" onclick="nav('kanban')" id="nav-kanban"><i class="fa fa-columns"></i><span>Kanban Board</span></div>
      <div class="nav-item" onclick="nav('backlog')" id="nav-backlog"><i class="fa fa-list-ul"></i><span>Backlog</span></div>
      <div class="nav-section">Planning</div>
      <div class="nav-item" onclick="nav('projects')" id="nav-projects"><i class="fa fa-folder-open"></i><span>Projects</span></div>
      <div class="nav-item" onclick="nav('sprints')" id="nav-sprints"><i class="fa fa-running"></i><span>Sprints</span></div>
      <div class="nav-item" onclick="nav('roadmap')" id="nav-roadmap"><i class="fa fa-road"></i><span>Roadmap</span></div>
      <div class="nav-section">Analytics</div>
      <div class="nav-item" onclick="nav('reports')" id="nav-reports"><i class="fa fa-chart-bar"></i><span>Reports</span></div>
      <div class="nav-item" onclick="nav('sla')" id="nav-sla"><i class="fa fa-clock"></i><span>SLA Monitor</span></div>
      <div class="nav-item" onclick="nav('audit')" id="nav-audit"><i class="fa fa-history"></i><span>Audit Log</span></div>
      <div class="nav-section">Admin</div>
      <div class="nav-item" onclick="nav('team')" id="nav-team"><i class="fa fa-users"></i><span>Team</span></div>
      <div class="nav-item" onclick="nav('notifications')" id="nav-notifications"><i class="fa fa-bell"></i><span>Notifications</span><span class="nav-badge" id="notif-nav-count" style="display:none">0</span></div>
      <div class="nav-item" onclick="nav('settings')" id="nav-settings"><i class="fa fa-cog"></i><span>Settings</span></div>
    </nav>
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar" id="sidebar-avatar" style="background:#1B1F6B;">AB</div>
        <div style="flex:1;min-width:0;"><div class="user-name" id="sidebar-name">User</div><div class="user-role-txt" id="sidebar-role">Role</div></div>
        <button class="logout-btn" onclick="doLogout()" title="Logout"><i class="fa fa-sign-out-alt"></i></button>
      </div>
    </div>
  </div>
  <div class="main">
    <div class="topbar">
      <div class="topbar-title" id="topbar-title">Dashboard</div>
      <div class="search-box"><i class="fa fa-search" style="color:#6b7280;font-size:13px;"></i><input type="text" placeholder="Search issues, projects..." id="global-search" oninput="globalSearch(this.value)"/></div>
      <button class="btn btn-orange btn-sm" onclick="openCreateIssue()"><i class="fa fa-plus"></i> New Issue</button>
      <button class="notif-btn" onclick="nav('notifications')" id="notif-topbar-btn"><i class="fa fa-bell"></i><span class="notif-badge" id="notif-badge" style="display:none">0</span></button>
      <div style="width:1px;height:30px;background:var(--border);"></div>
      <div style="display:flex;align-items:center;gap:8px;cursor:pointer;" onclick="nav('settings')">
        <div class="user-avatar" id="topbar-avatar" style="background:#1B1F6B;width:32px;height:32px;font-size:11px;">AB</div>
        <span style="font-size:13px;font-weight:600;" id="topbar-name">User</span>
      </div>
    </div>
    <div class="content" id="main-content">
      <div id="page-dashboard" class="page active"></div>
      <div id="page-issues" class="page"></div>
      <div id="page-myissues" class="page"></div>
      <div id="page-kanban" class="page"></div>
      <div id="page-backlog" class="page"></div>
      <div id="page-projects" class="page"></div>
      <div id="page-sprints" class="page"></div>
      <div id="page-roadmap" class="page"></div>
      <div id="page-reports" class="page"></div>
      <div id="page-sla" class="page"></div>
      <div id="page-audit" class="page"></div>
      <div id="page-team" class="page"></div>
      <div id="page-notifications" class="page"></div>
      <div id="page-settings" class="page"></div>
    </div>
  </div>
</div>
<!-- Modals -->
<div id="modal-create-issue" class="modal-overlay" style="display:none;" onclick="if(event.target===this)closeModal('create-issue')">
  <div class="modal">
    <div class="modal-header"><span class="modal-title"><i class="fa fa-plus-circle" style="color:#F5A623;margin-right:8px;"></i>Create Issue</span><button class="modal-close" onclick="closeModal('create-issue')">&times;</button></div>
    <div class="modal-body">
      <div class="form-group"><label>Title *</label><input type="text" id="ci-title" placeholder="Issue summary..."/></div>
      <div class="form-row">
        <div class="form-group"><label>Type</label><select id="ci-type"><option value="task">Task</option><option value="bug">Bug</option><option value="feature">Feature</option><option value="story">Story</option><option value="epic">Epic</option><option value="improvement">Improvement</option><option value="security">Security</option><option value="incident">Incident</option></select></div>
        <div class="form-group"><label>Priority</label><select id="ci-priority"><option value="medium">Medium</option><option value="critical">Critical</option><option value="high">High</option><option value="low">Low</option></select></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Project *</label><select id="ci-project"><option value="">Select project...</option></select></div>
        <div class="form-group"><label>Status</label><select id="ci-status"><option value="backlog">Backlog</option><option value="todo">To Do</option><option value="in_progress">In Progress</option></select></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Assignee</label><select id="ci-assignee"><option value="">Unassigned</option></select></div>
        <div class="form-group"><label>Sprint</label><select id="ci-sprint"><option value="">No Sprint</option></select></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Story Points</label><input type="number" id="ci-points" placeholder="0" min="0" max="100"/></div>
        <div class="form-group"><label>Due Date</label><input type="date" id="ci-due"/></div>
      </div>
      <div class="form-group"><label>Description</label><textarea id="ci-desc" rows="4" placeholder="Describe the issue in detail..."></textarea></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('create-issue')">Cancel</button>
      <button class="btn btn-primary" onclick="submitCreateIssue()"><i class="fa fa-save"></i> Create Issue</button>
    </div>
  </div>
</div>
<div id="modal-issue-detail" class="modal-overlay" style="display:none;" onclick="if(event.target===this)closeModal('issue-detail')">
  <div class="modal modal-lg">
    <div class="modal-header">
      <span class="modal-title" id="detail-key-title">Issue Detail</span>
      <div style="display:flex;gap:8px;">
        <button class="btn btn-sm btn-outline" onclick="editCurrentIssue()"><i class="fa fa-edit"></i> Edit</button>
        <button class="modal-close" onclick="closeModal('issue-detail')">&times;</button>
      </div>
    </div>
    <div class="modal-body" id="issue-detail-body">
      <div style="text-align:center;padding:40px;"><div class="spinner"></div></div>
    </div>
  </div>
</div>
<div id="modal-create-project" class="modal-overlay" style="display:none;" onclick="if(event.target===this)closeModal('create-project')">
  <div class="modal">
    <div class="modal-header"><span class="modal-title"><i class="fa fa-folder-plus" style="color:#F5A623;margin-right:8px;"></i>Create Project</span><button class="modal-close" onclick="closeModal('create-project')">&times;</button></div>
    <div class="modal-body">
      <div class="form-row">
        <div class="form-group"><label>Project Key *</label><input type="text" id="cp-key" placeholder="e.g. CBS" maxlength="6" style="text-transform:uppercase;"/></div>
        <div class="form-group"><label>Project Name *</label><input type="text" id="cp-name" placeholder="Project name..."/></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Department</label><select id="cp-dept"><option value="">Select...</option><option>Project Management</option><option>Business Analysis</option><option>Quality Assurance</option><option>DevOps</option><option>Development</option><option>Security</option><option>Infrastructure</option><option>Core Banking</option><option>Digital Banking</option><option>Compliance</option></select></div>
        <div class="form-group"><label>Color</label><input type="color" id="cp-color" value="#1B1F6B" style="height:42px;padding:4px;"/></div>
      </div>
      <div class="form-group"><label>Description</label><textarea id="cp-desc" rows="3" placeholder="Project description..."></textarea></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('create-project')">Cancel</button>
      <button class="btn btn-primary" onclick="submitCreateProject()"><i class="fa fa-save"></i> Create Project</button>
    </div>
  </div>
</div>
<div id="modal-create-sprint" class="modal-overlay" style="display:none;" onclick="if(event.target===this)closeModal('create-sprint')">
  <div class="modal">
    <div class="modal-header"><span class="modal-title"><i class="fa fa-running" style="color:#F5A623;margin-right:8px;"></i>Create Sprint</span><button class="modal-close" onclick="closeModal('create-sprint')">&times;</button></div>
    <div class="modal-body">
      <div class="form-group"><label>Sprint Name *</label><input type="text" id="cs-name" placeholder="Sprint 1 - Foundation"/></div>
      <div class="form-group"><label>Project *</label><select id="cs-project"><option value="">Select project...</option></select></div>
      <div class="form-group"><label>Sprint Goal</label><textarea id="cs-goal" rows="2" placeholder="What is the goal of this sprint?"></textarea></div>
      <div class="form-row">
        <div class="form-group"><label>Start Date</label><input type="date" id="cs-start"/></div>
        <div class="form-group"><label>End Date</label><input type="date" id="cs-end"/></div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('create-sprint')">Cancel</button>
      <button class="btn btn-primary" onclick="submitCreateSprint()"><i class="fa fa-save"></i> Create Sprint</button>
    </div>
  </div>
</div>
<div id="modal-create-user" class="modal-overlay" style="display:none;" onclick="if(event.target===this)closeModal('create-user')">
  <div class="modal">
    <div class="modal-header"><span class="modal-title"><i class="fa fa-user-plus" style="color:#F5A623;margin-right:8px;"></i>Add Team Member</span><button class="modal-close" onclick="closeModal('create-user')">&times;</button></div>
    <div class="modal-body">
      <div class="form-row">
        <div class="form-group"><label>Employee ID</label><input type="text" id="cu-empid" placeholder="AWB-XXX"/></div>
        <div class="form-group"><label>Username *</label><input type="text" id="cu-username" placeholder="username"/></div>
      </div>
      <div class="form-group"><label>Full Name *</label><input type="text" id="cu-fullname" placeholder="Full name"/></div>
      <div class="form-group"><label>Email *</label><input type="email" id="cu-email" placeholder="email@awashbank.com"/></div>
      <div class="form-row">
        <div class="form-group"><label>Password *</label><input type="password" id="cu-password" placeholder="Min 6 characters"/></div>
        <div class="form-group"><label>Role</label><select id="cu-role"><option value="viewer">Viewer</option><option value="developer">Developer</option><option value="qa_engineer">QA Engineer</option><option value="business_analyst">Business Analyst</option><option value="devops_engineer">DevOps Engineer</option><option value="security_engineer">Security Engineer</option><option value="project_manager">Project Manager</option><option value="admin">Admin</option></select></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Department</label><select id="cu-dept"><option value="">Select...</option><option>Project Management</option><option>Business Analysis</option><option>Quality Assurance</option><option>DevOps</option><option>Development</option><option>Security</option><option>Infrastructure</option><option>Core Banking</option><option>Digital Banking</option><option>Compliance</option></select></div>
        <div class="form-group"><label>Branch</label><input type="text" id="cu-branch" placeholder="Head Office" value="Head Office"/></div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('create-user')">Cancel</button>
      <button class="btn btn-primary" onclick="submitCreateUser()"><i class="fa fa-save"></i> Add Member</button>
    </div>
  </div>
</div>
<script src="app.js"></script>
</body>
</html>"""
write("index.html", INDEX)

# ── app.js PART 1: Core + API + Auth ─────────────────────────────────────────
JS1 = """
'use strict';
const API = 'http://localhost:8000';
let currentUser = null, currentView = 'dashboard', charts = {}, allProjects = [], allUsers = [], allSprints = [], currentIssueId = null, currentPage = 1, searchTimer = null;

// ── API Helper ────────────────────────────────────────────────────────────────
async function api(method, path, body = null) {
  const token = localStorage.getItem('awash_token');
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  if (body) opts.body = JSON.stringify(body);
  try {
    const r = await fetch(API + path, opts);
    if (r.status === 401) { doLogout(); return null; }
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Request failed');
    return data;
  } catch (e) { throw e; }
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function toast(msg, type = 'success') {
  const icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
  const colors = { success: '#16a34a', error: '#dc2626', warning: '#F5A623', info: '#1B1F6B' };
  const el = document.createElement('div');
  el.className = 'toast toast-' + type;
  el.innerHTML = '<i class="fa ' + icons[type] + '" style="color:' + colors[type] + ';font-size:18px;"></i><span class="toast-msg">' + msg + '</span>';
  document.getElementById('toasts').appendChild(el);
  setTimeout(() => { el.style.animation = 'slideIn .3s ease reverse'; setTimeout(() => el.remove(), 300); }, 3000);
}

// ── Auth ──────────────────────────────────────────────────────────────────────
async function doLogin() {
  const u = document.getElementById('login-username').value.trim();
  const p = document.getElementById('login-password').value;
  if (!u || !p) { showLoginError('Please enter username and password'); return; }
  const btn = document.getElementById('login-btn');
  btn.disabled = true; btn.innerHTML = '<div class="spinner"></div> Signing in...';
  try {
    const fd = new FormData();
    fd.append('username', u); fd.append('password', p);
    const r = await fetch(API + '/api/auth/login', { method: 'POST', body: fd });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Login failed');
    localStorage.setItem('awash_token', data.access_token);
    localStorage.setItem('awash_user', JSON.stringify(data.user));
    currentUser = data.user;
    initApp();
  } catch (e) {
    showLoginError(e.message);
    btn.disabled = false; btn.innerHTML = '<i class="fa fa-sign-in-alt"></i> Sign In to Awash Bank';
  }
}

function showLoginError(msg) {
  const el = document.getElementById('login-error');
  el.textContent = msg; el.style.display = 'block';
}

function doLogout() {
  localStorage.removeItem('awash_token'); localStorage.removeItem('awash_user');
  currentUser = null;
  document.getElementById('app').style.display = 'none';
  document.getElementById('login-page').style.display = 'flex';
  document.getElementById('login-error').style.display = 'none';
  document.getElementById('login-username').value = '';
  document.getElementById('login-password').value = '';
}

document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('awash_token');
  const user = localStorage.getItem('awash_user');
  if (token && user) { currentUser = JSON.parse(user); initApp(); }
  document.getElementById('login-password').addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });
  document.getElementById('login-username').addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });
});

function initApp() {
  document.getElementById('login-page').style.display = 'none';
  document.getElementById('app').style.display = 'flex';
  updateUserUI();
  loadNotifCount();
  loadOpenCount();
  loadDropdowns();
  nav('dashboard');
  setInterval(loadNotifCount, 30000);
}

function updateUserUI() {
  if (!currentUser) return;
  const initials = currentUser.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  const color = currentUser.avatar_color || '#1B1F6B';
  document.getElementById('sidebar-avatar').textContent = initials;
  document.getElementById('sidebar-avatar').style.background = color;
  document.getElementById('sidebar-name').textContent = currentUser.full_name;
  document.getElementById('sidebar-role').textContent = currentUser.role.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
  document.getElementById('topbar-avatar').textContent = initials;
  document.getElementById('topbar-avatar').style.background = color;
  document.getElementById('topbar-name').textContent = currentUser.full_name.split(' ')[0];
}

async function loadNotifCount() {
  try {
    const data = await api('GET', '/api/notifications/?unread_only=true');
    if (!data) return;
    const count = data.length;
    const badge = document.getElementById('notif-badge');
    const navBadge = document.getElementById('notif-nav-count');
    if (count > 0) {
      badge.textContent = count; badge.style.display = 'flex';
      navBadge.textContent = count; navBadge.style.display = 'inline';
    } else { badge.style.display = 'none'; navBadge.style.display = 'none'; }
  } catch (e) {}
}

async function loadOpenCount() {
  try {
    const data = await api('GET', '/api/issues/?status=todo&page_size=1');
    if (data) document.getElementById('open-count').textContent = data.length || '0';
  } catch (e) {}
}

async function loadDropdowns() {
  try {
    allProjects = await api('GET', '/api/projects/') || [];
    allUsers = await api('GET', '/api/users/') || [];
    allSprints = await api('GET', '/api/sprints/') || [];
    populateSelect('ci-project', allProjects, 'id', 'name', 'Select project...');
    populateSelect('ci-assignee', allUsers, 'id', 'full_name', 'Unassigned');
    populateSelect('ci-sprint', allSprints, 'id', 'name', 'No Sprint');
    populateSelect('cs-project', allProjects, 'id', 'name', 'Select project...');
  } catch (e) {}
}

function populateSelect(id, items, valKey, labelKey, placeholder) {
  const sel = document.getElementById(id);
  if (!sel) return;
  sel.innerHTML = '<option value="">' + placeholder + '</option>';
  items.forEach(item => {
    const opt = document.createElement('option');
    opt.value = item[valKey]; opt.textContent = item[labelKey];
    sel.appendChild(opt);
  });
}

// ── Navigation ────────────────────────────────────────────────────────────────
const PAGE_TITLES = { dashboard: 'Dashboard', issues: 'All Issues', myissues: 'My Issues', kanban: 'Kanban Board', backlog: 'Backlog', projects: 'Projects', sprints: 'Sprints', roadmap: 'Roadmap', reports: 'Reports', sla: 'SLA Monitor', audit: 'Audit Log', team: 'Team', notifications: 'Notifications', settings: 'Settings' };

function nav(view) {
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  const navEl = document.getElementById('nav-' + view);
  if (navEl) navEl.classList.add('active');
  document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
  const page = document.getElementById('page-' + view);
  if (page) page.classList.add('active');
  document.getElementById('topbar-title').textContent = PAGE_TITLES[view] || view;
  currentView = view;
  const loaders = { dashboard: loadDashboard, issues: loadIssues, myissues: loadMyIssues, kanban: loadKanban, backlog: loadBacklog, projects: loadProjects, sprints: loadSprints, roadmap: loadRoadmap, reports: loadReports, sla: loadSLA, audit: loadAudit, team: loadTeam, notifications: loadNotifications, settings: loadSettings };
  if (loaders[view]) loaders[view]();
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function initials(name) { return (name || 'U').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase(); }
function fmtDate(d) { if (!d) return '—'; const dt = new Date(d); return dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }); }
function fmtDateTime(d) { if (!d) return '—'; const dt = new Date(d); return dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }); }
function timeAgo(d) { if (!d) return ''; const s = Math.floor((Date.now() - new Date(d)) / 1000); if (s < 60) return 'just now'; if (s < 3600) return Math.floor(s/60) + 'm ago'; if (s < 86400) return Math.floor(s/3600) + 'h ago'; return Math.floor(s/86400) + 'd ago'; }
function statusBadge(s) { return '<span class="badge s-' + s + '">' + s.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase()) + '</span>'; }
function priorityBadge(p) { const icons = { critical: '&#9888;', high: '&#8679;', medium: '&#8680;', low: '&#8681;' }; return '<span class="badge p-' + p + '">' + (icons[p] || '') + ' ' + p.charAt(0).toUpperCase() + p.slice(1) + '</span>'; }
function typeIcon(t) { const icons = { bug: 'fa-bug', feature: 'fa-star', task: 'fa-check-square', epic: 'fa-bolt', story: 'fa-bookmark', improvement: 'fa-arrow-up', security: 'fa-shield-alt', incident: 'fa-fire' }; return '<span class="type-icon t-' + t + '"><i class="fa ' + (icons[t] || 'fa-circle') + '"></i></span>'; }
function roleBadge(r) { return '<span class="badge r-' + r + '">' + r.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase()) + '</span>'; }
function avatarEl(user, size) { if (!user) return '<span class="avatar" style="background:#ccc;">?</span>'; const sz = size || 28; return '<span class="avatar" style="background:' + (user.avatar_color || '#1B1F6B') + ';width:' + sz + 'px;height:' + sz + 'px;font-size:' + Math.floor(sz * 0.38) + 'px;" title="' + user.full_name + '">' + initials(user.full_name) + '</span>'; }
function priorityColor(p) { return { critical: '#dc2626', high: '#c2410c', medium: '#1d4ed8', low: '#64748b' }[p] || '#6b7280'; }
function openModal(id) { document.getElementById('modal-' + id).style.display = 'flex'; }
function closeModal(id) { document.getElementById('modal-' + id).style.display = 'none'; }
function globalSearch(val) { clearTimeout(searchTimer); searchTimer = setTimeout(() => { if (val.length > 1) { nav('issues'); setTimeout(() => { const s = document.getElementById('filter-search'); if (s) { s.value = val; filterIssues(); } }, 200); } }, 400); }
"""
write("app.js", JS1)

# ── app.js (Part 1: Core & API) ──────────────────────────────────────────────
JS_PART1 = """
const API_BASE = 'http://localhost:8000';
let currentUser = null;
let currentView = 'dashboard';
let allIssues = [];
let allProjects = [];
let allUsers = [];
let allSprints = [];
let currentIssue = null;
let charts = {};

// ── API Helper ────────────────────────────────────────────────────────────────
async function api(method, path, body = null) {
  const token = localStorage.getItem('awash_token');
  const headers = {'Content-Type': 'application/json'};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const opts = {method, headers};
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(API_BASE + path, opts);
    if (res.status === 401) {
      localStorage.clear();
      location.reload();
      return;
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({detail: 'Request failed'}));
      throw new Error(err.detail || 'Request failed');
    }
    return await res.json();
  } catch (e) {
    toast(e.message, 'error');
    throw e;
  }
}

// ── Toast Notifications ───────────────────────────────────────────────────────
function toast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.innerHTML = `<i class="fa fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i><span class="toast-msg">${msg}</span>`;
  document.getElementById('toasts').appendChild(t);
  setTimeout(() => {
    t.style.animation = 'fadeOut .3s ease forwards';
    setTimeout(() => t.remove(), 300);
  }, 3000);
}

// ── Auth ──────────────────────────────────────────────────────────────────────
async function doLogin() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const btn = document.getElementById('login-btn');
  const err = document.getElementById('login-error');
  err.style.display = 'none';
  if (!username || !password) {
    err.textContent = 'Please enter username and password';
    err.style.display = 'block';
    return;
  }
  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Signing in...';
  try {
    const form = new FormData();
    form.append('username', username);
    form.append('password', password);
    const res = await fetch(API_BASE + '/api/auth/login', {method: 'POST', body: form});
    if (!res.ok) throw new Error('Invalid credentials');
    const data = await res.json();
    localStorage.setItem('awash_token', data.access_token);
    localStorage.setItem('awash_user', JSON.stringify(data.user));
    currentUser = data.user;
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('app').style.display = 'flex';
    initApp();
  } catch (e) {
    err.textContent = e.message;
    err.style.display = 'block';
    btn.disabled = false;
    btn.innerHTML = '<i class="fa fa-sign-in-alt"></i> Sign In to Awash Bank';
  }
}

function doLogout() {
  if (confirm('Are you sure you want to logout?')) {
    localStorage.clear();
    location.reload();
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
async function initApp() {
  updateUserUI();
  await Promise.all([loadProjects(), loadUsers(), loadSprints()]);
  nav('dashboard');
  loadNotifications();
  setInterval(loadNotifications, 60000);
  document.getElementById('login-password').addEventListener('keypress', e => {
    if (e.key === 'Enter') doLogin();
  });
}

function updateUserUI() {
  const initials = currentUser.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  const color = currentUser.avatar_color || '#1B1F6B';
  ['sidebar', 'topbar'].forEach(p => {
    document.getElementById(`${p}-avatar`).textContent = initials;
    document.getElementById(`${p}-avatar`).style.background = color;
    document.getElementById(`${p}-name`).textContent = currentUser.full_name;
  });
  document.getElementById('sidebar-role').textContent = currentUser.role.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
}

// ── Navigation ────────────────────────────────────────────────────────────────
function nav(page) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const navItem = document.getElementById(`nav-${page}`);
  const pageEl = document.getElementById(`page-${page}`);
  if (navItem) navItem.classList.add('active');
  if (pageEl) pageEl.classList.add('active');
  currentView = page;
  const titles = {
    dashboard: 'Dashboard', issues: 'All Issues', myissues: 'My Issues',
    kanban: 'Kanban Board', backlog: 'Backlog', projects: 'Projects',
    sprints: 'Sprints', roadmap: 'Roadmap', reports: 'Reports',
    sla: 'SLA Monitor', audit: 'Audit Log', team: 'Team',
    notifications: 'Notifications', settings: 'Settings'
  };
  document.getElementById('topbar-title').textContent = titles[page] || 'Awash Bank';
  loadPage(page);
}

async function loadPage(page) {
  const el = document.getElementById(`page-${page}`);
  if (!el) return;
  el.innerHTML = '<div style="text-align:center;padding:60px;"><div class="spinner"></div></div>';
  try {
    switch (page) {
      case 'dashboard': await renderDashboard(el); break;
      case 'issues': await renderIssues(el); break;
      case 'myissues': await renderMyIssues(el); break;
      case 'kanban': await renderKanban(el); break;
      case 'backlog': await renderBacklog(el); break;
      case 'projects': await renderProjects(el); break;
      case 'sprints': await renderSprints(el); break;
      case 'roadmap': await renderRoadmap(el); break;
      case 'reports': await renderReports(el); break;
      case 'sla': await renderSLA(el); break;
      case 'audit': await renderAudit(el); break;
      case 'team': await renderTeam(el); break;
      case 'notifications': await renderNotifications(el); break;
      case 'settings': await renderSettings(el); break;
      default: el.innerHTML = '<div class="empty-state"><i class="fa fa-construction"></i><h3>Coming Soon</h3><p>This feature is under development</p></div>';
    }
  } catch (e) {
    el.innerHTML = `<div class="empty-state"><i class="fa fa-exclamation-triangle"></i><h3>Error Loading Page</h3><p>${e.message}</p></div>`;
  }
}

// ── Data Loaders ──────────────────────────────────────────────────────────────
async function loadProjects() {
  allProjects = await api('GET', '/api/projects/');
  const sel = document.getElementById('ci-project');
  const sel2 = document.getElementById('cs-project');
  if (sel) {
    sel.innerHTML = '<option value="">Select project...</option>' + allProjects.map(p => `<option value="${p.id}">${p.key} - ${p.name}</option>`).join('');
    if (sel2) sel2.innerHTML = sel.innerHTML;
  }
}

async function loadUsers() {
  allUsers = await api('GET', '/api/users/');
  const sel = document.getElementById('ci-assignee');
  if (sel) sel.innerHTML = '<option value="">Unassigned</option>' + allUsers.filter(u => u.is_active).map(u => `<option value="${u.id}">${u.full_name} (${u.role.replace(/_/g, ' ')})</option>`).join('');
}

async function loadSprints() {
  allSprints = await api('GET', '/api/sprints/');
  const sel = document.getElementById('ci-sprint');
  if (sel) sel.innerHTML = '<option value="">No Sprint</option>' + allSprints.filter(s => s.status !== 'completed').map(s => `<option value="${s.id}">${s.name}</option>`).join('');
}

async function loadNotifications() {
  try {
    const notifs = await api('GET', '/api/notifications/?unread_only=true');
    const count = notifs.length;
    ['notif-badge', 'notif-nav-count'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.textContent = count;
        el.style.display = count > 0 ? 'flex' : 'none';
      }
    });
  } catch (e) {}
}

// ── Modals ────────────────────────────────────────────────────────────────────
function openModal(id) {
  document.getElementById(`modal-${id}`).style.display = 'flex';
}

function closeModal(id) {
  document.getElementById(`modal-${id}`).style.display = 'none';
}

function openCreateIssue() {
  openModal('create-issue');
}

async function submitCreateIssue() {
  const data = {
    title: document.getElementById('ci-title').value.trim(),
    description: document.getElementById('ci-desc').value.trim(),
    issue_type: document.getElementById('ci-type').value,
    status: document.getElementById('ci-status').value,
    priority: document.getElementById('ci-priority').value,
    project_id: parseInt(document.getElementById('ci-project').value),
    assignee_id: document.getElementById('ci-assignee').value ? parseInt(document.getElementById('ci-assignee').value) : null,
    sprint_id: document.getElementById('ci-sprint').value ? parseInt(document.getElementById('ci-sprint').value) : null,
    story_points: parseInt(document.getElementById('ci-points').value) || 0,
    due_date: document.getElementById('ci-due').value || null,
  };
  if (!data.title || !data.project_id) return toast('Title and Project are required', 'error');
  try {
    const issue = await api('POST', '/api/issues/', data);
    toast(`Issue ${issue.key} created successfully!`, 'success');
    closeModal('create-issue');
    document.getElementById('ci-title').value = '';
    document.getElementById('ci-desc').value = '';
    if (currentView === 'issues' || currentView === 'myissues' || currentView === 'backlog') loadPage(currentView);
  } catch (e) {}
}

async function openCreateProject() {
  if (!['admin', 'project_manager'].includes(currentUser.role)) return toast('Only admins and PMs can create projects', 'error');
  openModal('create-project');
}

async function submitCreateProject() {
  const data = {
    key: document.getElementById('cp-key').value.trim().toUpperCase(),
    name: document.getElementById('cp-name').value.trim(),
    description: document.getElementById('cp-desc').value.trim(),
    department: document.getElementById('cp-dept').value,
    color: document.getElementById('cp-color').value,
  };
  if (!data.key || !data.name) return toast('Key and Name are required', 'error');
  try {
    await api('POST', '/api/projects/', data);
    toast(`Project ${data.key} created!`, 'success');
    closeModal('create-project');
    await loadProjects();
    if (currentView === 'projects') loadPage('projects');
  } catch (e) {}
}

async function openCreateSprint() {
  openModal('create-sprint');
}

async function submitCreateSprint() {
  const data = {
    name: document.getElementById('cs-name').value.trim(),
    goal: document.getElementById('cs-goal').value.trim(),
    project_id: parseInt(document.getElementById('cs-project').value),
    start_date: document.getElementById('cs-start').value || null,
    end_date: document.getElementById('cs-end').value || null,
  };
  if (!data.name || !data.project_id) return toast('Name and Project are required', 'error');
  try {
    await api('POST', '/api/sprints/', data);
    toast(`Sprint created!`, 'success');
    closeModal('create-sprint');
    await loadSprints();
    if (currentView === 'sprints') loadPage('sprints');
  } catch (e) {}
}

async function openCreateUser() {
  if (currentUser.role !== 'admin') return toast('Only admins can add users', 'error');
  openModal('create-user');
}

async function submitCreateUser() {
  const data = {
    employee_id: document.getElementById('cu-empid').value.trim() || null,
    username: document.getElementById('cu-username').value.trim(),
    full_name: document.getElementById('cu-fullname').value.trim(),
    email: document.getElementById('cu-email').value.trim(),
    password: document.getElementById('cu-password').value,
    role: document.getElementById('cu-role').value,
    department: document.getElementById('cu-dept').value || null,
    branch: document.getElementById('cu-branch').value.trim(),
  };
  if (!data.username || !data.full_name || !data.email || !data.password) return toast('All required fields must be filled', 'error');
  try {
    await api('POST', '/api/auth/register', data);
    toast(`User ${data.username} created!`, 'success');
    closeModal('create-user');
    await loadUsers();
    if (currentView === 'team') loadPage('team');
  } catch (e) {}
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function fmt(date) {
  if (!date) return '-';
  const d = new Date(date);
  return d.toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'});
}

function fmtTime(date) {
  if (!date) return '-';
  const d = new Date(date);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return fmt(date);
}

function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
}

function getStatusBadge(status) {
  const icons = {backlog: 'inbox', todo: 'list', in_progress: 'spinner', in_review: 'eye', testing: 'flask', done: 'check-circle', closed: 'lock', cancelled: 'times-circle'};
  return `<span class="badge s-${status}"><i class="fa fa-${icons[status] || 'circle'}"></i> ${status.replace(/_/g, ' ')}</span>`;
}

function getPriorityBadge(priority) {
  const icons = {critical: 'exclamation-triangle', high: 'arrow-up', medium: 'minus', low: 'arrow-down'};
  return `<span class="badge p-${priority}"><i class="fa fa-${icons[priority]}"></i> ${priority}</span>`;
}

function getTypeIcon(type) {
  const icons = {bug: 'bug', feature: 'star', task: 'check-square', epic: 'bolt', story: 'bookmark', improvement: 'arrow-up', security: 'shield-alt', incident: 'fire'};
  return `<span class="type-icon t-${type}" title="${type}"><i class="fa fa-${icons[type]}"></i></span>`;
}

function getRoleBadge(role) {
  return `<span class="badge r-${role}">${role.replace(/_/g, ' ')}</span>`;
}

function getAvatar(user, size = 28) {
  if (!user) return '';
  const initials = getInitials(user.full_name || user.username);
  const color = user.avatar_color || '#1B1F6B';
  return `<div class="avatar" style="width:${size}px;height:${size}px;background:${color};font-size:${Math.floor(size / 2.8)}px;" title="${user.full_name}">${initials}</div>`;
}

function globalSearch(q) {
  if (!q || q.length < 2) return;
  console.log('Search:', q);
}
"""
write("app.js", JS_PART1)

# ── app.js (Part 2: Page Renderers) ──────────────────────────────────────────
JS_PART2 = """
// ── Dashboard ─────────────────────────────────────────────────────────────────
async function renderDashboard(el) {
  const stats = await api('GET', '/api/dashboard/stats');
  el.innerHTML = `
    <div class="stats-grid">
      <div class="stat-card" style="border-left-color:#1B1F6B;"><div class="stat-icon" style="background:#e8eaf6;color:#1B1F6B;"><i class="fa fa-tasks"></i></div><div><div class="stat-value">${stats.total_issues}</div><div class="stat-label">Total Issues</div></div></div>
      <div class="stat-card" style="border-left-color:#1d4ed8;"><div class="stat-icon" style="background:#dbeafe;color:#1d4ed8;"><i class="fa fa-folder-open"></i></div><div><div class="stat-value">${stats.open_issues}</div><div class="stat-label">Open Issues</div></div></div>
      <div class="stat-card" style="border-left-color:#c2410c;"><div class="stat-icon" style="background:#fff7ed;color:#c2410c;"><i class="fa fa-spinner"></i></div><div><div class="stat-value">${stats.in_progress}</div><div class="stat-label">In Progress</div></div></div>
      <div class="stat-card" style="border-left-color:#15803d;"><div class="stat-icon" style="background:#dcfce7;color:#15803d;"><i class="fa fa-check-circle"></i></div><div><div class="stat-value">${stats.resolved_today}</div><div class="stat-label">Resolved Today</div></div></div>
      <div class="stat-card" style="border-left-color:#dc2626;"><div class="stat-icon" style="background:#fee2e2;color:#dc2626;"><i class="fa fa-exclamation-triangle"></i></div><div><div class="stat-value">${stats.overdue}</div><div class="stat-label">Overdue</div></div></div>
    </div>
    ${stats.sprint_progress ? `<div class="sprint-progress-card"><div class="card-title"><i class="fa fa-running" style="color:#F5A623;"></i> Active Sprint: ${stats.sprint_progress.name}</div><div class="progress-bar"><div class="progress-fill" style="width:${stats.sprint_progress.percent}%;"></div></div><div style="display:flex;justify-content:space-between;font-size:13px;margin-top:8px;"><span>${stats.sprint_progress.done} / ${stats.sprint_progress.total} issues completed</span><span style="font-weight:700;color:#1B1F6B;">${stats.sprint_progress.percent}%</span></div></div>` : ''}
    <div class="charts-grid">
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-pie"></i> Issues by Status</div><div class="chart-wrap"><canvas id="chart-status"></canvas></div></div>
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-bar"></i> Issues by Priority</div><div class="chart-wrap"><canvas id="chart-priority"></canvas></div></div>
      <div class="chart-card"><div class="chart-title"><i class="fa fa-chart-line"></i> Daily Trend</div><div class="chart-wrap"><canvas id="chart-daily"></canvas></div></div>
    </div>
    <div class="bottom-grid">
      <div class="card"><div class="card-header"><div class="card-title"><i class="fa fa-history"></i> Recent Activity</div></div><div id="activity-list"></div></div>
      <div class="card"><div class="card-header"><div class="card-title"><i class="fa fa-users"></i> Top Assignees</div></div><div id="assignee-list"></div></div>
    </div>
  `;
  renderCharts(stats);
  renderActivity(stats.recent_activity);
  renderAssignees(stats.by_assignee);
  document.getElementById('open-count').textContent = stats.open_issues;
}

function renderCharts(stats) {
  const statusLabels = Object.keys(stats.by_status).map(s => s.replace(/_/g, ' '));
  const statusData = Object.values(stats.by_status);
  const statusColors = ['#64748b', '#1d4ed8', '#c2410c', '#7c3aed', '#a16207', '#15803d', '#374151', '#dc2626'];
  if (charts.status) charts.status.destroy();
  charts.status = new Chart(document.getElementById('chart-status'), {
    type: 'doughnut',
    data: {labels: statusLabels, datasets: [{data: statusData, backgroundColor: statusColors}]},
    options: {responsive: true, maintainAspectRatio: false, plugins: {legend: {position: 'bottom'}}}
  });
  const priorityLabels = Object.keys(stats.by_priority).map(p => p.charAt(0).toUpperCase() + p.slice(1));
  const priorityData = Object.values(stats.by_priority);
  const priorityColors = ['#dc2626', '#c2410c', '#1d4ed8', '#64748b'];
  if (charts.priority) charts.priority.destroy();
  charts.priority = new Chart(document.getElementById('chart-priority'), {
    type: 'bar',
    data: {labels: priorityLabels, datasets: [{label: 'Issues', data: priorityData, backgroundColor: priorityColors}]},
    options: {responsive: true, maintainAspectRatio: false, plugins: {legend: {display: false}}}
  });
  if (stats.daily_trend && stats.daily_trend.length) {
    const dailyLabels = stats.daily_trend.map(d => d.date);
    const dailyData = stats.daily_trend.map(d => d.count);
    if (charts.daily) charts.daily.destroy();
    charts.daily = new Chart(document.getElementById('chart-daily'), {
      type: 'line',
      data: {labels: dailyLabels, datasets: [{label: 'Issues Created', data: dailyData, borderColor: '#1B1F6B', backgroundColor: 'rgba(27,31,107,0.1)', tension: 0.3, fill: true}]},
      options: {responsive: true, maintainAspectRatio: false, plugins: {legend: {display: false}}}
    });
  }
}

function renderActivity(activities) {
  const el = document.getElementById('activity-list');
  if (!activities || !activities.length) {
    el.innerHTML = '<div class="empty-state"><i class="fa fa-inbox"></i><p>No recent activity</p></div>';
    return;
  }
  el.innerHTML = activities.slice(0, 10).map(a => `
    <div class="activity-item">
      ${getAvatar(a.user, 30)}
      <div style="flex:1;">
        <div class="activity-text"><strong>${a.user.full_name}</strong> ${a.action.replace(/_/g, ' ')} ${a.field_changed ? `<em>${a.field_changed}</em>` : ''}</div>
        <div class="activity-time">${fmtTime(a.created_at)}</div>
      </div>
    </div>
  `).join('');
}

function renderAssignees(assignees) {
  const el = document.getElementById('assignee-list');
  if (!assignees || !assignees.length) {
    el.innerHTML = '<div class="empty-state"><i class="fa fa-users"></i><p>No data</p></div>';
    return;
  }
  el.innerHTML = assignees.slice(0, 8).map(a => `
    <div class="metric-row">
      <div style="display:flex;align-items:center;gap:10px;">
        <div class="avatar" style="background:${a.color};width:32px;height:32px;font-size:12px;">${getInitials(a.name)}</div>
        <span class="metric-label">${a.name}</span>
      </div>
      <span class="metric-value">${a.count}</span>
    </div>
  `).join('');
}

// ── Issues List ───────────────────────────────────────────────────────────────
async function renderIssues(el, filters = {}) {
  const params = new URLSearchParams(filters);
  const issues = await api('GET', `/api/issues/?${params}`);
  allIssues = issues;
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">All Issues</div><div class="page-subtitle">${issues.length} issues found</div></div>
      <button class="btn btn-orange" onclick="openCreateIssue()"><i class="fa fa-plus"></i> New Issue</button>
    </div>
    <div class="filter-bar">
      <select onchange="filterIssues()" id="filter-project"><option value="">All Projects</option>${allProjects.map(p => `<option value="${p.id}">${p.key}</option>`).join('')}</select>
      <select onchange="filterIssues()" id="filter-status"><option value="">All Status</option><option value="backlog">Backlog</option><option value="todo">To Do</option><option value="in_progress">In Progress</option><option value="in_review">In Review</option><option value="testing">Testing</option><option value="done">Done</option></select>
      <select onchange="filterIssues()" id="filter-priority"><option value="">All Priority</option><option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select>
      <select onchange="filterIssues()" id="filter-type"><option value="">All Types</option><option value="bug">Bug</option><option value="feature">Feature</option><option value="task">Task</option><option value="story">Story</option><option value="epic">Epic</option></select>
      <div class="filter-spacer"></div>
      <input type="text" placeholder="Search..." oninput="filterIssues()" id="filter-search" style="width:200px;"/>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Key</th><th>Title</th><th>Type</th><th>Status</th><th>Priority</th><th>Assignee</th><th>Sprint</th><th>Created</th></tr></thead>
        <tbody id="issues-tbody"></tbody>
      </table>
    </div>
  `;
  renderIssuesTable(issues);
}

function renderIssuesTable(issues) {
  const tbody = document.getElementById('issues-tbody');
  if (!issues || !issues.length) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:40px;color:#6b7280;">No issues found</td></tr>';
    return;
  }
  tbody.innerHTML = issues.map(i => `
    <tr onclick="openIssueDetail(${i.id})">
      <td><strong style="color:#1B1F6B;">${i.key}</strong></td>
      <td>${i.title}</td>
      <td>${getTypeIcon(i.issue_type)}</td>
      <td>${getStatusBadge(i.status)}</td>
      <td>${getPriorityBadge(i.priority)}</td>
      <td>${i.assignee ? getAvatar(i.assignee) + ' ' + i.assignee.full_name : '<span style="color:#6b7280;">Unassigned</span>'}</td>
      <td>${i.sprint ? i.sprint.name : '-'}</td>
      <td>${fmt(i.created_at)}</td>
    </tr>
  `).join('');
}

function filterIssues() {
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
}

async function renderMyIssues(el) {
  const issues = await api('GET', `/api/issues/?assignee_id=${currentUser.id}`);
  allIssues = issues;
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">My Issues</div><div class="page-subtitle">${issues.length} issues assigned to you</div></div>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Key</th><th>Title</th><th>Type</th><th>Status</th><th>Priority</th><th>Project</th><th>Due Date</th></tr></thead>
        <tbody>${issues.map(i => `<tr onclick="openIssueDetail(${i.id})"><td><strong style="color:#1B1F6B;">${i.key}</strong></td><td>${i.title}</td><td>${getTypeIcon(i.issue_type)}</td><td>${getStatusBadge(i.status)}</td><td>${getPriorityBadge(i.priority)}</td><td>${i.project_key || '-'}</td><td>${fmt(i.due_date)}</td></tr>`).join('')}</tbody>
      </table>
    </div>
  `;
  document.getElementById('my-count').textContent = issues.filter(i => !['done', 'closed', 'cancelled'].includes(i.status)).length;
  document.getElementById('my-count').style.display = 'flex';
}

async function renderBacklog(el) {
  const issues = await api('GET', '/api/issues/?status=backlog');
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Backlog</div><div class="page-subtitle">${issues.length} issues in backlog</div></div>
      <button class="btn btn-orange" onclick="openCreateIssue()"><i class="fa fa-plus"></i> New Issue</button>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Key</th><th>Title</th><th>Type</th><th>Priority</th><th>Assignee</th><th>Story Points</th><th>Created</th></tr></thead>
        <tbody>${issues.map(i => `<tr onclick="openIssueDetail(${i.id})"><td><strong style="color:#1B1F6B;">${i.key}</strong></td><td>${i.title}</td><td>${getTypeIcon(i.issue_type)}</td><td>${getPriorityBadge(i.priority)}</td><td>${i.assignee ? getAvatar(i.assignee) + ' ' + i.assignee.full_name : '<span style="color:#6b7280;">Unassigned</span>'}</td><td>${i.story_points || '-'}</td><td>${fmt(i.created_at)}</td></tr>`).join('')}</tbody>
      </table>
    </div>
  `;
}

// ── Kanban Board ──────────────────────────────────────────────────────────────
async function renderKanban(el) {
  const sprints = allSprints.filter(s => s.status === 'active');
  if (!sprints.length) {
    el.innerHTML = '<div class="empty-state"><i class="fa fa-running"></i><h3>No Active Sprint</h3><p>Start a sprint to use the Kanban board</p><button class="btn btn-primary" onclick="nav(\'sprints\')">Go to Sprints</button></div>';
    return;
  }
  const sprint = sprints[0];
  const board = await api('GET', `/api/sprints/${sprint.id}/board`);
  const cols = ['backlog', 'todo', 'in_progress', 'in_review', 'testing', 'done'];
  const colNames = {backlog: 'Backlog', todo: 'To Do', in_progress: 'In Progress', in_review: 'In Review', testing: 'Testing', done: 'Done'};
  const colColors = {backlog: '#64748b', todo: '#1d4ed8', in_progress: '#c2410c', in_review: '#7c3aed', testing: '#a16207', done: '#15803d'};
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Kanban Board</div><div class="page-subtitle">${sprint.name}</div></div>
      <button class="btn btn-outline btn-sm" onclick="nav('sprints')"><i class="fa fa-cog"></i> Manage Sprints</button>
    </div>
    <div class="kanban-board">
      ${cols.map(col => `
        <div class="kanban-col">
          <div class="kanban-col-header" style="background:${colColors[col]};color:#fff;">
            <span>${colNames[col]}</span>
            <span class="kanban-col-count">${board[col]?.length || 0}</span>
          </div>
          <div class="kanban-col-body">
            ${(board[col] || []).map(i => `
              <div class="kanban-card" style="border-left-color:${colColors[col]};" onclick="openIssueDetail(${i.id})">
                <div class="kanban-card-key">${i.key}</div>
                <div class="kanban-card-title">${i.title}</div>
                <div class="kanban-card-footer">
                  <div style="display:flex;gap:4px;align-items:center;">
                    ${getTypeIcon(i.issue_type)}
                    ${getPriorityBadge(i.priority)}
                  </div>
                  <div style="display:flex;gap:6px;align-items:center;">
                    ${i.story_points ? `<span class="sp-badge">${i.story_points} SP</span>` : ''}
                    ${i.assignee ? getAvatar(i.assignee, 24) : ''}
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `).join('')}
    </div>
  `;
}
"""
pass  # already written

# ── app.js (Part 3: Remaining Pages) ─────────────────────────────────────────
JS_PART3 = """
// ── Projects ──────────────────────────────────────────────────────────────────
async function renderProjects(el) {
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Projects</div><div class="page-subtitle">${allProjects.length} active projects</div></div>
      <button class="btn btn-orange" onclick="openCreateProject()"><i class="fa fa-plus"></i> New Project</button>
    </div>
    <div class="projects-grid">
      ${allProjects.map(p => `
        <div class="project-card" onclick="filterProjectIssues(${p.id})">
          <div class="project-card-top" style="background:${p.color};"></div>
          <div class="project-card-body">
            <div class="project-key" style="background:${p.color};">${p.key}</div>
            <div class="project-name">${p.name}</div>
            <div class="project-dept">${p.department || 'No Department'}</div>
            <div class="project-stats">
              <div><div class="project-stat-val">${p.issue_count || 0}</div><div class="project-stat-lbl">Issues</div></div>
              <div><div class="project-stat-val">${p.member_count || 0}</div><div class="project-stat-lbl">Members</div></div>
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function filterProjectIssues(projectId) {
  nav('issues');
  setTimeout(() => {
    document.getElementById('filter-project').value = projectId;
    filterIssues();
  }, 100);
}

// ── Sprints ───────────────────────────────────────────────────────────────────
async function renderSprints(el) {
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Sprints</div><div class="page-subtitle">${allSprints.length} sprints</div></div>
      <button class="btn btn-orange" onclick="openCreateSprint()"><i class="fa fa-plus"></i> New Sprint</button>
    </div>
    <div class="sprint-list">
      ${allSprints.map(s => `
        <div class="sprint-item">
          <div class="sprint-item-header">
            <div class="sprint-name">${s.name}</div>
            <span class="badge s-${s.status}">${s.status}</span>
            <div class="sprint-dates">${fmt(s.start_date)} - ${fmt(s.end_date)}</div>
          </div>
          ${s.goal ? `<div class="sprint-goal">"${s.goal}"</div>` : ''}
          <div class="progress-bar"><div class="progress-fill" style="width:${s.done_count && s.issue_count ? Math.round(s.done_count / s.issue_count * 100) : 0}%;"></div></div>
          <div style="display:flex;justify-content:space-between;font-size:13px;margin-top:8px;">
            <span>${s.done_count || 0} / ${s.issue_count || 0} issues completed</span>
            <button class="btn btn-sm btn-outline" onclick="viewSprintBoard(${s.id})"><i class="fa fa-columns"></i> View Board</button>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function viewSprintBoard(sprintId) {
  nav('kanban');
}

// ── Team ──────────────────────────────────────────────────────────────────────
async function renderTeam(el) {
  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Team</div><div class="page-subtitle">${allUsers.length} members</div></div>
      ${currentUser.role === 'admin' ? '<button class="btn btn-orange" onclick="openCreateUser()"><i class="fa fa-user-plus"></i> Add Member</button>' : ''}
    </div>
    <div class="users-grid">
      ${allUsers.map(u => `
        <div class="user-card">
          <div class="user-card-avatar" style="background:${u.avatar_color};">${getInitials(u.full_name)}</div>
          <div class="user-card-name">${u.full_name}</div>
          <div class="user-card-dept">${u.department || 'No Department'}</div>
          ${getRoleBadge(u.role)}
          <div style="margin-top:8px;font-size:12px;color:#6b7280;">${u.email}</div>
        </div>
      `).join('')}
    </div>
  `;
}

// ── Reports ───────────────────────────────────────────────────────────────────
async function renderReports(el) {
  const summary = await api('GET', '/api/dashboard/projects/summary');
  el.innerHTML = `
    <div class="page-header"><div class="page-title">Reports & Analytics</div></div>
    <div class="card">
      <div class="card-title"><i class="fa fa-folder-open"></i> Project Summary</div>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>Project</th><th>Key</th><th>Department</th><th>Total Issues</th><th>Open Issues</th><th>Health</th></tr></thead>
          <tbody>
            ${summary.map(p => {
              const health = p.open_issues === 0 ? 'Excellent' : p.open_issues < 10 ? 'Good' : p.open_issues < 30 ? 'Fair' : 'Needs Attention';
              const healthColor = p.open_issues === 0 ? '#15803d' : p.open_issues < 10 ? '#16a34a' : p.open_issues < 30 ? '#F5A623' : '#dc2626';
              return `<tr><td><strong>${p.name}</strong></td><td><span class="badge" style="background:${p.color};color:#fff;">${p.key}</span></td><td>${p.department || '-'}</td><td>${p.total_issues}</td><td>${p.open_issues}</td><td><span style="color:${healthColor};font-weight:600;">${health}</span></td></tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// ── SLA Monitor ───────────────────────────────────────────────────────────────
async function renderSLA(el) {
  const issues = await api('GET', '/api/issues/');
  const now = new Date();
  const slaIssues = issues.filter(i => i.due_date && !['done', 'closed', 'cancelled'].includes(i.status)).map(i => {
    const due = new Date(i.due_date);
    const diff = Math.floor((due - now) / (1000 * 60 * 60 * 24));
    const status = diff < 0 ? 'breach' : diff < 2 ? 'warn' : 'ok';
    return {...i, sla_days: diff, sla_status: status};
  }).sort((a, b) => a.sla_days - b.sla_days);
  el.innerHTML = `
    <div class="page-header"><div><div class="page-title">SLA Monitor</div><div class="page-subtitle">${slaIssues.length} issues with due dates</div></div></div>
    <div class="tbl-wrap">
      <table class="sla-table">
        <thead><tr><th>Key</th><th>Title</th><th>Priority</th><th>Assignee</th><th>Due Date</th><th>Days Remaining</th><th>SLA Status</th></tr></thead>
        <tbody>
          ${slaIssues.map(i => `
            <tr onclick="openIssueDetail(${i.id})">
              <td><strong style="color:#1B1F6B;">${i.key}</strong></td>
              <td>${i.title}</td>
              <td>${getPriorityBadge(i.priority)}</td>
              <td>${i.assignee ? getAvatar(i.assignee) + ' ' + i.assignee.full_name : '-'}</td>
              <td>${fmt(i.due_date)}</td>
              <td style="font-weight:600;color:${i.sla_status === 'breach' ? '#dc2626' : i.sla_status === 'warn' ? '#F5A623' : '#15803d'};">${i.sla_days} days</td>
              <td><div class="sla-bar"><div class="sla-fill sla-${i.sla_status}" style="width:${i.sla_status === 'breach' ? 100 : i.sla_status === 'warn' ? 60 : 30}%;"></div></div></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

// ── Audit Log ─────────────────────────────────────────────────────────────────
async function renderAudit(el) {
  const logs = await api('GET', '/api/dashboard/stats');
  const activities = logs.recent_activity || [];
  el.innerHTML = `
    <div class="page-header"><div class="page-title">Audit Log</div></div>
    <div class="card">
      ${activities.map(a => `
        <div class="audit-row">
          <div class="audit-time">${fmt(a.created_at)} ${new Date(a.created_at).toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'})}</div>
          <div class="audit-action"><span class="audit-user">${a.user.full_name}</span> ${a.action.replace(/_/g, ' ')} ${a.field_changed ? `<strong>${a.field_changed}</strong>` : ''} ${a.old_value && a.new_value ? `from <em>${a.old_value}</em> to <em>${a.new_value}</em>` : ''}</div>
        </div>
      `).join('')}
    </div>
  `;
}

// ── Notifications ─────────────────────────────────────────────────────────────
async function renderNotifications(el) {
  const notifs = await api('GET', '/api/notifications/');
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
      `).join('') : '<div class="empty-state"><i class="fa fa-bell-slash"></i><h3>No Notifications</h3><p>You\'re all caught up!</p></div>'}
    </div>
  `;
}

async function markAllRead() {
  await api('POST', '/api/notifications/mark-read');
  toast('All notifications marked as read', 'success');
  loadNotifications();
  renderNotifications(document.getElementById('page-notifications'));
}

async function markNotifRead(notifId, issueId) {
  await api('POST', `/api/notifications/${notifId}/read`);
  loadNotifications();
  if (issueId) openIssueDetail(issueId);
}

// ── Settings ──────────────────────────────────────────────────────────────────
async function renderSettings(el) {
  el.innerHTML = `
    <div class="page-header"><div class="page-title">Settings</div></div>
    <div class="card">
      <div class="card-title"><i class="fa fa-user-circle"></i> Profile</div>
      <div class="two-col">
        <div class="detail-field"><div class="detail-label">Full Name</div><div class="detail-value">${currentUser.full_name}</div></div>
        <div class="detail-field"><div class="detail-label">Username</div><div class="detail-value">${currentUser.username}</div></div>
        <div class="detail-field"><div class="detail-label">Email</div><div class="detail-value">${currentUser.email}</div></div>
        <div class="detail-field"><div class="detail-label">Role</div><div class="detail-value">${getRoleBadge(currentUser.role)}</div></div>
        <div class="detail-field"><div class="detail-label">Department</div><div class="detail-value">${currentUser.department || '-'}</div></div>
        <div class="detail-field"><div class="detail-label">Branch</div><div class="detail-value">${currentUser.branch || '-'}</div></div>
      </div>
    </div>
    <div class="card" style="margin-top:16px;">
      <div class="card-title"><i class="fa fa-info-circle"></i> System Information</div>
      <div class="metric-row"><span class="metric-label">Version</span><span class="metric-value">1.0.0</span></div>
      <div class="metric-row"><span class="metric-label">Backend API</span><span class="metric-value">${API_BASE}</span></div>
      <div class="metric-row"><span class="metric-label">Total Projects</span><span class="metric-value">${allProjects.length}</span></div>
      <div class="metric-row"><span class="metric-label">Total Users</span><span class="metric-value">${allUsers.length}</span></div>
    </div>
  `;
}

// ── Roadmap (Placeholder) ─────────────────────────────────────────────────────
async function renderRoadmap(el) {
  el.innerHTML = '<div class="empty-state"><i class="fa fa-road"></i><h3>Roadmap View</h3><p>Timeline and roadmap visualization coming soon</p></div>';
}

// ── Issue Detail ──────────────────────────────────────────────────────────────
async function openIssueDetail(issueId) {
  openModal('issue-detail');
  const body = document.getElementById('issue-detail-body');
  body.innerHTML = '<div style="text-align:center;padding:40px;"><div class="spinner"></div></div>';
  try {
    const issue = await api('GET', `/api/issues/${issueId}`);
    const comments = await api('GET', `/api/issues/${issueId}/comments`);
    const activity = await api('GET', `/api/issues/${issueId}/activity`);
    currentIssue = issue;
    document.getElementById('detail-key-title').innerHTML = `<strong style="color:#1B1F6B;">${issue.key}</strong> ${issue.title}`;
    body.innerHTML = `
      <div class="issue-tabs">
        <div class="issue-tab active" onclick="switchTab('details')">Details</div>
        <div class="issue-tab" onclick="switchTab('comments')">Comments (${comments.length})</div>
        <div class="issue-tab" onclick="switchTab('activity')">Activity (${activity.length})</div>
      </div>
      <div class="issue-detail-grid">
        <div>
          <div id="tab-details" class="tab-pane active">
            <div class="detail-field"><div class="detail-label">Description</div><div class="detail-value">${issue.description || '<em style="color:#6b7280;">No description</em>'}</div></div>
          </div>
          <div id="tab-comments" class="tab-pane">
            <div id="comments-list">${comments.map(c => `
              <div class="comment-item">
                ${getAvatar(c.author, 32)}
                <div class="comment-body ${c.is_internal ? 'comment-internal' : ''}">
                  <div><span class="comment-author">${c.author.full_name}</span><span class="comment-time">${fmtTime(c.created_at)}</span>${c.is_internal ? ' <span class="badge" style="background:#F5A623;color:#fff;font-size:10px;">Internal</span>' : ''}</div>
                  <div class="comment-text">${c.content}</div>
                </div>
              </div>
            `).join('')}</div>
            <div class="form-group" style="margin-top:16px;"><textarea id="new-comment" rows="3" placeholder="Add a comment..."></textarea></div>
            <div style="display:flex;gap:10px;align-items:center;"><button class="btn btn-primary btn-sm" onclick="addComment()"><i class="fa fa-comment"></i> Add Comment</button><label style="font-size:13px;display:flex;align-items:center;gap:6px;cursor:pointer;"><input type="checkbox" id="comment-internal"/> Internal Note</label></div>
          </div>
          <div id="tab-activity" class="tab-pane">
            ${activity.map(a => `
              <div class="audit-row">
                <div class="audit-time">${fmtTime(a.created_at)}</div>
                <div class="audit-action"><span class="audit-user">${a.user.full_name}</span> ${a.action.replace(/_/g, ' ')} ${a.field_changed ? `<strong>${a.field_changed}</strong>` : ''} ${a.old_value && a.new_value ? `from <em>${a.old_value}</em> to <em>${a.new_value}</em>` : ''}</div>
              </div>
            `).join('')}
          </div>
        </div>
        <div class="detail-sidebar">
          <div class="detail-field"><div class="detail-label">Status</div><div class="detail-value">${getStatusBadge(issue.status)}</div></div>
          <div class="detail-field"><div class="detail-label">Priority</div><div class="detail-value">${getPriorityBadge(issue.priority)}</div></div>
          <div class="detail-field"><div class="detail-label">Type</div><div class="detail-value">${getTypeIcon(issue.issue_type)} ${issue.issue_type}</div></div>
          <div class="detail-field"><div class="detail-label">Reporter</div><div class="detail-value">${issue.reporter ? getAvatar(issue.reporter, 24) + ' ' + issue.reporter.full_name : '-'}</div></div>
          <div class="detail-field"><div class="detail-label">Assignee</div><div class="detail-value">${issue.assignee ? getAvatar(issue.assignee, 24) + ' ' + issue.assignee.full_name : 'Unassigned'}</div></div>
          <div class="detail-field"><div class="detail-label">Sprint</div><div class="detail-value">${issue.sprint ? issue.sprint.name : 'No Sprint'}</div></div>
          <div class="detail-field"><div class="detail-label">Story Points</div><div class="detail-value">${issue.story_points || 0}</div></div>
          <div class="detail-field"><div class="detail-label">Due Date</div><div class="detail-value">${fmt(issue.due_date)}</div></div>
          <div class="detail-field"><div class="detail-label">Created</div><div class="detail-value">${fmt(issue.created_at)}</div></div>
          <div class="detail-field"><div class="detail-label">Updated</div><div class="detail-value">${fmt(issue.updated_at)}</div></div>
        </div>
      </div>
    `;
  } catch (e) {
    body.innerHTML = `<div class="empty-state"><i class="fa fa-exclamation-triangle"></i><h3>Error</h3><p>${e.message}</p></div>`;
  }
}

function switchTab(tab) {
  document.querySelectorAll('.issue-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelector(`.issue-tab:nth-child(${tab === 'details' ? 1 : tab === 'comments' ? 2 : 3})`).classList.add('active');
  document.getElementById(`tab-${tab}`).classList.add('active');
}

async function addComment() {
  const content = document.getElementById('new-comment').value.trim();
  const isInternal = document.getElementById('comment-internal').checked;
  if (!content) return toast('Comment cannot be empty', 'error');
  try {
    await api('POST', `/api/issues/${currentIssue.id}/comments`, {content, is_internal: isInternal});
    toast('Comment added', 'success');
    openIssueDetail(currentIssue.id);
  } catch (e) {}
}

function editCurrentIssue() {
  toast('Edit functionality coming soon', 'warning');
}

// ── Init on Load ──────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('awash_token');
  const user = localStorage.getItem('awash_user');
  if (token && user) {
    currentUser = JSON.parse(user);
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('app').style.display = 'flex';
    initApp();
  }
});
"""
with open(os.path.join(FE, "app.js"), "w", encoding="utf-8") as f: f.write(JS_PART1 + JS_PART2 + JS_PART3); print(f"  wrote app.js ({len(JS_PART1 + JS_PART2 + JS_PART3)} bytes)")

# ── Run Generator ─────────────────────────────────────────────────────────────
print("\nGenerating frontend files...")
print("=" * 60)
print("✓ Frontend generated successfully!")
print("\nFiles created:")
print("  - frontend/index.html")
print("  - frontend/app.css")
print("  - frontend/app.js")
print("\nTo run the application:")
print("  1. cd 'issues tracking/backend'")
print("  2. pip install -r requirements.txt")
print("  3. python -m app.seed  (seed demo data)")
print("  4. uvicorn main:app --reload")
print("  5. Open http://localhost:8000 in your browser")
print("\nDemo accounts:")
print("  admin / Admin@123")
print("  pm.sara / Pass@123")
print("  qa.meron / Pass@123")
print("  dev.yonas / Pass@123")
print("=" * 60)
