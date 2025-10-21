from unittest.mock import patch, Mock

from conftest import test_user


def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json={
            "first_name": "Tester",
            "last_name": "Real",
            "email": "test@email.me",
            "phone": "234 343 34 55",
            "date_of_birth": "1993-10-21",
            "info": "This is tester contact",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == "Tester"
    assert "id" in data


def test_get_contacts(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/contacts", headers=headers)

    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list)
    assert data[0]["first_name"] == "Tester"
    assert "id" in data[0]


def test_get_contact_by_id(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Tester"
    assert "id" in data


def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_update_contact(client, get_token):
    response = client.put(
        "/api/contacts/1",
        json={
            "first_name": "Admin",
            "last_name": "Unreal",
            "email": "admin@test.me",
            "phone": "123 343 34 55",
            "date_of_birth": "1993-10-21",
            "info": "This is admin contact",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Admin"
    assert "id" in data


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Admin"
    assert "id" in data
