# backend/app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
#用于注册新用户

from uuid import UUID
from datetime import datetime
#UserRead：返回给前端的用户信息

#用于注册新用户
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., max_length=255, description="用户邮箱")

class UserRead(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # 允许从 ORM 模型中读取数据
