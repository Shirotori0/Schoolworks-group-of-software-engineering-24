from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from config import get_db
from utils.exceptions import AppException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class RoleItem(BaseModel):
    role_id: int
    role_name: str
    gentleness: float
    rationality: float

@router.get("/roles", response_model=list[RoleItem])
async def get_roles(db: Session = Depends(get_db)):
    try:
        sql = text("SELECT id, role_name, gentleness, rationality FROM ai_role")
        rows = db.execute(sql).fetchall()
        return [
            RoleItem(
                role_id=row[0],
                role_name=row[1],
                gentleness=float(row[2]),
                rationality=float(row[3])
            )
            for row in rows
        ]
    except Exception as e:
        logger.error(f"查询角色失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="查询角色失败")