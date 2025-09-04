# backend/app/schemas/prompt.py
from pydantic import BaseModel, Field
from typing import List, Optional
#PromptCreate：用于新建提示词

from typing import Optional
#PromptUpdate：用于编辑提示词

from uuid import UUID
from datetime import datetime
#PromptRead - 返回完整提示词信息



#PromptCreate：用于新建提示词
class PromptCreate(BaseModel):
    title: str = Field(..., max_length=255, description="提示词标题")
    content: str = Field(..., min_length=1, description="提示词正文内容")
    description: Optional[str] = Field(None, description="可选描述")
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = Field(None, max_length=100)
    variables: List[str] = Field(default_factory=list)
#default_factory=list：避免用 [] 作为默认值，这样每次实例化都会新建一个列表，防止“多个用户共享一个标签列表”的 bug。



#PromptUpdate：用于编辑提示词
class PromptUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = Field(None, max_length=100)
    variables: Optional[List[str]] = None



#PromptRead - 返回完整提示词信息
class PromptRead(BaseModel):
    id: UUID
    title: str
    content: str
    description: Optional[str]
    tags: List[str]
    category: Optional[str]
    variables: List[str]
    version: int
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True