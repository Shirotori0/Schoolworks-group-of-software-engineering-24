
class TextChunker:

    def paragraph_split(self, text: str, chunk_size: int = 300):
        
        chunks = []

        current = ""

        for paragraph in text.split("\n"):
            if paragraph.strip() == "":
                continue
            if len(paragraph) <= chunk_size:
                current += paragraph + "\n"
                chunks.append(current.strip())
                current = ""
            else:
                paragraphs = paragraph.split("。")
                current_sentence_index = 0
                for sentence in paragraphs:
                    # 如果当前句子加上之前的内容不超过chunk_size，或者剩余的句子数量不超过3，就继续添加到当前块
                    if len(current) + len(sentence) <= chunk_size or len(paragraphs[current_sentence_index:]) <= 3:
                        current += sentence + "。"
                    # 否则，就添加到新的块
                    else:
                        current += sentence + "。"
                        chunks.append(current.strip())
                        current = sentence + "。"

                    current_sentence_index += 1
        
        if current:
            chunks.append(current.strip())
        
        return chunks

