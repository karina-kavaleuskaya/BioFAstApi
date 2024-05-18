from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker



SQLALCHEMY_DATABASE_URL= "postgresql+asyncpg://postgres:****@****/****"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()