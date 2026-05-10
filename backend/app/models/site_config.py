"""
站点配置模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base


class SiteConfig(Base):
    """站点配置表"""
    __tablename__ = "site_configs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="配置ID")
    key = Column(String(100), unique=True, nullable=False, comment="配置键")
    value = Column(Text, nullable=True, comment="配置值")
    description = Column(String(255), nullable=True, comment="配置描述")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    
    def __repr__(self):
        return f"<SiteConfig(key={self.key})>"
