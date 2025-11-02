from datetime import datetime, timedelta
from typing import Optional
import jwt
import hashlib

# Hardcoded credentials
VALID_USERNAME = "rrt@apgov"
VALID_PASSWORD = "P@ssw0rd@001"

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = "arunachal-schemes-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def verify_credentials(username: str, password: str) -> bool:
    """
    Verify if username and password match the hardcoded credentials
    
    Args:
        username: Username to verify
        password: Password to verify
        
    Returns:
        True if credentials are valid, False otherwise
    """
    return username == VALID_USERNAME and password == VALID_PASSWORD

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token (usually username)
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

