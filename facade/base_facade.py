from sqlalchemy.ext.asyncio import AsyncSession


class BaseFacade:
    db: AsyncSession = None

    @classmethod
    def set_db(cls, db: AsyncSession):
        cls.db = db