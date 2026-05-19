from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.database import get_db
from app.models import User, Issue, Comment, UserRole
from app.schemas import CommentCreate, CommentOut
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/issues/{issue_id}/comments", tags=["Comments"])


@router.get("", response_model=List[CommentOut])
async def list_comments(
    issue_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.issue_id == issue_id)
        .order_by(Comment.created_at)
    )
    comments = result.scalars().all()

    # Filter internal notes for non-privileged users
    if current_user.role in [UserRole.VIEWER]:
        comments = [c for c in comments if not c.is_internal]

    return comments


@router.post("", response_model=CommentOut, status_code=201)
async def create_comment(
    issue_id: int,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Verify issue exists
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Issue not found")

    comment = Comment(
        content=comment_data.content,
        issue_id=issue_id,
        author_id=current_user.id,
        is_internal=comment_data.is_internal,
    )
    db.add(comment)
    await db.commit()

    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.id == comment.id)
    )
    return result.scalar_one()


@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment(
    issue_id: int,
    comment_id: int,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.id == comment_id, Comment.issue_id == issue_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")

    comment.content = comment_data.content
    comment.is_internal = comment_data.is_internal
    await db.commit()
    await db.refresh(comment)
    return comment


@router.delete("/{comment_id}")
async def delete_comment(
    issue_id: int,
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.issue_id == issue_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await db.delete(comment)
    await db.commit()
    return {"message": "Comment deleted"}
