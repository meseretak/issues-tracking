from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
from app.database import get_db
from app.models import User, WorkflowStatus, WorkflowTransitionRule, UserRole
from app.auth import get_current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/workflow", tags=["Workflow"])

class WorkflowStatusCreate(BaseModel):
    name: str
    key: str
    color: str = "#0052CC"
    category: str = "todo"
    order_index: int = 0

class WorkflowStatusOut(WorkflowStatusCreate):
    id: int
    model_config = {"from_attributes": True}

class WorkflowRuleCreate(BaseModel):
    from_status_key: str
    to_status_key: str
    allowed_role: str

class WorkflowRuleOut(WorkflowRuleCreate):
    id: int
    model_config = {"from_attributes": True}

@router.get("/statuses", response_model=List[WorkflowStatusOut])
async def get_statuses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkflowStatus).order_by(WorkflowStatus.order_index))
    return result.scalars().all()

@router.post("/statuses", response_model=WorkflowStatusOut)
async def create_status(status_data: WorkflowStatusCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if exists
    res = await db.execute(select(WorkflowStatus).where(WorkflowStatus.key == status_data.key))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Status key already exists")
        
    status = WorkflowStatus(**status_data.model_dump())
    db.add(status)
    await db.commit()
    await db.refresh(status)
    return status

@router.delete("/statuses/{status_id}")
async def delete_status(status_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    res = await db.execute(select(WorkflowStatus).where(WorkflowStatus.id == status_id))
    status = res.scalar_one_or_none()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    await db.delete(status)
    await db.commit()
    return {"message": "Deleted"}

@router.get("/rules", response_model=List[WorkflowRuleOut])
async def get_rules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkflowTransitionRule))
    return result.scalars().all()

@router.post("/rules", response_model=WorkflowRuleOut)
async def create_rule(rule_data: WorkflowRuleCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    rule = WorkflowTransitionRule(**rule_data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    res = await db.execute(select(WorkflowTransitionRule).where(WorkflowTransitionRule.id == rule_id))
    rule = res.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    await db.commit()
    return {"message": "Deleted"}
