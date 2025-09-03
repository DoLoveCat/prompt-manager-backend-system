# backend/app/api/v1/prompts.py
from fastapi import APIRouter, Depends
from app.schemas.prompt import PromptCreate, PromptRead
from app.services import prompt_service
from app.api.deps import get_current_user, get_db_session, verify_api_key
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_db_session

router = APIRouter()


#防止 A 用户看到 B 用户的数据，必须“每个 API 调用都验证用户身份”
@router.post("/", response_model=PromptRead, dependencies=[Depends(verify_api_key)])
async def create_prompt(
    prompt_in: PromptCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    return await prompt_service.create_prompt(db, user_id=current_user.id, prompt_in=prompt_in)
    #加上 user_id 限制查询范围。