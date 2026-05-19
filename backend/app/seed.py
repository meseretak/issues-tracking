"""Seed script — run with: python -m app.seed"""
import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy import insert, text
from app.database import init_db, AsyncSessionLocal
from app.models import (
    User, Project, ProjectMember, Sprint, Issue, Label, ActivityLog,
    Team, Comment, team_members,
    UserRole, IssuePriority, IssueType, SprintStatus, IssueSeverity,
    WorkflowStatus, WorkflowTransitionRule
)
from app.auth import get_password_hash


USERS = [
    dict(employee_id="AWB-001", username="admin",       full_name="System Administrator",  email="admin@awashbank.com",       role=UserRole.SUPER_ADMIN,       department="IT",                 branch="Head Office",  avatar_color="#1B1F6B", phone="+251911000001", password="Admin@123"),
    dict(employee_id="AWB-002", username="pm.sara",     full_name="Sara Tesfaye",           email="sara.t@awashbank.com",      role=UserRole.PROJECT_MANAGER,   department="Project Management", branch="Head Office",  avatar_color="#7c3aed", phone="+251911000002", password="Pass@123"),
    dict(employee_id="AWB-003", username="sm.bekele",   full_name="Bekele Girma",           email="bekele.g@awashbank.com",    role=UserRole.SCRUM_MASTER,      department="Project Management", branch="Head Office",  avatar_color="#0d7377", phone="+251911000003", password="Pass@123"),
    dict(employee_id="AWB-004", username="ba.ruth",     full_name="Ruth Alemu",             email="ruth.a@awashbank.com",      role=UserRole.BUSINESS_ANALYST,  department="Business Analysis",  branch="Head Office",  avatar_color="#c2410c", phone="+251911000004", password="Pass@123"),
    dict(employee_id="AWB-005", username="dev.yonas",   full_name="Yonas Haile",            email="yonas.h@awashbank.com",     role=UserRole.DEVELOPER,         department="Development",        branch="Head Office",  avatar_color="#1d4ed8", phone="+251911000005", password="Pass@123"),
    dict(employee_id="AWB-006", username="dev.tigist",  full_name="Tigist Bekele",          email="tigist.b@awashbank.com",    role=UserRole.DEVELOPER,         department="Development",        branch="Head Office",  avatar_color="#0891b2", phone="+251911000006", password="Pass@123"),
    dict(employee_id="AWB-007", username="qa.meron",    full_name="Meron Tadesse",          email="meron.t@awashbank.com",     role=UserRole.QA_ENGINEER,       department="Quality Assurance",  branch="Head Office",  avatar_color="#15803d", phone="+251911000007", password="Pass@123"),
    dict(employee_id="AWB-008", username="qa.dawit",    full_name="Dawit Kebede",           email="dawit.k@awashbank.com",     role=UserRole.QA_ENGINEER,       department="Quality Assurance",  branch="Head Office",  avatar_color="#16a34a", phone="+251911000008", password="Pass@123"),
    dict(employee_id="AWB-009", username="devops.abel", full_name="Abel Mulugeta",          email="abel.m@awashbank.com",      role=UserRole.DEVOPS_ENGINEER,   department="DevOps",             branch="Head Office",  avatar_color="#b45309", phone="+251911000009", password="Pass@123"),
    dict(employee_id="AWB-010", username="sec.hana",    full_name="Hana Worku",             email="hana.w@awashbank.com",      role=UserRole.SECURITY_ENGINEER, department="Security",           branch="Head Office",  avatar_color="#dc2626", phone="+251911000010", password="Pass@123"),
    dict(employee_id="AWB-011", username="viewer.test", full_name="Test Viewer",            email="viewer@awashbank.com",      role=UserRole.VIEWER,            department="Operations",         branch="Addis Branch", avatar_color="#6b7280", phone="+251911000011", password="Pass@123"),
]

TEAMS = [
    dict(name="Development Team",   team_type="dev",      color="#1d4ed8", description="Core software development team"),
    dict(name="QA Team",            team_type="qa",       color="#15803d", description="Quality assurance and testing team"),
    dict(name="DevOps Team",        team_type="devops",   color="#b45309", description="Infrastructure and deployment team"),
    dict(name="Project Management", team_type="pm",       color="#7c3aed", description="Project planning and management team"),
    dict(name="Business Analysis",  team_type="ba",       color="#c2410c", description="Requirements and analysis team"),
    dict(name="Security Team",      team_type="security", color="#dc2626", description="Security and compliance team"),
]

PROJECTS = [
    dict(key="CBS", name="Core Banking System Upgrade",   department="Core Banking",    color="#1B1F6B", risk_level="high",     project_type="scrum"),
    dict(key="MOB", name="Awash Mobile Banking",          department="Digital Banking", color="#7c3aed", risk_level="medium",   project_type="scrum"),
    dict(key="INF", name="Infrastructure Modernization",  department="DevOps",          color="#b45309", risk_level="high",     project_type="kanban"),
    dict(key="SEC", name="Security Hardening Initiative", department="Security",        color="#dc2626", risk_level="critical", project_type="task_tracking"),
    dict(key="DIG", name="Digital Transformation",        department="IT",              color="#0891b2", risk_level="medium",   project_type="business"),
]

LABELS = [
    ("backend", "#1d4ed8"), ("frontend", "#7c3aed"), ("database", "#b45309"),
    ("security", "#dc2626"), ("performance", "#c2410c"), ("regression", "#15803d"),
    ("hotfix", "#ef4444"), ("enhancement", "#0891b2"), ("compliance", "#6b7280"), ("mobile", "#a21caf"),
]

ISSUES = [
    dict(title="Login page crashes on mobile Safari",         issue_type=IssueType.BUG,      status="in_progress", priority=IssuePriority.CRITICAL, severity=IssueSeverity.CRITICAL, story_points=5,  estimated_hours=8,  project_key="MOB", description="Users on iOS Safari cannot log in. The page freezes after entering credentials.", environment="Production", component="Auth"),
    dict(title="Implement biometric authentication",          issue_type=IssueType.FEATURE,  status="todo",        priority=IssuePriority.HIGH,     severity=IssueSeverity.MAJOR,    story_points=13, estimated_hours=24, project_key="MOB", description="Add fingerprint and face ID support for mobile app login.", component="Auth"),
    dict(title="Transaction history pagination broken",       issue_type=IssueType.BUG,      status="testing",     priority=IssuePriority.HIGH,     severity=IssueSeverity.MAJOR,    story_points=3,  estimated_hours=4,  project_key="CBS", description="Pagination on transaction history page skips every other page.", environment="Staging", component="UI"),
    dict(title="Core banking API rate limiting",              issue_type=IssueType.TASK,     status="in_review",   priority=IssuePriority.HIGH,     severity=IssueSeverity.MAJOR,    story_points=8,  estimated_hours=16, project_key="CBS", description="Implement rate limiting on all core banking API endpoints.", component="API"),
    dict(title="Database connection pool exhaustion",         issue_type=IssueType.INCIDENT, status="done",        priority=IssuePriority.CRITICAL, severity=IssueSeverity.BLOCKER,  story_points=5,  estimated_hours=6,  project_key="INF", description="Production DB connection pool exhausted during peak hours.", environment="Production"),
    dict(title="SSL certificate renewal automation",          issue_type=IssueType.TASK,     status="qa_approved", priority=IssuePriority.MEDIUM,   severity=IssueSeverity.MINOR,    story_points=3,  estimated_hours=4,  project_key="SEC", description="Automate SSL certificate renewal to prevent expiry incidents."),
    dict(title="Penetration testing Q2 2026",                 issue_type=IssueType.TASK,     status="todo",        priority=IssuePriority.HIGH,     severity=IssueSeverity.MAJOR,    story_points=8,  estimated_hours=40, project_key="SEC", description="Conduct full penetration testing for all public-facing services."),
    dict(title="Kubernetes cluster upgrade to 1.29",          issue_type=IssueType.TASK,     status="in_progress", priority=IssuePriority.HIGH,     severity=IssueSeverity.MAJOR,    story_points=5,  estimated_hours=8,  project_key="INF", description="Upgrade K8s cluster from 1.27 to 1.29 with zero downtime.", environment="Infrastructure"),
    dict(title="Fund transfer performance degradation",       issue_type=IssueType.BUG,      status="backlog",     priority=IssuePriority.CRITICAL, severity=IssueSeverity.CRITICAL, story_points=8,  estimated_hours=12, project_key="CBS", description="Fund transfer API response time increased from 200ms to 2s.", environment="Production", component="API"),
    dict(title="Mobile push notification delivery failure",   issue_type=IssueType.BUG,      status="testing",     priority=IssuePriority.HIGH,     severity=IssueSeverity.MAJOR,    story_points=5,  estimated_hours=8,  project_key="MOB", description="Push notifications not delivered to Android 14 devices.", environment="Production", component="Notifications"),
    dict(title="GDPR data retention policy implementation",   issue_type=IssueType.TASK,     status="todo",        priority=IssuePriority.HIGH,     severity=IssueSeverity.MAJOR,    story_points=13, estimated_hours=32, project_key="SEC", description="Implement automated data retention and deletion policies per GDPR."),
    dict(title="Dashboard loading time optimization",         issue_type=IssueType.IMPROVEMENT, status="in_progress", priority=IssuePriority.MEDIUM, severity=IssueSeverity.MINOR, story_points=5, estimated_hours=8, project_key="DIG", description="Dashboard takes 8s to load. Target is under 2s.", component="UI"),
    dict(title="Two-factor authentication for admin accounts",issue_type=IssueType.SECURITY, status="uat",         priority=IssuePriority.CRITICAL, severity=IssueSeverity.CRITICAL, story_points=8, estimated_hours=16, project_key="SEC", description="Enforce 2FA for all admin and privileged accounts.", component="Auth"),
    dict(title="API documentation update",                    issue_type=IssueType.TASK,     status="done",        priority=IssuePriority.LOW,      severity=IssueSeverity.TRIVIAL,  story_points=2,  estimated_hours=4,  project_key="DIG", description="Update OpenAPI documentation for all v2 endpoints."),
    dict(title="Automated regression test suite",             issue_type=IssueType.TEST_CASE,status="in_progress", priority=IssuePriority.HIGH,     severity=IssueSeverity.MAJOR,    story_points=13, estimated_hours=40, project_key="MOB", description="Build automated regression suite covering 80% of critical paths.", component="QA"),
    dict(title="Account balance display rounding error",      issue_type=IssueType.BUG,      status="blocked",     priority=IssuePriority.HIGH,     severity=IssueSeverity.MAJOR,    story_points=3,  estimated_hours=4,  project_key="CBS", description="Account balance shows incorrect decimal rounding for ETB amounts.", environment="Production", component="UI"),
    dict(title="Implement audit trail for all transactions",  issue_type=IssueType.FEATURE,  status="todo",        priority=IssuePriority.HIGH,     severity=IssueSeverity.MAJOR,    story_points=8,  estimated_hours=20, project_key="CBS", description="Full audit trail for all financial transactions per compliance requirements."),
    dict(title="Mobile app dark mode support",                issue_type=IssueType.IMPROVEMENT, status="backlog",  priority=IssuePriority.LOW,      severity=IssueSeverity.TRIVIAL,  story_points=5,  estimated_hours=12, project_key="MOB", description="Add dark mode theme support to the mobile banking app.", component="UI"),
]


async def seed():
    print("🌱 Seeding Awash Bank Issue Tracker...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # ── Users ──────────────────────────────────────────────────────────────
        user_map = {}
        for u in USERS:
            pwd = u.pop("password")
            user = User(**u, hashed_password=get_password_hash(pwd), is_active=True, is_verified=True)
            db.add(user)
            await db.flush()
            user_map[u["username"]] = user

        # ── Teams ──────────────────────────────────────────────────────────────
        lead_map = {
            "dev": "dev.yonas", "qa": "qa.meron", "devops": "devops.abel",
            "pm": "pm.sara", "ba": "ba.ruth", "security": "sec.hana",
        }
        team_member_map = {
            "dev":      ["dev.yonas", "dev.tigist"],
            "qa":       ["qa.meron", "qa.dawit"],
            "devops":   ["devops.abel"],
            "pm":       ["pm.sara", "sm.bekele"],
            "ba":       ["ba.ruth"],
            "security": ["sec.hana"],
        }
        for t in TEAMS:
            lead = user_map.get(lead_map.get(t["team_type"]))
            team = Team(**t, lead_id=lead.id if lead else None)
            db.add(team)
            await db.flush()
            # Use direct insert into association table to avoid lazy load
            for uname in team_member_map.get(t["team_type"], []):
                if uname in user_map:
                    await db.execute(
                        insert(team_members).values(team_id=team.id, user_id=user_map[uname].id)
                    )

        # ── Labels ─────────────────────────────────────────────────────────────
        label_map = {}
        for name, color in LABELS:
            lbl = Label(name=name, color=color)
            db.add(lbl)
            await db.flush()
            label_map[name] = lbl

        # ── Projects ───────────────────────────────────────────────────────────
        project_map = {}
        for p in PROJECTS:
            proj = Project(**p, lead_id=user_map["pm.sara"].id)
            db.add(proj)
            await db.flush()
            project_map[p["key"]] = proj
            for uname in ["pm.sara", "sm.bekele", "dev.yonas", "dev.tigist",
                          "qa.meron", "qa.dawit", "devops.abel", "ba.ruth", "sec.hana"]:
                db.add(ProjectMember(project_id=proj.id, user_id=user_map[uname].id,
                                     role=user_map[uname].role))

        # ── Sprints ────────────────────────────────────────────────────────────
        now = datetime.now(timezone.utc)
        sprint_defs = [
            dict(name="Sprint 1 - Foundation",   project_key="CBS", status=SprintStatus.COMPLETED,
                 goal="Set up core infrastructure", start_date=now-timedelta(days=28), end_date=now-timedelta(days=14), velocity=34.0),
            dict(name="Sprint 2 - Core Features", project_key="CBS", status=SprintStatus.ACTIVE,
                 goal="Implement core banking APIs", start_date=now-timedelta(days=7), end_date=now+timedelta(days=7), capacity=40),
            dict(name="Sprint 3 - Mobile MVP",    project_key="MOB", status=SprintStatus.ACTIVE,
                 goal="Launch mobile banking MVP", start_date=now-timedelta(days=5), end_date=now+timedelta(days=9), capacity=50),
            dict(name="Sprint 4 - Security",      project_key="SEC", status=SprintStatus.PLANNED,
                 goal="Security hardening phase 1", start_date=now+timedelta(days=3), end_date=now+timedelta(days=17)),
            dict(name="Sprint 5 - DevOps",        project_key="INF", status=SprintStatus.ACTIVE,
                 goal="K8s upgrade and monitoring", start_date=now-timedelta(days=3), end_date=now+timedelta(days=11), capacity=30),
        ]
        sprint_map = {}
        for sd in sprint_defs:
            pkey = sd.pop("project_key")
            sp = Sprint(**sd, project_id=project_map[pkey].id)
            db.add(sp)
            await db.flush()
            sprint_map[pkey] = sp

        # ── Issues ─────────────────────────────────────────────────────────────
        assignees = ["dev.yonas", "dev.tigist", "qa.meron", "devops.abel", "sec.hana",
                     "ba.ruth", "dev.yonas", "devops.abel", "dev.tigist", "qa.dawit",
                     "sec.hana", "dev.yonas", "sec.hana", "ba.ruth", "qa.meron",
                     "dev.tigist", "dev.yonas", "qa.meron"]
        issue_objs = []
        for idx, iss in enumerate(ISSUES):
            pkey = iss.pop("project_key")
            proj = project_map[pkey]
            assignee_name = assignees[idx % len(assignees)]
            sp = sprint_map.get(pkey)
            use_sprint = sp and sp.status != SprintStatus.PLANNED and iss["status"] not in ["backlog", "todo"]
            issue = Issue(
                **iss,
                key=f"{pkey}-{idx+1}",
                project_id=proj.id,
                reporter_id=user_map["pm.sara"].id,
                assignee_id=user_map[assignee_name].id,
                sprint_id=sp.id if use_sprint else None,
            )
            if iss.get("status") in ["done", "closed"]:
                issue.resolved_at = now - timedelta(hours=idx * 3)
            db.add(issue)
            await db.flush()
            issue_objs.append(issue)
            db.add(ActivityLog(action="created_issue", issue_id=issue.id,
                               user_id=user_map["pm.sara"].id))

        # ── Comments ───────────────────────────────────────────────────────────
        comments_data = [
            (0, "dev.yonas",   "Reproduced on iPhone 14 Pro. Investigating the Safari WebKit issue."),
            (0, "qa.meron",    "Confirmed on iOS 17.3. Not reproducible on Android."),
            (2, "dev.tigist",  "Fixed the pagination offset calculation. PR submitted."),
            (2, "qa.dawit",    "Tested fix on staging. Works correctly now."),
            (4, "devops.abel", "Root cause: connection pool size was set to 10. Increased to 50."),
            (7, "devops.abel", "Upgrade plan drafted. Will execute during maintenance window."),
            (12, "sec.hana",   "2FA implementation complete. Ready for UAT testing."),
        ]
        for issue_idx, author_name, content in comments_data:
            db.add(Comment(content=content, issue_id=issue_objs[issue_idx].id,
                           author_id=user_map[author_name].id))

        # ── Workflow Statuses & Rules ──────────────────────────────────────────
        default_statuses = [
            {"name": "Backlog", "key": "backlog", "color": "#42526E", "category": "todo", "order_index": 0},
            {"name": "To Do", "key": "todo", "color": "#0052CC", "category": "todo", "order_index": 1},
            {"name": "In Progress", "key": "in_progress", "color": "#0052CC", "category": "in_progress", "order_index": 2},
            {"name": "Testing", "key": "testing", "color": "#FF991F", "category": "in_progress", "order_index": 3},
            {"name": "QA Approved", "key": "qa_approved", "color": "#008DA6", "category": "done", "order_index": 4},
            {"name": "UAT", "key": "uat", "color": "#6554C0", "category": "done", "order_index": 5},
            {"name": "Done", "key": "done", "color": "#36B37E", "category": "done", "order_index": 6},
            {"name": "Closed", "key": "closed", "color": "#172B4D", "category": "done", "order_index": 7},
            {"name": "Blocked", "key": "blocked", "color": "#FF5630", "category": "in_progress", "order_index": 8},
        ]
        for ds in default_statuses:
            db.add(WorkflowStatus(**ds))
            
        default_rules = [
            {"from_status_key": "todo", "to_status_key": "in_progress", "allowed_role": "developer"},
            {"from_status_key": "in_progress", "to_status_key": "testing", "allowed_role": "developer"},
            {"from_status_key": "in_progress", "to_status_key": "todo", "allowed_role": "developer"},
            {"from_status_key": "testing", "to_status_key": "qa_approved", "allowed_role": "qa_engineer"},
            {"from_status_key": "testing", "to_status_key": "in_progress", "allowed_role": "qa_engineer"},
            {"from_status_key": "qa_approved", "to_status_key": "done", "allowed_role": "business_analyst"},
            {"from_status_key": "qa_approved", "to_status_key": "uat", "allowed_role": "business_analyst"},
            {"from_status_key": "uat", "to_status_key": "done", "allowed_role": "business_analyst"},
            {"from_status_key": "qa_approved", "to_status_key": "in_progress", "allowed_role": "business_analyst"},
        ]
        for dr in default_rules:
            db.add(WorkflowTransitionRule(**dr))

        await db.commit()

    print("✅ Seed complete!\n")
    print("📋 Demo Accounts:")
    creds = [("admin","Admin@123","Super Admin"), ("pm.sara","Pass@123","Project Manager"),
             ("qa.meron","Pass@123","QA Engineer"), ("dev.yonas","Pass@123","Developer"),
             ("devops.abel","Pass@123","DevOps"), ("sec.hana","Pass@123","Security")]
    for u, p, r in creds:
        print(f"  {u:20s} / {p:12s}  ({r})")


asyncio.run(seed())
