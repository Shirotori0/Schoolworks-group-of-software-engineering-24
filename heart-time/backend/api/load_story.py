import sys
sys.path.insert(0, r"D:\develop\Schoolworks-group-of-software-engineering-24\heart-time")

from fastapi import APIRouter
from ai.pipeline.embedding_runtime import EmbeddingRuntime
from pydantic import BaseModel

router = APIRouter()

class LoadStoryRequest(BaseModel):
    file_path: str

class LoadStoryResponse(BaseModel):
    message: str

@router.post("/load_story", response_model=LoadStoryResponse)
async def load_story(request: LoadStoryRequest):
    embedding_runtime = EmbeddingRuntime(request.file_path)
    embedding_runtime.process_file()
    return LoadStoryResponse(message=f"File '{request.file_path}' loaded and processed successfully.")