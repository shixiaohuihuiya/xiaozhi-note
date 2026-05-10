"""
文章Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ArticleBase(BaseModel):
    """文章基础Schema"""
    title: str = Field(..., min_length=2, max_length=200, description="文章标题")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    content: str = Field(..., description="文章内容")
    content_type: int = Field(default=1, description="内容类型: 1-Markdown, 2-HTML")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片URL")
    category_id: Optional[int] = Field(None, description="分类ID")
    tag_ids: Optional[List[int]] = Field(None, description="标签ID列表")
    status: int = Field(default=0, description="状态: 0-草稿, 1-已发布, 2-下架")
    is_top: bool = Field(default=False, description="是否置顶")


class ArticleCreate(ArticleBase):
    """文章创建Schema"""
    pass


class ArticleUpdate(BaseModel):
    """文章更新Schema"""
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    content_type: Optional[int] = None
    cover_image: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    status: Optional[int] = None
    is_top: Optional[bool] = None


class ArticleResponse(BaseModel):
    """文章响应Schema"""
    id: int
    title: str
    slug: str
    summary: Optional[str]
    content: str
    content_type: int
    cover_image: Optional[str]
    author_id: int
    category_id: Optional[int]
    status: int
    is_top: bool
    view_count: int
    like_count: int
    comment_count: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """文章列表响应Schema"""
    id: int
    title: str
    slug: str
    summary: Optional[str]
    cover_image: Optional[str]
    status: int
    view_count: int
    like_count: int
    comment_count: int
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
