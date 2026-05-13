"""
用户Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator


class UserBase(BaseModel):
    """用户基础Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")


class UserCreate(UserBase):
    """用户创建Schema"""
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名只能包含字母、数字、下划线"""
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v


class UserUpdate(BaseModel):
    """用户更新Schema"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")


class UserPasswordUpdate(BaseModel):
    """密码更新Schema"""
    old_password: Optional[str] = Field(None, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=32, description="新密码")


class UserResponse(BaseModel):
    """用户响应Schema"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")  # Use str instead of EmailStr to allow .local domains
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    role: int = Field(..., description="角色: 0-普通用户, 1-管理员, 2-超级管理员")
    status: int = Field(..., description="状态: 0-禁用, 1-正常")
    is_verified: bool = Field(..., description="邮箱是否验证")
    must_change_password: bool = Field(False, description="是否必须修改密码")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime = Field(..., description="创建时间")
    article_count: Optional[int] = Field(0, description="文章数量")
    comment_count: Optional[int] = Field(0, description="评论数量")
    
    class Config:
        from_attributes = True


class UserSimpleResponse(BaseModel):
    """用户简要信息Schema"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    
    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """数据库中的用户Schema（包含敏感信息）"""
    id: int
    password_hash: str
    role: int
    status: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求Schema"""
    account: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    captcha_key: str = Field(..., description="验证码key")
    captcha_code: str = Field(..., description="验证码")


class RegisterRequest(BaseModel):
    """注册请求Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    captcha_key: str = Field(..., description="验证码key")
    captcha_code: str = Field(..., description="验证码")
