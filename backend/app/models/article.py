"""
文章模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, SmallInteger, Integer, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base


class Article(Base):
    """文章表"""
    __tablename__ = "articles"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="文章ID")
    title = Column(String(200), nullable=False, comment="文章标题")
    slug = Column(String(200), unique=True, nullable=False, comment="URL标识")
    summary = Column(String(500), nullable=True, comment="文章摘要")
    content = Column(Text, nullable=False, comment="文章内容")
    content_type = Column(SmallInteger, default=1, nullable=False, comment="内容类型: 1-Markdown, 2-HTML")
    cover_image = Column(String(500), nullable=True, comment="封面图片URL")
    
    # 外键关联
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="作者ID")
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=True, comment="分类ID")
    
    # 状态统计
    status = Column(SmallInteger, default=0, nullable=False, comment="状态: 0-草稿, 1-已发布, 2-下架")
    needs_reapproval = Column(Boolean, default=False, nullable=False, comment="被管理员下架后需要重新申请审核")
    is_top = Column(Boolean, default=False, nullable=False, comment="是否置顶")
    view_count = Column(Integer, default=0, nullable=False, comment="阅读次数")
    like_count = Column(Integer, default=0, nullable=False, comment="点赞次数")
    comment_count = Column(Integer, default=0, nullable=False, comment="评论数量")
    
    # 时间字段
    published_at = Column(DateTime, nullable=True, comment="发布时间")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="软删除时间")
    
    # 关联关系
    author = relationship("User", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    article_tags = relationship("ArticleTag", back_populates="article", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="article")
    uploads = relationship("Upload", back_populates="article")
    likes = relationship("Like", back_populates="article", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_author', 'author_id'),
        Index('idx_category', 'category_id'),
        Index('idx_status', 'status'),
        Index('idx_published_at', 'published_at'),
        Index('idx_is_top', 'is_top'),
    )
    
    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title}, slug={self.slug})>"
    
    @property
    def is_published(self) -> bool:
        """是否已发布"""
        return self.status == 1
    
    @property
    def is_draft(self) -> bool:
        """是否为草稿"""
        return self.status == 0
    
    @property
    def tags(self):
        """获取文章的所有标签"""
        return [at.tag for at in self.article_tags]
    
    def increment_view(self):
        """增加阅读数"""
        self.view_count += 1
    
    def increment_like(self):
        """增加点赞数"""
        self.like_count += 1
    
    def decrement_like(self):
        """减少点赞数"""
        if self.like_count > 0:
            self.like_count -= 1
