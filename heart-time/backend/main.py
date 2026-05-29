from dotenv import load_dotenv
load_dotenv()

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import time

# 1. 先配置日志（force=True 覆盖 uvicorn 默认配置）
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
logger = logging.getLogger(__name__)

# 2. 创建 FastAPI 应用
app = FastAPI(title="心语时光 API", version="1.0")

# 3. 导入自定义异常和路由
from utils.exceptions import AppException
from api.chat import router as chat_router
from api.auth import router as auth_router
from api.diaries import router as diaries_router
from api.roles import router as roles_router
from api.chat_sessions import router as sessions_router
from api.load_story import router as load_story_router

# 挂载路由
app.include_router(chat_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(diaries_router, prefix="/api/v1")   
app.include_router(roles_router, prefix="/api/v1")     
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(load_story_router, prefix="/api/v1")

# 4. 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - 耗时: {process_time:.3f}s - 状态码: {response.status_code}")
    return response

# 5. 统一异常处理
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": exc.code}
    )


@app.get("/")
def root():
    return {"message": "心语时光 API 运行中"}