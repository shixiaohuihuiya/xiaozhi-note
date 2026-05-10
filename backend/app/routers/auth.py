"""
认证路由 - 注册/登录/Token刷新
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User
from schemas.user import LoginRequest, RegisterRequest, UserResponse
from schemas.common import ResponseModel, TokenResponse
from utils.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from utils.captcha import generate_captcha, verify_captcha

router = APIRouter()


@router.get("/captcha", response_model=ResponseModel[dict])
async def get_captcha():
    """获取图形验证码"""
    key, image_base64 = generate_captcha()
    return ResponseModel(
        code=200,
        message="success",
        data={"key": key, "image": image_base64}
    )


@router.post("/register", response_model=ResponseModel[UserResponse])
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    - 验证验证码
    - 检查用户名是否已存在
    - 检查邮箱是否已存在
    - 创建新用户
    """
    # 验证验证码
    if not verify_captcha(request.captcha_key, request.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # 检查用户名
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建用户
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=get_password_hash(request.password),
        nickname=request.username,  # 默认昵称为用户名
        role=0,  # 普通用户
        status=1  # 正常状态
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return ResponseModel(
        code=200,
        message="注册成功",
        data=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=ResponseModel[dict])
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    - 支持用户名或邮箱登录
    - 验证密码
    - 返回JWT Token
    """
    # 验证验证码
    if not verify_captcha(request.captcha_key, request.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # 查询用户（按用户名或邮箱）
    result = await db.execute(
        select(User).where(
            (User.username == request.account) | (User.email == request.account)
        )
    )
    user = result.scalar_one_or_none()
    
    # 验证用户存在且密码正确
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查用户状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    # 更新最后登录时间
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # 生成Token
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return ResponseModel(
        code=200,
        message="登录成功",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 86400,  # 24小时
            "must_change_password": user.must_change_password,
            "user": UserResponse.model_validate(user)
        }
    )


@router.post("/refresh", response_model=ResponseModel[dict])
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新Access Token
    
    - 使用Refresh Token获取新的Access Token
    """
    # 验证Refresh Token
    user_id = verify_token(refresh_token, token_type="refresh")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 生成新的Access Token
    new_access_token = create_access_token(user.id)
    
    return ResponseModel(
        code=200,
        message="刷新成功",
        data={
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": 86400
        }
    )


@router.post("/logout", response_model=ResponseModel[None])
async def logout():
    """
    用户退出
    
    - 前端清除Token即可
    - 后端可在此处理Token黑名单（如需）
    """
    return ResponseModel(
        code=200,
        message="退出成功",
        data=None
    )
