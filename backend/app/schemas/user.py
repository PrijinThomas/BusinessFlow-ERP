from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserBase(BaseModel):
    """
    Base Pydantic schema for User containing shared fields.
    """
    email: EmailStr = Field(..., description="The unique email address of the user")


class UserCreate(UserBase):
    """
    Schema for user registration / creation.
    Includes the plain-text password, which will be hashed before storing.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="The plain-text password of the user. Must be between 8 and 128 characters."
    )


class UserResponse(UserBase):
    """
    Schema for user data returned in API responses.
    Excludes sensitive data like passwords (plain or hashed).
    """
    # configures Pydantic v2 to work with ORM models (like SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="The unique identifier of the user")
    is_active: bool = Field(..., description="Flag indicating if the user account is active")
    is_superuser: bool = Field(..., description="Flag indicating if the user has superuser privileges")
    created_at: datetime = Field(..., description="The timestamp when the user account was created")


class UserLogin(BaseModel):
    """
    Schema for user login credentials.
    """
    email: EmailStr = Field(..., description="The user's registered email address")
    password: str = Field(..., description="The user's password")


class Token(BaseModel):
    """
    Schema for the returned authentication token.
    """
    access_token: str = Field(..., description="The generated JWT access token")
    token_type: str = Field(..., description="The type of token (typically bearer)")

