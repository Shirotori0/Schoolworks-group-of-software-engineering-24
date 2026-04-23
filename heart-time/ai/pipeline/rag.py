#组装embedding和vector store模块
from ..embedding import embedder
from ..vector_store import vector_store

def retrieve_memory(text: str, user_id: str, top_k: int = 3):
    # 将用户输入文本转换为向量
    query_vector = embedder.embed(text)

    # 检索与输入文本向量相似的历史文本
    memories = vector_store.search(
        query_vector,
        user_id
        , top_k
    )
    
    return memories