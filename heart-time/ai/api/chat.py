from ..pipeline.generator import generate_response
from ..api_schemas.chat import ChatRequest, ChatResponse
from fastapi import APIRouter

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:

    response = generate_response(
        user_input=request.user_input,
        user_id=request.user_id
    )

    return ChatResponse(
        response=response
    )