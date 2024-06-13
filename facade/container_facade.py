import models
import schemas
from facade.base_facade import BaseFacade


class ContainerFacade(BaseFacade):
    async def create_container(self, user_id: int, file_path: str) -> models.Container:
        db_container = models.Container(
            user_id=user_id,
            file_path=file_path,
        )

        self.db.add(db_container)
        await self.db.commit()
        await self.db.refresh(db_container)
        return db_container


container_facade = ContainerFacade()