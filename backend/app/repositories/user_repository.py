from typing import Sequence, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    Repository class for handling database operations for the User model.
    Encapsulates all direct database queries using SQLAlchemy 2.0.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the repository with a database session.
        """
        self.db = db

    def create(self, user: User) -> User:
        """
        Persist a new User model in the database.
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their unique primary key ID.
        """
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their unique email address.
        """
        statement = select(User).where(User.email == email)
        result = self.db.execute(statement)
        return result.scalars().first()

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """
        Retrieve a paginated list of users.
        """
        statement = select(User).offset(skip).limit(limit)
        result = self.db.execute(statement)
        return result.scalars().all()

    def update(self, db_user: User, update_data: dict) -> User:
        """
        Update an existing user with new attributes.
        """
        for field, value in update_data.items():
            setattr(db_user, field, value)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, db_user: User) -> User:
        """
        Delete a user from the database.
        """
        self.db.delete(db_user)
        self.db.commit()
        return db_user
