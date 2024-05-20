import os
from fastapi import UploadFile, HTTPException
import aiofiles


class FileManager:
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        os.makedirs(self.base_directory, exist_ok=True)

    async def save_file(self, file: UploadFile, file_path: str) -> None:
        try:
            full_path = os.path.join(self.base_directory, file_path)
            directory = os.path.dirname(full_path)
            os.makedirs(directory, exist_ok=True)

            async with aiofiles.open(full_path, 'wb') as out_file:
                while content := await file.read(1024):
                    await out_file.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    async def get_file(self, file_path: str) -> bytes:
        full_path = os.path.join(self.base_directory, file_path)
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        try:
            async with aiofiles.open(full_path, 'rb') as file:
                return await file.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not read file: {str(e)}")


FILE_MANAGER = FileManager(base_directory="static/containers")