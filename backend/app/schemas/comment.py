"""
评论Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    """评论基础Schema"""
    content: str = Field(..., min_length=2, max_length=1000, description="评论内容")
    parent_id: Optional[int] = Field(None, description="父评论ID")


class CommentCreate(CommentBase):
    """评论创建Schema"""
    pass


class CommentUpdate(BaseModel):
    """评论更新Schema"""
    content: Optional[str] = Field(None, min_length=2, max_length=1000)


class CommentUser(BaseModel):
    """评论用户信息"""
    id: int
    username: str
    nickname: Optional[str]
    avatar: Optional[str]
    
    class Config:
        from_attributes = True


class CommentReply(BaseModel):
    """评论回复Schema"""
    id: int
    content: str
    user: CommentUser
    is_author: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommentResponse(CommentBase):
    """评论响应Schema"""
    id: int
    article_id: int
    user: CommentUser
    like_count: int
    is_author: bool
    status: int
    created_at: datetime
    replies: Optional[List[CommentReply]] = []
    
    class Config:
        from_attributes = True
