"""
标签Schema
"""
from typing import Optional
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """标签基础Schema"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    slug: str = Field(..., min_length=1, max_length=50, description="URL标识")
    color: Optional[str] = Field(None, max_length=7, description="标签颜色(HEX)")


class TagCreate(TagBase):
    """标签创建Schema"""
    pass


class TagUpdate(BaseModel):
    """标签更新Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, max_length=7)


class TagResponse(TagBase):
    """标签响应Schema"""
    id: int
    article_count: int
    
    class Config:
        from_attributes = True
