import os
from typing import AsyncGenerator
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, Depends, HTTPException, Query
from starlette.responses import StreamingResponse
from service.document_service import upload_document, process_document_for_rag
from .dependency import get_current_user
from database.models import User
from database.utils import get_documents_by_user, get_document_by_name_or_id, create_document

document_router = APIRouter()


@document_router.post("/process-document")
async def process_document(file: UploadFile, user: User = Depends(get_current_user)):
    """
    Process the uploaded document and store it in the local storage
    Args:
        file:

    Returns:

    """
    existing_document = await get_document_by_name_or_id(user.id, name=file.filename)
    if existing_document:
        return {"message": f"Document '{file.filename}' has already been uploaded by the user", "success": True}
    
    file_path = await upload_document(file, user.id)
    res, message = process_document_for_rag(file_path, user_id=user.id)
    if res:
        await create_document(file.filename, file_path, user.id)
    return {"message": message.format(file.filename), "success": res}


@document_router.get("/get-documents")
async def get_documents(
    user: User = Depends(get_current_user),
    page: int = Query(1, title="Page Number", description="Page number for pagination (default: 1)"),
    per_page: int = Query(10, title="Per Page", description="Number of documents per page (max: 25)"),
):
    """
    Fetch documents for a user, paginate the response, and return document id and name tuples.
    """
    if per_page < 1 or per_page > 25:
        raise HTTPException(status_code=400, detail="Per page must be between 1 and 25")

    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be positive")

    documents = await get_documents_by_user(user_id=user.id)

    total_documents = len(documents)
    total_pages = (total_documents + per_page - 1) // per_page

    if page > total_pages:
        raise HTTPException(status_code=400, detail=f"Page number must be between 1 and {total_pages}")

    next_page = page + 1 if page < total_pages else None

    prev_page = page - 1 if page > 1 else None

    data = [
        [documents[i].id, documents[i].name] for i in range((page - 1) * per_page, min(total_documents, page * per_page))
    ]

    response = {"next_page": next_page, "prev_page": prev_page}
    response["data"] = data
    return response


@document_router.get("/get-document/{doc_id}")
async def get_document(doc_id: int, user: User = Depends(get_current_user)):
    """
    Get a specific document by its id
    Args:
        doc_id: The ID of the document to retrieve
        user: The current user

    Returns:
        StreamingResponse: The document file streamed as a response
    """

    async def get_data_from_file(file_path: os.PathLike) -> AsyncGenerator:
        async with aiofiles.open(file=file_path, mode="rb") as file_like:
            yield await file_like.read()

    docs = await get_document_by_name_or_id(user_id=user.id, doc_id=doc_id)
    if not docs:
        raise HTTPException(status_code=404, detail="Document not found")
    doc_path = Path(docs.path)
    if not doc_path.is_file():
        raise HTTPException(status_code=404, detail="Document file not found")

    return StreamingResponse(content=get_data_from_file(doc_path))
