import uuid

from ..rag.chunk import textChunker
from ..rag.vector_store import vectorStore
from ..rag.embedding import embedder

from ..utils.load_file import textLoader
from ..rag.chunk.chunk import Chunk

class EmbeddingRuntime:

    def __init__(self, source_path: str):
        self.source_path = source_path
        
        self.textChunker = textChunker
        self.vectorStore = vectorStore
        self.embedder = embedder
        self.fileLoader = self.choose_fileloader()

        
        self.vectorStore.path = f"ai/data/vectors/{source_path.split('/')[-1]}.jsonl"

    
    def process_file(self):

        text = self.fileLoader.load(self.source_path)

        chunk_texts = self.textChunker.paragraph_split(text)

        for index, chunk_text in enumerate(chunk_texts):

            chunk_vector = self.embedder.embed(chunk_text)

            chunk = Chunk(
                chunk_id = str(uuid.uuid4()),
                text = chunk_text,
                vector = chunk_vector,
                metadata = {
                    "file_path": self.source_path,
                    "index": index
                }
            )

            self.vectorStore.add_to_buffer(chunk)

        self.vectorStore.flush()

    def choose_fileloader(self):

        if self.source_path.endswith(".txt"):
            return textLoader
        
        # 其它类型待实现







