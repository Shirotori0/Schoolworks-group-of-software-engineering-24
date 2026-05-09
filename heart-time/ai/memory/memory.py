# 向量化并存储用户历史记录
from ..vector_store import vector_store
from ..embedding import embedder

def store_memory(text: str, user_id: str):
    # 将用户输入文本转换为向量
    vector = embedder.embed(text)

    # 存储文本、向量和用户ID
    vector_store.add(text, vector, user_id)