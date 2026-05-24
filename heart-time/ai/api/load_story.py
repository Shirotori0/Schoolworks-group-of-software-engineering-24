from ..pipeline.embedding_runtime import EmbeddingRuntime
from ..api_schemas.load_story import LoadStoryRequest, LoadStoryResponse
from fastapi import APIRouter

router = APIRouter()

# 功能：加载故事文本文件，进行分块和向量化处理，并存储到向量数据库中
@router.post("/load_story", response_model=LoadStoryResponse)
def load_story(request: LoadStoryRequest) -> LoadStoryResponse:

    file_path = request.file_path
    
    embedding_runtime = EmbeddingRuntime(file_path)
    embedding_runtime.process_file()
    
    return LoadStoryResponse(
        message=f"File '{file_path}' loaded and processed successfully."
    )