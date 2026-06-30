from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.role import Role


def test_register_user(client: TestClient) -> None:
    """
    Test successful user registration.
    """
    response = client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    # Ensure sensitive fields are not leaked in response
    assert "hashed_password" not in data


def test_register_user_duplicate(client: TestClient) -> None:
    """
    Test that registering with an already existing email returns HTTP 409.
    """
    # First registration
    client.post(
        "/users/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    # Second registration with same email
    response = client.post(
        "/users/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered."


def test_login_user(client: TestClient) -> None:
    """
    Test successful login and JWT access token retrieval.
    """
    # Register user first
    client.post(
        "/users/register",
        json={"email": "login@example.com", "password": "password123"}
    )
    # Login user
    response = client.post(
        "/users/login",
        json={"email": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_invalid_credentials(client: TestClient) -> None:
    """
    Test that logging in with incorrect credentials returns HTTP 401.
    """
    # Attempt login for non-existent user
    response = client.post(
        "/users/login",
        json={"email": "wrong@example.com", "password": "password123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."


def test_get_me_endpoint(client: TestClient) -> None:
    """
    Test accessing the JWT-protected /users/me endpoint.
    """
    # Register user
    client.post(
        "/users/register",
        json={"email": "me@example.com", "password": "password123"}
    )
    # Login user
    login_response = client.post(
        "/users/login",
        json={"email": "me@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Access protected route with Bearer token
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"


def test_list_users_non_admin_forbidden(client: TestClient) -> None:
    """
    Test that a non-admin user cannot access the Admin-only /users/ list endpoint.
    """
    # Register user
    client.post(
        "/users/register",
        json={"email": "regular@example.com", "password": "password123"}
    )
    # Login user
    login_response = client.post(
        "/users/login",
        json={"email": "regular@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Attempt to list all users
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "do not have permission" in response.json()["detail"]


def test_list_users_admin_allowed(client: TestClient, db_session: Session) -> None:
    """
    Test that an admin user can access the Admin-only /users/ list endpoint.
    """
    # 1. Register a user
    client.post(
        "/users/register",
        json={"email": "admin@example.com", "password": "password123"}
    )
    
    # 2. Query the user directly in the database and assign the "Admin" role
    user = db_session.execute(
        select(User).where(User.email == "admin@example.com")
    ).scalar_one()
    
    admin_role = db_session.execute(
        select(Role).where(Role.name == "Admin")
    ).scalar_one()
    
    user.role_id = admin_role.id
    db_session.commit()

    # 3. Login the admin user
    login_response = client.post(
        "/users/login",
        json={"email": "admin@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # 4. Access list users endpoint
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    users_list = response.json()
    assert len(users_list) >= 1
    emails = [u["email"] for u in users_list]
    assert "admin@example.com" in emails
