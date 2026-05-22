from fastapi import FastAPI
from .api.chat import router as chat_router

app = FastAPI()

app.include_router(chat_router)

from .pipeline.generator import generate_response, generate_runtime

#小测试
print("开始")
session_id = input("请输入本次会话id：")
aiRuntime = generate_runtime(session_id)

while True:
    user_input = input("用户：")
    response=aiRuntime.chat(user_input)
    print("小助手：", response)