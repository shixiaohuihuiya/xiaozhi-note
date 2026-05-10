"""
通用Schema
"""
from typing import TypeVar, Generic, Optional, List, Any
from pydantic import BaseModel, Field


T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="消息")
    data: Optional[T] = Field(default=None, description="数据")

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")
    
    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页数量")
    pages: int = Field(description="总页数")
    items: List[T] = Field(description="数据列表")
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int):
        """创建分页响应"""
        pages = (total + size - 1) // size
        return cls(
            total=total,
            page=page,
            size=size,
            pages=pages,
            items=items
        )


class TokenPayload(BaseModel):
    """Token载荷"""
    sub: Optional[int] = None  # 用户ID
    exp: Optional[int] = None  # 过期时间
    type: Optional[str] = None  # token类型: access/refresh


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
