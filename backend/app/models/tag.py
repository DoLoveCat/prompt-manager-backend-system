# backend/app/models/tag.py
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#6B7280")  # hex颜色
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    # usage_count 可以做标签排序。不一定需要，先写着
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
