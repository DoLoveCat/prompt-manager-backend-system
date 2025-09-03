# backend/app/api/mcp.py
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.security import get_user_by_api_key_or_401  # 后面实现？
from app.services import prompt_service

router = APIRouter()

# ==== MCP 协议数据模型 ====
class MCPMessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]


# 两个工具的入参定义（方便文档与校验）
class ListPromptsArgs(BaseModel):
    tags: Optional[List[str]] = None
    search: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)  # 合理限制，避免滥用
    category: Optional[str] = Field(default=None, max_length=100)

class GetPromptArgs(BaseModel):
    prompt_id: str = Field(..., description="提示词ID（UUID 字符串）")

# ==== 工具注册 ====
TOOLS: List[MCPTool] = [
    MCPTool(
        name="list_available_prompts",
        description="获取用户可用的提示词列表",
        inputSchema=ListPromptsArgs.model_json_schema()
    ),
    MCPTool(
        name="get_prompt_content",
        description="获取指定提示词的完整内容",
        inputSchema=GetPromptArgs.model_json_schema()
    )
]

@router.post("/v1/tools/list", response_model=MCPResponse)
async def mcp_tools_list(
    db: AsyncSession = Depends(get_db_session),
    authorization: Optional[str] = Header(default=None)
):
    """
    列出可用工具。注意：也要认证，避免暴露工具清单给未授权用户。
    API Key 读取规则：Authorization: Bearer <api_key>
    """
    user = await get_user_by_api_key_or_401(db, authorization)
    # 这里不返回用户信息，仅返回工具清单
    return MCPResponse(result={"tools": [t.model_dump() for t in TOOLS]})

@router.post("/v1/tools/call", response_model=MCPResponse)
async def mcp_tools_call(
    req: MCPRequest,
    db: AsyncSession = Depends(get_db_session),
    authorization: Optional[str] = Header(default=None)
):
    """
    调用指定工具。
    请求示例：
    {
      "method": "tools/call",
      "params": { "name": "list_available_prompts", "arguments": {...} }
    }
    """
    user = await get_user_by_api_key_or_401(db, authorization)

    if req.method != "tools/call":
        return MCPResponse(error={"code": -32601, "message": "Unknown method"})

    if not req.params or "name" not in req.params:
        return MCPResponse(error={"code": -32602, "message": "Missing 'name' in params"})

    tool_name = req.params["name"]
    args = req.params.get("arguments", {}) or {}

    try:
        if tool_name == "list_available_prompts":
            parsed = ListPromptsArgs(**args)
            data = await prompt_service.mcp_list_available_prompts(
                db=db,
                user_id=user.id,
                tags=parsed.tags,
                search=parsed.search,
                limit=parsed.limit,
                category=parsed.category
            )
            return MCPResponse(result=data)

        elif tool_name == "get_prompt_content":
            parsed = GetPromptArgs(**args)
            data = await prompt_service.mcp_get_prompt_content(
                db=db,
                user_id=user.id,
                prompt_id=parsed.prompt_id
            )
            return MCPResponse(result=data)

        else:
            return MCPResponse(error={"code": -32601, "message": f"Unknown tool: {tool_name}"})
    except HTTPException as e:
        return MCPResponse(error={"code": e.status_code, "message": e.detail})
    except Exception as e:
        return MCPResponse(error={"code": 500, "message": str(e)})
