"""
小智笔记 - FastAPI主应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from config import settings
from database import init_db
from routers import auth, user, article, category, tag, comment, admin, ai, guestbook, site_config, upload, notification


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    启动时执行:
    - 初始化数据库表
    
    关闭时执行:
    - 清理资源
    """
    # 启动
    print("🚀 正在初始化数据库...")
    await init_db()
    print("✅ 数据库初始化完成")
    
    yield
    
    # 关闭
    print("👋 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(user.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(article.router, prefix="/api/v1/articles", tags=["文章"])
app.include_router(category.router, prefix="/api/v1/categories", tags=["分类"])
app.include_router(tag.router, prefix="/api/v1/tags", tags=["标签"])
app.include_router(comment.router, prefix="/api/v1", tags=["评论"])
app.include_router(guestbook.router, prefix="/api/v1/guestbooks", tags=["留言墙"])
app.include_router(site_config.router, prefix="/api/v1/config", tags=["站点配置"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI助手"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["后台管理"])
app.include_router(upload.router, prefix="/api/v1/uploads", tags=["文件上传"])
app.include_router(notification.router, prefix="/api/v1/notifications", tags=["通知"])

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# 静态文件服务 - 上传的图片
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/")
async def root():
    """根路径 - API信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    # 使用相对导入路径启动
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
