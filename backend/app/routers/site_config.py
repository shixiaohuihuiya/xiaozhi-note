"""
站点配置路由
"""
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import SiteConfig, User
from schemas.common import ResponseModel
from dependencies import get_current_active_user

router = APIRouter()


class SiteThemeConfig(BaseModel):
    """站点主题配置"""
    primary_color: str = Field(default="#1890ff", description="主题色")
    dark_mode: bool = Field(default=False, description="暗色模式")


@router.get("/theme", response_model=ResponseModel[dict])
async def get_theme_config(
    db: AsyncSession = Depends(get_db)
):
    """获取站点主题配置"""
    # 获取主题色
    result = await db.execute(
        select(SiteConfig).where(SiteConfig.key == "theme_primary_color")
    )
    color_config = result.scalar_one_or_none()
    
    # 获取暗色模式
    result = await db.execute(
        select(SiteConfig).where(SiteConfig.key == "theme_dark_mode")
    )
    dark_mode_config = result.scalar_one_or_none()
    
    return ResponseModel(
        code=200,
        message="success",
        data={
            "primary_color": color_config.value if color_config else "#1890ff",
            "dark_mode": dark_mode_config.value == "true" if dark_mode_config else False
        }
    )


@router.put("/theme", response_model=ResponseModel[dict])
async def update_theme_config(
    config: SiteThemeConfig,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新站点主题配置（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    # 更新主题色
    result = await db.execute(
        select(SiteConfig).where(SiteConfig.key == "theme_primary_color")
    )
    color_config = result.scalar_one_or_none()
    
    if color_config:
        color_config.value = config.primary_color
    else:
        color_config = SiteConfig(
            key="theme_primary_color",
            value=config.primary_color,
            description="站点主题色"
        )
        db.add(color_config)
    
    # 更新暗色模式
    result = await db.execute(
        select(SiteConfig).where(SiteConfig.key == "theme_dark_mode")
    )
    dark_mode_config = result.scalar_one_or_none()
    
    if dark_mode_config:
        dark_mode_config.value = "true" if config.dark_mode else "false"
    else:
        dark_mode_config = SiteConfig(
            key="theme_dark_mode",
            value="true" if config.dark_mode else "false",
            description="站点暗色模式"
        )
        db.add(dark_mode_config)
    
    await db.commit()
    
    return ResponseModel(
        code=200,
        message="主题配置已更新",
        data={
            "primary_color": config.primary_color,
            "dark_mode": config.dark_mode
        }
    )


@router.get("/info", response_model=ResponseModel[dict])
async def get_site_info(
    db: AsyncSession = Depends(get_db)
):
    """获取站点信息"""
    from models import User, Article
    from datetime import datetime

    configs = {}
    result = await db.execute(select(SiteConfig))
    for config in result.scalars().all():
        configs[config.key] = config.value

    # 网站运行时间
    now = datetime.utcnow()
    oldest_user = await db.execute(select(func.min(User.created_at)))
    oldest_article = await db.execute(select(func.min(Article.created_at)))
    oldest = min(
        oldest_user.scalar() or now,
        oldest_article.scalar() or now
    )
    site_uptime_days = (now - oldest).days + 1

    return ResponseModel(
        code=200,
        message="success",
        data={
            "title": configs.get("site_title", "小智笔记"),
            "description": configs.get("site_description", "智能写作助手，让创作更轻松"),
            "logo": configs.get("site_logo", ""),
            "icp": configs.get("site_icp", ""),
            "footer": configs.get("site_footer", ""),
            "code_copy_suffix": configs.get("site_code_copy_suffix", ""),
            "site_uptime_days": site_uptime_days
        }
    )


@router.put("/info", response_model=ResponseModel[dict])
async def update_site_info(
    data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新站点信息（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    key_mapping = {
        "title": "site_title",
        "description": "site_description",
        "logo": "site_logo",
        "icp": "site_icp",
        "footer": "site_footer",
        "code_copy_suffix": "site_code_copy_suffix"
    }
    
    for key, db_key in key_mapping.items():
        if key in data:
            result = await db.execute(
                select(SiteConfig).where(SiteConfig.key == db_key)
            )
            config = result.scalar_one_or_none()
            
            if config:
                config.value = data[key]
            else:
                config = SiteConfig(
                    key=db_key,
                    value=data[key],
                    description=f"站点{key}"
                )
                db.add(config)
    
    await db.commit()
    
    return ResponseModel(code=200, message="站点信息已更新", data=None)


@router.get("/ai", response_model=ResponseModel[dict])
async def get_ai_config(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取AI配置（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    result = await db.execute(select(SiteConfig))
    configs = {c.key: c.value for c in result.scalars().all()}
    
    api_key = configs.get("ai_api_key", "")
    # 掩码处理：只显示前4位和后4位，中间用****代替
    masked_key = ""
    if api_key and len(api_key) > 8:
        masked_key = api_key[:4] + "****" + api_key[-4:]
    elif api_key:
        masked_key = "****"
    
    return ResponseModel(
        code=200,
        message="success",
        data={
            "api_key": masked_key,
            "model": configs.get("ai_model", "doubao-pro-32k"),
            "lite_model": configs.get("ai_lite_model", "doubao-lite-32k"),
            "base_url": configs.get("ai_base_url", "https://ark.cn-beijing.volces.com/api/v3"),
            "enabled": configs.get("ai_enabled", "true").lower() == "true",
            "max_tokens": int(configs.get("ai_max_tokens", "4000")),
            "daily_limit": int(configs.get("ai_daily_limit", "100"))
        }
    )


@router.put("/ai", response_model=ResponseModel[dict])
async def update_ai_config(
    data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新AI配置（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    key_mapping = {
        "api_key": "ai_api_key",
        "model": "ai_model",
        "lite_model": "ai_lite_model",
        "base_url": "ai_base_url",
        "enabled": "ai_enabled",
        "max_tokens": "ai_max_tokens",
        "daily_limit": "ai_daily_limit"
    }
    
    for key, db_key in key_mapping.items():
        if key not in data:
            continue
        
        result = await db.execute(
            select(SiteConfig).where(SiteConfig.key == db_key)
        )
        config = result.scalar_one_or_none()
        
        value = str(data[key])
        # 布尔值转为小写字符串
        if isinstance(data[key], bool):
            value = "true" if data[key] else "false"
        # API Key 特殊处理：如果传入的是掩码（包含****），则不更新
        if key == "api_key" and "****" in value:
            continue
        
        if config:
            config.value = value
        else:
            config = SiteConfig(
                key=db_key,
                value=value,
                description=f"AI配置-{key}"
            )
            db.add(config)
    
    await db.commit()
    
    # 刷新内存中的配置
    from config import settings
    result = await db.execute(select(SiteConfig))
    for c in result.scalars().all():
        if c.key == "ai_api_key":
            settings.DOUBAO_API_KEY = c.value
        elif c.key == "ai_model":
            settings.DOUBAO_MODEL = c.value
        elif c.key == "ai_lite_model":
            settings.DOUBAO_LITE_MODEL = c.value
        elif c.key == "ai_base_url":
            settings.DOUBAO_BASE_URL = c.value
        elif c.key == "ai_enabled":
            settings.AI_ENABLED = c.value.lower() == "true"
        elif c.key == "ai_max_tokens":
            settings.AI_MAX_TOKENS_PER_REQUEST = int(c.value)
        elif c.key == "ai_daily_limit":
            settings.AI_DAILY_LIMIT_PER_USER = int(c.value)
    
    # 刷新AI服务实例
    from services.ai_service import ai_service
    if settings.DOUBAO_API_KEY:
        from openai import AsyncOpenAI
        ai_service.client = AsyncOpenAI(
            api_key=settings.DOUBAO_API_KEY,
            base_url=settings.DOUBAO_BASE_URL,
            timeout=180.0
        )
    else:
        ai_service.client = None
    ai_service.model = settings.DOUBAO_MODEL
    
    return ResponseModel(code=200, message="AI配置已更新", data=None)
