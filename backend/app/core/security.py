# backend/app/core/security.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import get_settings


from fastapi import Header, HTTPException, status
# API

#基于 API Key 的用户识别（数据库校验）
from typing import Optional
from app.services.user_service import get_user_by_api_key
#user_service.py ↑
from sqlalchemy.ext.asyncio import AsyncSession


settings = get_settings()

ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes: int = 60):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """
    解码 JWT返回完整 payload(dict)
    让上游通过 payload.get("sub") 读取用户 ID。
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # 让上层看到 401
        raise HTTPException(status_code=401, detail="Invalid token")


# 从 Authorization 头提取 Bearer token
def _extract_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    return parts[1]

# 根据 API Key 查用户，失败抛 401
async def get_user_by_api_key_or_401(db: AsyncSession, authorization: Optional[str]):
    api_key = _extract_bearer_token(authorization)
    user = await get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    return user



#API Key 验证（用于用户隔离）
#这个弄到dep.py里了，后面看看哪里更合适一点
#async def verify_api_key(x_api_key: str = Header(...)):
#    # 示例：用数据库查验Key是否有效
#    if x_api_key != "your-hardcoded-test-key":  #  或许替换成数据库查验
#        raise HTTPException(status_code=403, detail="Invalid API Key")
