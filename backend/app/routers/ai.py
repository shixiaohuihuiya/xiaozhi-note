"""
AI路由 - 豆包AI功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database import get_db
from models import User, AIConversation
from schemas.common import ResponseModel, PaginatedResponse, PaginationParams
from dependencies import get_current_active_user
from services.ai_service import ai_service
from config import settings

router = APIRouter()


def _check_ai_enabled():
    """检查AI功能是否启用"""
    if not settings.AI_ENABLED:
        raise HTTPException(status_code=403, detail="AI功能已禁用")
    if not ai_service.client:
        raise HTTPException(status_code=503, detail="AI服务未配置，请先配置API Key")


@router.post("/assist", response_model=ResponseModel[dict])
async def ai_assist(
    action: str,  # continue, polish, expand, title, summary
    content: str,
    context: Optional[str] = None,
    tone: str = "professional",
    length: str = "medium",
    current_user: User = Depends(get_current_active_user)
):
    """
    AI写作辅助
    
    - action: continue(续写), polish(润色), expand(扩写), title(生成标题), summary(生成摘要)
    """
    _check_ai_enabled()
    try:
        result = await ai_service.assist_writing(
            action=action,
            content=content,
            context=context,
            tone=tone,
            length=length
        )
        
        return ResponseModel(
            code=200,
            message="success",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ResponseModel[dict])
async def ai_chat(
    message: str,
    session_id: Optional[str] = None,
    article_id: Optional[int] = None,
    context_type: Optional[str] = None,
    context_content: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    AI智能问答
    
    - 支持多轮对话
    - 支持上下文感知
    """
    _check_ai_enabled()
    try:
        # 构建上下文
        context = None
        if context_type and context_content:
            context = {
                "type": context_type,
                "content": context_content
            }
        
        # 调用AI服务
        result = await ai_service.chat(
            message=message,
            session_id=session_id,
            context=context
        )
        
        # 保存用户消息
        user_msg = AIConversation(
            user_id=current_user.id,
            session_id=result["session_id"],
            article_id=article_id,
            role=1,  # 用户
            content=message
        )
        db.add(user_msg)
        
        # 保存AI回复
        ai_msg = AIConversation(
            user_id=current_user.id,
            session_id=result["session_id"],
            article_id=article_id,
            role=2,  # AI
            content=result["reply"],
            model=ai_service.model,
            tokens_used=result["tokens_used"]
        )
        db.add(ai_msg)
        
        await db.commit()
        
        return ResponseModel(
            code=200,
            message="success",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check", response_model=ResponseModel[dict])
async def ai_check(
    content: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    AI内容检查
    
    - 语法检查
    - 用词建议
    """
    _check_ai_enabled()
    try:
        result = await ai_service.check_content(content)
        return ResponseModel(
            code=200,
            message="success",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_conversations(
    session_id: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取AI对话历史"""
    query = select(AIConversation).where(
        AIConversation.user_id == current_user.id
    )
    
    if session_id:
        query = query.where(AIConversation.session_id == session_id)
    
    query = query.order_by(desc(AIConversation.created_at))
    
    # 统计总数
    from sqlalchemy import func
    count_result = await db.execute(
        select(func.count(AIConversation.id)).where(
            AIConversation.user_id == current_user.id,
            AIConversation.session_id == session_id if session_id else True
        )
    )
    total = count_result.scalar()
    
    # 分页
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    items = [
        {
            "id": conv.id,
            "role": conv.role,
            "content": conv.content,
            "model": conv.model,
            "tokens_used": conv.tokens_used,
            "created_at": conv.created_at.isoformat()
        }
        for conv in conversations
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
