from ..pipeline.generator import generate_runtime
from ..api_schemas.chat import ChatRequest, ChatResponse
from fastapi import APIRouter

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:

    user_input=request.user_input,
    session_id=request.session_id
    
    runtime = generate_runtime(session_id)
    response = runtime.chat(user_input)
    
    return ChatResponse(
        response=response
    )