from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from async_db import get_db
from facade.container_facade import container_facade
from Bio.Data import CodonTable
import users
import admin
from create_task import run_analysis_periodically

@app.on_event('startup')
async def startup_event():
    async for db in get_db():
        set_db_for_facades(db)
        break
    await run_analysis_periodically()

genetic_code = CodonTable.unambiguous_dna_by_name["Standard"]

# Initialize the BLAST results cache
blast_results_cache = {}


app.include_router(users.router)
app.include_router(admin.router)


@app.get('/')
async def index():
    return {'message': 'Hello World'}