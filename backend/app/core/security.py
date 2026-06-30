from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, JWTError
from pwdlib import PasswordHash

from app.core.config import settings

# Initialize password hashing using pwdlib (configured with bcrypt)
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using the recommended password hashing scheme (bcrypt).
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against its hashed value.
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(subject: Union[str, Any], expires_delta: Union[timedelta, None] = None) -> str:
    """
    Generate a JSON Web Token (JWT) access token.
    
    Args:
        subject: The identifier to store in the 'sub' claim (typically the user's ID).
        expires_delta: Optional custom duration for the token's validity.
        
    Returns:
        str: The encoded JWT token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "sub": str(subject)
    }

    # Encode the payload using the secret key and algorithm from our global Settings
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> str:
    """
    Decode and verify a JSON Web Token (JWT).
    
    Args:
        token: The encoded JWT token string.
        
    Returns:
        str: The user subject (user ID) stored in the token's 'sub' claim.
        
    Raises:
        JWTError: If the token is invalid, expired, or has a missing 'sub' claim.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    token_data = payload.get("sub")
    if token_data is None:
        raise JWTError("Token payload is missing the subject ('sub') claim.")
    return token_data
