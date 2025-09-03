# backend/app/api/deps.py
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import verify_token
from app.db.session import get_db
from app.services.user_service import get_user_by_email
from app.models.user import User

from app.services.user_service import get_user_by_id
from types import SimpleNamespace

# ✅ 读取配置（不要 from app.core.config import settings）
settings = get_settings()

# 仅用于 OpenAPI 文档展示；实际用的是 Bearer 头
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

# DB 会话依赖
async def get_db_session() -> AsyncSession:
    async for session in get_db():
        yield session


# 从 Bearer Token 解出当前用户（用 sub 作为 User.id）
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    try:
        # email = verify_token(token)
        # user_id = verify_token(token) 
        payload_or_sub = verify_token(token)
        if isinstance(payload_or_sub, dict):
            user_id = payload_or_sub.get("sub")
        else:
            user_id = payload_or_sub
        #这里总报错兼容一下

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub")
            # 兜底：如果 DB 暂时没这条用户记录（比如老 token），先返回一个轻量对象，保证 current_user.id 可用
            return SimpleNamespace(id=user_id, email=None)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# API Key 校验；显式使用 X-API-Key 作为头名
async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )