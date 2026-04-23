# 向量处理模块，负责存储文本、向量和用户ID，并提供基于余弦相似度的搜索功能

import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class VectorStore:
    def __init__(self):
        self.texts = []
        self.vectors = []
        self.user_ids = []

# 添加向量
    def add(self, text, vector, user_id):
        self.texts.append(text)
        self.vectors.append(vector)
        self.user_ids.append(user_id)

# 匹配向量
    def search(self, query_vector, user_id, top_k=3):
        results = []

        for i, vector in enumerate(self.vectors):
            if self.user_ids[i] == user_id:
                sim = cosine_similarity(query_vector, vector)
                results.append((sim, self.texts[i]))

        results.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in results[:top_k]]
    

