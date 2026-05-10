"""
分类Schema
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """分类基础Schema"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    slug: str = Field(..., min_length=1, max_length=50, description="URL标识")
    description: Optional[str] = Field(None, max_length=255, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: int = Field(default=0, description="排序顺序")


class CategoryCreate(CategoryBase):
    """分类创建Schema"""
    pass


class CategoryUpdate(BaseModel):
    """分类更新Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    """分类响应Schema"""
    id: int
    article_count: int
    
    class Config:
        from_attributes = True


class CategoryTreeResponse(CategoryResponse):
    """分类树响应Schema"""
    children: Optional[List["CategoryTreeResponse"]] = []
