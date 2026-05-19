from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List
from app.database import get_db
from app.models import User, ChatMessage
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.get("/", response_model=List[dict])
async def get_chat_messages(
    team_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(ChatMessage).options(selectinload(ChatMessage.user)).order_by(ChatMessage.created_at.asc())
    if team_id and team_id > 0:
        query = query.where(ChatMessage.team_id == team_id)
    else:
        query = query.where(ChatMessage.team_id == None)
        
    result = await db.execute(query.limit(100))
    messages = result.scalars().all()
    return [
        {
            "id": msg.id,
            "message": msg.message,
            "team_id": msg.team_id,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
            "user": {
                "id": msg.user.id,
                "username": msg.user.username,
                "full_name": msg.user.full_name,
                "avatar_color": msg.user.avatar_color,
                "role": msg.user.role.value if hasattr(msg.user.role, "value") else msg.user.role,
            }
        }
        for msg in messages
    ]


@router.post("/", response_model=dict, status_code=201)
async def post_chat_message(
    message: str,
    team_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Handle team_id=0 or none
    actual_team_id = team_id if (team_id and team_id > 0) else None
    msg = ChatMessage(user_id=current_user.id, team_id=actual_team_id, message=message.strip())
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    
    result = await db.execute(
        select(ChatMessage)
        .options(selectinload(ChatMessage.user))
        .where(ChatMessage.id == msg.id)
    )
    msg_full = result.scalar_one()
    
    return {
        "id": msg_full.id,
        "message": msg_full.message,
        "team_id": msg_full.team_id,
        "created_at": msg_full.created_at.isoformat() if msg_full.created_at else None,
        "user": {
            "id": msg_full.user.id,
            "username": msg_full.user.username,
            "full_name": msg_full.user.full_name,
            "avatar_color": msg_full.user.avatar_color,
            "role": msg_full.user.role.value if hasattr(msg_full.user.role, "value") else msg_full.user.role,
        }
    }
