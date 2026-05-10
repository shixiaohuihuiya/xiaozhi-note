"""
评论路由
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from database import get_db
from models import Comment, Article, User
from pydantic import BaseModel, Field
from schemas.common import ResponseModel, PaginatedResponse, PaginationParams
from dependencies import get_current_active_user

router = APIRouter()


def build_comment_tree(comments_list):
    """将扁平评论列表构建为嵌套树"""
    comment_map = {}
    roots = []
    
    for c in comments_list:
        comment_map[c["id"]] = {**c, "replies": []}
    
    for c in comments_list:
        node = comment_map[c["id"]]
        if c.get("parent_id"):
            parent = comment_map.get(c["parent_id"])
            if parent:
                parent["replies"].append(node)
            else:
                roots.append(node)
        else:
            roots.append(node)
    
    return roots


@router.get("/articles/{article_id}/comments", response_model=ResponseModel[dict])
async def get_article_comments(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取文章评论列表（嵌套结构）"""
    # 查询所有已通过审核的评论
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(
            Comment.article_id == article_id,
            Comment.status == 1
        )
        .order_by(Comment.created_at)
    )
    all_comments = result.scalars().all()
    
    # 构建扁平列表
    flat_list = []
    for c in all_comments:
        flat_list.append({
            "id": c.id,
            "content": c.content,
            "parent_id": c.parent_id,
            "user": {
                "id": c.user.id,
                "username": c.user.username,
                "nickname": c.user.nickname,
                "avatar": c.user.avatar
            } if c.user else None,
            "like_count": c.like_count,
            "is_author": c.is_author,
            "created_at": c.created_at.isoformat()
        })
    
    # 构建嵌套树
    tree = build_comment_tree(flat_list)
    
    return ResponseModel(
        code=200,
        message="success",
        data={
            "items": tree,
            "total": len(flat_list)
        }
    )


class CommentCreate(BaseModel):
    """创建评论请求"""
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")
    parent_id: Optional[int] = Field(None, description="父评论ID")


@router.post("/articles/{article_id}/comments", response_model=ResponseModel[dict])
async def create_comment(
    article_id: int,
    comment_data: CommentCreate,
    request: Request = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """发表评论"""
    # 检查文章是否存在
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.status == 1)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查父评论是否存在
    if comment_data.parent_id:
        result = await db.execute(
            select(Comment).where(Comment.id == comment_data.parent_id, Comment.status == 1)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="回复的评论不存在"
            )
    
    # 检查是否是作者回复
    is_author = current_user.id == article.author_id
    
    # 创建评论
    comment = Comment(
        article_id=article_id,
        parent_id=comment_data.parent_id,
        user_id=current_user.id,
        content=comment_data.content,
        is_author=is_author,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        status=1  # 直接通过，如需审核可改为0
    )
    
    db.add(comment)
    
    # 发送通知给文章作者（如果不是自己评论自己的文章）
    if article.author_id != current_user.id:
        from models import Notification
        notify = Notification(
            user_id=article.author_id,
            type=3,
            title=f"{current_user.nickname or current_user.username} 评论了你的文章《{article.title}》",
            content=comment_data.content,
            related_id=comment.id
        )
        db.add(notify)
    
    # 发送通知给被回复的评论作者（如果不是回复自己）
    if comment_data.parent_id:
        from models import Notification
        parent_result = await db.execute(
            select(Comment).where(Comment.id == comment_data.parent_id)
        )
        parent_comment = parent_result.scalar_one_or_none()
        if parent_comment and parent_comment.user_id != current_user.id:
            notify = Notification(
                user_id=parent_comment.user_id,
                type=3,
                title=f"{current_user.nickname or current_user.username} 回复了你的评论",
                content=comment_data.content,
                related_id=comment.id
            )
            db.add(notify)
    
    # 更新文章评论数
    article.comment_count += 1
    
    await db.commit()
    await db.refresh(comment)
    
    return ResponseModel(
        code=200,
        message="评论成功",
        data={
            "id": comment.id,
            "content": comment.content,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "nickname": current_user.nickname,
                "avatar": current_user.avatar
            },
            "created_at": comment.created_at.isoformat()
        }
    )


@router.delete("/comments/{comment_id}", response_model=ResponseModel[None])
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除评论"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查权限：评论作者、文章作者或管理员可以删除
    result = await db.execute(select(Article).where(Article.id == comment.article_id))
    article = result.scalar_one_or_none()
    
    can_delete = (
        current_user.id == comment.user_id or
        (article and current_user.id == article.author_id) or
        current_user.is_admin
    )
    
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此评论"
        )
    
    # 软删除：修改状态
    comment.status = 2
    
    # 更新文章评论数
    if article and article.comment_count > 0:
        article.comment_count -= 1
    
    await db.commit()
    
    return ResponseModel(code=200, message="删除成功", data=None)
