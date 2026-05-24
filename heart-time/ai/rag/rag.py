#组装embedding和vector store模块
from .embedding import embedder
from .vector_store import vectorStore

def retrieve_context(text: str, top_k: int = 10):
    # 将用户输入文本转换为向量
    query_vector = embedder.embed(text)

    # 检索与输入文本向量相似的历史文本
    context = vectorStore.retrieve_vectors(
        query_vector,
        top_k
    )
    
    return context
