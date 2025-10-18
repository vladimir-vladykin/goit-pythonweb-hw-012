from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel
from src.database.models import User


class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def get_contacts(self, skip: int, limit: int, user: User):
        return await self.contact_repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def create_contact(self, body: ContactModel, user: User):
        return await self.contact_repository.create_contact(body, user)

    async def delete_contact(self, contact_id: int, user: User):
        return await self.contact_repository.delete_contact(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactModel, user: User):
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def search_contacts(
        self,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        skip: int,
        limit: int,
        user: User,
    ):
        return await self.contact_repository.search_contacts(
            first_name, last_name, email, skip, limit, user
        )

    async def get_closest_brithday_contacts(self, user: User):
        return await self.contact_repository.get_closest_brithday_contacts(user)
