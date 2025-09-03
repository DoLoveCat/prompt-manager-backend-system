# backend/app/api/__init__.py

# 注册路由
from .routes import router as api_router

# Alembic 自动识别所有模型的 metadata
from app.models.base import Base
from app.models.user import User
from app.models.prompt import Prompt
from app.models.tag import Tag

# 注册 API 路由
from fastapi import APIRouter
from app.api.v1 import users, prompts

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(prompts.router)


# 挂载 MCP，独立前缀
# MCP还没写完，先挂着吧
mcp_router = APIRouter()
mcp_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])