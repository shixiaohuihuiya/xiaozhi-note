"""
文章路由
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import selectinload
from database import get_db
from models import Article, User, Category, Tag, ArticleTag, Comment, Like
from schemas.common import ResponseModel, PaginatedResponse, PaginationParams
from schemas.article import ArticleCreate, ArticleUpdate
from dependencies import get_current_active_user, get_optional_user
from utils.security import generate_slug
import re
import urllib.parse
import io

router = APIRouter()


@router.get("", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_articles(
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    keyword: Optional[str] = None,
    order_by: str = Query("latest", enum=["latest", "hot", "top"]),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """获取文章列表"""
    # 构建查询 - 只查询已发布的文章，预加载作者、分类、标签信息
    query = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.article_tags).selectinload(ArticleTag.tag)
        )
        .where(Article.status == 1, Article.deleted_at.is_(None))
    )
    
    # 分类筛选
    if category_id:
        query = query.where(Article.category_id == category_id)
    
    # 标签筛选
    if tag_id:
        query = query.join(ArticleTag).where(ArticleTag.tag_id == tag_id)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            Article.title.contains(keyword) | Article.summary.contains(keyword)
        )
    
    # 置顶筛选 + 排序
    if order_by == "top":
        query = query.where(Article.is_top == True).order_by(desc(Article.published_at))
    elif order_by == "hot":
        query = query.order_by(desc(Article.view_count))
    else:  # latest
        query = query.order_by(desc(Article.published_at))
    
    # 统计总数查询（使用 distinct 避免 join 导致重复）
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    articles = result.scalars().all()
    
    # 构建响应
    items = []
    for article in articles:
        items.append({
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "cover_image": article.cover_image,
            "author": {
                "id": article.author.id,
                "username": article.author.username,
                "nickname": article.author.nickname,
                "avatar": article.author.avatar
            } if article.author else None,
            "category": {
                "id": article.category.id,
                "name": article.category.name,
                "slug": article.category.slug
            } if article.category else None,
            "tags": [{"id": at.tag.id, "name": at.tag.name, "slug": at.tag.slug} for at in article.article_tags if at.tag],
            "view_count": article.view_count,
            "like_count": article.like_count,
            "comment_count": article.comment_count,
            "published_at": article.published_at.isoformat() if article.published_at else None
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


@router.get("/stats/public", response_model=ResponseModel[dict])
async def get_public_stats(
    db: AsyncSession = Depends(get_db)
):
    """获取公开统计数据（首页展示）"""
    # 文章总数（已发布）
    article_count = await db.execute(
        select(func.count(Article.id)).where(Article.status == 1, Article.deleted_at.is_(None))
    )
    # 用户总数
    user_count = await db.execute(
        select(func.count(User.id)).where(User.status == 1)
    )
    # 总阅读量
    view_count = await db.execute(
        select(func.coalesce(func.sum(Article.view_count), 0)).where(Article.status == 1, Article.deleted_at.is_(None))
    )
    # 评论总数
    comment_count = await db.execute(
        select(func.count(Comment.id)).where(Comment.status == 1)
    )

    return ResponseModel(
        code=200,
        message="success",
        data={
            "article_count": article_count.scalar(),
            "user_count": user_count.scalar(),
            "view_count": view_count.scalar(),
            "comment_count": comment_count.scalar()
        }
    )


@router.get("/{slug}", response_model=ResponseModel[dict])
async def get_article(
    slug: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """获取文章详情"""
    from models import ArticleTag, Tag
    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author), 
            selectinload(Article.category), 
            selectinload(Article.article_tags).selectinload(ArticleTag.tag)
        )
        .where(Article.slug == slug, Article.deleted_at.is_(None))
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查权限：草稿或已下架的文章只能作者查看
    if article.status in (0, 2):
        if not current_user or current_user.id != article.author_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文章不存在"
            )
    
    # 增加阅读数
    article.view_count += 1
    await db.commit()
    
    # 检查当前用户是否点赞
    is_liked = False
    if current_user:
        like_result = await db.execute(
            select(Like).where(Like.article_id == article.id, Like.user_id == current_user.id)
        )
        is_liked = like_result.scalar_one_or_none() is not None
    
    # 计算作者统计数据
    author_article_count = await db.execute(
        select(func.count(Article.id)).where(
            Article.author_id == article.author_id,
            Article.status == 1,
            Article.deleted_at.is_(None)
        )
    )
    author_total_likes = await db.execute(
        select(func.coalesce(func.sum(Article.like_count), 0)).where(
            Article.author_id == article.author_id,
            Article.status == 1,
            Article.deleted_at.is_(None)
        )
    )

    # 构建响应
    data = {
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "summary": article.summary,
        "content": article.content,
        "content_type": article.content_type,
        "cover_image": article.cover_image,
        "author": {
            "id": article.author.id,
            "username": article.author.username,
            "nickname": article.author.nickname,
            "avatar": article.author.avatar,
            "bio": article.author.bio,
            "created_at": article.author.created_at.isoformat() if article.author.created_at else None,
            "article_count": author_article_count.scalar(),
            "total_likes": author_total_likes.scalar()
        } if article.author else None,
        "category": {
            "id": article.category.id,
            "name": article.category.name,
            "slug": article.category.slug
        } if article.category else None,
        "tags": [{"id": at.tag.id, "name": at.tag.name, "slug": at.tag.slug, "color": at.tag.color} for at in article.article_tags if at.tag],
        "view_count": article.view_count,
        "like_count": article.like_count,
        "comment_count": article.comment_count,
        "is_liked": is_liked,
        "needs_reapproval": article.needs_reapproval,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "created_at": article.created_at.isoformat(),
        "updated_at": article.updated_at.isoformat()
    }
    
    return ResponseModel(code=200, message="success", data=data)


@router.post("", response_model=ResponseModel[dict])
async def create_article(
    article_data: ArticleCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建文章"""
    # 生成slug
    base_slug = generate_slug(article_data.title)
    slug = base_slug
    counter = 1
    
    # 确保slug唯一
    while True:
        result = await db.execute(select(Article).where(Article.slug == slug))
        if not result.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # 创建文章
    article = Article(
        title=article_data.title,
        slug=slug,
        summary=article_data.summary,
        content=article_data.content,
        content_type=article_data.content_type,
        cover_image=article_data.cover_image,
        author_id=current_user.id,
        category_id=article_data.category_id,
        status=article_data.status,
        is_top=article_data.is_top,
        published_at=datetime.utcnow() if article_data.status == 1 else None
    )
    
    db.add(article)
    await db.flush()  # 获取article.id
    
    # 添加标签关联
    if article_data.tag_ids:
        for tag_id in article_data.tag_ids:
            article_tag = ArticleTag(article_id=article.id, tag_id=tag_id)
            db.add(article_tag)
    
    await db.commit()
    await db.refresh(article)
    
    return ResponseModel(
        code=200,
        message="创建成功",
        data={
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "status": article.status,
            "created_at": article.created_at.isoformat()
        }
    )


@router.put("/{article_id}", response_model=ResponseModel[dict])
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新文章"""
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查权限：只能修改自己的文章，管理员可以修改所有
    if current_user.id != article.author_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此文章"
        )
    
    # 更新字段
    if article_data.title is not None:
        article.title = article_data.title
    if article_data.content is not None:
        article.content = article_data.content
    if article_data.summary is not None:
        article.summary = article_data.summary
    if article_data.cover_image is not None:
        article.cover_image = article_data.cover_image
    if article_data.category_id is not None:
        article.category_id = article_data.category_id
    if article_data.status is not None:
        # 被管理员下架后需要重新申请审核
        if article_data.status == 1 and article.needs_reapproval:
            article.status = 0  # 保持待审核状态
            # 发送管理员审核通知（发给所有管理员）
            from models import Notification, User
            admin_result = await db.execute(
                select(User).where(User.role.in_([1, 2]), User.status == 1)
            )
            admins = admin_result.scalars().all()
            for admin in admins:
                notify = Notification(
                    user_id=admin.id,
                    type=1,
                    title=f"文章《{article.title}》申请重新发布",
                    content=f"用户 {current_user.nickname or current_user.username} 申请重新发布文章《{article.title}》，请前往后台审核。",
                    related_id=article.id
                )
                db.add(notify)
        else:
            article.status = article_data.status
            # 如果发布，设置发布时间
            if article_data.status == 1 and article.published_at is None:
                article.published_at = datetime.utcnow()
    if article_data.is_top is not None:
        article.is_top = article_data.is_top
    
    # 更新标签
    if article_data.tag_ids is not None:
        # 删除旧标签
        await db.execute(
            select(ArticleTag).where(ArticleTag.article_id == article_id)
        )
        # 添加新标签
        for tag_id in article_data.tag_ids:
            article_tag = ArticleTag(article_id=article.id, tag_id=tag_id)
            db.add(article_tag)
    
    await db.commit()
    await db.refresh(article)
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data={
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "updated_at": article.updated_at.isoformat()
        }
    )


@router.delete("/{article_id}", response_model=ResponseModel[None])
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文章（软删除）"""
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查权限
    if current_user.id != article.author_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此文章"
        )
    
    # 软删除
    article.deleted_at = datetime.utcnow()
    await db.commit()
    
    return ResponseModel(code=200, message="删除成功", data=None)


@router.get("/{article_id}/export")
async def export_article_md(
    article_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """导出文章为Markdown文件"""
    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.article_tags).selectinload(ArticleTag.tag)
        )
        .where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )

    # 权限检查：作者本人或管理员
    if current_user.id != article.author_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权导出此文章"
        )

    # 获取站点基础URL（支持反向代理）
    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    host = request.headers.get("host", request.headers.get("x-forwarded-host", ""))
    if forwarded_proto and host:
        base_url = f"{forwarded_proto}://{host}"
    else:
        base_url = str(request.base_url).rstrip('/')

    # 构建Markdown内容
    lines = [f"# {article.title}", ""]

    # 添加元信息
    meta_parts = []
    if article.author:
        author_name = article.author.nickname or article.author.username
        meta_parts.append(f"**作者**: {author_name}")
    if article.category:
        meta_parts.append(f"**分类**: {article.category.name}")
    if article.article_tags:
        tag_names = [at.tag.name for at in article.article_tags if at.tag]
        if tag_names:
            meta_parts.append(f"**标签**: {', '.join(tag_names)}")
    if article.published_at:
        meta_parts.append(f"**发布时间**: {article.published_at.strftime('%Y-%m-%d %H:%M')}")

    if meta_parts:
        lines.extend(meta_parts)
        lines.append("")
        lines.append("---")
        lines.append("")

    # 添加摘要
    if article.summary:
        lines.append(f"> {article.summary}")
        lines.append("")

    # 处理内容 - 将相对图片路径转换为绝对URL
    content = article.content or ""

    def replace_image_path(match):
        alt_text = match.group(1)
        path = match.group(2)
        if path.startswith('http://') or path.startswith('https://'):
            return match.group(0)
        if path.startswith('/'):
            return f'![{alt_text}]({base_url}{path})'
        return f'![{alt_text}]({base_url}/{path})'

    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image_path, content)

    lines.append(content)

    md_content = "\n".join(lines)

    # 生成安全文件名
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', article.title)
    filename = f"{safe_title}.md"

    return StreamingResponse(
        iter([md_content.encode('utf-8')]),
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{urllib.parse.quote(filename)}"
        }
    )


@router.post("/{article_id}/like", response_model=ResponseModel[dict])
async def toggle_like(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """点赞/取消点赞"""
    # 检查文章是否存在
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.status == 1, Article.deleted_at.is_(None))
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查是否已点赞
    like_result = await db.execute(
        select(Like).where(Like.article_id == article_id, Like.user_id == current_user.id)
    )
    existing_like = like_result.scalar_one_or_none()
    
    if existing_like:
        # 取消点赞
        await db.delete(existing_like)
        article.like_count -= 1
        if article.like_count < 0:
            article.like_count = 0
        await db.commit()
        return ResponseModel(
            code=200,
            message="取消点赞成功",
            data={"is_liked": False, "like_count": article.like_count}
        )
    else:
        # 点赞
        like = Like(article_id=article_id, user_id=current_user.id)
        db.add(like)
        article.like_count += 1
        await db.commit()
        return ResponseModel(
            code=200,
            message="点赞成功",
            data={"is_liked": True, "like_count": article.like_count}
        )


@router.get("/{slug}/export")
async def export_article(
    slug: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """导出文章为 Markdown 文件"""
    result = await db.execute(
        select(Article).where(Article.slug == slug, Article.deleted_at.is_(None))
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查权限：只能导出自己或管理员
    if current_user.id != article.author_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权导出此文章"
        )
    
    # 构建基础 URL
    base_url = str(request.base_url).rstrip('/')
    
    # 获取文章内容
    content = article.content or ''
    
    # 将相对图片路径转换为绝对 URL
    # 处理 Markdown 图片语法: ![alt](/uploads/...)
    content = re.sub(
        r'!\[(.*?)\]\((/uploads/[^)]+)\)',
        lambda m: f'![{m.group(1)}]({base_url}{m.group(2)})',
        content
    )
    # 处理 HTML img 标签: <img src="/uploads/...">
    content = re.sub(
        r'<img\s+([^>]*?)src="(/uploads/[^"]+)"([^>]*?)>',
        lambda m: f'<img {m.group(1)}src="{base_url}{m.group(2)}"{m.group(3)}>',
        content
    )
    # 处理 HTML img 标签单引号: <img src='/uploads/...'>
    content = re.sub(
        r"<img\s+([^>]*?)src='(/uploads/[^']+)'([^>]*?)>",
        lambda m: f"<img {m.group(1)}src='{base_url}{m.group(2)}'{m.group(3)}>",
        content
    )
    
    # 构建 Markdown 文件内容
    md_content = f"# {article.title}\n\n"
    
    if article.summary:
        md_content += f"> {article.summary}\n\n"
    
    if article.cover_image:
        cover_url = article.cover_image if article.cover_image.startswith('http') else f"{base_url}{article.cover_image}"
        md_content += f"![封面]({cover_url})\n\n"
    
    md_content += content
    
    # 添加导出信息
    md_content += f"\n\n---\n\n"
    md_content += f"*导出时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*\n"
    md_content += f"*原文链接: {base_url}/article/{article.slug}*\n"
    
    # 返回文件下载
    filename = f"{article.title.replace(' ', '_')}.md"
    return StreamingResponse(
        io.BytesIO(md_content.encode('utf-8')),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename.encode('utf-8').decode('latin-1')}"}
    )
