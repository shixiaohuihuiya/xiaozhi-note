"""
分类路由
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Category, Article
from schemas.common import ResponseModel
from dependencies import require_admin

router = APIRouter()


class CategoryCreate(BaseModel):
    """创建分类请求"""
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    """更新分类请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


@router.get("", response_model=ResponseModel[List[dict]])
async def get_categories(
    tree: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """获取分类列表（动态计算文章数量）"""
    if tree:
        # 获取顶级分类
        result = await db.execute(
            select(Category).where(Category.parent_id.is_(None)).order_by(Category.sort_order)
        )
        categories = result.scalars().all()

        # 批量统计各分类的文章数
        category_ids = [c.id for c in categories]
        for child in categories:
            if child.children:
                category_ids.extend([c.id for c in child.children])

        count_result = await db.execute(
            select(Article.category_id, func.count(Article.id))
            .where(
                Article.category_id.in_(category_ids),
                Article.status == 1,
                Article.deleted_at.is_(None)
            )
            .group_by(Article.category_id)
        )
        count_map = {cid: cnt for cid, cnt in count_result.all()}

        # 递归构建树形结构
        def build_tree(cat):
            return {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "description": cat.description,
                "sort_order": cat.sort_order,
                "article_count": count_map.get(cat.id, 0),
                "children": [build_tree(child) for child in cat.children] if cat.children else []
            }

        data = [build_tree(cat) for cat in categories]
    else:
        # 扁平列表
        result = await db.execute(select(Category).order_by(Category.sort_order))
        categories = result.scalars().all()

        # 批量统计各分类的文章数
        category_ids = [c.id for c in categories]
        count_result = await db.execute(
            select(Article.category_id, func.count(Article.id))
            .where(
                Article.category_id.in_(category_ids),
                Article.status == 1,
                Article.deleted_at.is_(None)
            )
            .group_by(Article.category_id)
        )
        count_map = {cid: cnt for cid, cnt in count_result.all()}

        data = [
            {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "description": cat.description,
                "parent_id": cat.parent_id,
                "sort_order": cat.sort_order,
                "article_count": count_map.get(cat.id, 0)
            }
            for cat in categories
        ]

    return ResponseModel(code=200, message="success", data=data)


@router.get("/{slug}", response_model=ResponseModel[dict])
async def get_category(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """获取分类详情"""
    result = await db.execute(select(Category).where(Category.slug == slug))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    return ResponseModel(
        code=200,
        message="success",
        data={
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "parent_id": category.parent_id,
            "article_count": category.article_count
        }
    )


@router.post("", response_model=ResponseModel[dict])
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """创建分类（管理员）"""
    # 检查slug是否已存在
    result = await db.execute(select(Category).where(Category.slug == data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类标识已存在"
        )
    
    category = Category(
        name=data.name,
        slug=data.slug,
        description=data.description,
        parent_id=data.parent_id,
        sort_order=data.sort_order
    )
    
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return ResponseModel(
        code=200,
        message="创建成功",
        data={
            "id": category.id,
            "name": category.name,
            "slug": category.slug
        }
    )


@router.put("/{category_id}", response_model=ResponseModel[dict])
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """更新分类（管理员）"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 检查slug唯一性
    if data.slug and data.slug != category.slug:
        result = await db.execute(select(Category).where(Category.slug == data.slug))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类标识已存在"
            )
        category.slug = data.slug
    
    if data.name is not None:
        category.name = data.name
    if data.description is not None:
        category.description = data.description
    if data.parent_id is not None:
        category.parent_id = data.parent_id
    if data.sort_order is not None:
        category.sort_order = data.sort_order
    
    await db.commit()
    await db.refresh(category)
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data={
            "id": category.id,
            "name": category.name,
            "slug": category.slug
        }
    )


@router.delete("/{category_id}", response_model=ResponseModel[None])
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """删除分类（管理员）"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 检查是否有子分类
    if category.children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先删除子分类"
        )
    
    # 将该分类下的文章设为无分类
    await db.execute(
        select(Article).where(Article.category_id == category_id)
    )
    
    await db.delete(category)
    await db.commit()
    
    return ResponseModel(code=200, message="删除成功", data=None)
