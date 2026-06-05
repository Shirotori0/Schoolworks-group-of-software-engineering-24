from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text as db_text
from config import get_db
from api_schemas import CreateDiaryRequest, CreateDiaryResponse, DiaryItem
from utils.exceptions import AppException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/diaries", response_model=CreateDiaryResponse)
async def create_diary(request: CreateDiaryRequest, db: Session = Depends(get_db)):
    try:
        if not request.content.strip():
            raise AppException(status_code=400, detail="日记内容不能为空")

        # TODO: 等组长封装AI函数后替换这里
        emotion_tags = "愉悦-日常记录"
        ai_reply = f"感谢你的记录。我感受到了你的分享，继续保持哦。"

        sql = db_text("""
            INSERT INTO emotion_diary (user_id, diary_content, emotion_tags, ai_reply)
            VALUES (:user_id, :content, :tags, :reply)
        """)
        result = db.execute(sql, {
            "user_id": request.user_id,
            "content": request.content,
            "tags": emotion_tags,
            "reply": ai_reply
        })
        db.commit()

        diary_id = result.lastrowid
        logger.info(f"用户 {request.user_id} 创建日记 {diary_id}")

        return CreateDiaryResponse(diary_id=diary_id, status="completed")

    except AppException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建日记失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="创建日记失败")


@router.get("/diaries", response_model=list[DiaryItem])
async def get_diaries(
    user_id: int = Query(..., description="用户ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页条数"),
    db: Session = Depends(get_db)
):
    try:
        offset = (page - 1) * page_size
        sql = db_text("""
            SELECT id, diary_content, emotion_tags, ai_reply, create_time
            FROM emotion_diary
            WHERE user_id = :user_id
            ORDER BY create_time DESC
            LIMIT :limit OFFSET :offset
        """)
        rows = db.execute(sql, {
            "user_id": user_id,
            "limit": page_size,
            "offset": offset
        }).fetchall()

        return [
            DiaryItem(
                diary_id=row[0],
                content=row[1],
                emotion_tags=row[2],
                ai_reply=row[3],
                create_time=str(row[4])
            )
            for row in rows
        ]

    except Exception as e:
        logger.error(f"查询日记失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="查询日记失败")