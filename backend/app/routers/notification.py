"""
通知路由
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import get_db
from models import Notification, User
from schemas.common import ResponseModel, PaginatedResponse, PaginationParams
from dependencies import get_current_active_user, require_admin
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic models for admin notification
class AdminNotificationCreate(BaseModel):
    """管理员创建通知的请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="通知标题")
    content: Optional[str] = Field(None, description="通知内容")
    type: int = Field(5, description="通知类型: 4-系统公告, 5-管理员通知")
    target_user_ids: Optional[List[int]] = Field(None, description="目标用户ID列表，为空表示全员通知")
    related_id: Optional[int] = Field(None, description="关联ID")


class NotificationResponse(BaseModel):
    """通知响应模型"""
    id: int
    user_id: Optional[int]
    type: int
    title: str
    content: Optional[str]
    is_read: bool
    is_system: bool
    created_by: Optional[int]
    created_at: str


@router.get("", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_notifications(
    is_read: Optional[bool] = None,
    pagination: PaginationParams = Depends(),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的通知列表"""
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if is_read is not None:
        query = query.where(Notification.is_read == is_read)
    
    query = query.order_by(desc(Notification.created_at))
    
    # 统计总数
    count_query = select(func.count(Notification.id)).where(Notification.user_id == current_user.id)
    if is_read is not None:
        count_query = count_query.where(Notification.is_read == is_read)
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    # 批量获取评论相关的文章slug
    comment_ids = [n.related_id for n in notifications if n.type == 3 and n.related_id]
    comment_article_map = {}
    if comment_ids:
        from sqlalchemy import select as sa_select
        from models import Comment, Article
        comment_result = await db.execute(
            sa_select(Comment.id, Article.slug)
            .join(Article, Comment.article_id == Article.id)
            .where(Comment.id.in_(comment_ids))
        )
        comment_article_map = {row[0]: row[1] for row in comment_result.all()}
    
    items = [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "content": n.content,
            "related_id": n.related_id,
            "article_slug": comment_article_map.get(n.related_id) if n.type == 3 else None,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        }
        for n in notifications
    ]
    
    return ResponseModel(
        code=200,
        message="success",
        data=PaginatedResponse.create(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size
        )
    )


@router.get("/unread-count", response_model=ResponseModel[dict])
async def get_unread_count(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取未读通知数量"""
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    count = result.scalar()
    
    return ResponseModel(
        code=200,
        message="success",
        data={"count": count}
    )


@router.put("/{notification_id}/read", response_model=ResponseModel[dict])
async def mark_as_read(
    notification_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """标记单条通知为已读"""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    notification.is_read = True
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="标记已读成功",
        data={"id": notification.id}
    )


@router.put("/{notification_id}/unread", response_model=ResponseModel[dict])
async def mark_as_unread(
    notification_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """标记单条通知为未读"""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    notification.is_read = False
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="标记未读成功",
        data={"id": notification.id}
    )


@router.delete("/{notification_id}", response_model=ResponseModel[dict])
async def delete_notification(
    notification_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除单条通知"""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    await db.delete(notification)
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="删除成功",
        data={"id": notification_id}
    )


@router.put("/read-all", response_model=ResponseModel[dict])
async def mark_all_as_read(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """标记所有通知为已读"""
    from sqlalchemy import update
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="全部标记已读成功",
        data=None
    )


# ==================== Admin Notification Management ====================

@router.post("/admin/send", response_model=ResponseModel[dict])
async def send_admin_notification(
    data: AdminNotificationCreate,
    current_user = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """管理员发送通知（支持个人和全员）"""
    created_count = 0
    
    # 如果指定了目标用户，发送给特定用户
    if data.target_user_ids:
        for user_id in data.target_user_ids:
            # 验证用户是否存在
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                continue
            
            notification = Notification(
                user_id=user_id,
                type=data.type,
                title=data.title,
                content=data.content,
                related_id=data.related_id,
                is_system=True,
                created_by=current_user.id
            )
            db.add(notification)
            created_count += 1
    else:
        # 全员通知：为每个活跃用户创建通知
        users_result = await db.execute(
            select(User).where(User.status == 1)
        )
        users = users_result.scalars().all()
        
        for user in users:
            notification = Notification(
                user_id=user.id,
                type=data.type,
                title=data.title,
                content=data.content,
                related_id=data.related_id,
                is_system=True,
                created_by=current_user.id
            )
            db.add(notification)
            created_count += 1
    
    await db.commit()
    
    return ResponseModel(
        code=200,
        message=f"成功发送 {created_count} 条通知",
        data={"sent_count": created_count}
    )


@router.get("/admin/list", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_admin_notifications(
    user_id: Optional[int] = None,
    is_system: Optional[bool] = None,
    notification_type: Optional[int] = None,
    pagination: PaginationParams = Depends(),
    current_user = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """管理员查看所有通知记录"""
    from sqlalchemy.orm import selectinload
    
    query = select(Notification).options(
        selectinload(Notification.user),
        selectinload(Notification.creator)
    )
    
    # 筛选条件
    if user_id is not None:
        query = query.where(Notification.user_id == user_id)
    if is_system is not None:
        query = query.where(Notification.is_system == is_system)
    if notification_type is not None:
        query = query.where(Notification.type == notification_type)
    
    query = query.order_by(desc(Notification.created_at))
    
    # 统计总数
    count_query = select(func.count(Notification.id))
    if user_id is not None:
        count_query = count_query.where(Notification.user_id == user_id)
    if is_system is not None:
        count_query = count_query.where(Notification.is_system == is_system)
    if notification_type is not None:
        count_query = count_query.where(Notification.type == notification_type)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    items = [
        {
            "id": n.id,
            "user_id": n.user_id,
            "username": n.user.username if n.user else "全员",
            "type": n.type,
            "title": n.title,
            "content": n.content,
            "is_read": n.is_read,
            "is_system": n.is_system,
            "created_by": n.created_by,
            "creator_name": n.creator.username if n.creator else "系统",
            "created_at": n.created_at.isoformat()
        }
        for n in notifications
    ]
    
    return ResponseModel(
        code=200,
        message="success",
        data=PaginatedResponse.create(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size
        )
    )


@router.delete("/admin/{notification_id}", response_model=ResponseModel[dict])
async def delete_admin_notification(
    notification_id: int,
    current_user = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """管理员删除通知"""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    await db.delete(notification)
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="删除成功",
        data={"id": notification_id}
    )


@router.get("/admin/stats", response_model=ResponseModel[dict])
async def get_notification_stats(
    current_user = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取通知统计数据"""
    # 总通知数
    total_result = await db.execute(select(func.count(Notification.id)))
    total_count = total_result.scalar()
    
    # 系统通知数
    system_result = await db.execute(
        select(func.count(Notification.id)).where(Notification.is_system == True)
    )
    system_count = system_result.scalar()
    
    # 今日新增
    from datetime import datetime, timedelta
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(Notification.id)).where(Notification.created_at >= today)
    )
    today_count = today_result.scalar()
    
    # 按类型统计
    type_stats_result = await db.execute(
        select(Notification.type, func.count(Notification.id))
        .group_by(Notification.type)
    )
    type_stats = {row[0]: row[1] for row in type_stats_result.all()}
    
    return ResponseModel(
        code=200,
        message="success",
        data={
            "total_count": total_count,
            "system_count": system_count,
            "today_count": today_count,
            "type_stats": type_stats
        }
    )
