import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.users import UserRepository
from src.database.models import User
from src.schemas import UserCreate


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.mark.asyncio
async def test_create_user(user_repository: UserRepository, mock_session: AsyncMock):
    user_model = UserCreate(
        username="new_user", email="user@test.com", password="123456789"
    )

    mock_result = MagicMock()

    result = await user_repository.create_user(user_model, "testavatar")
    assert isinstance(result, User)
    assert result.username == "new_user"
