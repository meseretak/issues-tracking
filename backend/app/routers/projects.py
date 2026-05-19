from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database import get_db
from app.models import User, Project, ProjectMember, Issue, UserRole
from app.schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.auth import get_current_active_user, require_roles

router = APIRouter(prefix="/api/projects", tags=["Projects"])


async def _enrich_project(project: Project, db: AsyncSession) -> dict:
    issue_count = await db.execute(
        select(func.count(Issue.id)).where(Issue.project_id == project.id)
    )
    member_count = await db.execute(
        select(func.count(ProjectMember.id)).where(ProjectMember.project_id == project.id)
    )
    data = {
        "id": project.id,
        "key": project.key,
        "name": project.name,
        "description": project.description,
        "department": project.department,
        "status": project.status,
        "color": project.color,
        "project_type": getattr(project, "project_type", "scrum"),
        "category": getattr(project, "category", "Software"),
        "url": getattr(project, "url", None),
        "created_at": project.created_at,
        "lead": None,
        "issue_count": issue_count.scalar(),
        "member_count": member_count.scalar(),
    }
    if project.lead:
        data["lead"] = {
            "id": project.lead.id,
            "username": project.lead.username,
            "full_name": project.lead.full_name,
            "role": project.lead.role,
            "department": project.lead.department,
            "avatar_color": project.lead.avatar_color,
        }
    return data


async def _load_project(project_id: int, db: AsyncSession):
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.lead))
        .where(Project.id == project_id)
    )
    return result.scalar_one_or_none()


@router.get("/", response_model=List[dict])
async def list_projects(
    department: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(Project).options(selectinload(Project.lead))
    if department:
        query = query.where(Project.department == department)
    if status:
        query = query.where(Project.status == status)

    if current_user.role in [UserRole.DEVELOPER, UserRole.VIEWER]:
        query = query.join(ProjectMember).where(ProjectMember.user_id == current_user.id)

    query = query.order_by(Project.name)
    result = await db.execute(query)
    projects = result.scalars().all()
    return [await _enrich_project(p, db) for p in projects]


@router.post("/", response_model=dict, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.QA_ENGINEER)),
):
    result = await db.execute(select(Project).where(Project.key == project_data.key))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Project key '{project_data.key}' already exists")

    project = Project(**project_data.model_dump())
    db.add(project)
    await db.flush()

    member = ProjectMember(project_id=project.id, user_id=current_user.id, role=current_user.role)
    db.add(member)
    await db.commit()

    project = await _load_project(project.id, db)
    return await _enrich_project(project, db)


@router.get("/{project_id}", response_model=dict)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    project = await _load_project(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await _enrich_project(project, db)


@router.put("/{project_id}", response_model=dict)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    project = await _load_project(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        if project.lead_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this project")

    for field, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    await db.commit()
    project = await _load_project(project_id, db)
    return await _enrich_project(project, db)


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.status = "archived"
    await db.commit()
    return {"message": "Project archived"}


@router.get("/{project_id}/members")
async def get_project_members(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(ProjectMember, User)
        .join(User, ProjectMember.user_id == User.id)
        .where(ProjectMember.project_id == project_id)
    )
    rows = result.all()
    return [
        {
            "id": pm.id,
            "user_id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "role": pm.role.value,
            "department": u.department,
            "avatar_color": u.avatar_color,
            "joined_at": pm.joined_at,
        }
        for pm, u in rows
    ]


@router.post("/{project_id}/members")
async def add_project_member(
    project_id: int,
    user_id: int,
    role: UserRole = UserRole.VIEWER,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PROJECT_MANAGER)),
):
    # Check project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    # Check user exists
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")

    # Check not already member
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member")

    member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(member)
    await db.commit()
    return {"message": "Member added successfully"}
