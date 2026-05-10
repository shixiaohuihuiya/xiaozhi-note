"""
点赞模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Like(Base):
    """点赞表"""
    __tablename__ = "likes"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="点赞ID")
    article_id = Column(BigInteger, ForeignKey("articles.id"), nullable=False, comment="文章ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    
    # 关联关系
    article = relationship("Article", back_populates="likes")
    user = relationship("User", back_populates="likes")
    
    # 联合唯一索引：每个用户每篇文章只能点赞一次
    __table_args__ = (
        UniqueConstraint('article_id', 'user_id', name='uix_article_user_like'),
    )
    
    def __repr__(self):
        return f"<Like(article_id={self.article_id}, user_id={self.user_id})>"
