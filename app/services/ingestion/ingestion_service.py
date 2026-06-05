from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.chunk import Chunk
from app.db.models.document import Document
from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.file_parser import parse_file
from app.services.rag.embedding import get_default_embedding_service


class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # 共享 chat.py 同一个 bge-m3 单例(由 get_default_embedding_service 管理)
        # 不要在 __init__ 里 new EmbeddingService(),会绕过单例
        self.embedding = get_default_embedding_service()

    async def ingest_file(self, filename: str, content: bytes):
        # 1️⃣ 解析文件
        text = parse_file(filename, content)

        # 2️⃣ chunk 切分
        chunks = chunk_text(text)

        # 3️⃣ embedding
        embeddings = await self.embedding.aembed_texts(chunks)

        # 4️⃣ 保存 document
        doc = Document(
            filename=filename,
        )
        self.db.add(doc)
        await self.db.flush()  # 获取 doc.id

        # 5️⃣ 保存 chunks
        chunk_objs = []
        for i, chunk in enumerate(chunks):
            chunk_obj = Chunk(
                content=chunk,
                embedding=embeddings[i],
                document_id=doc.id,
            )
            chunk_objs.append(chunk_obj)

        self.db.add_all(chunk_objs)

        await self.db.commit()

        return {
            "document_id": doc.id,
            "chunks": len(chunks),
        }