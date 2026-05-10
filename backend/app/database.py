"""
小智笔记 - 数据库连接配置
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 调试模式下打印SQL
    poolclass=NullPool,   # 异步模式下使用NullPool
    future=True
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 声明性基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    获取数据库会话 - 依赖注入使用
    
    Usage:
        @get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库 - 创建所有表、添加缺失的列、插入默认数据"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # 尝试添加 must_change_password 列（如果不存在）
    await _add_missing_columns()
    # 插入默认超级管理员
    await _seed_superadmin()
    # 插入默认标签和分类
    await _seed_default_tags()
    await _seed_default_categories()
    # 从数据库加载AI配置（覆盖.env默认值）
    await _load_ai_config_from_db()


async def _add_missing_columns():
    """为现有表添加缺失的列"""
    from sqlalchemy import text
    async with engine.begin() as conn:
        try:
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT FALSE NOT NULL"
            ))
            print("✅ 已添加 must_change_password 列")
        except Exception:
            pass

        try:
            await conn.execute(text(
                "ALTER TABLE articles ADD COLUMN needs_reapproval BOOLEAN DEFAULT FALSE NOT NULL"
            ))
            print("✅ 已添加 articles.needs_reapproval 列")
        except Exception:
            pass

        # Add new columns to notifications table if they don't exist
        try:
            await conn.execute(text(
                "ALTER TABLE notifications MODIFY COLUMN user_id BIGINT COMMENT '接收用户ID，为空表示全员通知'"
            ))
            print("✅ 已更新 notifications.user_id 列为可空")
        except Exception:
            pass

        try:
            await conn.execute(text(
                "ALTER TABLE notifications ADD COLUMN is_system BOOLEAN DEFAULT FALSE NOT NULL COMMENT '是否为系统/管理员发送的通知'"
            ))
            print("✅ 已添加 notifications.is_system 列")
        except Exception:
            pass

        try:
            await conn.execute(text(
                "ALTER TABLE notifications ADD COLUMN created_by BIGINT COMMENT '创建者ID（管理员）'"
            ))
            print("✅ 已添加 notifications.created_by 列")
        except Exception:
            pass

        try:
            await conn.execute(text(
                "ALTER TABLE notifications ADD CONSTRAINT fk_notifications_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL"
            ))
            print("✅ 已添加 notifications.created_by 外键约束")
        except Exception:
            pass

        try:
            await conn.execute(text('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT COMMENT '接收用户ID，为空表示全员通知',
                    type SMALLINT NOT NULL COMMENT '类型: 1-文章下架, 2-评论审核不通过, 3-新评论, 4-系统公告, 5-管理员通知',
                    title VARCHAR(200) NOT NULL,
                    content TEXT,
                    related_id BIGINT,
                    is_read BOOLEAN DEFAULT FALSE NOT NULL,
                    is_system BOOLEAN DEFAULT FALSE NOT NULL COMMENT '是否为系统/管理员发送的通知',
                    created_by BIGINT COMMENT '创建者ID（管理员）',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    INDEX idx_user_id (user_id),
                    INDEX idx_is_read (is_read),
                    INDEX idx_created (created_at),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''))
            print("✅ 已创建 notifications 表")
        except Exception:
            pass


async def _seed_superadmin():
    """创建默认超级管理员（如果不存在任何超级管理员）"""
    from sqlalchemy import select
    from models import User
    from utils.security import get_password_hash

    superadmin_defaults = {
        "username": "superadmin",
        "email": "superadmin@xiaozhi.local",
        "nickname": "超级管理员",
        "password": "admin123456",
    }

    async with AsyncSessionLocal() as db:
        try:
            # 检查是否已存在超级管理员
            result = await db.execute(select(User).where(User.role == 2))
            existing = result.scalar_one_or_none()
            if existing:
                return

            superadmin = User(
                username=superadmin_defaults["username"],
                email=superadmin_defaults["email"],
                nickname=superadmin_defaults["nickname"],
                password_hash=get_password_hash(superadmin_defaults["password"]),
                role=2,
                status=1,
                is_verified=True
            )
            db.add(superadmin)
            await db.commit()
            print(f"✅ 已创建默认超级管理员 (用户名: {superadmin_defaults['username']}, 密码: {superadmin_defaults['password']})")
            print("⚠️  请尽快登录后修改默认密码！")
        except Exception as e:
            await db.rollback()
            print(f"⚠️ 创建超级管理员失败: {e}")
        finally:
            await db.close()


async def _seed_default_categories():
    """插入默认分类（如果不存在）"""
    from sqlalchemy import select
    from models import Category
    default_categories = [
        {"name": "技术分享", "slug": "tech-share", "description": "技术文章与经验分享", "sort_order": 0},
        {"name": "学习笔记", "slug": "study-notes", "description": "学习过程中的记录与总结", "sort_order": 1},
        {"name": "项目实战", "slug": "project-practice", "description": "实际项目开发经验", "sort_order": 2},
        {"name": "问题解决", "slug": "problem-solving", "description": "Bug修复与问题排查", "sort_order": 3},
        {"name": "随笔杂谈", "slug": "random-thoughts", "description": "生活感悟与随想", "sort_order": 4},
    ]
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Category.id).limit(1))
            if result.scalar_one_or_none() is not None:
                return
            for cat_data in default_categories:
                cat = Category(**cat_data)
                db.add(cat)
            await db.commit()
            print(f"✅ 已插入 {len(default_categories)} 个默认分类")
        except Exception as e:
            await db.rollback()
            print(f"⚠️ 插入默认分类失败: {e}")
        finally:
            await db.close()


async def _seed_default_tags():
    """插入默认技术标签（如果不存在）"""
    from sqlalchemy import select
    from models import Tag
    default_tags = [
        {"name": "Python", "slug": "python", "color": "#306998"},
        {"name": "JavaScript", "slug": "javascript", "color": "#f7df1e"},
        {"name": "Vue", "slug": "vue", "color": "#42b883"},
        {"name": "React", "slug": "react", "color": "#61dafb"},
        {"name": "Node.js", "slug": "nodejs", "color": "#339933"},
        {"name": "Java", "slug": "java", "color": "#007396"},
        {"name": "Go", "slug": "go", "color": "#00add8"},
        {"name": "Docker", "slug": "docker", "color": "#2496ed"},
        {"name": "Linux", "slug": "linux", "color": "#fcc624"},
        {"name": "MySQL", "slug": "mysql", "color": "#4479a1"},
        {"name": "Redis", "slug": "redis", "color": "#dc382d"},
        {"name": "AI", "slug": "ai", "color": "#9c27b0"},
        {"name": "前端", "slug": "frontend", "color": "#ff9800"},
        {"name": "后端", "slug": "backend", "color": "#795548"},
        {"name": "算法", "slug": "algorithm", "color": "#e91e63"},
        {"name": "数据库", "slug": "database", "color": "#3f51b5"},
        {"name": "运维", "slug": "devops", "color": "#607d8b"},
        {"name": "网络安全", "slug": "cybersecurity", "color": "#4caf50"},
        {"name": "Git", "slug": "git", "color": "#f05032"},
        {"name": "Markdown", "slug": "markdown", "color": "#000000"},
    ]
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Tag.id).limit(1))
            if result.scalar_one_or_none() is not None:
                return  # 已有标签，跳过
            for tag_data in default_tags:
                tag = Tag(**tag_data)
                db.add(tag)
            await db.commit()
            print(f"✅ 已插入 {len(default_tags)} 个默认标签")
        except Exception as e:
            await db.rollback()
            print(f"⚠️ 插入默认标签失败: {e}")
        finally:
            await db.close()


async def _load_ai_config_from_db():
    """从数据库加载AI配置，覆盖.env默认值"""
    from sqlalchemy import select
    from models import SiteConfig
    from config import settings
    from services.ai_service import ai_service
    from openai import AsyncOpenAI
    
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(SiteConfig))
            configs = {c.key: c.value for c in result.scalars().all()}
            
            if configs.get("ai_api_key"):
                settings.DOUBAO_API_KEY = configs["ai_api_key"]
            if configs.get("ai_model"):
                settings.DOUBAO_MODEL = configs["ai_model"]
            if configs.get("ai_lite_model"):
                settings.DOUBAO_LITE_MODEL = configs["ai_lite_model"]
            if configs.get("ai_base_url"):
                settings.DOUBAO_BASE_URL = configs["ai_base_url"]
            if configs.get("ai_enabled") is not None:
                settings.AI_ENABLED = configs["ai_enabled"].lower() == "true"
            if configs.get("ai_max_tokens"):
                settings.AI_MAX_TOKENS_PER_REQUEST = int(configs["ai_max_tokens"])
            if configs.get("ai_daily_limit"):
                settings.AI_DAILY_LIMIT_PER_USER = int(configs["ai_daily_limit"])
            
            # 刷新AI服务实例
            if settings.DOUBAO_API_KEY:
                ai_service.client = AsyncOpenAI(
                    api_key=settings.DOUBAO_API_KEY,
                    base_url=settings.DOUBAO_BASE_URL,
                    timeout=180.0
                )
            else:
                ai_service.client = None
            ai_service.model = settings.DOUBAO_MODEL
            
            print("✅ AI配置已从数据库加载")
        except Exception as e:
            print(f"⚠️ 加载AI配置失败: {e}")
        finally:
            await db.close()


async def drop_db():
    """删除所有表 - 谨慎使用"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
