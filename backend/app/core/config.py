# backend/app/core/config.py
from pydantic_settings import BaseSettings
# 使用 pydantic.BaseSettings 可以直接从.env或系统环境变量加载配置，并自动做类型检查（如 int、str）。
from functools import lru_cache
import os
# or

class Settings(BaseSettings):
    PROJECT_NAME: str = "Prompt Management System"  # 项目名称
    API_V1_STR: str = "/api/v1"  # API 版本路径前缀

    DATABASE_URL: str  # PostgreSQL 连接URL
    SECRET_KEY: str  # JWT加密密钥
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Token有效期（分钟）
    API_KEY: str 
    # API_KEY: Optional[str] = None

#    class Config:
#        env_file = ".env"  # 指定环境变量文件位置
#        case_sensitive = True  # 变量名大小写敏感

    class Config:
        # 根据 ENV_MODE 加载不同的 env 文件
        env_file = (
            ".env.test" if os.getenv("ENV_MODE") == "test" else ".env"
        )
        case_sensitive = True



@lru_cache()
def get_settings():
    """
    使用lru_cache避免重复读取.env,提高性能
    """
    return Settings()
