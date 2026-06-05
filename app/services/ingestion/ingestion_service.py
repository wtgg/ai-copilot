from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.chunk import Chunk
from app.db.models.document import Document
from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.file_parser import parse_file


class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # 不要在 __init__ 里调 get_default_embedding_service(),
        # 会同步触发 bge-m3 加载并冻结 event loop(80s+),Ctrl+C 都杀不掉。
        # 改用懒加载: 首次 aembed_texts 时才取(此时应已被 main.py lifespan warm-up 完)
        self._embedding = None

    @property
    def embedding(self):
        if self._embedding is None:
            from app.services.rag.embedding import get_default_embedding_service
            self._embedding = get_default_embedding_service()
        return self._embedding

    async def ingest_file(self, filename: str, content: bytes):
        # 1️⃣ 解析文件
        text = parse_file(filename, content)
        logger.debug(f"解析文件: {filename}, 文本长度: {len(text)}")

        # 2️⃣ chunk 切分
        chunks = chunk_text(text)
        logger.debug(f"切分文件: {filename}, 切分后的 chunk 数量: {len(chunks)}")

        # 3️⃣ embedding
        embeddings = await self.embedding.aembed_texts(chunks)
        logger.debug(f"embedding 文件: {filename}, 嵌入向量长度: {len(embeddings)}")

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