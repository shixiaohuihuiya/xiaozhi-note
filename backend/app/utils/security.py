"""
安全工具 - 密码加密和JWT处理
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
import bcrypt
from config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 验证结果
    """
    # bcrypt 限制密码长度为 72 字节
    password_bytes = plain_password[:72].encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    # bcrypt 限制密码长度为 72 字节
    password_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问Token
    
    Args:
        user_id: 用户ID
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT Token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """
    创建刷新Token
    
    Args:
        user_id: 用户ID
        
    Returns:
        str: JWT Refresh Token
    """
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    解码Token
    
    Args:
        token: JWT Token
        
    Returns:
        Optional[dict]: Token载荷或None
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[int]:
    """
    验证Token
    
    Args:
        token: JWT Token
        token_type: Token类型 (access/refresh)
        
    Returns:
        Optional[int]: 用户ID或None
    """
    payload = decode_token(token)
    if payload is None:
        return None
    
    # 验证Token类型
    if payload.get("type") != token_type:
        return None
    
    # 获取用户ID
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    return int(user_id)


def generate_slug(text: str) -> str:
    """
    生成URL友好的slug
    
    Args:
        text: 原始文本
        
    Returns:
        str: slug
    """
    import re
    import unicodedata
    
    # 转换为小写
    text = text.lower()
    
    # 移除音标符号
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    
    # 替换非字母数字字符为连字符
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # 移除首尾连字符
    text = text.strip('-')
    
    # 限制长度
    return text[:200]
