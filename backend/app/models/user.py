"""
用户模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, SmallInteger, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    bio = Column(Text, nullable=True, comment="个人简介")
    role = Column(SmallInteger, default=0, nullable=False, comment="角色: 0-普通用户, 1-管理员, 2-超级管理员")
    status = Column(SmallInteger, default=1, nullable=False, comment="状态: 0-禁用, 1-正常")
    is_verified = Column(Boolean, default=False, nullable=False, comment="邮箱是否验证")
    must_change_password = Column(Boolean, default=False, nullable=False, comment="是否必须修改密码")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    
    # 关联关系
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="user", cascade="all, delete-orphan")
    uploads = relationship("Upload", back_populates="user", cascade="all, delete-orphan")
    guestbooks = relationship("Guestbook", back_populates="user")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    # 接收的通知（通过 user_id 关联）
    notifications = relationship(
        "Notification", 
        foreign_keys="Notification.user_id",
        back_populates="user", 
        cascade="all, delete-orphan", 
        order_by="desc(Notification.created_at)"
    )
    # 创建的通知（通过 created_by 关联）
    created_notifications = relationship(
        "Notification",
        foreign_keys="Notification.created_by",
        back_populates="creator"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
    @property
    def is_admin(self) -> bool:
        """是否为管理员（含超级管理员）"""
        return self.role in (1, 2)

    @property
    def is_superadmin(self) -> bool:
        """是否为超级管理员"""
        return self.role == 2
    
    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == 1
