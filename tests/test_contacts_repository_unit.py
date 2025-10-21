import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.contacts import ContactRepository
from src.database.models import User, Contact
from src.schemas import ContactModel
from datetime import date


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_all_contacts(
    user: User, contact_repository: ContactRepository, mock_session: AsyncMock
):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [create_contact(user)]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(user=user, skip=0, limit=10)

    assert len(contacts) == 1
    assert contacts[0].first_name == "John"


@pytest.mark.asyncio
async def test_get_contact_by_id(
    user: User, contact_repository: ContactRepository, mock_session: AsyncMock
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = create_contact(user)
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "John"


@pytest.mark.asyncio
async def test_create_contact(
    user: User, contact_repository: ContactRepository, mock_session: AsyncMock
):
    contact_model = create_contact_model()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        first_name=contact_model.first_name,
        last_name=contact_model.last_name,
        email=contact_model.email,
        phone=contact_model.phone,
        user=user,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.create_contact(body=contact_model, user=user)

    assert isinstance(result, Contact)
    assert result.first_name == "John"


@pytest.mark.asyncio
async def test_delete_contact(
    user: User, contact_repository: ContactRepository, mock_session: AsyncMock
):
    existing_contact = create_contact(user=user)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.delete_contact(
        contact_id=existing_contact.id, user=user
    )

    assert result is not None
    assert result.first_name == "John"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_contact(
    user: User, contact_repository: ContactRepository, mock_session: AsyncMock
):
    existing_contact_model = create_contact_model()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact_model
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(
        contact_id=1, body=existing_contact_model, user=user
    )

    assert result is not None
    assert result.first_name == "John"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact_model)


@pytest.mark.asyncio
async def test_search_contacts(
    user: User, contact_repository: ContactRepository, mock_session: AsyncMock
):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [create_contact(user)]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.search_contacts(
        user=user, first_name="John", last_name=None, email=None, skip=0, limit=10
    )

    assert len(contacts) == 1
    assert contacts[0].first_name == "John"


def create_contact(user: User) -> Contact:
    return Contact(id=1, first_name="John", last_name="Doe", user=user)


def create_contact_model() -> ContactModel:
    return ContactModel(
        first_name="John",
        last_name="Doe",
        email="test@test.me",
        phone="034 434 23 54",
        date_of_birth=date.today(),
        info="Friend",
    )
