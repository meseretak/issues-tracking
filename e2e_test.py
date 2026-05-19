x=1

import urllib.request, urllib.parse, json, os, time

BASE = 'http://localhost:8000'
PASS = []; FAIL = []

def check(name, ok, detail=''):
    if ok: PASS.append(name); print('  OK: ' + name)
    else: FAIL.append(name); print('  FAIL: ' + name + (' - ' + str(detail) if detail else ''))

def req(method, path, data=None, token=None, form=False, timeout=5):
    url = BASE + path
    headers = {}
    if token: headers['Authorization'] = 'Bearer ' + token
    if data and not form:
        body = json.dumps(data).encode()
        headers['Content-Type'] = 'application/json'
    elif data and form:
        body = urllib.parse.urlencode(data).encode()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        body = None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=timeout)
        return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read()), e.code
        except: return {'error': str(e)}, e.code
    except Exception as e:
        return {'error': str(e)}, 0

print('=== FULL END-TO-END TEST ===')
print()

# ── 1. Frontend Files ─────────────────────────────────────────────────────────
print('[1] Frontend Files')
try:
    r = urllib.request.urlopen(BASE + '/', timeout=3)
    html = r.read().decode()
    check('index.html serves', 'Awash Bank' in html)
    lp_idx = html.find('login-page')
    lp_tag = html[lp_idx-5:lp_idx+80] if lp_idx >= 0 else ''
    check('login-page visible by default', 'display:none' not in lp_tag[:60])
    ap_idx = html.find('"app"')
    ap_tag = html[ap_idx:ap_idx+60] if ap_idx >= 0 else ''
    check('app hidden by default', 'display:none' in ap_tag)
    check('app.css linked', 'app.css' in html)
    check('app.js linked', 'app.js' in html)
except Exception as e:
    check('Frontend loads', False, str(e))

try:
    r2 = urllib.request.urlopen(BASE + '/app.js', timeout=3)
    js = r2.read().decode()
    check('app.js serves (' + str(len(js)) + ' bytes)', len(js) > 50000)
    check('DOMContentLoaded in JS', 'DOMContentLoaded' in js)
    check('doLogin in JS', 'doLogin' in js)
    check('ROLE_PERMS in JS', 'ROLE_PERMS' in js)
    check('can() permission fn', 'function can(' in js)
    check('STATUS_TRANSITIONS', 'STATUS_TRANSITIONS' in js)
    check('renderTasks in JS', 'renderTasks' in js)
    check('renderGroups in JS', 'renderGroups' in js)
    check('renderChat in JS', 'renderChat' in js)
    check('renderExecutive in JS', 'renderExecutive' in js)
    check('renderIntegrations in JS', 'renderIntegrations' in js)
    check('renderBacklog drag-drop', 'dragIssue' in js)
    check('quickUpdateIssue', 'quickUpdateIssue' in js)
    check('editCurrentIssue', 'editCurrentIssue' in js)
    check('deleteCurrentIssue', 'deleteCurrentIssue' in js)
    check('assignToMe', 'assignToMe' in js)
    check('filterIssues', 'filterIssues' in js)
    check('globalSearch', 'globalSearch' in js)
    check('exportToCSV', 'exportToCSV' in js)
    check('renderBurndownChart', 'renderBurndownChart' in js)
except Exception as e:
    check('app.js serves', False, str(e))

try:
    r3 = urllib.request.urlopen(BASE + '/app.css', timeout=3)
    css = r3.read().decode()
    check('app.css serves (' + str(len(css)) + ' bytes)', len(css) > 10000)
    statuses = ['backlog','todo','in_progress','in_review','testing','qa_approved','uat','done','closed','cancelled','blocked']
    check('All 11 status badges in CSS', all('.s-'+s in css for s in statuses))
    check('Full-screen layout (.main flex:1)', '.main{flex:1' in css)
    check('Login page CSS', '#login-page' in css)
except Exception as e:
    check('app.css serves', False, str(e))

# ── 2. Authentication ─────────────────────────────────────────────────────────
print()
print('[2] Authentication')
d, s = req('POST', '/api/auth/login', {'username':'admin','password':'Admin@123'}, form=True)
check('Admin login', s == 200 and 'access_token' in d, d.get('detail',''))
admin_token = d.get('access_token','')

d2, s2 = req('POST', '/api/auth/login', {'username':'pm.sara','password':'Pass@123'}, form=True)
check('PM login', s2 == 200)
pm_token = d2.get('access_token','')

d3, s3 = req('POST', '/api/auth/login', {'username':'qa.meron','password':'Pass@123'}, form=True)
check('QA login', s3 == 200)
qa_token = d3.get('access_token','')

d4, s4 = req('POST', '/api/auth/login', {'username':'dev.yonas','password':'Pass@123'}, form=True)
check('Dev login', s4 == 200)

d5, s5 = req('POST', '/api/auth/login', {'username':'devops.abel','password':'Pass@123'}, form=True)
check('DevOps login', s5 == 200)

d6, s6 = req('POST', '/api/auth/login', {'username':'sec.hana','password':'Pass@123'}, form=True)
check('Security login', s6 == 200)

d_bad, s_bad = req('POST', '/api/auth/login', {'username':'admin','password':'wrong'}, form=True)
check('Bad login rejected (401)', s_bad == 401)

# ── 3. Users ──────────────────────────────────────────────────────────────────
print()
print('[3] Users & Roles')
users, s = req('GET', '/api/users/', token=admin_token)
check('List users', s == 200 and len(users) >= 7, len(users) if isinstance(users,list) else users)
check('Users have roles', all('role' in u for u in users) if isinstance(users,list) else False)
check('Users have departments', any(u.get('department') for u in users) if isinstance(users,list) else False)
check('Users have employee_id', any(u.get('employee_id') for u in users) if isinstance(users,list) else False)
check('Users have phone', any(u.get('phone') for u in users) if isinstance(users,list) else False)

# ── 4. Projects ───────────────────────────────────────────────────────────────
print()
print('[4] Projects')
projects, s = req('GET', '/api/projects/', token=admin_token)
check('List projects', s == 200 and len(projects) >= 4, len(projects) if isinstance(projects,list) else projects)
check('Projects have issue_count', all('issue_count' in p for p in projects) if isinstance(projects,list) else False)
check('Projects have member_count', all('member_count' in p for p in projects) if isinstance(projects,list) else False)
pid = projects[0]['id'] if projects else 1

pkey = 'T' + str(int(time.time()) % 9999)
new_proj, s = req('POST', '/api/projects/', {'key':pkey,'name':'Test Project','department':'QA'}, token=admin_token)
check('Admin can create project', s == 201, new_proj.get('detail',''))

new_proj2, s2 = req('POST', '/api/projects/', {'key':pkey+'P','name':'PM Project','department':'Dev'}, token=pm_token)
check('PM can create project', s2 == 201, new_proj2.get('detail',''))

# ── 5. Issues ─────────────────────────────────────────────────────────────────
print()
print('[5] Issues')
issues_list, s = req('GET', '/api/issues/', token=admin_token)
check('List issues', s == 200 and len(issues_list) >= 15, len(issues_list) if isinstance(issues_list,list) else issues_list)
if isinstance(issues_list, list) and issues_list:
    statuses_found = set(i['status'] for i in issues_list)
    check('Multiple statuses present', len(statuses_found) >= 5, str(statuses_found))
    check('New statuses (qa_approved/uat/blocked)', any(i['status'] in ['qa_approved','uat','blocked'] for i in issues_list))

new_issue, s = req('POST', '/api/issues/', {
    'title': 'E2E Test Issue', 'issue_type': 'bug',
    'status': 'todo', 'priority': 'high',
    'project_id': pid, 'story_points': 3
}, token=admin_token)
check('Create issue', s == 201 and 'key' in new_issue, new_issue.get('detail',''))
iid = new_issue.get('id', 1)

issue_detail, s = req('GET', '/api/issues/' + str(iid), token=admin_token)
check('Get issue detail', s == 200 and issue_detail.get('id') == iid)

updated, s = req('PUT', '/api/issues/' + str(iid), {'status': 'in_progress'}, token=admin_token)
check('Update issue status', s == 200 and updated.get('status') == 'in_progress', updated.get('detail',''))

# Filter tests
filtered, s = req('GET', '/api/issues/?status=backlog', token=admin_token)
check('Filter by status', s == 200 and all(i['status']=='backlog' for i in filtered) if isinstance(filtered,list) else False)

my_issues, s = req('GET', '/api/issues/?assignee_id=1', token=admin_token)
check('Filter by assignee', s == 200 and isinstance(my_issues, list))

search_res, s = req('GET', '/api/issues/?search=login', token=admin_token)
check('Search issues', s == 200 and isinstance(search_res, list))

# ── 6. Comments ───────────────────────────────────────────────────────────────
print()
print('[6] Comments')
comment, s = req('POST', '/api/issues/' + str(iid) + '/comments', {'content': 'Test comment', 'is_internal': False}, token=admin_token)
check('Add comment', s == 201, comment.get('detail',''))

int_comment, s = req('POST', '/api/issues/' + str(iid) + '/comments', {'content': 'Internal note', 'is_internal': True}, token=admin_token)
check('Add internal comment', s == 201 and int_comment.get('is_internal') == True)

comments_list, s = req('GET', '/api/issues/' + str(iid) + '/comments', token=admin_token)
check('List comments', s == 200 and len(comments_list) >= 1)

activity, s = req('GET', '/api/issues/' + str(iid) + '/activity', token=admin_token)
check('Get activity log', s == 200 and len(activity) >= 1)

# ── 7. Time Tracking ─────────────────────────────────────────────────────────
print()
print('[7] Time Tracking')
tl, s = req('POST', '/api/issues/' + str(iid) + '/time-logs?hours=2.5&work_date=2026-05-14T00:00:00Z&description=Testing', token=admin_token)
check('Log time', s == 200 and 'total_logged' in tl, tl.get('detail',''))

logs, s = req('GET', '/api/issues/' + str(iid) + '/time-logs', token=admin_token)
check('Get time logs', s == 200 and len(logs) >= 1)
check('Time log has correct hours', logs[0]['hours'] == 2.5 if logs else False)

# ── 8. Sprints ────────────────────────────────────────────────────────────────
print()
print('[8] Sprints')
sprints, s = req('GET', '/api/sprints/', token=admin_token)
check('List sprints', s == 200 and len(sprints) >= 3, len(sprints) if isinstance(sprints,list) else sprints)
check('Sprints have issue_count', all('issue_count' in sp for sp in sprints) if isinstance(sprints,list) else False)
check('Sprints have done_count', all('done_count' in sp for sp in sprints) if isinstance(sprints,list) else False)

sid = sprints[0]['id'] if sprints else 1
board, s = req('GET', '/api/sprints/' + str(sid) + '/board', token=admin_token)
check('Sprint board', s == 200 and 'backlog' in board)
check('Board has all status columns', all(col in board for col in ['backlog','todo','in_progress','done']) if s == 200 else False)

add_sp, s = req('POST', '/api/sprints/' + str(sid) + '/issues/' + str(iid), token=admin_token)
check('Add issue to sprint', s == 200, add_sp.get('detail',''))

remove_sp, s = req('DELETE', '/api/sprints/' + str(sid) + '/issues/' + str(iid), token=admin_token)
check('Remove issue from sprint', s == 200, remove_sp.get('detail',''))

# ── 9. Teams ──────────────────────────────────────────────────────────────────
print()
print('[9] Teams')
teams, s = req('GET', '/api/teams/', token=admin_token)
check('List teams', s == 200 and len(teams) >= 6, len(teams) if isinstance(teams,list) else teams)
check('Teams have members', all('members' in t for t in teams) if isinstance(teams,list) else False)
check('Dev team has 2 members', any(t['team_type']=='dev' and t['member_count']==2 for t in teams) if isinstance(teams,list) else False)
check('QA team has members', any(t['team_type']=='qa' and t['member_count']>0 for t in teams) if isinstance(teams,list) else False)

# ── 10. Dashboard ─────────────────────────────────────────────────────────────
print()
print('[10] Dashboard')
stats, s = req('GET', '/api/dashboard/stats', token=admin_token)
check('Dashboard stats', s == 200 and 'total_issues' in stats)
check('Stats has by_status', 'by_status' in stats and isinstance(stats.get('by_status'), dict))
check('Stats has by_priority', 'by_priority' in stats)
check('Stats has daily_trend (14 days)', len(stats.get('daily_trend',[])) == 14)
check('Stats has sprint_progress', 'sprint_progress' in stats)
check('Stats has by_assignee', 'by_assignee' in stats and len(stats.get('by_assignee',[])) > 0)
check('Stats has velocity_trend', 'velocity_trend' in stats)

proj_sum, s = req('GET', '/api/dashboard/projects/summary', token=admin_token)
check('Project summary', s == 200 and len(proj_sum) >= 4)
check('Project summary has health data', all('open_issues' in p and 'total_issues' in p for p in proj_sum) if isinstance(proj_sum,list) else False)

# ── 11. Reports ───────────────────────────────────────────────────────────────
print()
print('[11] Reports')
r_csv = urllib.request.Request(BASE + '/api/reports/export/csv', headers={'Authorization': 'Bearer ' + admin_token})
try:
    resp = urllib.request.urlopen(r_csv, timeout=5)
    lines = resp.read().decode('utf-8-sig').strip().split('\n')
    check('CSV export', len(lines) >= 2 and 'Key' in lines[0], str(len(lines)) + ' rows')
    check('CSV has all columns', all(col in lines[0] for col in ['Key','Title','Status','Priority']))
except Exception as e:
    check('CSV export', False, str(e))

active_sprints = [sp for sp in sprints if sp['status'] == 'active'] if isinstance(sprints,list) else []
if active_sprints:
    burndown, s = req('GET', '/api/reports/burndown/' + str(active_sprints[0]['id']), token=admin_token)
    check('Burndown data', s == 200 and 'data' in burndown)
    check('Burndown has sprint name', 'sprint_name' in burndown if s == 200 else False)
else:
    print('  SKIP: No active sprint for burndown test')

velocity, s = req('GET', '/api/reports/velocity', token=admin_token)
check('Velocity data', s == 200 and isinstance(velocity, list))

# ── 12. Notifications ─────────────────────────────────────────────────────────
print()
print('[12] Notifications')
notifs, s = req('GET', '/api/notifications/', token=admin_token)
check('List notifications', s == 200 and isinstance(notifs, list))

mark, s = req('POST', '/api/notifications/mark-read', token=admin_token)
check('Mark all read', s == 200)

# ── 13. Attachments ───────────────────────────────────────────────────────────
print()
print('[13] Attachments')
atts, s = req('GET', '/api/issues/' + str(iid) + '/attachments', token=admin_token)
check('Get attachments', s == 200 and isinstance(atts, list))

# ── 14. Delete Issue ──────────────────────────────────────────────────────────
print()
print('[14] Cleanup')
del_r, s = req('DELETE', '/api/issues/' + str(iid), token=admin_token)
check('Delete test issue', s == 200, del_r.get('detail',''))

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print('=' * 55)
total = len(PASS) + len(FAIL)
print('PASSED: ' + str(len(PASS)) + '/' + str(total))
if FAIL:
    print('FAILED: ' + str(len(FAIL)))
    for f in FAIL:
        print('  - ' + f)
    print()
    print('System has ' + str(len(FAIL)) + ' issue(s) to fix.')
else:
    print()
    print('ALL ' + str(total) + ' TESTS PASSED! System is fully operational.')
    print('Open http://localhost:8000 in your browser (Ctrl+Shift+R to hard refresh)')
