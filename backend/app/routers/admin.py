"""
后台管理路由
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from database import get_db
from models import User, Article, Comment, Category, Tag, Notification
from schemas.common import ResponseModel, PaginatedResponse, PaginationParams
from dependencies import require_admin, require_superadmin
from utils.security import get_password_hash

router = APIRouter()


@router.get("/dashboard", response_model=ResponseModel[dict])
async def get_dashboard(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """仪表盘统计"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=6)
    
    # 转换为北京时间（UTC+8）用于显示
    beijing_offset = timedelta(hours=8)
    now_beijing = now + beijing_offset
    today_start_beijing = now_beijing.replace(hour=0, minute=0, second=0, microsecond=0) - beijing_offset
    week_start_beijing = today_start_beijing - timedelta(days=6)

    # 统计总数
    user_count = await db.execute(select(func.count(User.id)))
    article_count = await db.execute(select(func.count(Article.id)))
    comment_count = await db.execute(select(func.count(Comment.id)))

    # 总阅读量（所有文章 view_count 之和）
    total_views_result = await db.execute(select(func.coalesce(func.sum(Article.view_count), 0)))
    total_views = total_views_result.scalar()

    # 今日新增文章数（使用北京时间）
    today_articles_count = await db.execute(
        select(func.count(Article.id)).where(Article.created_at >= today_start_beijing)
    )

    # 七日新增文章数（使用北京时间）
    week_articles_count = await db.execute(
        select(func.count(Article.id)).where(Article.created_at >= week_start_beijing)
    )

    # 网站运行时间（取最早的用户或文章创建时间）
    oldest_user = await db.execute(select(func.min(User.created_at)))
    oldest_article = await db.execute(select(func.min(Article.created_at)))
    oldest = min(
        oldest_user.scalar() or now,
        oldest_article.scalar() or now
    )
    site_uptime_days = (now - oldest).days + 1

    # 今日新增文章列表（使用北京时间）
    today_articles_result = await db.execute(
        select(Article)
        .options(selectinload(Article.author))
        .where(Article.created_at >= today_start_beijing)
        .order_by(desc(Article.created_at))
        .limit(10)
    )
    today_articles = today_articles_result.scalars().all()

    # 七日每日文章数（使用北京时间）
    daily_counts = []
    for i in range(6, -1, -1):
        day_start = today_start_beijing - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count_result = await db.execute(
            select(func.count(Article.id)).where(
                Article.created_at >= day_start,
                Article.created_at < day_end
            )
        )
        daily_counts.append({
            "date": (day_start + beijing_offset).strftime("%m-%d"),
            "count": count_result.scalar()
        })

    # 最近文章
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.author))
        .order_by(desc(Article.created_at))
        .limit(5)
    )
    recent_articles = result.scalars().all()

    # 待审核文章（needs_reapproval = True）
    pending_articles_count = await db.execute(
        select(func.count(Article.id)).where(Article.needs_reapproval == True)
    )
    pending_articles_result = await db.execute(
        select(Article)
        .options(selectinload(Article.author))
        .where(Article.needs_reapproval == True)
        .order_by(desc(Article.updated_at))
        .limit(10)
    )
    pending_articles = pending_articles_result.scalars().all()

    # 待审核评论数
    pending_comments = await db.execute(
        select(func.count(Comment.id)).where(Comment.status == 0)
    )

    return ResponseModel(
        code=200,
        message="success",
        data={
            "statistics": {
                "total_users": user_count.scalar(),
                "total_articles": article_count.scalar(),
                "total_comments": comment_count.scalar(),
                "total_views": total_views,
                "today_articles": today_articles_count.scalar(),
                "week_articles": week_articles_count.scalar(),
                "site_uptime_days": site_uptime_days,
                "pending_articles": pending_articles_count.scalar()
            },
            "daily_articles": daily_counts,
            "today_articles_list": [
                {
                    "id": a.id,
                    "title": a.title,
                    "author": a.author.nickname or a.author.username if a.author else None,
                    "status": a.status,
                    "created_at": a.created_at.isoformat()
                }
                for a in today_articles
            ],
            "pending_articles_list": [
                {
                    "id": a.id,
                    "title": a.title,
                    "author": a.author.nickname or a.author.username if a.author else None,
                    "status": a.status,
                    "updated_at": a.updated_at.isoformat()
                }
                for a in pending_articles
            ],
            "recent_articles": [
                {
                    "id": a.id,
                    "title": a.title,
                    "author": a.author.nickname or a.author.username if a.author else None,
                    "status": a.status,
                    "created_at": a.created_at.isoformat()
                }
                for a in recent_articles
            ],
            "pending_comments": pending_comments.scalar()
        }
    )


# ========== 用户管理 ==========

@router.get("/users", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_users(
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    role: Optional[int] = None,
    pagination: PaginationParams = Depends(),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    query = select(User)
    
    if keyword:
        query = query.where(
            User.username.contains(keyword) | User.email.contains(keyword)
        )
    if status is not None:
        query = query.where(User.status == status)
    if role is not None:
        query = query.where(User.role == role)
    
    query = query.order_by(desc(User.created_at))
    
    # 统计总数
    count_query = select(func.count(User.id))
    if keyword:
        count_query = count_query.where(
            User.username.contains(keyword) | User.email.contains(keyword)
        )
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    items = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "nickname": u.nickname,
            "role": u.role,
            "is_superadmin": u.is_superadmin,
            "status": u.status,
            "is_verified": u.is_verified,
            "created_at": u.created_at.isoformat()
        }
        for u in users
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


@router.put("/users/{user_id}/status", response_model=ResponseModel[dict])
async def update_user_status(
    user_id: int,
    status: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新用户状态"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 超级管理员的状态不能被修改
    if user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法修改超级管理员状态"
        )
    
    # 普通管理员不能修改其他管理员的状态
    if user.is_admin and not admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限才能修改管理员状态"
        )
    
    user.status = status
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="状态更新成功",
        data={"id": user.id, "status": user.status}
    )


@router.put("/users/{user_id}/role", response_model=ResponseModel[dict])
async def update_user_role(
    user_id: int,
    role: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """设置用户角色"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 超级管理员的角色不能被修改
    if user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法修改超级管理员角色"
        )
    
    # 只有超级管理员才能设置管理员角色
    if role in (1, 2) and not admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限才能设置管理员角色"
        )
    
    # 不能设置超级管理员角色（超级管理员只能通过初始化创建）
    if role == 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="超级管理员只能通过系统初始化创建"
        )
    
    user.role = role
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="角色更新成功",
        data={"id": user.id, "role": user.role}
    )


@router.put("/users/{user_id}/reset-password", response_model=ResponseModel[dict])
async def reset_user_password(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """重置用户密码（随机生成6位数字）"""
    import random
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 超级管理员的密码不能被重置
    if user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法重置超级管理员密码"
        )
    
    # 普通管理员不能重置其他管理员的密码，只有超级管理员可以
    if user.is_admin and not admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限才能重置管理员密码"
        )
    
    # 随机生成6位数字密码
    new_password = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # 设置新密码并标记必须修改
    user.password_hash = get_password_hash(new_password)
    user.must_change_password = True
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="密码重置成功",
        data={"id": user.id, "new_password": new_password}
    )


@router.put("/users/{user_id}", response_model=ResponseModel[dict])
async def update_user(
    user_id: int,
    username: Optional[str] = None,
    email: Optional[str] = None,
    nickname: Optional[str] = None,
    role: Optional[int] = None,
    status: Optional[int] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """管理员更新用户信息"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 超级管理员的信息不能被普通管理员修改角色和状态
    if user.is_superadmin and not admin.is_superadmin:
        # 超级管理员只能修改自己的信息（用户名、邮箱、昵称），不能修改角色和状态
        if role is not None and role != user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无法修改超级管理员角色"
            )
        if status is not None and status != user.status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无法修改超级管理员状态"
            )
    
    # 只有超级管理员才能设置管理员角色
    if role is not None and role != user.role:
        if role in (1, 2) and not admin.is_superadmin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要超级管理员权限才能设置管理员角色"
            )
        if role == 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="超级管理员只能通过系统初始化创建"
            )
    
    
    # 检查用户名是否被其他用户占用
    if username is not None and username != user.username:
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        user.username = username
    
    
    # 检查邮箱是否被其他用户占用
    if email is not None and email != user.email:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        user.email = email
    
    
    if nickname is not None:
        user.nickname = nickname
    if role is not None:
        user.role = role
    if status is not None:
        user.status = status
    
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="用户信息更新成功",
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "role": user.role,
            "status": user.status
        }
    )


@router.delete("/users/{user_id}", response_model=ResponseModel[dict])
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """管理员删除用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 超级管理员不能被删除
    if user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法删除超级管理员"
        )
    
    # 普通管理员不能删除其他管理员
    if user.is_admin and not admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限才能删除管理员"
        )
    
    await db.delete(user)
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="用户删除成功",
        data={"id": user_id}
    )


@router.post("/users", response_model=ResponseModel[dict])
async def create_user(
    username: str,
    email: str,
    password: str,
    nickname: Optional[str] = None,
    role: int = 0,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """管理员创建用户"""
    # 只有超级管理员才能创建管理员
    if role in (1, 2) and not admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限才能创建管理员"
        )
    
    # 不能创建超级管理员
    if role == 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="超级管理员只能通过系统初始化创建"
        )
    # 检查用户名
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    new_user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        nickname=nickname or username,
        role=role,
        status=1,
        is_verified=True
    )
    db.add(new_user)
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="用户创建成功",
        data={"id": new_user.id, "username": new_user.username}
    )


@router.post("/users/batch", response_model=ResponseModel[dict])
async def batch_create_users(
    file: UploadFile = File(...),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """批量导入用户（支持 Excel .xlsx）"""
    import io
    try:
        import openpyxl
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器未安装 openpyxl，请联系管理员"
        )
    
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传 .xlsx 格式的 Excel 文件"
        )
    
    content = await file.read()
    workbook = openpyxl.load_workbook(io.BytesIO(content))
    sheet = workbook.active
    
    success_count = 0
    failed_rows = []
    
    # 表头占第一行，从第二行开始读取
    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        if not row or not row[0]:
            continue
        
        username = str(row[0]).strip() if row[0] else None
        email = str(row[1]).strip() if len(row) > 1 and row[1] else None
        password = str(row[2]).strip() if len(row) > 2 and row[2] else None
        nickname = str(row[3]).strip() if len(row) > 3 and row[3] else None
        role_str = str(row[4]).strip() if len(row) > 4 and row[4] else '0'
        
        if not username or not email or not password:
            failed_rows.append({"row": idx, "reason": "用户名、邮箱或密码为空"})
            continue
        
        try:
            role = int(role_str) if role_str in ('0', '1') else 0
        except ValueError:
            role = 0
        
        # 批量导入不允许创建管理员，强制设为普通用户
        if role in (1, 2):
            role = 0
        
        # 检查用户名重复
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            failed_rows.append({"row": idx, "reason": f"用户名 '{username}' 已存在"})
            continue
        
        # 检查邮箱重复
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            failed_rows.append({"row": idx, "reason": f"邮箱 '{email}' 已被注册"})
            continue
        
        new_user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            nickname=nickname or username,
            role=role,
            status=1,
            is_verified=True
        )
        db.add(new_user)
        success_count += 1
    
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="批量导入完成",
        data={
            "success_count": success_count,
            "failed_count": len(failed_rows),
            "failed_rows": failed_rows
        }
    )


@router.get("/users/template")
async def download_user_template(
    admin: User = Depends(require_admin)
):
    """下载用户批量导入模板"""
    from fastapi.responses import FileResponse
    import os

    template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "用户导入模板.xlsx")

    if not os.path.exists(template_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="模板文件不存在"
        )

    return FileResponse(
        template_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="用户导入模板.xlsx"
    )


# ========== 文章管理 ==========

@router.get("/articles", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_all_articles(
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    pagination: PaginationParams = Depends(),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取全部文章（管理员可查看所有状态，不包括已删除）"""
    query = select(Article).options(selectinload(Article.author)).where(Article.deleted_at.is_(None))

    if keyword:
        query = query.where(Article.title.contains(keyword))
    if status is not None:
        query = query.where(Article.status == status)

    # 统计总数
    count_query = select(func.count(Article.id)).where(Article.deleted_at.is_(None))
    if keyword:
        count_query = count_query.where(Article.title.contains(keyword))
    if status is not None:
        count_query = count_query.where(Article.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    query = query.order_by(desc(Article.created_at)).offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    articles = result.scalars().all()

    items = [
        {
            "id": a.id,
            "title": a.title,
            "slug": a.slug,
            "status": a.status,
            "needs_reapproval": a.needs_reapproval,
            "view_count": a.view_count,
            "author": {
                "id": a.author.id,
                "username": a.author.username,
                "nickname": a.author.nickname
            } if a.author else None,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "created_at": a.created_at.isoformat()
        }
        for a in articles
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


@router.get("/articles/pending", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_pending_articles(
    pagination: PaginationParams = Depends(),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取待审核文章"""
    query = select(Article).where(Article.status == 0).order_by(desc(Article.created_at))
    
    count_result = await db.execute(select(func.count(Article.id)).where(Article.status == 0))
    total = count_result.scalar()
    
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query.options(selectinload(Article.author)))
    articles = result.scalars().all()

    items = [
        {
            "id": a.id,
            "title": a.title,
            "slug": a.slug,
            "author": {
                "id": a.author.id,
                "username": a.author.username,
                "nickname": a.author.nickname
            } if a.author else None,
            "created_at": a.created_at.isoformat()
        }
        for a in articles
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


@router.put("/articles/{article_id}/review", response_model=ResponseModel[dict])
async def review_article(
    article_id: int,
    status: int,  # 1-通过, 2-拒绝
    reason: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """审核文章"""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    article.status = status
    if status == 1 and article.published_at is None:
        article.published_at = datetime.utcnow()
    
    # 审核通过时重置重新申请标志
    if status == 1:
        article.needs_reapproval = False
    
    # 下架时设置需要重新申请审核
    if status == 2:
        article.needs_reapproval = True
    
    # 拒绝时发送通知给作者
    if status == 2:
        notification = Notification(
            user_id=article.author_id,
            type=1,
            title=f"文章《{article.title}》已被下架",
            content=f"您的文章《{article.title}》已被管理员下架。{('原因：' + reason) if reason else ''}",
            related_id=article.id
        )
        db.add(notification)
    
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="审核完成",
        data={"id": article.id, "status": article.status}
    )


@router.delete("/articles/{article_id}", response_model=ResponseModel[dict])
async def delete_article_admin(
    article_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """管理员删除文章（软删除）"""
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 软删除
    article.deleted_at = datetime.utcnow()
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="删除成功",
        data={"id": article.id}
    )


# ========== 评论管理 ==========

@router.get("/comments", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_comments(
    status: Optional[int] = None,
    pagination: PaginationParams = Depends(),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取评论列表"""
    query = select(Comment).order_by(desc(Comment.created_at))
    
    if status is not None:
        query = query.where(Comment.status == status)
    
    count_query = select(func.count(Comment.id))
    if status is not None:
        count_query = count_query.where(Comment.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query.options(selectinload(Comment.user), selectinload(Comment.article)))
    comments = result.scalars().all()

    items = [
        {
            "id": c.id,
            "content": c.content,
            "user": {
                "id": c.user.id,
                "username": c.user.username,
                "nickname": c.user.nickname
            } if c.user else None,
            "article": {
                "id": c.article.id,
                "title": c.article.title
            } if c.article else None,
            "status": c.status,
            "created_at": c.created_at.isoformat()
        }
        for c in comments
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


@router.put("/comments/{comment_id}/review", response_model=ResponseModel[dict])
async def review_comment(
    comment_id: int,
    status: int,  # 1-通过, 2-拒绝/撤回
    reason: Optional[str] = "违反规定",
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """审核评论（撤回时通知用户原因）"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    comment.status = status
    
    # 拒绝/撤回时发送通知给用户
    if status == 2:
        notification = Notification(
            user_id=comment.user_id,
            type=2,
            title="您的评论已被管理员撤回",
            content=f"原因：{reason}",
            related_id=comment.id
        )
        db.add(notification)
    
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="审核完成",
        data={"id": comment.id, "status": comment.status}
    )


# ========== 通知管理 ==========

@router.get("/notifications", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_admin_notifications(
    type: Optional[int] = None,
    user_id: Optional[int] = None,
    pagination: PaginationParams = Depends(),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取通知列表（管理员）"""
    query = select(Notification).order_by(desc(Notification.created_at))
    count_query = select(func.count(Notification.id))

    if type is not None:
        query = query.where(Notification.type == type)
        count_query = count_query.where(Notification.type == type)
    if user_id is not None:
        query = query.where(Notification.user_id == user_id)
        count_query = count_query.where(Notification.user_id == user_id)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    notifications = result.scalars().all()

    # 批量获取用户名
    user_ids = list(set(n.user_id for n in notifications))
    user_map = {}
    if user_ids:
        users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
        user_map = {u.id: u for u in users_result.scalars().all()}

    items = [
        {
            "id": n.id,
            "user_id": n.user_id,
            "username": user_map.get(n.user_id).username if user_map.get(n.user_id) else None,
            "nickname": user_map.get(n.user_id).nickname if user_map.get(n.user_id) else None,
            "type": n.type,
            "title": n.title,
            "content": n.content,
            "related_id": n.related_id,
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


@router.post("/notifications/send", response_model=ResponseModel[dict])
async def send_notification(
    title: str,
    content: Optional[str] = None,
    user_id: Optional[int] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """发送通知（指定用户或全员广播）"""
    if not title or not title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="通知标题不能为空"
        )

    if user_id is not None:
        # 发送给指定用户
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        notification = Notification(
            user_id=user_id,
            type=99,  # 管理员手动发送的通知类型
            title=title.strip(),
            content=content.strip() if content else None
        )
        db.add(notification)
        await db.commit()

        return ResponseModel(
            code=200,
            message="通知发送成功",
            data={"sent_count": 1, "target": "user", "user_id": user_id}
        )
    else:
        # 全员广播
        result = await db.execute(select(User).where(User.status == 1))
        users = result.scalars().all()

        for user in users:
            notification = Notification(
                user_id=user.id,
                type=99,
                title=title.strip(),
                content=content.strip() if content else None
            )
            db.add(notification)

        await db.commit()

        return ResponseModel(
            code=200,
            message=f"通知已发送给 {len(users)} 位用户",
            data={"sent_count": len(users), "target": "all"}
        )


@router.delete("/notifications/{notification_id}", response_model=ResponseModel[dict])
async def delete_admin_notification(
    notification_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除通知（管理员）"""
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
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
        message="通知删除成功",
        data={"id": notification_id}
    )


@router.delete("/notifications", response_model=ResponseModel[dict])
async def batch_delete_notifications(
    ids: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """批量删除通知"""
    id_list = [int(i) for i in ids.split(",") if i.strip().isdigit()]
    if not id_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供有效的通知ID"
        )

    count = 0
    for nid in id_list:
        result = await db.execute(select(Notification).where(Notification.id == nid))
        n = result.scalar_one_or_none()
        if n:
            await db.delete(n)
            count += 1

    await db.commit()

    return ResponseModel(
        code=200,
        message=f"成功删除 {count} 条通知",
        data={"deleted_count": count}
    )
