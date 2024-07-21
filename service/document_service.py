import os
from fastapi import UploadFile

from repository.vector_db import vdb
from utils.file_handler import FileHandler


# This needs to be changed for switching between different file storage methods
FILE_HANDLER = os.getenv("FILE_HANDLER", "local")


async def upload_document(file: UploadFile, user_id: int):
    file_handler = FileHandler(FILE_HANDLER)
    return await file_handler.save_file(file=file, user_id=user_id)


def process_document_for_rag(file_path: os.PathLike, user_id: int):
    res = False
    message = "File {} uploaded sucessfully"
    try:
        chunks = vdb.generate_text_chunks(file_path)
        vdb.encode_and_store(chunks=chunks, user_id=user_id)
        res = True
    except Exception as e:
        message = "Exception occured while processing the doc {}: " + f"{e}"
    return res, message
