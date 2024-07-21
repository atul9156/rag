from fastapi import APIRouter, Depends, status, HTTPException
import shutil
import os

from service.conversation_service import ConversationService
from .dependency import get_current_user
from database.models import User
from repository.vector_db import vdb
from database.utils import delete_documents_by_user

from pydantic import BaseModel

conversation_router = APIRouter()
conversation_service = ConversationService()

class ChatRequest(BaseModel):
    query: str


@conversation_router.post("/chat")
async def chat(chatRequest: ChatRequest, user: User = Depends(get_current_user)):
    """
    Chat endpoint to get a response from the model
    Args:
        query:

    Returns:

    """
    if not chatRequest.query:
        raise HTTPException(status_code=400, detail="Request is not well formed. Please check the API docs")
    return {"message": conversation_service.chat(chatRequest.query, user_id=user.id, vdb=vdb)}


@conversation_router.post("/new-chat", status_code=status.HTTP_200_OK)
async def new_chat(user: User = Depends(get_current_user)):
    """
    This will invalidate the context (currently uploaded documents and chunks) and start a new conversation
    Args:
        query:

    Returns:

    """
    # From vector db remove the old entry
    vdb.delete(user.id)
    # from docuemnt model, remove all documents
    folder_path = os.path.join(os.getcwd(), "files", str(user.id))
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    # from files, remove all files
    await delete_documents_by_user(user_id=user.id)
    return {"sucess": True, "message": "Previous chat data deleted successfully"}
