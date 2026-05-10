"""
分类模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Category(Base):
    """分类表"""
    __tablename__ = "categories"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="分类ID")
    name = Column(String(50), nullable=False, comment="分类名称")
    slug = Column(String(50), unique=True, nullable=False, comment="URL标识")
    description = Column(String(255), nullable=True, comment="分类描述")
    parent_id = Column(BigInteger, ForeignKey("categories.id"), nullable=True, comment="父分类ID")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序顺序")
    article_count = Column(Integer, default=0, nullable=False, comment="文章数量")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    
    # 关联关系
    articles = relationship("Article", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="children")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, slug={self.slug})>"
    
    def to_dict(self, include_children=False):
        """转换为字典"""
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "parent_id": self.parent_id,
            "sort_order": self.sort_order,
            "article_count": self.article_count
        }
        if include_children and self.children:
            data["children"] = [child.to_dict() for child in self.children]
        return data
