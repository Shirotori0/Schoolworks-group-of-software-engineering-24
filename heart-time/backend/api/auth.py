from fastapi import APIRouter
from api_schemas import LoginRequest, LoginResponse
from utils.exceptions import AppException
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# 模拟用户表（后续替换为数据库查询）
FAKE_USERS = {
    "testuser": {"password": "123456", "user_id": "user_001"}
}

@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    try:
        user = FAKE_USERS.get(request.username)
        if not user or user["password"] != request.password:
            raise AppException(status_code=401, detail="用户名或密码错误", code=401)

        fake_token = f"token_{user['user_id']}_{uuid.uuid4()}"

        logger.info(f"用户 {user['user_id']} 登录成功")
        return LoginResponse(token=fake_token, user_id=user["user_id"])

    except AppException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="登录失败，请稍后重试")