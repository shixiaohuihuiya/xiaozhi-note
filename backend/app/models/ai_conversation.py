"""
AI对话模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, SmallInteger, Integer, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from database import Base


class AIConversation(Base):
    """AI对话表"""
    __tablename__ = "ai_conversations"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")
    session_id = Column(String(64), nullable=False, comment="会话ID")
    article_id = Column(BigInteger, ForeignKey("articles.id"), nullable=True, comment="关联文章ID")
    role = Column(SmallInteger, nullable=False, comment="角色: 1-用户, 2-AI")
    content = Column(Text, nullable=False, comment="对话内容")
    model = Column(String(50), nullable=True, comment="使用的AI模型")
    tokens_used = Column(Integer, nullable=True, comment="消耗的token数")
    context_refs = Column(JSON, nullable=True, comment="引用的上下文信息")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    
    # 关联关系
    user = relationship("User", back_populates="ai_conversations")
    article = relationship("Article", back_populates="ai_conversations")
    
    # 索引
    __table_args__ = (
        Index('idx_user', 'user_id'),
        Index('idx_session', 'session_id'),
        Index('idx_article', 'article_id'),
        Index('idx_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AIConversation(id={self.id}, session_id={self.session_id}, role={self.role})>"
    
    @property
    def is_user(self) -> bool:
        """是否为用户消息"""
        return self.role == 1
    
    @property
    def is_ai(self) -> bool:
        """是否为AI回复"""
        return self.role == 2
