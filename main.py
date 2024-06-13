from fastapi import FastAPI, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from async_db import get_db
from facade.container_facade import container_facade
import users
import admin
from tasks import run_analysis_periodically


def set_db_for_facades(db):
    container_facade.set_db(db)


OAuth2_SCHEME = OAuth2PasswordBearer('user/login/')

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    async for db in get_db():
        set_db_for_facades(db)
        break
    run_analysis_periodically.apply_async()


app.include_router(users.router)
app.include_router(admin.router)



@app.get('/')
async def index():
    return {'message': 'Hello World'}