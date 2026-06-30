import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)



class UserAlreadyExistsException(ValueError):
    """
    Exception raised when a user email is already registered.
    """
    pass


class InvalidCredentialsException(ValueError):
    """
    Exception raised when authentication fails.
    """
    pass


class ResourceNotFoundException(Exception):
    """
    Exception raised when a requested resource is not found.
    """
    pass


async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unexpected server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error."}
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for custom application exceptions.
    """
    app.add_exception_handler(UserAlreadyExistsException, user_already_exists_handler)
    app.add_exception_handler(InvalidCredentialsException, invalid_credentials_handler)
    app.add_exception_handler(ResourceNotFoundException, resource_not_found_handler)
    app.add_exception_handler(Exception, unexpected_exception_handler)

