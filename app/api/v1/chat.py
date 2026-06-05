from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag.embedding import get_default_embedding_service
from app.services.rag.generator import RAGService
from app.services.rag.retriever import Retriever

router = APIRouter(prefix="/chat", tags=["chat"])


# Retriever / RAGService 构造无开销,保持 module-level
retriever = Retriever()
rag_service = RAGService()


@router.post("", response_model=ChatResponse)
async def chat(
        request: ChatRequest,
        db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    # bge-m3 走统一 lazy 单例,首次调用才加载(~80s)
    embedding_service = get_default_embedding_service()
    query_vec = await embedding_service.aembed_query(request.query)

    docs = await retriever.search(query_vec, db)

    answer = await rag_service.generate(request.query, docs)
    return ChatResponse(answer=answer)
