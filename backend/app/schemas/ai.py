"""
AI Schema
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AIAssistRequest(BaseModel):
    """AI写作辅助请求"""
    action: str = Field(..., description="操作类型: continue/polish/expand/title/summary")
    content: str = Field(..., description="当前内容")
    context: Optional[str] = Field(None, description="上下文信息")
    tone: str = Field(default="professional", description="语气风格")
    length: str = Field(default="medium", description="长度")


class AIChatRequest(BaseModel):
    """AI对话请求"""
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")
    article_id: Optional[int] = Field(None, description="关联文章ID")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class AICheckRequest(BaseModel):
    """AI内容检查请求"""
    content: str = Field(..., description="需要检查的文本")


class AISuggestion(BaseModel):
    """AI建议"""
    type: str = Field(..., description="类型: spelling/grammar/punctuation")
    position: str = Field(..., description="位置")
    original: str = Field(..., description="原文")
    suggestion: str = Field(..., description="建议修改")
    explanation: str = Field(..., description="说明")


class AIAssistResponse(BaseModel):
    """AI写作辅助响应"""
    result: str = Field(..., description="AI生成的结果")
    tokens_used: int = Field(..., description="消耗的token数")


class AIChatResponse(BaseModel):
    """AI对话响应"""
    session_id: str = Field(..., description="会话ID")
    reply: str = Field(..., description="AI回复")
    tokens_used: int = Field(..., description="消耗的token数")


class AICheckResponse(BaseModel):
    """AI内容检查响应"""
    has_errors: bool = Field(..., description="是否有错误")
    suggestions: List[AISuggestion] = Field(default=[], description="建议列表")


class AIConversationItem(BaseModel):
    """AI对话记录项"""
    id: int
    role: int = Field(..., description="1-用户, 2-AI")
    content: str
    model: Optional[str]
    tokens_used: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True
