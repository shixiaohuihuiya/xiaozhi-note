"""
标签路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import get_db
from models import Tag, ArticleTag, Article
from schemas.common import ResponseModel, PaginatedResponse, PaginationParams
from dependencies import require_admin

router = APIRouter()


@router.get("", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_tags(
    sort: str = "hot",  # hot, name
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """获取标签列表（动态计算文章数量）"""
    query = select(Tag)

    if sort == "hot":
        query = query.order_by(desc(Tag.article_count))
    else:
        query = query.order_by(Tag.name)

    # 统计总数
    count_result = await db.execute(select(func.count(Tag.id)))
    total = count_result.scalar()

    # 分页
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    tags = result.scalars().all()

    # 批量统计各标签的文章数（只统计已发布且未删除的文章）
    if tags:
        tag_ids = [t.id for t in tags]
        count_result = await db.execute(
            select(ArticleTag.tag_id, func.count(ArticleTag.id))
            .join(Article, ArticleTag.article_id == Article.id)
            .where(
                ArticleTag.tag_id.in_(tag_ids),
                Article.status == 1,
                Article.deleted_at.is_(None)
            )
            .group_by(ArticleTag.tag_id)
        )
        count_map = {tid: cnt for tid, cnt in count_result.all()}
    else:
        count_map = {}

    items = [
        {
            "id": tag.id,
            "name": tag.name,
            "slug": tag.slug,
            "color": tag.color,
            "article_count": count_map.get(tag.id, 0)
        }
        for tag in tags
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


@router.get("/hot", response_model=ResponseModel[List[dict]])
async def get_hot_tags(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取热门标签（动态计算文章数量）"""
    result = await db.execute(
        select(Tag).order_by(desc(Tag.article_count)).limit(limit)
    )
    tags = result.scalars().all()

    # 批量统计各标签的文章数
    if tags:
        tag_ids = [t.id for t in tags]
        count_result = await db.execute(
            select(ArticleTag.tag_id, func.count(ArticleTag.id))
            .join(Article, ArticleTag.article_id == Article.id)
            .where(
                ArticleTag.tag_id.in_(tag_ids),
                Article.status == 1,
                Article.deleted_at.is_(None)
            )
            .group_by(ArticleTag.tag_id)
        )
        count_map = {tid: cnt for tid, cnt in count_result.all()}
    else:
        count_map = {}

    data = [
        {
            "id": tag.id,
            "name": tag.name,
            "slug": tag.slug,
            "color": tag.color,
            "article_count": count_map.get(tag.id, 0)
        }
        for tag in tags
    ]

    return ResponseModel(code=200, message="success", data=data)


@router.post("", response_model=ResponseModel[dict])
async def create_tag(
    name: str,
    slug: str,
    color: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """创建标签（管理员）"""
    # 检查名称或slug是否已存在
    result = await db.execute(
        select(Tag).where((Tag.name == name) | (Tag.slug == slug))
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签名称或标识已存在"
        )
    
    tag = Tag(name=name, slug=slug, color=color)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    
    return ResponseModel(
        code=200,
        message="创建成功",
        data={
            "id": tag.id,
            "name": tag.name,
            "slug": tag.slug,
            "color": tag.color
        }
    )


@router.put("/{tag_id}", response_model=ResponseModel[dict])
async def update_tag(
    tag_id: int,
    name: Optional[str] = None,
    slug: Optional[str] = None,
    color: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """更新标签（管理员）"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    # 检查唯一性
    if name and name != tag.name:
        result = await db.execute(select(Tag).where(Tag.name == name))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签名称已存在"
            )
        tag.name = name
    
    if slug and slug != tag.slug:
        result = await db.execute(select(Tag).where(Tag.slug == slug))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签标识已存在"
            )
        tag.slug = slug
    
    if color is not None:
        tag.color = color
    
    await db.commit()
    await db.refresh(tag)
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data={
            "id": tag.id,
            "name": tag.name,
            "slug": tag.slug,
            "color": tag.color
        }
    )


@router.delete("/{tag_id}", response_model=ResponseModel[None])
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """删除标签（管理员）"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    await db.delete(tag)
    await db.commit()
    
    return ResponseModel(code=200, message="删除成功", data=None)
