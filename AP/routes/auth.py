from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from services.auth_service import verify_credentials, create_access_token, verify_token
from models.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with username and password
    
    Hardcoded credentials:
    - Username: rrt@apgov
    - Password: P@ssw0rd@001
    
    Returns a JWT access token that can be used for authenticated requests.
    
    Example request:
    {
        "username": "rrt@apgov",
        "password": "P@ssw0rd@001"
    }
    
    Example response:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "username": "rrt@apgov",
        "message": "Login successful"
    }
    """
    if not verify_credentials(request.username, request.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": request.username})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        username=request.username,
        message="Login successful"
    )

@router.get("/verify")
async def verify_token_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify if the current token is valid
    
    Returns user information if token is valid.
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return {
        "valid": True,
        "username": payload.get("sub"),
        "message": "Token is valid"
    }

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency function to get current authenticated user
    
    Use this as a dependency in protected routes:
    async def my_endpoint(current_user: str = Depends(get_current_user)):
        ...
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return username

