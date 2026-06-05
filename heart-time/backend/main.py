from dotenv import load_dotenv
load_dotenv()

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
import logging
import time

# 1. 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
logger = logging.getLogger(__name__)

# 2. 创建 FastAPI 应用
app = FastAPI(title="心语时光 API", version="1.0")

# 3. 导入自定义异常
from utils.exceptions import AppException

# 4. 导入 AI 层函数
from ai.pipeline.generator import generate_runtime

# 5. 导入数据库引擎
from config import engine
from sqlalchemy import text as db_text

# 6. 导入 Pydantic 模型
from pydantic import BaseModel
from typing import Optional

# 7. 定义支持 memory_id 的 Chat 模型
class ExtendedChatRequest(BaseModel):
    session_id: str
    user_input: str
    memory_id: Optional[str] = None

class ExtendedChatResponse(BaseModel):
    response: str

# 8. 创建自定义路由（支持 memory_id）
custom_router = APIRouter()

@custom_router.post("/chat", response_model=ExtendedChatResponse)
def chat_with_memory(request: ExtendedChatRequest):
    """支持 memory_id 的 Chat 接口"""
    vector_paths = None
    if request.memory_id:
        with engine.connect() as conn:
            result = conn.execute(
                db_text("SELECT vector_file_path FROM memory WHERE memory_id = :mid"),
                {"mid": request.memory_id}
            ).fetchone()
            if result and result[0]:
                vector_paths = [result[0]]
                logger.info(f"使用向量文件: {vector_paths}")  # 新增调试日志
            else:
                logger.info(f"未找到记忆体 {request.memory_id} 的向量文件")  # 新增
    
    runtime = generate_runtime(request.session_id, vector_paths=vector_paths)
    response = runtime.chat(request.user_input)
    
    return ExtendedChatResponse(response=response)

# 9. 导入其他路由
from api.auth import router as auth_router
from api.diaries import router as diaries_router
from api.roles import router as roles_router
from api.chat_sessions import router as sessions_router
from api.memories import router as memories_router
from ai.api.load_story import router as load_story_router

# 10. 挂载路由
app.include_router(custom_router, prefix="/api/v1")
app.include_router(load_story_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(diaries_router, prefix="/api/v1")
app.include_router(roles_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(memories_router, prefix="/api/v1")

# 11. 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - 耗时: {process_time:.3f}s - 状态码: {response.status_code}")
    return response

# 12. 统一异常处理
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": exc.code}
    )

@app.get("/")
def root():
    return {"message": "心语时光 API 运行中"}