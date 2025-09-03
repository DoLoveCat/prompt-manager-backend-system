# backend/app/db/session.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# 创建数据库引擎（异步）
engine = create_async_engine(
    settings.DATABASE_URL.replace("psycopg2", "asyncpg"),  # 使用 asyncpg 驱动
    pool_pre_ping=True,   # 检查连接是否可用
    pool_size=5,          # 连接池大小
    max_overflow=10       # 允许的最大连接溢出数
)

# 创建异步 Session 厂
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# 获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# FastAPI 依赖
#async def get_session() -> AsyncSession:
#    async with AsyncSessionLocal() as session:
#        yield session

