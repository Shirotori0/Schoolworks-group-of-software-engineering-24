from .schemas.chat_cosplay import ChatCosplayRequest, ChatCosplayResponse
from ..pipeline.generator import generate_runtime
from fastapi import APIRouter

router = APIRouter()

@router.post("", response_model=ChatCosplayResponse)
def chat_cosplay(request: ChatCosplayRequest) -> ChatCosplayResponse:
    runtime = generate_runtime(request.session_id)
    response = runtime.chat(request.user_input, script_path=request.script_path)
    
    return ChatCosplayResponse(
        response=response
    )