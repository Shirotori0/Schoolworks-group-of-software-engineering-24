from pydantic import BaseModel

class LoadStoryRequest(BaseModel):
    file_path: str

class LoadStoryResponse(BaseModel):
    message: str