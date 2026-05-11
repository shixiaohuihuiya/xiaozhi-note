"""
留言墙路由
"""
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from database import get_db
from models import Guestbook, User
from schemas.common import ResponseModel, PaginatedResponse, PaginationParams
from dependencies import get_optional_user
from utils.redis import check_ip_rate_limit

router = APIRouter()

# 匿名留言限流：每个IP每天最多 15 条
ANONYMOUS_DAILY_LIMIT = 15


def _get_client_ip(request: Optional[Request]) -> Optional[str]:
    """获取客户端真实IP，优先处理反向代理头"""
    if not request:
        return None
    # X-Forwarded-For 可能包含多个IP，取第一个
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    return request.client.host if request.client else None



class GuestbookCreate(BaseModel):
    """创建留言请求"""
    content: str = Field(..., min_length=1, max_length=2000, description="留言内容")
    nickname: str = Field(..., min_length=1, max_length=50, description="昵称")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    website: Optional[str] = Field(None, max_length=200, description="个人网站")
    parent_id: Optional[int] = Field(None, description="父留言ID")


class GuestbookReply(BaseModel):
    """回复留言请求"""
    content: str = Field(..., min_length=1, max_length=2000, description="回复内容")


@router.get("", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_guestbooks(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """获取留言墙列表"""
    # 只查询已通过审核的顶级留言
    query = select(Guestbook).options(
        selectinload(Guestbook.user)
    ).where(
        Guestbook.parent_id.is_(None),
        Guestbook.status == 1
    ).order_by(desc(Guestbook.created_at))
    
    # 统计总数
    count_result = await db.execute(
        select(func.count(Guestbook.id)).where(
            Guestbook.parent_id.is_(None),
            Guestbook.status == 1
        )
    )
    total = count_result.scalar()
    
    # 分页
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    guestbooks = result.scalars().all()
    
    # 构建响应（包含回复）
    items = []
    for guestbook in guestbooks:
        # 获取回复
        replies_result = await db.execute(
            select(Guestbook).options(selectinload(Guestbook.user)).where(
                Guestbook.parent_id == guestbook.id,
                Guestbook.status == 1
            ).order_by(Guestbook.created_at)
        )
        replies = replies_result.scalars().all()
        
        items.append({
            "id": guestbook.id,
            "content": guestbook.content,
            "nickname": guestbook.nickname,
            "email": guestbook.email,
            "website": guestbook.website,
            "user": {
                "id": guestbook.user.id,
                "username": guestbook.user.username,
                "nickname": guestbook.user.nickname,
                "avatar": guestbook.user.avatar
            } if guestbook.user else None,
            "like_count": guestbook.like_count,
            "created_at": guestbook.created_at.isoformat(),
            "replies": [
                {
                    "id": reply.id,
                    "content": reply.content,
                    "nickname": reply.nickname,
                    "user": {
                        "id": reply.user.id,
                        "username": reply.user.username,
                        "nickname": reply.user.nickname,
                        "avatar": reply.user.avatar
                    } if reply.user else None,
                    "created_at": reply.created_at.isoformat()
                }
                for reply in replies
            ]
        })
    
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


@router.post("", response_model=ResponseModel[dict])
async def create_guestbook(
    data: GuestbookCreate,
    request: Request = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """发表留言"""
    # 检查父留言是否存在
    if data.parent_id:
        result = await db.execute(
            select(Guestbook).where(Guestbook.id == data.parent_id, Guestbook.status == 1)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="回复的留言不存在"
            )

    client_ip = _get_client_ip(request)

    # 匿名（未登录）用户限流：使用 Redis 记录，同一IP 24小时内最多15条
    if not current_user and client_ip:
        is_allowed, current_count = await check_ip_rate_limit(
            ip_address=client_ip,
            limit=ANONYMOUS_DAILY_LIMIT,
            ttl_seconds=86400  # 24小时
        )
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"您今日留言已达上限（{ANONYMOUS_DAILY_LIMIT} 条），请登录后再发或明日再来"
            )
    
    # 如果已登录，使用用户信息
    if current_user:
        nickname = current_user.nickname or current_user.username
        email = current_user.email
    else:
        nickname = data.nickname
        email = data.email
    
    # 创建留言
    guestbook = Guestbook(
        parent_id=data.parent_id,
        user_id=current_user.id if current_user else None,
        nickname=nickname,
        email=email,
        website=data.website,
        content=data.content,
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent") if request else None,
        status=1  # 直接通过，如需审核可改为0
    )
    
    db.add(guestbook)
    await db.commit()
    await db.refresh(guestbook)
    
    return ResponseModel(
        code=200,
        message="留言成功",
        data={
            "id": guestbook.id,
            "content": guestbook.content,
            "nickname": guestbook.nickname,
            "created_at": guestbook.created_at.isoformat()
        }
    )


@router.post("/{guestbook_id}/like", response_model=ResponseModel[dict])
async def like_guestbook(
    guestbook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """点赞留言"""
    result = await db.execute(
        select(Guestbook).where(Guestbook.id == guestbook_id, Guestbook.status == 1)
    )
    guestbook = result.scalar_one_or_none()
    
    if not guestbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="留言不存在"
        )
    
    # 增加点赞数
    guestbook.like_count += 1
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="点赞成功",
        data={"like_count": guestbook.like_count}
    )


@router.delete("/{guestbook_id}", response_model=ResponseModel[None])
async def delete_guestbook(
    guestbook_id: int,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """删除留言（管理员或本人）"""
    result = await db.execute(select(Guestbook).where(Guestbook.id == guestbook_id))
    guestbook = result.scalar_one_or_none()
    
    if not guestbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="留言不存在"
        )
    
    # 检查权限
    can_delete = (
        current_user and (
            current_user.id == guestbook.user_id or
            current_user.is_admin
        )
    )
    
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此留言"
        )
    
    # 软删除
    guestbook.status = 2
    await db.commit()
    
    return ResponseModel(code=200, message="删除成功", data=None)
