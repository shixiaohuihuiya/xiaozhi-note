"""
通知模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, SmallInteger, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base


class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="通知ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, comment="接收用户ID，为空表示全员通知")
    type = Column(SmallInteger, nullable=False, comment="类型: 1-文章下架, 2-评论审核不通过, 3-新评论, 4-系统公告, 5-管理员通知")
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=True, comment="内容")
    related_id = Column(BigInteger, nullable=True, comment="关联ID(文章ID或评论ID)")
    is_read = Column(Boolean, default=False, nullable=False, comment="是否已读")
    is_system = Column(Boolean, default=False, nullable=False, comment="是否为系统/管理员发送的通知")
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True, comment="创建者ID（管理员）")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    
    # 关联关系
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    creator = relationship("User", foreign_keys=[created_by])
    
    # 索引
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_is_read', 'is_read'),
        Index('idx_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type})>"
