from fastapi import APIRouter
from api_schemas import CreateSessionRequest, CreateSessionResponse, DeleteSessionResponse
from utils.exceptions import AppException
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """创建新会话，返回 session_id"""
    try:
        session_id = str(uuid.uuid4())
        logger.info(f"用户 {request.user_id} 创建会话 {session_id}")
        return CreateSessionResponse(session_id=session_id)
    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="创建会话失败")

@router.delete("/chat/sessions/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(session_id: str):
    """删除会话"""
    try:
        logger.info(f"删除会话 {session_id}")
        # 组长的 Runtime 会自动保存会话状态到 JSON 文件
        return DeleteSessionResponse(status="deleted")
    except Exception as e:
        logger.error(f"删除会话失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="删除会话失败")