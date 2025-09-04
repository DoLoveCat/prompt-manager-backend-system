# backend/app/models/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """所有模型的基类,Alembic 会用它识别模型"""
    pass