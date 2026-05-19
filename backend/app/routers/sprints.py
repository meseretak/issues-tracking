from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database import get_db
from app.models import User, Sprint, Issue, SprintStatus, UserRole
from app.schemas import SprintCreate, SprintUpdate, SprintOut
from app.auth import get_current_active_user, require_roles

router = APIRouter(prefix="/api/sprints", tags=["Sprints"])


@router.get("/", response_model=List[dict])
async def list_sprints(
    project_id: Optional[int] = None,
    status: Optional[SprintStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(Sprint)
    if project_id:
        query = query.where(Sprint.project_id == project_id)
    if status:
        query = query.where(Sprint.status == status)
    query = query.order_by(Sprint.created_at.desc())
    result = await db.execute(query)
    sprints = result.scalars().all()

    out = []
    for sprint in sprints:
        count = await db.execute(
            select(func.count(Issue.id)).where(Issue.sprint_id == sprint.id)
        )
        done_count = await db.execute(
            select(func.count(Issue.id)).where(
                Issue.sprint_id == sprint.id,
                Issue.status.in_(["done", "closed"])
            )
        )
        d = SprintOut.model_validate(sprint).model_dump()
        d["issue_count"] = count.scalar()
        d["done_count"] = done_count.scalar()
        out.append(d)
    return out


@router.post("/", response_model=dict, status_code=201)
async def create_sprint(
    sprint_data: SprintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.DEVELOPER)
    ),
):
    sprint = Sprint(**sprint_data.model_dump())
    db.add(sprint)
    await db.commit()
    await db.refresh(sprint)
    d = SprintOut.model_validate(sprint).model_dump()
    d["issue_count"] = 0
    d["done_count"] = 0
    return d


@router.get("/{sprint_id}", response_model=dict)
async def get_sprint(
    sprint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    count = await db.execute(
        select(func.count(Issue.id)).where(Issue.sprint_id == sprint_id)
    )
    done_count = await db.execute(
        select(func.count(Issue.id)).where(
            Issue.sprint_id == sprint_id,
            Issue.status.in_(["done", "closed"])
        )
    )
    d = SprintOut.model_validate(sprint).model_dump()
    d["issue_count"] = count.scalar()
    d["done_count"] = done_count.scalar()
    return d


@router.put("/{sprint_id}", response_model=dict)
async def update_sprint(
    sprint_id: int,
    sprint_data: SprintUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.DEVELOPER)
    ),
):
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    for field, value in sprint_data.model_dump(exclude_unset=True).items():
        setattr(sprint, field, value)

    await db.commit()
    await db.refresh(sprint)
    d = SprintOut.model_validate(sprint).model_dump()
    return d


@router.get("/{sprint_id}/board")
async def get_sprint_board(
    sprint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Returns issues grouped by status for Kanban board view."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Issue)
        .options(
            selectinload(Issue.assignee),
            selectinload(Issue.reporter),
            selectinload(Issue.labels),
        )
        .where(Issue.sprint_id == sprint_id)
        .order_by(Issue.priority)
    )
    issues = result.scalars().all()

    from app.models import WorkflowStatus
    res_statuses = await db.execute(select(WorkflowStatus))
    workflow_statuses = res_statuses.scalars().all()
    status_keys = [ws.key for ws in workflow_statuses] if workflow_statuses else ["backlog", "todo", "in_progress", "in_review", "testing", "done"]
    
    board = {key: [] for key in status_keys}
    for issue in issues:
        status_val = issue.status.value if hasattr(issue.status, 'value') else issue.status
        if status_val not in board:
            board[status_val] = []
        board[status_val].append({
            "id": issue.id,
            "key": issue.key,
            "title": issue.title,
            "issue_type": issue.issue_type.value if hasattr(issue.issue_type, 'value') else issue.issue_type,
            "priority": issue.priority.value if hasattr(issue.priority, 'value') else issue.priority,
            "story_points": issue.story_points,
            "assignee": {
                "id": issue.assignee.id,
                "full_name": issue.assignee.full_name,
                "avatar_color": issue.assignee.avatar_color,
            } if issue.assignee else None,
            "labels": [{"id": l.id, "name": l.name, "color": l.color} for l in issue.labels],
        })
    return board


@router.post("/{sprint_id}/issues/{issue_id}")
async def add_issue_to_sprint(
    sprint_id: int,
    issue_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add an issue to a sprint (drag from backlog to sprint)"""
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    result2 = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result2.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.sprint_id = sprint_id
    # Move from backlog to todo when added to sprint
    if issue.status == "backlog":
        issue.status = "todo"

    await db.commit()
    return {"message": f"Issue {issue.key} added to sprint {sprint.name}"}


@router.delete("/{sprint_id}/issues/{issue_id}")
async def remove_issue_from_sprint(
    sprint_id: int,
    issue_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove an issue from a sprint (send back to backlog)"""
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.sprint_id = None
    issue.status = "backlog"
    await db.commit()
    return {"message": f"Issue {issue.key} moved back to backlog"}


@router.post("/{sprint_id}/start")
async def start_sprint(
    sprint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
):
    """Start a planned sprint"""
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    if sprint.status != SprintStatus.PLANNED:
        raise HTTPException(status_code=400, detail="Only planned sprints can be started")
    sprint.status = SprintStatus.ACTIVE
    await db.commit()
    return {"message": f"Sprint '{sprint.name}' started"}


@router.post("/{sprint_id}/complete")
async def complete_sprint(
    sprint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
):
    """Complete an active sprint"""
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    if sprint.status != SprintStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Only active sprints can be completed")
    sprint.status = SprintStatus.COMPLETED
    # Move incomplete issues back to backlog
    result2 = await db.execute(
        select(Issue).where(
            Issue.sprint_id == sprint_id,
            Issue.status.not_in(["done", "closed", "cancelled"])
        )
    )
    incomplete = result2.scalars().all()
    for issue in incomplete:
        issue.sprint_id = None
        issue.status = "backlog"
    await db.commit()
    return {"message": f"Sprint '{sprint.name}' completed. {len(incomplete)} issues moved back to backlog."}


@router.delete("/{sprint_id}")
async def delete_sprint(
    sprint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
):
    """Delete a sprint and send its issues back to backlog"""
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Send issues back to backlog
    result2 = await db.execute(
        select(Issue).where(Issue.sprint_id == sprint_id)
    )
    issues = result2.scalars().all()
    for issue in issues:
        issue.sprint_id = None
        issue.status = "backlog"
        
    await db.delete(sprint)
    await db.commit()
    return {"message": f"Sprint '{sprint.name}' deleted successfully"}

