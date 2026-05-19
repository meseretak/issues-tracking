from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone
import os
import uuid
from app.database import get_db
from app.models import (
    User, Issue, Project, Sprint, Label, ActivityLog, Attachment,
    IssuePriority, IssueType, UserRole, Notification, TimeLog,
    WorkflowTransitionRule
)
from app.schemas import IssueCreate, IssueUpdate
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/issues", tags=["Issues"])


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _generate_issue_key(project_id: int, db: AsyncSession) -> str:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    count_result = await db.execute(
        select(func.count(Issue.id)).where(Issue.project_id == project_id)
    )
    count = count_result.scalar() + 1
    return f"{project.key}-{count}"


async def _log_activity(db, user_id, issue_id, action, field=None, old_val=None, new_val=None):
    db.add(ActivityLog(
        action=action, field_changed=field,
        old_value=old_val, new_value=new_val,
        issue_id=issue_id, user_id=user_id,
    ))


async def _notify(db, user_id, issue_id, message, ntype="info"):
    db.add(Notification(user_id=user_id, issue_id=issue_id, message=message, type=ntype))


def _serialize_user(user):
    if not user:
        return None
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role.value if hasattr(user.role, 'value') else user.role,
        "department": user.department,
        "avatar_color": user.avatar_color,
    }


def _serialize_sprint(sprint):
    if not sprint:
        return None
    return {
        "id": sprint.id,
        "name": sprint.name,
        "status": sprint.status.value if hasattr(sprint.status, 'value') else sprint.status,
    }


def _build_issue_out(issue: Issue) -> dict:
    return {
        "id": issue.id,
        "key": issue.key,
        "title": issue.title,
        "description": issue.description,
        "issue_type": issue.issue_type.value if hasattr(issue.issue_type, 'value') else issue.issue_type,
        "status": issue.status.value if hasattr(issue.status, 'value') else issue.status,
        "priority": issue.priority.value if hasattr(issue.priority, 'value') else issue.priority,
        "story_points": issue.story_points or 0,
        "estimated_hours": issue.estimated_hours or 0,
        "logged_hours": issue.logged_hours or 0,
        "project_id": issue.project_id,
        "project_key": issue.project.key if issue.project else None,
        "reporter": _serialize_user(issue.reporter),
        "assignee": _serialize_user(issue.assignee),
        "sprint": _serialize_sprint(issue.sprint),
        "parent_id": issue.parent_id,
        "due_date": issue.due_date.isoformat() if issue.due_date else None,
        "resolved_at": issue.resolved_at.isoformat() if issue.resolved_at else None,
        "created_at": issue.created_at.isoformat() if issue.created_at else None,
        "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
        "comment_count": len(issue.comments) if issue.comments else 0,
        "labels": [{"id": l.id, "name": l.name, "color": l.color} for l in (issue.labels or [])],
    }


_ISSUE_OPTS = [
    selectinload(Issue.reporter),
    selectinload(Issue.assignee),
    selectinload(Issue.sprint),
    selectinload(Issue.project),
    selectinload(Issue.labels),
    selectinload(Issue.comments),
]


# ── List / Create ─────────────────────────────────────────────────────────────

@router.get("/", response_model=List[dict])
async def list_issues(
    project_id: Optional[int] = None,
    sprint_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    reporter_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[IssuePriority] = None,
    issue_type: Optional[IssueType] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(Issue).options(*_ISSUE_OPTS).order_by(desc(Issue.created_at))
    filters = []
    if project_id:  filters.append(Issue.project_id == project_id)
    if sprint_id:   filters.append(Issue.sprint_id == sprint_id)
    if assignee_id: filters.append(Issue.assignee_id == assignee_id)
    if reporter_id: filters.append(Issue.reporter_id == reporter_id)
    if status:      filters.append(Issue.status == status)
    if priority:    filters.append(Issue.priority == priority)
    if issue_type:  filters.append(Issue.issue_type == issue_type)
    if search:
        filters.append(or_(
            Issue.title.ilike(f"%{search}%"),
            Issue.key.ilike(f"%{search}%"),
            Issue.description.ilike(f"%{search}%"),
        ))
    if filters:
        query = query.where(and_(*filters))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return [_build_issue_out(i) for i in result.scalars().all()]


@router.post("/", response_model=dict, status_code=201)
async def create_issue(
    issue_data: IssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    key = await _generate_issue_key(issue_data.project_id, db)
    label_ids = issue_data.label_ids or []
    issue = Issue(**issue_data.model_dump(exclude={"label_ids"}), key=key, reporter_id=current_user.id)
    if label_ids:
        res = await db.execute(select(Label).where(Label.id.in_(label_ids)))
        issue.labels = res.scalars().all()
    db.add(issue)
    await db.flush()
    await _log_activity(db, current_user.id, issue.id, "created_issue")
    if issue.assignee_id and issue.assignee_id != current_user.id:
        await _notify(db, issue.assignee_id, issue.id, f"You were assigned to {key}: {issue.title}")
    await db.commit()
    result = await db.execute(select(Issue).options(*_ISSUE_OPTS).where(Issue.id == issue.id))
    return _build_issue_out(result.scalar_one())


# ── Single Issue ──────────────────────────────────────────────────────────────

@router.get("/{issue_id}", response_model=dict)
async def get_issue(
    issue_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Issue).options(
            *_ISSUE_OPTS,
            selectinload(Issue.watchers),
            selectinload(Issue.sub_issues),
        ).where(Issue.id == issue_id)
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return _build_issue_out(issue)


@router.put("/{issue_id}", response_model=dict)
async def update_issue(
    issue_id: int,
    issue_data: IssueUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Issue).options(*_ISSUE_OPTS).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue_data.status and issue_data.status != issue.status:
        new_status = issue_data.status
        old_status = issue.status
        role = current_user.role

        # Check assignee-based card transition for non-admins
        if role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.SCRUM_MASTER]:
            if issue.assignee_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="You are not assigned to this issue. Only the assigned developer/QA can transition this card."
                )

        # Super admin, admin, and project manager can always transition
        if role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.SCRUM_MASTER]:
            is_valid = True
        else:
            # Check dynamic workflow rules for the role
            role_val = role.value if hasattr(role, "value") else role
            rule = await db.execute(
                select(WorkflowTransitionRule).where(
                    WorkflowTransitionRule.from_status_key == old_status,
                    WorkflowTransitionRule.to_status_key == new_status,
                    WorkflowTransitionRule.allowed_role == role_val,
                )
            )
            is_valid = rule.scalar_one_or_none() is not None

        if not is_valid:
            role_val = role.value if hasattr(role, "value") else role
            raise HTTPException(
                status_code=403,
                detail=f"Role '{role_val}' cannot transition issue from '{old_status}' to '{new_status}'.",
            )

        # If moving to a terminal state, set resolved_at automatically
        if new_status in ["done", "closed", "cancelled"]:
            issue.resolved_at = datetime.now(timezone.utc)

    update_data = issue_data.model_dump(exclude_unset=True, exclude={"label_ids"})
    
    # Check assignee change permission
    if "assignee_id" in update_data and update_data["assignee_id"] != issue.assignee_id:
        role = current_user.role
        if role in [UserRole.DEVELOPER, UserRole.VIEWER]:
            raise HTTPException(
                status_code=403,
                detail="Developers and Viewers cannot assign issues. Only PMs, Scrum Masters, BAs, QA Engineers, and Admins can assign."
            )

    for field, new_value in update_data.items():
        old_value = getattr(issue, field)
        if old_value != new_value:
            await _log_activity(db, current_user.id, issue.id, f"updated_{field}", field,
                                 str(old_value) if old_value else None,
                                 str(new_value) if new_value else None)
            setattr(issue, field, new_value)

    if issue_data.status in ["done", "closed"]:
        issue.resolved_at = datetime.now(timezone.utc)

    if issue_data.label_ids is not None:
        res = await db.execute(select(Label).where(Label.id.in_(issue_data.label_ids)))
        issue.labels = res.scalars().all()

    if issue_data.assignee_id and issue_data.assignee_id != current_user.id:
        await _notify(db, issue_data.assignee_id, issue.id,
                      f"You were assigned to {issue.key}: {issue.title}")

    await db.commit()
    result = await db.execute(select(Issue).options(*_ISSUE_OPTS).where(Issue.id == issue_id))
    return _build_issue_out(result.scalar_one())


@router.delete("/{issue_id}")
async def delete_issue(
    issue_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        if issue.reporter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this issue")
    await db.delete(issue)
    await db.commit()
    return {"message": "Issue deleted"}


# ── Activity ──────────────────────────────────────────────────────────────────

@router.get("/{issue_id}/activity")
async def get_issue_activity(
    issue_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(ActivityLog)
        .options(selectinload(ActivityLog.user))
        .where(ActivityLog.issue_id == issue_id)
        .order_by(desc(ActivityLog.created_at))
    )
    return [
        {
            "id": log.id,
            "action": log.action,
            "field_changed": log.field_changed,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "user": {
                "id": log.user.id,
                "username": log.user.username,
                "full_name": log.user.full_name,
                "avatar_color": log.user.avatar_color,
            },
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in result.scalars().all()
    ]


# ── Time Tracking ─────────────────────────────────────────────────────────────

@router.post("/{issue_id}/time-logs")
async def log_time(
    issue_id: int,
    hours: float,
    description: str = "",
    work_date: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if hours <= 0:
        raise HTTPException(status_code=400, detail="Hours must be positive")

    work_dt = datetime.fromisoformat(work_date.replace('Z', '+00:00')) if work_date else datetime.now(timezone.utc)
    db.add(TimeLog(issue_id=issue_id, user_id=current_user.id, hours=hours,
                   description=description, work_date=work_dt))
    issue.logged_hours = (issue.logged_hours or 0) + hours
    await _log_activity(db, current_user.id, issue_id, "logged_time", "time_logged", None, f"{hours}h")
    await db.commit()
    return {"message": "Time logged successfully", "total_logged": issue.logged_hours}


@router.get("/{issue_id}/time-logs")
async def get_time_logs(
    issue_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(TimeLog).options(selectinload(TimeLog.user))
        .where(TimeLog.issue_id == issue_id)
        .order_by(desc(TimeLog.logged_at))
    )
    return [
        {
            "id": log.id,
            "hours": log.hours,
            "description": log.description,
            "work_date": log.work_date.isoformat() if log.work_date else None,
            "logged_at": log.logged_at.isoformat() if log.logged_at else None,
            "user": {"id": log.user.id, "full_name": log.user.full_name, "avatar_color": log.user.avatar_color},
        }
        for log in result.scalars().all()
    ]


# ── Attachments ───────────────────────────────────────────────────────────────

@router.post("/{issue_id}/attachments")
async def upload_attachment(
    issue_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Issue not found")

    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads"))
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "file")[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    contents = await file.read()
    with open(os.path.join(upload_dir, unique_name), "wb") as f:
        f.write(contents)

    att = Attachment(filename=file.filename, file_path=unique_name, file_size=len(contents),
                     mime_type=file.content_type, issue_id=issue_id, uploaded_by=current_user.id)
    db.add(att)
    await _log_activity(db, current_user.id, issue_id, "added_attachment", "attachment", None, file.filename)
    await db.commit()
    await db.refresh(att)
    return {"id": att.id, "filename": att.filename, "file_size": att.file_size,
            "mime_type": att.mime_type, "created_at": att.created_at.isoformat() if att.created_at else None}


@router.get("/{issue_id}/attachments")
async def get_attachments(
    issue_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Attachment).options(selectinload(Attachment.uploader))
        .where(Attachment.issue_id == issue_id)
        .order_by(desc(Attachment.created_at))
    )
    return [
        {
            "id": att.id, "filename": att.filename, "file_size": att.file_size,
            "mime_type": att.mime_type,
            "created_at": att.created_at.isoformat() if att.created_at else None,
            "uploader": {"id": att.uploader.id, "full_name": att.uploader.full_name},
        }
        for att in result.scalars().all()
    ]
