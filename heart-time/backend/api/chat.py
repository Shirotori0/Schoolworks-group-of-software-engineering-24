import logging
from fastapi import APIRouter

from ai.pipeline.generator import generate_runtime
from api_schemas import ChatRequest, ChatResponse
from utils.exceptions import AppException

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        user_input = request.user_input.strip()
        if not user_input:
            raise AppException(status_code=400, detail="输入不能为空")

        logger.info(f"会话 {request.session_id} 收到消息: {user_input[:30]}...")

        # 调用 AI 层函数
        runtime = generate_runtime(request.session_id)
        ai_response = runtime.chat(user_input)

        logger.info(f"会话 {request.session_id} AI回复: {ai_response[:30]}...")

        return ChatResponse(response=ai_response)

    except AppException:
        raise
    except Exception as e:
        logger.error(f"Chat 处理出错: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="服务器内部错误")