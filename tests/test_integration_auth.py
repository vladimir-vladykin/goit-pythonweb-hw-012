from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import User
from src.services.auth import create_email_confirm_token, create_password_reset_token
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "ron009",
    "email": "ron009@gmail.com",
    "password": "12345678",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "User already exists"


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email is not confirmed"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Wrong credentials"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Wrong credentials"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_confirmed_email_fail(client):
    token = "fake_123"
    response = client.get(f"api/auth/confirmed_email/{token}")

    assert response.status_code == 422, response.text


@pytest.mark.asyncio
async def test_confirmed_email_success(client):
    email = user_data.get("email")
    token = create_email_confirm_token({"sub": email})
    response = client.get(f"api/auth/confirmed_email/{token}")

    assert response.status_code == 200, response.text
    data = response.json()

    # we expect this because user already marked as confirmed
    assert data["message"] == "Email already confirmed"


@pytest.mark.asyncio
async def test_request_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)

    email = user_data.get("email")
    response = client.post("api/auth/request_email", json={"email": email})
    assert response.status_code == 200, response.text
    data = response.json()

    # we expect this because user already marked as confirmed
    assert data["message"] == "Email already confirmed"


@pytest.mark.asyncio
async def test_request_reset_password(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_reset_email", mock_send_email)

    email = user_data.get("email")
    response = client.post("api/auth/request_reset_password", json={"email": email})

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["message"] == "Check your email"


@pytest.mark.asyncio
async def test_get_password_reset_page(client):
    email = user_data.get("email")
    token = create_password_reset_token({"sub": email})

    response = client.get(f"api/auth/password_reset/{token}")
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_password_reset_fail(client):
    token = "fake_123"
    response = client.post(
        f"api/auth/password_reset/{token}", data={"new_password": "some_password"}
    )

    assert response.status_code == 422, response.text


@pytest.mark.asyncio
async def test_password_reset_success(client):
    email = user_data.get("email")
    token = create_password_reset_token({"sub": email})
    response = client.post(
        f"api/auth/password_reset/{token}", data={"new_password": "some_password"}
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["message"] == "Password updated successfully"
