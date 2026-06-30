import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.models.user import User
from app.core.security import verify_access_token

logger = logging.getLogger(__name__)

# Define the OAuth2 security scheme pointing to the user login endpoint.
# Swagger UI uses this configuration to provide interactive authorization features.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")



def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """
    Dependency provider for UserRepository.
    """
    return UserRepository(db)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    """
    Dependency provider for UserService.
    """
    return UserService(user_repository)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Dependency injection helper to retrieve the authenticated current user.
    
    Checks the Bearer token in the request header, decodes/verifies the JWT,
    resolves the user ID, and returns the User record from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Decode & verify JWT, extracting the user ID subject ('sub')
        user_id_str = verify_access_token(token)
    except JWTError:
        raise credentials_exception

    # Convert subject string back to integer user ID
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    # 2. Fetch the user using the injected Service
    user = user_service.get_user_by_id(user_id)


    # 3. Raise 401 if user not found or is inactive
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_roles(*allowed_roles: str):
    """
    Dependency factory to enforce role-based access control (RBAC).
    Accepts one or multiple role names.
    
    If the user has the 'is_superuser' flag set to True, they bypass the check.
    """
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        # 1. Superuser bypass for administrative flexibility
        if current_user.is_superuser:
            return current_user

        # 2. Check if user is associated with an allowed role
        if not current_user.role or current_user.role.name not in allowed_roles:
            user_role = current_user.role.name if current_user.role else "None"
            logger.warning(
                f"Authorization failed: User {current_user.email} (ID: {current_user.id}) "
                f"with role '{user_role}' tried to access a resource requiring roles {allowed_roles}."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to access this resource."
            )
        return current_user


    return role_dependency



