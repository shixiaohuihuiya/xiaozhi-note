"""
标签模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="标签ID")
    name = Column(String(50), unique=True, nullable=False, comment="标签名称")
    slug = Column(String(50), unique=True, nullable=False, comment="URL标识")
    color = Column(String(7), nullable=True, comment="标签颜色(HEX)")
    article_count = Column(Integer, default=0, nullable=False, comment="文章数量")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    
    # 关联关系
    article_tags = relationship("ArticleTag", back_populates="tag", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, slug={self.slug})>"


class ArticleTag(Base):
    """文章标签关联表"""
    __tablename__ = "article_tags"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    article_id = Column(BigInteger, ForeignKey("articles.id"), nullable=False, comment="文章ID")
    tag_id = Column(BigInteger, ForeignKey("tags.id"), nullable=False, comment="标签ID")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    
    # 关联关系
    article = relationship("Article", back_populates="article_tags")
    tag = relationship("Tag", back_populates="article_tags")
    
    def __repr__(self):
        return f"<ArticleTag(article_id={self.article_id}, tag_id={self.tag_id})>"
