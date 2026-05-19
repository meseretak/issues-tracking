from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database import get_db
from app.models import User, Team, UserRole, Issue
from app.auth import get_current_active_user, require_roles

router = APIRouter(prefix="/api/teams", tags=["Teams"])


def _ser_user(u):
    return {"id": u.id, "username": u.username, "full_name": u.full_name,
            "role": u.role.value, "department": u.department,
            "avatar_color": u.avatar_color, "email": u.email, "is_active": u.is_active}


@router.get("/", response_model=List[dict])
async def list_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Team).options(selectinload(Team.members), selectinload(Team.lead))
    )
    teams = result.scalars().all()
    return [
        {
            "id": t.id, "name": t.name, "description": t.description,
            "team_type": t.team_type, "color": t.color,
            "lead": _ser_user(t.lead) if t.lead else None,
            "member_count": len(t.members),
            "members": [_ser_user(m) for m in t.members],
        }
        for t in teams
    ]


@router.post("/", response_model=dict, status_code=201)
async def create_team(
    name: str, team_type: str, description: str = "", color: str = "#1B1F6B",
    lead_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER)),
):
    team = Team(name=name, team_type=team_type, description=description,
                color=color, lead_id=lead_id)
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return {"id": team.id, "name": team.name, "team_type": team.team_type,
            "color": team.color, "member_count": 0, "members": []}


@router.post("/{team_id}/members/{user_id}")
async def add_member(
    team_id: int, user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER)),
):
    result = await db.execute(select(Team).options(selectinload(Team.members)).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(404, "Team not found")
    result2 = await db.execute(select(User).where(User.id == user_id))
    user = result2.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    if user not in team.members:
        team.members.append(user)
        await db.commit()
    return {"message": "Member added"}


@router.delete("/{team_id}/members/{user_id}")
async def remove_member(
    team_id: int, user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER)),
):
    result = await db.execute(select(Team).options(selectinload(Team.members)).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(404, "Team not found")
    team.members = [m for m in team.members if m.id != user_id]
    await db.commit()
    return {"message": "Member removed"}


@router.put("/{team_id}")
async def update_team(
    team_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    color: Optional[str] = None,
    lead_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER)),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(404, "Team not found")
    if name is not None:
        team.name = name
    if description is not None:
        team.description = description
    if color is not None:
        team.color = color
    if lead_id is not None:
        team.lead_id = lead_id
    await db.commit()
    return {"message": "Team updated successfully"}

