# backend/app/services/user_service.py

#from sqlalchemy.ext.asyncio import AsyncSession
#from sqlalchemy import select
#from app.models.user import User
#from app.schemas.user import UserCreate
#import uuid

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate

import secrets


# API key生成
from fastapi import HTTPException                   
from secrets import token_urlsafe                   


# 唯一 API Key 生成器
async def _gen_unique_api_key(db: AsyncSession) -> str:
    for _ in range(5):
        candidate = token_urlsafe(32)
        exists = await db.execute(select(User.id).where(User.api_key == candidate))
        if exists.scalar_one_or_none() is None:
            return candidate
    return token_urlsafe(48)


#创建用户
async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    new_user = User(
        # id=uuid.uuid4(),
        # 修改一下，User.id 是 UUID 主键
        id=uuid4(),
        username=user_in.username,
        email=user_in.email,
        # api_key="temp_key"  # 先用着测试，之后再加API Key生成逻辑
        api_key = getattr(user_in, "api_key", None) or await _gen_unique_api_key(db)
    )
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="username/email/api_key already exists")
    await db.refresh(new_user)
    return new_user

#查找用户（by email）
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

#查找用户（by id）
async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:

    try:
        id_val = UUID(user_id)
        stmt = select(User).where(User.id == id_val).limit(1)
    except ValueError:
        stmt = select(User).where(User.id == user_id).limit(1)

    res = await db.execute(stmt)
    return res.scalar_one_or_none()

# 查找用户（by API Key）
# 对backend/app/core/security.py的一个补充
async def get_user_by_api_key(db: AsyncSession, api_key: str) -> User | None:
    res = await db.execute(select(User).where(User.api_key == api_key))
    return res.scalar_one_or_none()