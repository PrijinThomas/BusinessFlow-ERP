from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# 1. Retrieve the database URL from settings.
# We fetch the connection string defined in our centralized configuration.
DATABASE_URL = settings.DATABASE_URL

# 2. Ensure we use the psycopg (v3) driver.
# If the connection URL starts with "postgresql://", we replace it with "postgresql+psycopg://".
# This guarantees SQLAlchemy uses the modern psycopg 3 driver we installed instead of psycopg2.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# 3. Create the SQLAlchemy Engine.
# The engine is the entry point to the database, managing a pool of connections.
# Production-ready configurations:
# - pool_pre_ping=True: Tests connection liveness before checking it out of the pool.
#   This automatically recovers from database restarts or dropped connections.
# - pool_size=20: Keeps up to 20 persistent connections in the pool.
# - max_overflow=10: Allows up to 10 additional temporary connections under high load.
# - pool_recycle=3600: Closes and recreates connections older than 1 hour to prevent stale connections.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
)

# 4. Create SessionLocal.
# A factory for creating database sessions (unit of work).
# - autocommit=False: Disable automatic commits; transactions must be committed explicitly.
# - autoflush=False: Disable automatic flushing; changes are only sent to the DB when explicitly requested.
# - bind=engine: Link the session to our database engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Define the Declarative Base class.
# In SQLAlchemy 2.0, declarative models inherit from a class that derives from DeclarativeBase.
# This provides type-safety and modern typing support (MAPPED/mapped_column).
class Base(DeclarativeBase):
    """
    Base class for all database models.
    All future database models will inherit from this class.
    """
    pass

# 6. Database Session Dependency.
# A helper function to be used as a FastAPI dependency (via Depends).
# It creates a new database session for a request and ensures it is closed when the request is done.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
