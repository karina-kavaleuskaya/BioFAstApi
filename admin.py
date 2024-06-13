import models
import schemas
from users import get_current_user
from fastapi import HTTPException, status, Depends, APIRouter, Form, UploadFile, File
from pathlib import Path

router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


