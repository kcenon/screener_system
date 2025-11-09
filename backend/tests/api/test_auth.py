"""Tests for authentication API endpoints"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.db.models import User


class TestAuthRegistration:
    """Test user registration endpoint"""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration"""
        response = await client.post(
            "/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "name": "New User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["name"] == "New User"
        assert data["user"]["subscription_tier"] == "free"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, db: AsyncSession):
        """Test registration with existing email"""
        # Create existing user
        existing_user = User(
            email="existing@example.com",
            password_hash=get_password_hash("password"),
            name="Existing User",
        )
        db.add(existing_user)
        await db.commit()

        # Try to register with same email
        response = await client.post(
            "/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "AnotherPass123",
                "name": "Another User",
            },
        )

        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        response = await client.post(
            "/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "weak",
                "name": "User",
            },
        )

        assert response.status_code == 422


class TestAuthLogin:
    """Test user login endpoint"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, db: AsyncSession):
        """Test successful login"""
        # Create user
        user = User(
            email="testuser@example.com",
            password_hash=get_password_hash("TestPassword123"),
            name="Test User",
        )
        db.add(user)
        await db.commit()

        # Login
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "testuser@example.com"

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, db: AsyncSession):
        """Test login with invalid password"""
        # Create user
        user = User(
            email="testuser@example.com",
            password_hash=get_password_hash("CorrectPassword123"),
            name="Test User",
        )
        db.add(user)
        await db.commit()

        # Login with wrong password
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "WrongPassword123",
            },
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user"""
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123",
            },
        )

        assert response.status_code == 401


class TestAuthProtectedEndpoints:
    """Test protected endpoints requiring authentication"""

    @pytest.mark.asyncio
    async def test_get_current_user_success(
        self, client: AsyncClient, db: AsyncSession
    ):
        """Test accessing protected endpoint with valid token"""
        # Create user
        user = User(
            email="testuser@example.com",
            password_hash=get_password_hash("Password123"),
            name="Test User",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Create access token
        access_token = create_access_token(user.id)

        # Access protected endpoint
        response = await client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "testuser@example.com"
        assert data["name"] == "Test User"

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token"""
        response = await client.get("/v1/auth/me")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test accessing protected endpoint with invalid token"""
        response = await client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401
