from pydantic import BaseModel

class MakeScriptRequest(BaseModel):
    file_path: str
    user_input: str

class MakeScriptResponse(BaseModel):
    message: str