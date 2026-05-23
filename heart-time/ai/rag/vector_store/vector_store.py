# 向量处理模块，负责存储文本、向量和用户ID，并提供基于余弦相似度的搜索功能
import json
import os
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class VectorStore:
    def __init__(self):
        self.texts = []
        self.vectors = []
        self.user_ids = []

        self.buffer = []
        self.flush_size = 20
        self.path = "ai/data/vectors/vector.jsonl"

# 添加向量
    def add(self, text, vector, user_id):
        self.texts.append(text)
        self.vectors.append(vector)
        self.user_ids.append(user_id)

    def add_to_buffer(self, chunk):
        self.buffer.append(chunk)

# 匹配向量
    def search(self, query_vector, user_id, top_k=3):
        results = []

        for i, vector in enumerate(self.vectors):
            if self.user_ids[i] == user_id:
                sim = cosine_similarity(query_vector, vector)
                results.append((sim, self.texts[i]))

        results.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in results[:top_k]]
    

    def flush(self):

        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        with open(self.path, "a", encoding="utf-8") as f:

            for text_chunk in self.buffer:

                f.write(json.dumps(
                    {
                        "chunk_id": text_chunk.chunk_id,
                        "text": text_chunk.text,
                        "vector": text_chunk.vector,
                        "metadata": text_chunk.metadata
                    },
                    ensure_ascii=False
                ))
                f.write("\n")

        self.buffer.clear()