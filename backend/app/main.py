# backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title="提示词管理系统",
    description="MCP协议提示词管理服务",
    version="1.0.0"
)


# class PromptCreate(BaseModel):


# 1. 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源访问，生产环境建议改成具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)
#CORS 配置好后，前端（React）才能直接请求API。

# 2. 全局异常处理（示例：500 错误）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部错误，请稍后重试"},
    )

# 3. 路由挂载示例
from app.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)




# 健康检查等简单端点
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/test/env")
async def test_env():
    settings = get_settings()
    # 对SECRET_KEY进行掩码处理（显示前3后3字符，中间用*代替）
    masked_key = settings.SECRET_KEY[:3] + "*" * (len(settings.SECRET_KEY) - 6) + settings.SECRET_KEY[-3:]
    return {
        "PROJECT_NAME": settings.PROJECT_NAME,
        "DATABASE_URL": settings.DATABASE_URL,
        "SECRET_KEY": masked_key
    }

@app.get("/test/error")
async def test_error():
    raise Exception("模拟错误")



#测试数据库连接
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.session import get_db

@app.get("/test/db-connect")
async def test_db_connect(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"db_result": result.scalar()}



# 注册具体的 API 路由
from app.api.v1 import users, prompts
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])


# 在 main.py 中分开挂：
from app.api import mcp
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(mcp_router)


# 打印DATABASE_URL
print(">>> EFFECTIVE DATABASE_URL:", settings.DATABASE_URL)