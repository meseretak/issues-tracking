from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.database import get_db
from app.models import User, UserRole, Issue
from app.schemas import UserOut, UserUpdate, UserSummary
from app.auth import get_current_active_user, require_admin, get_password_hash
from app.config import settings

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/", response_model=List[UserOut])
async def list_users(
    role: Optional[UserRole] = None,
    department: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(User)
    if role:
        query = query.where(User.role == role)
    if department:
        query = query.where(User.department == department)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    query = query.order_by(User.full_name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/departments", response_model=List[str])
async def get_departments(current_user: User = Depends(get_current_active_user)):
    return settings.DEPARTMENTS


@router.get("/roles", response_model=List[dict])
async def get_roles(current_user: User = Depends(get_current_active_user)):
    return [
        {"value": r.value, "label": r.value.replace("_", " ").title()}
        for r in UserRole
    ]


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Only admin or self can update
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only admin can change roles
    if user_data.role and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can change roles")

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Soft delete
    user.is_active = False
    await db.commit()
    return {"message": f"User {user.username} deactivated"}


@router.get("/{user_id}/stats")
async def get_user_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.models import IssueStatus
    result = await db.execute(
        select(Issue.status, func.count(Issue.id))
        .where(Issue.assignee_id == user_id)
        .group_by(Issue.status)
    )
    by_status = {row[0].value: row[1] for row in result.all()}

    total = await db.execute(
        select(func.count(Issue.id)).where(Issue.assignee_id == user_id)
    )
    reported = await db.execute(
        select(func.count(Issue.id)).where(Issue.reporter_id == user_id)
    )
    return {
        "assigned_issues": total.scalar(),
        "reported_issues": reported.scalar(),
        "by_status": by_status,
    }
