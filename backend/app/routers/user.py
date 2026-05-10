"""
用户路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import User, Article, Comment
from schemas.user import UserUpdate, UserPasswordUpdate, UserResponse, UserSimpleResponse
from schemas.common import ResponseModel, PaginatedResponse, PaginationParams
from dependencies import get_current_active_user
from utils.security import verify_password, get_password_hash

router = APIRouter()


@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前登录用户信息"""
    # 统计文章数量
    article_result = await db.execute(
        select(func.count(Article.id)).where(Article.author_id == current_user.id)
    )
    article_count = article_result.scalar()
    
    # 统计评论数量
    comment_result = await db.execute(
        select(func.count(Comment.id)).where(Comment.user_id == current_user.id)
    )
    comment_count = comment_result.scalar()
    
    # 构建响应
    user_data = UserResponse.model_validate(current_user)
    user_data.article_count = article_count
    user_data.comment_count = comment_count
    
    return ResponseModel(
        code=200,
        message="success",
        data=user_data
    )


@router.put("/me", response_model=ResponseModel[UserResponse])
async def update_current_user(
    request: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    # 更新字段
    if request.nickname is not None:
        current_user.nickname = request.nickname
    if request.avatar is not None:
        current_user.avatar = request.avatar
    if request.bio is not None:
        current_user.bio = request.bio
    if request.phone is not None:
        current_user.phone = request.phone
    
    await db.commit()
    await db.refresh(current_user)
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data=UserResponse.model_validate(current_user)
    )


@router.put("/me/password", response_model=ResponseModel[None])
async def update_password(
    request: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    # 如果用户被标记为必须修改密码，则跳过旧密码验证
    if not current_user.must_change_password:
        if not request.old_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入旧密码"
            )
        if not verify_password(request.old_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
    
    # 更新密码并清除强制修改标记
    current_user.password_hash = get_password_hash(request.new_password)
    current_user.must_change_password = False
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="密码修改成功",
        data=None
    )


@router.get("/{user_id}", response_model=ResponseModel[UserSimpleResponse])
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取用户公开信息"""
    result = await db.execute(
        select(User).where(User.id == user_id, User.status == 1)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return ResponseModel(
        code=200,
        message="success",
        data=UserSimpleResponse.model_validate(user)
    )


@router.get("/me/articles", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_my_articles(
    status: int = None,
    keyword: str = None,
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取我的文章列表"""
    from models import Article
    
    # 构建查询（排除已删除文章）
    query = select(Article).where(
        Article.author_id == current_user.id,
        Article.deleted_at.is_(None)
    )
    
    # 状态筛选
    if status is not None:
        query = query.where(Article.status == status)
    
    # 关键词搜索
    if keyword:
        query = query.where(Article.title.contains(keyword))
    
    # 排序
    query = query.order_by(Article.created_at.desc())
    
    # 统计总数（排除已删除文章，应用相同筛选条件）
    count_query = select(func.count(Article.id)).where(
        Article.author_id == current_user.id,
        Article.deleted_at.is_(None)
    )
    if status is not None:
        count_query = count_query.where(Article.status == status)
    if keyword:
        count_query = count_query.where(Article.title.contains(keyword))
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    articles = result.scalars().all()
    
    # 构建响应数据
    items = []
    for article in articles:
        items.append({
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "cover_image": article.cover_image,
            "status": article.status,
            "needs_reapproval": article.needs_reapproval,
            "view_count": article.view_count,
            "like_count": article.like_count,
            "comment_count": article.comment_count,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "created_at": article.created_at.isoformat()
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


@router.get("/all")
async def get_all_users(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有用户列表（用于管理员发送通知等场景）"""
    result = await db.execute(
        select(User).where(User.status == 1).order_by(User.id)
    )
    users = result.scalars().all()
    
    user_list = [
        {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "avatar": user.avatar
        }
        for user in users
    ]
    
    return ResponseModel(
        code=200,
        message="success",
        data=user_list
    )
