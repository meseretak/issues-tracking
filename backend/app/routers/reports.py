from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from io import StringIO
import csv
from app.database import get_db
from app.models import User, Issue, Sprint
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/export/csv")
async def export_issues_csv(
    project_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export issues to CSV"""
    query = (
        select(Issue)
        .options(
            selectinload(Issue.reporter),
            selectinload(Issue.assignee),
            selectinload(Issue.project),
            selectinload(Issue.sprint),
        )
    )
    if project_id:
        query = query.where(Issue.project_id == project_id)

    result = await db.execute(query)
    issues = result.scalars().all()

    # Build CSV in memory using StringIO
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Key', 'Title', 'Type', 'Status', 'Priority', 'Project',
        'Reporter', 'Assignee', 'Sprint', 'Story Points',
        'Estimated Hours', 'Logged Hours', 'Due Date', 'Created', 'Updated'
    ])

    for issue in issues:
        writer.writerow([
            issue.key,
            issue.title,
            issue.issue_type.value if hasattr(issue.issue_type, 'value') else issue.issue_type,
            issue.status.value if hasattr(issue.status, 'value') else issue.status,
            issue.priority.value if hasattr(issue.priority, 'value') else issue.priority,
            issue.project.name if issue.project else '',
            issue.reporter.full_name if issue.reporter else '',
            issue.assignee.full_name if issue.assignee else '',
            issue.sprint.name if issue.sprint else '',
            issue.story_points or 0,
            issue.estimated_hours or 0,
            issue.logged_hours or 0,
            issue.due_date.strftime('%Y-%m-%d') if issue.due_date else '',
            issue.created_at.strftime('%Y-%m-%d %H:%M') if issue.created_at else '',
            issue.updated_at.strftime('%Y-%m-%d %H:%M') if issue.updated_at else '',
        ])

    csv_content = '\ufeff' + output.getvalue()  # UTF-8 BOM for Excel

    filename = f"issues_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/burndown/{sprint_id}")
async def get_burndown_data(
    sprint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get burndown chart data for a sprint"""
    result = await db.execute(
        select(Sprint)
        .options(selectinload(Sprint.issues))
        .where(Sprint.id == sprint_id)
    )
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    if not sprint.start_date or not sprint.end_date:
        return JSONResponse({"error": "Sprint dates not set"})

    total_points = sum(issue.story_points or 0 for issue in sprint.issues)

    completed_issues = [
        issue for issue in sprint.issues
        if (issue.status.value if hasattr(issue.status, 'value') else issue.status) in ['done', 'closed'] and issue.resolved_at
    ]

    current_date = sprint.start_date.date()
    end_date = sprint.end_date.date()
    total_days = max(1, (end_date - current_date).days)

    burndown_data = []
    remaining_points = total_points
    day = 0

    while current_date <= end_date:
        completed_on_date = sum(
            issue.story_points or 0
            for issue in completed_issues
            if issue.resolved_at and issue.resolved_at.date() == current_date
        )
        remaining_points -= completed_on_date

        burndown_data.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "remaining": max(0, remaining_points),
            "ideal": round(total_points * (1 - day / total_days), 1)
        })

        current_date += timedelta(days=1)
        day += 1

    return {
        "sprint_name": sprint.name,
        "total_points": total_points,
        "data": burndown_data
    }


@router.get("/velocity")
async def get_velocity_data(
    project_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get sprint velocity data"""
    query = select(Sprint).options(selectinload(Sprint.issues))
    if project_id:
        query = query.where(Sprint.project_id == project_id)
    query = query.where(Sprint.status == 'completed').order_by(Sprint.end_date)

    result = await db.execute(query)
    sprints = result.scalars().all()

    velocity_data = []
    for sprint in sprints:
        completed_points = sum(
            issue.story_points or 0
            for issue in sprint.issues
            if (issue.status.value if hasattr(issue.status, 'value') else issue.status) in ['done', 'closed']
        )
        total_points = sum(issue.story_points or 0 for issue in sprint.issues)
        velocity_data.append({
            "sprint": sprint.name,
            "completed": completed_points,
            "committed": total_points,
        })

    return velocity_data
