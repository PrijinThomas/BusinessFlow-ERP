from fastapi import FastAPI
from app.api.api import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging

# Initialize logging configuration
setup_logging()

app = FastAPI(

    title=settings.APP_NAME,
    description="Backend API for BusinessFlow ERP",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Register centralized exception handlers
register_exception_handlers(app)

app.include_router(api_router)



