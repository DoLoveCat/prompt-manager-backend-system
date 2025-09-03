# backend/app/models/prompt.py
import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

# for index
from sqlalchemy import Index, text

class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    # ARRAY(String) 用于多标签（比 JSONB 检索更快
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    variables: Mapped[list[str]] = mapped_column(JSONB, default=list)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系映射
    user = relationship("User", backref="prompts")


    # 全文搜索索引 - 改了一点
    __table_args__ = (
        Index("idx_prompts_user_id", "user_id"),
        Index("idx_prompts_tags", "tags", postgresql_using="gin"),
        Index(
            "idx_prompts_search",
            text("to_tsvector('english', title || ' ' || content)"),
            postgresql_using="gin"
        ),
    )