# backend/app/services/prompt_service.py
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
import uuid
from datetime import datetime

#MCP
from typing import List, Optional, Dict, Any 
from fastapi import HTTPException
from app.models.prompt import Prompt


#创建提示词
async def create_prompt(db: AsyncSession, user_id: uuid.UUID, prompt_in: PromptCreate) -> Prompt:
    new_prompt = Prompt(
        id=uuid.uuid4(),
        user_id=user_id,
        title=prompt_in.title,
        content=prompt_in.content,
        description=prompt_in.description,
        tags=prompt_in.tags,
        category=prompt_in.category,
        variables=prompt_in.variables,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_prompt)
    await db.commit()
    await db.refresh(new_prompt)
    return new_prompt


#查询提示词列表（按用户）
async def list_prompts(db: AsyncSession, user_id: uuid.UUID) -> list[Prompt]:
    result = await db.execute(select(Prompt).where(Prompt.user_id == user_id))
    return result.scalars().all()

#查询单个提示词
async def get_prompt_by_id(db: AsyncSession, prompt_id: uuid.UUID) -> Prompt | None:
    result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
    return result.scalar_one_or_none()



# MCP 相关服务实现

# 列出用户可用的提示词
async def mcp_list_available_prompts(
    db: AsyncSession,
    user_id: uuid.UUID,
    tags: Optional[List[str]],
    search: Optional[str],
    limit: int,
    category: Optional[str]
) -> Dict[str, Any]:
    q = select(Prompt).where(
        Prompt.user_id == user_id
    )

    if tags:
        # PostgreSQL ARRAY overlap：数组有交集即匹配
        q = q.where(Prompt.tags.op("&&")(tags))

    if category:
        q = q.where(Prompt.category == category)

    if search:
        # 简化的模糊匹配；若要全文检索可换成 to_tsvector/ts_rank
        like = f"%{search}%"
        q = q.where((Prompt.title.ilike(like)) | (Prompt.content.ilike(like)))

    q = q.order_by(Prompt.usage_count.desc()).limit(limit)
    res = await db.execute(q)
    rows = res.scalars().all()

    items = []
    for p in rows:
        items.append({
            "id": str(p.id),
            "title": p.title,
            "tags": p.tags or [],
            "description": p.description,
            "category": p.category,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "usage_count": p.usage_count or 0
        })

    # MCP 期望的 result.content 可返回“可读文本”，同时附带结构化数据
    readable = "找到 {} 个匹配的提示词:\n".format(len(items)) + "\n".join(
        [f"• {x['title']} (ID: {x['id']})" for x in items]
    )

    return {
        "content": [{"type": "text", "text": readable}],
        "prompts": items,
        "total": len(items),
    }


async def mcp_get_prompt_content(
    db: AsyncSession,
    user_id: uuid.UUID,
    prompt_id: str
) -> Dict[str, Any]:
    try:
        pid = uuid.UUID(prompt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid prompt_id")

    q = select(Prompt).where(Prompt.id == pid, Prompt.user_id == user_id)
    res = await db.execute(q)
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # 简单变量提取 {{var}}（可在后续替换为更健壮实现）
    import re
    variables = sorted(list(set(re.findall(r"\{\{(\w+)\}\}", p.content or ""))))

    readable = f"提示词: {p.title}\n\n{p.content}"

    return {
        "content": [{"type": "text", "text": readable}],
        "prompt": {
            "id": str(p.id),
            "title": p.title,
            "content": p.content,
            "description": p.description,
            "tags": p.tags or [],
            "category": p.category,
            "variables": variables,
            "version": p.version or 1,
            "metadata": {
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                "usage_count": p.usage_count or 0
            }
        }
    }