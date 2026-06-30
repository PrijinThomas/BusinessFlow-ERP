from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.user_service import UserService

from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.core.security import create_access_token
from app.api.dependencies import get_current_user, require_roles, get_user_service
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user in the system. The email must be unique."
)
def register_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    HTTP Endpoint to handle user registration.
    """
    return user_service.create_user(user_in)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticates a user and returns a JWT access token."
)
def login_user(
    user_in: UserLogin,
    user_service: UserService = Depends(get_user_service)
) -> Token:
    """
    HTTP Endpoint to handle user login.
    """
    # Authenticate user credentials
    user = user_service.authenticate_user(user_in.email, user_in.password)

    # Generate access token with user ID as subject (sub)
    access_token = create_access_token(subject=user.id)

    # Return serialized token response
    return Token(access_token=access_token, token_type="bearer")



@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user details",
    description="Returns the details of the currently authenticated user."
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    HTTP Endpoint to retrieve the authenticated user profile.
    """
    return current_user


@router.get(
    "/",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users (Admin only)",
    description="Returns a list of all registered users. Only accessible by users with the Admin role."
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    current_admin: User = Depends(require_roles("Admin"))
) -> List[UserResponse]:
    """
    HTTP Endpoint to retrieve all users. Protected by Admin role.
    """
    users = user_service.get_all_users(skip=skip, limit=limit)
    return users




