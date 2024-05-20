from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from async_db import get_db
from sqlalchemy.future import select
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import models
import schemas
from facade.file_facade import FILE_MANAGER
from facade.containrt_facade import container_facade



PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')
ALGORITHM = 'HS256'
SECRET_KEY = '****'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
OAuth2_SCHEME = OAuth2PasswordBearer(tokenUrl='users/login')

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


async def get_user(db: AsyncSession, email):
    async with db:
        result = await db.execute(select(models.User).filter(models.User.email == email))
        return result.scalars().first()


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta):
    data_to_process = data.copy()
    expire = datetime.utcnow() + expires_delta
    data_to_process.update({'exp': expire})
    encode_jwt = jwt.encode(data_to_process, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user(db, email)
    if not user or not verify_password(password, user.password_hash):
        return False
    return user


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(OAuth2_SCHEME),
                           db: AsyncSession = Depends(get_db)):

    credental_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        email: str = payload.get('sub')
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'}
            )
        user = await db.execute(select(models.User).filter(models.User.email == email))
        user = user.scalars().first()
        if not user:
            raise credental_exception
        return user
    except(JWTError, AttributeError):
        raise credental_exception


@router.post('/register/', response_model=schemas.User)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists!')
    hashed_password = PWD_CONTEXT.hash(user.password)
    db_user = models.User(email=user.email, password_hash=hashed_password, telegram=user.telegram)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post('/login/', response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers ={'WWW-Authenticate':'Bearer'}
        )
    token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.email}, expires_delta=token_expire
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/add-file/', response_model=schemas.Container)
async def create_container(
        file: UploadFile = File(...),
        current_user: models.User = Depends(get_current_user),
):
    file_path = f'static/containers/{current_user.id}/{file.filename}'
    await FILE_MANAGER.save_file(file, file_path)

    container_data = schemas.ContainerCreate(
        user_id=current_user.id,
        file_path=file_path
    )

    db_container = await container_facade.create_container(container_data, file_path)

    return db_container