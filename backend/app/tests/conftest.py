import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db, Base
from app.db.seed import seed_roles

# Create in-memory SQLite database for fast isolated unit tests
# StaticPool is used to share the same in-memory connection across threads
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Session-scoped fixture to build schemas and seed default data.
    Runs once for the entire test session.
    """
    # 1. Create all tables in the test SQLite database
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed default roles so RBAC tests have roles to verify
    db = TestingSessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()
        
    yield
    # 3. Clean up database schemas on session end
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Session:
    """
    Function-scoped fixture to provide a transactional database session.
    Rolls back any modifications made during a test to keep tests isolated.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> TestClient:
    """
    Function-scoped fixture providing a TestClient with overridden get_db dependency.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Override get_db in the FastAPI dependency container
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    # Clear overrides after the test completes
    app.dependency_overrides.clear()
