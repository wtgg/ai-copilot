from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.ingestion.ingestion_service import IngestionService

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    上传文件 → 解析 → chunk → embedding → 入库
    """

    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    content = await file.read()

    service = IngestionService(db)

    result = await service.ingest_file(
        filename=file.filename,
        content=content,
    )

    return {
        "filename": file.filename,
        "document_id": result["document_id"],
        "chunks": result["chunks"],
    }