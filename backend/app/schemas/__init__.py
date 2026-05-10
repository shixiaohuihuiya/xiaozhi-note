"""
Pydantic Schemas
"""
from schemas.user import UserBase, UserCreate, UserUpdate, UserResponse, UserInDB
from schemas.article import ArticleBase, ArticleCreate, ArticleUpdate, ArticleResponse, ArticleListResponse
from schemas.category import CategoryBase, CategoryCreate, CategoryUpdate, CategoryResponse
from schemas.tag import TagBase, TagCreate, TagResponse
from schemas.comment import CommentBase, CommentCreate, CommentResponse
from schemas.ai import AIAssistRequest, AIChatRequest, AIAssistResponse, AIChatResponse
from schemas.common import ResponseModel, PaginationParams, PaginatedResponse

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserInDB",
    # Article schemas
    "ArticleBase", "ArticleCreate", "ArticleUpdate", "ArticleResponse", "ArticleListResponse",
    # Category schemas
    "CategoryBase", "CategoryCreate", "CategoryUpdate", "CategoryResponse",
    # Tag schemas
    "TagBase", "TagCreate", "TagResponse",
    # Comment schemas
    "CommentBase", "CommentCreate", "CommentResponse",
    # AI schemas
    "AIAssistRequest", "AIChatRequest", "AIAssistResponse", "AIChatResponse",
    # Common schemas
    "ResponseModel", "PaginationParams", "PaginatedResponse"
]
