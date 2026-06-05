from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text as db_text
from typing import Optional
from config import get_db
from api_schemas import (
    CreateSessionRequest, CreateSessionResponse, DeleteSessionResponse,
    SessionItem, MessageItem
)
from utils.exceptions import AppException
import uuid
import logging
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    """创建新会话，可选绑定记忆体"""
    try:
        session_id = str(uuid.uuid4())

        sql = db_text("""
            INSERT INTO chat_sessions (session_id, user_id, memory_id, title)
            VALUES (:session_id, :user_id, :memory_id, :title)
        """)
        db.execute(sql, {
            "session_id": session_id,
            "user_id": request.user_id,
            "memory_id": request.memory_id,
            "title": "新对话"
        })
        db.commit()

        logger.info(f"用户 {request.user_id} 创建会话 {session_id}, 记忆体: {request.memory_id}")

        return CreateSessionResponse(
            session_id=session_id,
            memory_id=request.memory_id
        )

    except Exception as e:
        db.rollback()
        logger.error(f"创建会话失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="创建会话失败")


@router.delete("/chat/sessions/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """删除会话"""
    try:
        sql = db_text("DELETE FROM chat_sessions WHERE session_id = :session_id")
        db.execute(sql, {"session_id": session_id})
        db.commit()

        logger.info(f"删除会话 {session_id}")

        return DeleteSessionResponse(status="deleted")

    except Exception as e:
        db.rollback()
        logger.error(f"删除会话失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="删除会话失败")


@router.get("/chat/sessions", response_model=list[SessionItem])
async def get_sessions(
    user_id: str = Query(..., description="用户ID"),
    memory_id: Optional[str] = Query(None, description="记忆体ID（可选）"),
    db: Session = Depends(get_db)
):
    """获取用户的会话列表，可按记忆体筛选"""
    try:
        if memory_id:
            sql = db_text("""
                SELECT session_id, memory_id, title, created_at, updated_at
                FROM chat_sessions
                WHERE user_id = :user_id AND memory_id = :memory_id
                ORDER BY updated_at DESC
            """)
            rows = db.execute(sql, {"user_id": user_id, "memory_id": memory_id}).fetchall()
        else:
            sql = db_text("""
                SELECT session_id, memory_id, title, created_at, updated_at
                FROM chat_sessions
                WHERE user_id = :user_id
                ORDER BY updated_at DESC
            """)
            rows = db.execute(sql, {"user_id": user_id}).fetchall()

        return [
            SessionItem(
                session_id=row[0],
                memory_id=row[1],
                title=row[2],
                created_at=str(row[3]) if row[3] else "",
                updated_at=str(row[4]) if row[4] else ""
            )
            for row in rows
        ]

    except Exception as e:
        logger.error(f"查询会话列表失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="查询会话列表失败")


@router.get("/chat/sessions/{session_id}/messages", response_model=list[MessageItem])
async def get_session_messages(session_id: str):
    """获取某个会话的对话历史"""
    try:
        backend_dir = str(Path(__file__).parent.parent.parent)
        file_path = os.path.join(backend_dir, "ai", "data", "prompts", f"{session_id}.json")

        if not os.path.exists(file_path):
            raise AppException(status_code=404, detail="会话不存在或已被删除")

        with open(file_path, "r", encoding="utf-8") as f:
            session_data = json.load(f)

        chat_history = session_data.get("chat_history", [])

        messages = []
        for i, msg in enumerate(chat_history):
            if isinstance(msg, str):
                sender = "user" if i % 2 == 0 else "ai"
                content = msg
            elif isinstance(msg, dict):
                role = msg.get("role", "user")
                sender = "user" if role == "user" else "ai"
                content = msg.get("content", "")
            else:
                continue

            messages.append(MessageItem(
                message_id=f"msg_{i}",
                sender=sender,
                content=content,
                created_at=""
            ))

        return messages

    except AppException:
        raise
    except Exception as e:
        logger.error(f"查询会话消息失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="查询会话消息失败")