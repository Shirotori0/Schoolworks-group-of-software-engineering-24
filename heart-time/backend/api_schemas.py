from pydantic import BaseModel
from typing import Optional


# ===== Chat 接口模型 =====
class ChatRequest(BaseModel):
    session_id: str
    user_input: str
    memory_id: Optional[str] = None


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
    memory_id: Optional[str] = None


class CreateSessionResponse(BaseModel):
    session_id: str
    memory_id: Optional[str] = None


class DeleteSessionResponse(BaseModel):
    status: str


class SessionItem(BaseModel):
    session_id: str
    memory_id: Optional[str] = None
    title: str
    created_at: str
    updated_at: str


class MessageItem(BaseModel):
    message_id: str
    sender: str
    content: str
    created_at: str


# ===== 通用错误 =====
class ErrorResponse(BaseModel):
    error: str
    code: int


# ===== 记忆体相关模型 =====
class CreateMemoryRequest(BaseModel):
    user_id: str
    name: str
    summary: str = ""


class MemoryResponse(BaseModel):
    memory_id: str
    user_id: str
    name: str
    summary: str
    source_file_path: str
    vector_file_path: str
    import_status: str
    created_at: str
    updated_at: str


class DeleteMemoryResponse(BaseModel):
    status: str


class UpdateMemoryRequest(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None


class UpdateMemoryResponse(BaseModel):
    memory_id: str
    name: str
    summary: str
    updated_at: str