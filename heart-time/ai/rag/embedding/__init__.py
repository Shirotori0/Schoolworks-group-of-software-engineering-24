from .embedder import Embedder

embedder = Embedder()

def embed(text: str):
    return embedder.embed(text)

def embed_batch(texts: list):
    return embedder.embed_batch(texts)