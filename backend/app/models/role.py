from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Role(Base):
    """
    SQLAlchemy model representing a User Role in the ERP system.
    """
    __tablename__ = "roles"

    # 1. Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 2. Role Name
    # E.g. "admin", "manager", "employee"
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # 3. Description
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    # 4. Created Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # 5. Updated Timestamp
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # 6. Relationship to User
    # One-to-Many Relationship: A single Role can be associated with multiple Users.
    # back_populates="role" links this relationship to the 'role' attribute on the User model.
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="role"
    )
