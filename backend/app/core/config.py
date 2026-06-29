import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application Settings class.
    Decoupled configurations loaded from environment variables and/or a local .env file.
    """
    # model_config configures how Pydantic Settings should behave.
    model_config = SettingsConfigDict(
        # Resolve the absolute path to the backend/.env file relative to this file
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            ".env"
        ),
        # Specify the encoding of the .env file
        env_file_encoding="utf-8",
        # Force exact case-sensitive matching for environment variable names
        case_sensitive=True,
    )

    # Application name configurations
    APP_NAME: str = "BusinessFlow ERP"

    # Application version configurations
    APP_VERSION: str = "1.0.0"

    # Debug mode flag (defaults to False for production safety)
    DEBUG: bool = False

    # Database connection string (defaults to a standard local PostgreSQL database)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/erp_db"

# A single global instance of the Settings class to be used across the application.
settings = Settings()
