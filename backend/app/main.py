from fastapi import FastAPI
from app.api.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for BusinessFlow ERP",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.include_router(api_router)


