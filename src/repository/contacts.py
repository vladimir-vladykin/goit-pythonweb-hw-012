from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact, User
from src.schemas import ContactModel
from typing import List
from datetime import date, timedelta


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id, user)

    async def delete_contact(self, contact_id: int, user: User) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def search_contacts(
        self,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        skip: int,
        limit: int,
        user: User,
    ) -> List[Contact]:
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        if first_name:
            stmt = stmt.filter_by(first_name=first_name)
        if last_name:
            stmt = stmt.filter_by(last_name=last_name)
        if email:
            stmt = stmt.filter_by(email=email)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_closest_brithday_contacts(self, user: User) -> List[Contact]:
        today = date.today()
        week_from_now = today + timedelta(days=7)

        range_start_day = today.day
        range_start_month = today.month

        range_end_day = week_from_now.day
        range_end_month = week_from_now.month

        stmt = (
            select(Contact)
            .filter_by(user=user)
            .where(extract("day", Contact.date_of_birth) >= range_start_day)
            .where(extract("month", Contact.date_of_birth) >= range_start_month)
            .where(extract("day", Contact.date_of_birth) <= range_end_day)
            .where(extract("month", Contact.date_of_birth) <= range_end_month)
        )

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
