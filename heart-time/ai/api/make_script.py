from ..pipeline.generator import generate_runtime
from .schemas.make_script import MakeScriptRequest, MakeScriptResponse
from fastapi import APIRouter

router = APIRouter()

@router.post("", response_model=MakeScriptResponse)
def make_script(request: MakeScriptRequest) -> MakeScriptResponse:
    file_path = request.file_path
    user_input = request.user_input
    
    session_id = "make_script_session"
    runtime = generate_runtime(session_id, script_path=file_path)
    response = runtime.make_script(file_path, user_input)
    
    return MakeScriptResponse(
        message=response
    )