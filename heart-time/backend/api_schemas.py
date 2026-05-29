from pydantic import BaseModel

# ===== Chat 接口模型（已更新为 session_id）=====
class ChatRequest(BaseModel):
    session_id: str
    user_input: str

class ChatResponse(BaseModel):
    response: str

# ===== 登录模型 =====
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user_id: str

# ===== 日记模型 =====
class CreateDiaryRequest(BaseModel):
    user_id: int
    content: str
    content_type: str = "text"

class CreateDiaryResponse(BaseModel):
    diary_id: int
    status: str

class DiaryItem(BaseModel):
    diary_id: int
    content: str
    emotion_tags: str = None
    ai_reply: str = None
    create_time: str

# ===== 角色模型 =====
class RoleItem(BaseModel):
    role_id: int
    role_name: str
    gentleness: float
    rationality: float

# ===== 会话管理模型 =====
class CreateSessionRequest(BaseModel):
    user_id: str

class CreateSessionResponse(BaseModel):
    session_id: str

class DeleteSessionResponse(BaseModel):
    status: str

# ===== 通用错误 =====
class ErrorResponse(BaseModel):
    error: str
    code: int