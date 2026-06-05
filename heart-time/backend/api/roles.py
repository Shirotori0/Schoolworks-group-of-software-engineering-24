from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text as db_text
from config import get_db
from api_schemas import RoleItem
from utils.exceptions import AppException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/roles", response_model=list[RoleItem])
async def get_roles(db: Session = Depends(get_db)):
    try:
        sql = db_text("SELECT id, role_name, gentleness, rationality FROM ai_role")
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