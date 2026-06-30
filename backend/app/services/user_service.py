import logging
from typing import Sequence, Optional
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate


from app.core.exceptions import UserAlreadyExistsException, InvalidCredentialsException

logger = logging.getLogger(__name__)





class UserService:
    """
    Service class encapsulating all business logic related to Users.
    Coordinates database interactions via the UserRepository.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """
        Initialize the service with a UserRepository.
        """
        self.user_repository = user_repository

    def create_user(self, user_in: UserCreate) -> User:
        """
        Create a new user in the system after executing business validations.
        
        Raises:
            UserAlreadyExistsException: If the email is already registered.
        """
        # 1. Business Validation: Check email uniqueness
        existing_user = self.user_repository.get_by_email(user_in.email)
        if existing_user:
            logger.warning(f"Registration failed: Email '{user_in.email}' is already registered.")
            raise UserAlreadyExistsException(
                "Email already registered."
            )

        # 2. Map schema to SQLAlchemy model (with password hashing)
        db_user = User(
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            is_active=True,
            is_superuser=False
        )

        # 3. Persist via repository
        created_user = self.user_repository.create(db_user)
        logger.info(f"User registration successful for email: '{user_in.email}' (ID: {created_user.id})")
        return created_user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their unique ID.
        """
        return self.user_repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        """
        return self.user_repository.get_by_email(email)

    def get_all_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """
        Retrieve a paginated list of users.
        """
        return self.user_repository.get_all(skip=skip, limit=limit)

    def authenticate_user(self, email: str, plain_password: str) -> User:
        """
        Authenticate a user by verifying their email, password, and active status.
        
        Raises:
            InvalidCredentialsException: If email, password, or active check fails.
        """
        # 1. Verify user exists
        user = self.user_repository.get_by_email(email)
        if not user:
            logger.warning(f"Login failed: User with email '{email}' not found.")
            raise InvalidCredentialsException("Incorrect email or password.")

        # 2. Verify password is correct
        if not verify_password(plain_password, user.hashed_password):
            logger.warning(f"Login failed: Incorrect password for user '{email}'.")
            raise InvalidCredentialsException("Incorrect email or password.")

        # 3. Verify user is active
        if not user.is_active:
            logger.warning(f"Login failed: User account '{email}' is inactive.")
            raise InvalidCredentialsException("User account is inactive.")

        logger.info(f"User login successful for email: '{email}' (ID: {user.id})")
        return user


