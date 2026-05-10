"""
小智笔记 - 配置文件
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用配置
    APP_NAME: str = "小智笔记 API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "小智笔记后端API服务"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 6789
    
    # 数据库配置 - MySQL
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/xiaozhi_notes?charset=utf8mb4"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7天
    
    # 密码加密
    BCRYPT_ROUNDS: int = 12
    
    # 豆包AI配置
    DOUBAO_API_KEY: str = ""
    DOUBAO_MODEL: str = "doubao-pro-32k"
    DOUBAO_LITE_MODEL: str = "doubao-lite-32k"
    DOUBAO_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    
    # AI功能配置
    AI_ENABLED: bool = True
    AI_MAX_TOKENS_PER_REQUEST: int = 4000
    AI_DAILY_LIMIT_PER_USER: int = 100
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


settings = get_settings()
