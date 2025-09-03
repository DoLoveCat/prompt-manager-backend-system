# backend/app/api/routes.py

from fastapi import APIRouter
router = APIRouter()

@router.get("/test")
def test():
    return {"msg": "ok"}