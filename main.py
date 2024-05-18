from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from async_db import get_db
import users
import admin


OAuth2_SCHEME = OAuth2PasswordBearer('user/login/')

app = FastAPI()


app.include_router(users.router)
app.include_router(admin.router)


@app.get('/')
async def index():
    return {'message': 'Hello World'}