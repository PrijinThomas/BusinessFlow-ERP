from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.role import Role


class User(Base):
    """
    SQLAlchemy model representing a User in the ERP system.
    """
    __tablename__ = "users"

    # 1. Primary Key
    # Mapped[int] defines the Python type, and mapped_column(primary_key=True) tells SQLAlchemy 
    # to make this an autoincrementing integer primary key in the database.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 2. Email Address
    # String(255) defines the column type and length.
    # unique=True ensures no two users can have the same email.
    # index=True indexes this column for fast lookups during authentication/queries.
    # nullable=False ensures the field is mandatory.
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # 3. Hashed Password
    # Stores the secure, hashed representation of the user's password.
    # Never store plain-text passwords.
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # 4. Active Status Flag
    # Boolean flag to enable or disable the user's account.
    # default=True sets the default value for new Python instances.
    # server_default="true" (optional, but we use default=True here) sets default in SQLAlchemy.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 5. Superuser Privilege Flag
    # Boolean flag determining if the user has administrative/superuser privileges.
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 6. Created Timestamp
    # DateTime(timezone=True) ensures timestamps are timezone-aware (recommended for production).
    # server_default=func.now() instructs the database to automatically populate this field 
    # with the current timestamp when a row is created (e.g., DEFAULT CURRENT_TIMESTAMP).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # 7. Updated Timestamp
    # Similar to created_at, but onupdate=func.now() tells SQLAlchemy to automatically 
    # update this field to the current timestamp whenever the row is modified.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # 8. Foreign Key to Role Table
    # Stores the ID of the role assigned to the user.
    # Set to nullable=True and ondelete="SET NULL" so that if a role is deleted,
    # the user's role assignment is cleared rather than deleting the user.
    role_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True
    )

    # 9. Relationship to Role Model
    # Many-to-One Relationship: Multiple Users can belong to a single Role.
    # back_populates="users" links this to the 'users' attribute on the Role model.
    role: Mapped[Optional["Role"]] = relationship(
        "Role",
        back_populates="users"
    )

