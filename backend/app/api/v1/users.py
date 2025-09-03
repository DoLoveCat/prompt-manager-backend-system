# backend/app/api/v1/users.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserRead
from app.core.security import create_access_token
from app.api.deps import get_db_session, get_current_user  
from app.services.user_service import (
    create_user as create_user_service,
    get_user_by_email,
)

router = APIRouter()

# -------- 注册：写入数据库 --------
@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    # 查重
    exists = await get_user_by_email(db, email=user.email)
    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    # 真正写库（在 user_service 里已经有 create_user）
    new_user = await create_user_service(db, user_in=user)
    return new_user



# -------- 登录：从数据库读取用户，签发 JWT --------
class LoginRequest(BaseModel):
    email: EmailStr

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db_session)):
    user = await get_user_by_email(db, email=data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}




# -------- 调试 --------
@router.get("/me")
async def me(current_user = Depends(get_current_user)):
    return {"id": str(current_user.id), "email": getattr(current_user, "email", None)}
