from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify that the API is running correctly.
    """
    return {
        "status": "healthy",
        "message": "BusinessFlow ERP API is running"
    }
