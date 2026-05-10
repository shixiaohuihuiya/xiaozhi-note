"""
评论模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, SmallInteger, Integer, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base


class Comment(Base):
    """评论表"""
    __tablename__ = "comments"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="评论ID")
    article_id = Column(BigInteger, ForeignKey("articles.id"), nullable=False, comment="文章ID")
    parent_id = Column(BigInteger, ForeignKey("comments.id"), nullable=True, comment="父评论ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")
    content = Column(Text, nullable=False, comment="评论内容")
    like_count = Column(Integer, default=0, nullable=False, comment="点赞数")
    status = Column(SmallInteger, default=0, nullable=False, comment="状态: 0-待审核, 1-已通过, 2-已拒绝")
    is_author = Column(Boolean, default=False, nullable=False, comment="是否为作者回复")
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    user_agent = Column(String(500), nullable=True, comment="User-Agent")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    
    # 关联关系
    article = relationship("Article", back_populates="comments")
    user = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    
    # 索引
    __table_args__ = (
        Index('idx_article', 'article_id'),
        Index('idx_parent', 'parent_id'),
        Index('idx_user', 'user_id'),
        Index('idx_status', 'status'),
        Index('idx_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Comment(id={self.id}, article_id={self.article_id}, user_id={self.user_id})>"
    
    @property
    def is_approved(self) -> bool:
        """是否已通过审核"""
        return self.status == 1
    
    @property
    def is_pending(self) -> bool:
        """是否待审核"""
        return self.status == 0
    
    @property
    def is_rejected(self) -> bool:
        """是否已拒绝"""
        return self.status == 2
