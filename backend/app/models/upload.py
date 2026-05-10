"""
文件上传模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, SmallInteger, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base


class Upload(Base):
    """文件上传表"""
    __tablename__ = "uploads"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="上传用户ID")
    original_name = Column(String(255), nullable=False, comment="原始文件名")
    file_name = Column(String(255), nullable=False, comment="存储文件名")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_url = Column(String(500), nullable=False, comment="文件访问URL")
    file_type = Column(String(100), nullable=False, comment="MIME类型")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    file_ext = Column(String(10), nullable=False, comment="文件扩展名")
    usage_type = Column(SmallInteger, default=1, nullable=False, comment="用途: 1-文章封面, 2-文章内容, 3-头像")
    article_id = Column(BigInteger, ForeignKey("articles.id"), nullable=True, comment="关联文章ID")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    
    # 关联关系
    user = relationship("User", back_populates="uploads")
    article = relationship("Article", back_populates="uploads")
    
    # 索引
    __table_args__ = (
        Index('idx_user', 'user_id'),
        Index('idx_article', 'article_id'),
        Index('idx_usage', 'usage_type'),
    )
    
    def __repr__(self):
        return f"<Upload(id={self.id}, original_name={self.original_name}, file_type={self.file_type})>"
    
    @property
    def is_image(self) -> bool:
        """是否为图片"""
        return self.file_type.startswith("image/")
    
    @property
    def size_in_kb(self) -> float:
        """文件大小(KB)"""
        return round(self.file_size / 1024, 2)
    
    @property
    def size_in_mb(self) -> float:
        """文件大小(MB)"""
        return round(self.file_size / (1024 * 1024), 2)
