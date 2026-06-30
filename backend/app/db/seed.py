import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role

# Configure logger for tracking execution progress
logger = logging.getLogger(__name__)

# List of default roles to be seeded in the database
DEFAULT_ROLES = [
    {
        "name": "Admin",
        "description": "Administrator with full system privileges."
    },
    {
        "name": "HR",
        "description": "Human Resources staff responsible for managing employees and payroll."
    },
    {
        "name": "Sales",
        "description": "Sales department users managing clients, quotes, and orders."
    },
    {
        "name": "Inventory",
        "description": "Inventory and warehouse users tracking stock levels and suppliers."
    }
]


def seed_roles(db: Session) -> None:
    """
    Seed default roles into the database.
    Checks if a role exists by name before inserting to guarantee idempotency.
    """
    logger.info("Initializing role seeding...")

    for role_data in DEFAULT_ROLES:
        # 1. Query to see if the role name already exists in the database
        stmt = select(Role).where(Role.name == role_data["name"])
        existing_role = db.execute(stmt).scalars().first()

        if not existing_role:
            # 2. If it doesn't exist, instantiate and insert the new Role record
            new_role = Role(
                name=role_data["name"],
                description=role_data["description"]
            )
            db.add(new_role)
            logger.info(f"Role '{role_data['name']}' added to database queue.")
        else:
            logger.info(f"Role '{role_data['name']}' already exists. Skipping.")

    # 3. Commit the transactions to write all new entries to the database
    db.commit()
    logger.info("Role seeding process finished successfully.")


if __name__ == "__main__":
    # If executed directly as a script, initialize a database session and run the seed function.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    from app.db.database import SessionLocal
    
    db_session = SessionLocal()
    try:
        seed_roles(db_session)
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
    finally:
        db_session.close()
