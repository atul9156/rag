import os
import aiofiles
from fastapi import UploadFile


class LocalFileHandler:
    def __init__(self):
        self.base_path = os.path.join(os.getcwd(), "files")
        os.makedirs(self.base_path, exist_ok=True)

    async def save_file(self, file, user_id: int):
        user_path = os.path.join(self.base_path, str(user_id))
        os.makedirs(user_path, exist_ok=True)
        file_path = os.path.join(user_path, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await file.read())
        return file_path


FILE_HANDLER_TYPES = {
    "local": LocalFileHandler,
    # Add other classes here
}


class FileHandler:
    def __init__(self, file_handler_type: str):
        self.saver_object = FILE_HANDLER_TYPES.get(file_handler_type.lower(), None)
        if not self.saver_object:
            raise NotImplementedError(f"The following file saving variant is not yet implemented: {self.variant}")

    async def save_file(self, file: UploadFile, user_id: int):
        return await self.saver_object().save_file(file, user_id)
