"""
留言墙模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, SmallInteger, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base


class Guestbook(Base):
    """留言墙表"""
    __tablename__ = "guestbooks"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="留言ID")
    parent_id = Column(BigInteger, ForeignKey("guestbooks.id"), nullable=True, comment="父留言ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, comment="用户ID（游客可为空）")
    nickname = Column(String(50), nullable=False, comment="昵称")
    email = Column(String(100), nullable=True, comment="邮箱")
    website = Column(String(200), nullable=True, comment="个人网站")
    content = Column(Text, nullable=False, comment="留言内容")
    like_count = Column(BigInteger, default=0, nullable=False, comment="点赞数")
    status = Column(SmallInteger, default=0, nullable=False, comment="状态: 0-待审核, 1-已通过, 2-已拒绝")
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    user_agent = Column(String(500), nullable=True, comment="User-Agent")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="guestbooks")
    parent = relationship("Guestbook", remote_side=[id], backref="replies")
    
    # 索引
    __table_args__ = (
        Index('idx_parent', 'parent_id'),
        Index('idx_user', 'user_id'),
        Index('idx_status', 'status'),
        Index('idx_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Guestbook(id={self.id}, nickname={self.nickname})>"
    
    @property
    def is_approved(self) -> bool:
        """是否已通过审核"""
        return self.status == 1
