from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models import (
    User, Issue, Project, Sprint, ActivityLog,
    IssuePriority, IssueType, SprintStatus
)
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    project_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    base_filter = []
    if project_id:
        base_filter.append(Issue.project_id == project_id)

    # Total issues
    total = await db.execute(
        select(func.count(Issue.id)).where(*base_filter) if base_filter
        else select(func.count(Issue.id))
    )

    # Open issues (not done/closed/cancelled)
    open_filter = base_filter + [
        Issue.status.not_in(["done", "closed", "cancelled"])
    ]
    open_issues = await db.execute(select(func.count(Issue.id)).where(*open_filter))

    # In progress
    ip_filter = base_filter + [Issue.status == "in_progress"]
    in_progress = await db.execute(select(func.count(Issue.id)).where(*ip_filter))

    # Resolved today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_filter = base_filter + [
        Issue.resolved_at >= today_start,
        Issue.status.in_(["done", "closed"])
    ]
    resolved_today = await db.execute(select(func.count(Issue.id)).where(*resolved_filter))

    # Overdue
    now = datetime.now(timezone.utc)
    overdue_filter = base_filter + [
        Issue.due_date < now,
        Issue.status.not_in(["done", "closed", "cancelled"])
    ]
    overdue = await db.execute(select(func.count(Issue.id)).where(*overdue_filter))

    # By status
    status_q = select(Issue.status, func.count(Issue.id)).group_by(Issue.status)
    if base_filter:
        status_q = status_q.where(*base_filter)
    status_result = await db.execute(status_q)
    by_status = {getattr(row[0], "value", row[0]): row[1] for row in status_result.all()}

    # By priority
    priority_q = select(Issue.priority, func.count(Issue.id)).group_by(Issue.priority)
    if base_filter:
        priority_q = priority_q.where(*base_filter)
    priority_result = await db.execute(priority_q)
    by_priority = {getattr(row[0], "value", row[0]): row[1] for row in priority_result.all()}

    # By type
    type_q = select(Issue.issue_type, func.count(Issue.id)).group_by(Issue.issue_type)
    if base_filter:
        type_q = type_q.where(*base_filter)
    type_result = await db.execute(type_q)
    by_type = {getattr(row[0], "value", row[0]): row[1] for row in type_result.all()}

    # By assignee (top 10)
    assignee_q = (
        select(User.full_name, User.avatar_color, func.count(Issue.id).label("count"))
        .join(Issue, Issue.assignee_id == User.id)
        .group_by(User.id, User.full_name, User.avatar_color)
        .order_by(desc("count"))
        .limit(10)
    )
    if base_filter:
        assignee_q = assignee_q.where(*base_filter)
    assignee_result = await db.execute(assignee_q)
    by_assignee = [
        {"name": row[0], "color": row[1], "count": row[2]}
        for row in assignee_result.all()
    ]

    # Recent activity (last 20)
    activity_result = await db.execute(
        select(ActivityLog)
        .options(selectinload(ActivityLog.user))
        .order_by(desc(ActivityLog.created_at))
        .limit(20)
    )
    activities = activity_result.scalars().all()
    recent_activity = [
        {
            "id": a.id,
            "action": a.action,
            "field_changed": a.field_changed,
            "old_value": a.old_value,
            "new_value": a.new_value,
            "issue_id": a.issue_id,
            "user": {
                "id": a.user.id,
                "full_name": a.user.full_name,
                "avatar_color": a.user.avatar_color,
            },
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in activities
    ]

    # Active sprint progress
    sprint_progress = None
    sprint_q = select(Sprint).where(Sprint.status == SprintStatus.ACTIVE)
    if project_id:
        sprint_q = sprint_q.where(Sprint.project_id == project_id)
    sprint_result = await db.execute(sprint_q.limit(1))
    active_sprint = sprint_result.scalar_one_or_none()
    if active_sprint:
        total_sp = await db.execute(
            select(func.count(Issue.id)).where(Issue.sprint_id == active_sprint.id)
        )
        done_sp = await db.execute(
            select(func.count(Issue.id)).where(
                Issue.sprint_id == active_sprint.id,
                Issue.status.in_(["done", "closed"])
            )
        )
        t = total_sp.scalar() or 0
        d = done_sp.scalar() or 0
        days_remaining = None
        if active_sprint.end_date:
            now_utc = datetime.now(timezone.utc)
            # Make end_date aware if it's naive
            end_date_aware = active_sprint.end_date.replace(tzinfo=timezone.utc) if active_sprint.end_date.tzinfo is None else active_sprint.end_date
            delta = end_date_aware - now_utc
            days_remaining = max(0, delta.days)
        sprint_progress = {
            "id": active_sprint.id,
            "name": active_sprint.name,
            "total": t,
            "done": d,
            "percent": round((d / t * 100) if t > 0 else 0, 1),
            "start_date": active_sprint.start_date.isoformat() if active_sprint.start_date else None,
            "end_date": active_sprint.end_date.isoformat() if active_sprint.end_date else None,
            "days_remaining": days_remaining,
        }

    # Velocity trend (last 5 completed sprints)
    velocity_result = await db.execute(
        select(Sprint)
        .where(Sprint.status == SprintStatus.COMPLETED)
        .order_by(desc(Sprint.created_at))
        .limit(5)
    )
    completed_sprints = velocity_result.scalars().all()
    velocity_trend = []
    for sp in reversed(completed_sprints):
        pts = await db.execute(
            select(func.sum(Issue.story_points)).where(
                Issue.sprint_id == sp.id,
                Issue.status.in_(["done", "closed"])
            )
        )
        velocity_trend.append({
            "sprint": sp.name,
            "points": pts.scalar() or 0,
        })

    # Issues created per day (last 14 days)
    daily_trend = []
    for i in range(13, -1, -1):
        day = datetime.now(timezone.utc) - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count_q = select(func.count(Issue.id)).where(
            Issue.created_at >= day_start,
            Issue.created_at < day_end,
        )
        if base_filter:
            count_q = count_q.where(*base_filter)
        cnt = await db.execute(count_q)
        daily_trend.append({
            "date": day_start.strftime("%b %d"),
            "count": cnt.scalar() or 0,
        })

    return {
        "total_issues": total.scalar(),
        "open_issues": open_issues.scalar(),
        "in_progress": in_progress.scalar(),
        "resolved_today": resolved_today.scalar(),
        "overdue": overdue.scalar(),
        "by_status": by_status,
        "by_priority": by_priority,
        "by_type": by_type,
        "by_assignee": by_assignee,
        "recent_activity": recent_activity,
        "sprint_progress": sprint_progress,
        "velocity_trend": velocity_trend,
        "daily_trend": daily_trend,
    }


@router.get("/projects/summary")
async def get_projects_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.models import UserRole, ProjectMember
    query = select(Project).where(Project.status == "active")
    if current_user.role in [UserRole.DEVELOPER, UserRole.VIEWER]:
        query = query.join(ProjectMember).where(ProjectMember.user_id == current_user.id)
    result = await db.execute(query)
    projects = result.scalars().all()
    out = []
    for p in projects:
        total = await db.execute(select(func.count(Issue.id)).where(Issue.project_id == p.id))
        open_c = await db.execute(
            select(func.count(Issue.id)).where(
                Issue.project_id == p.id,
                Issue.status.not_in(["done", "closed", "cancelled"])
            )
        )
        done_c = await db.execute(
            select(func.count(Issue.id)).where(
                Issue.project_id == p.id,
                Issue.status.in_(["done", "closed"])
            )
        )
        progress_c = await db.execute(
            select(func.count(Issue.id)).where(
                Issue.project_id == p.id,
                Issue.status.in_(["in_progress", "testing", "in_review", "uat", "qa_approved"])
            )
        )
        todo_c = await db.execute(
            select(func.count(Issue.id)).where(
                Issue.project_id == p.id,
                Issue.status.in_(["todo", "backlog"])
            )
        )
        out.append({
            "id": p.id,
            "key": p.key,
            "name": p.name,
            "color": p.color,
            "department": p.department,
            "project_type": getattr(p, "project_type", "scrum"),
            "total_issues": total.scalar(),
            "open_issues": open_c.scalar(),
            "done_issues": done_c.scalar(),
            "progress_issues": progress_c.scalar(),
            "todo_issues": todo_c.scalar(),
        })
    return out


@router.get("/developer-stats")
async def get_developer_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Developer-specific dashboard stats: assigned, fixed, pending issues."""
    total_assigned = await db.execute(
        select(func.count(Issue.id)).where(Issue.assignee_id == current_user.id)
    )
    fixed = await db.execute(
        select(func.count(Issue.id)).where(
            Issue.assignee_id == current_user.id,
            Issue.status.in_(["done", "closed"])
        )
    )
    in_progress = await db.execute(
        select(func.count(Issue.id)).where(
            Issue.assignee_id == current_user.id,
            Issue.status.in_(["in_progress", "testing", "in_review", "uat", "qa_approved"])
        )
    )
    pending = await db.execute(
        select(func.count(Issue.id)).where(
            Issue.assignee_id == current_user.id,
            Issue.status.in_(["todo", "backlog"])
        )
    )
    # Top 10 issues assigned to this developer
    my_issues_result = await db.execute(
        select(Issue)
        .options(selectinload(Issue.project))
        .where(Issue.assignee_id == current_user.id)
        .order_by(desc(Issue.updated_at))
        .limit(20)
    )
    my_issues = my_issues_result.scalars().all()
    issues_data = [
        {
            "id": i.id,
            "key": i.key,
            "title": i.title,
            "status": getattr(i.status, "value", i.status),
            "priority": getattr(i.priority, "value", i.priority),
            "issue_type": getattr(i.issue_type, "value", i.issue_type),
            "project_key": i.project.key if i.project else "-",
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
            "due_date": i.due_date.isoformat() if i.due_date else None,
        }
        for i in my_issues
    ]
    return {
        "total_assigned": total_assigned.scalar() or 0,
        "fixed": fixed.scalar() or 0,
        "in_progress": in_progress.scalar() or 0,
        "pending": pending.scalar() or 0,
        "issues": issues_data,
    }
