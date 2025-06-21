"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, status

from core.security import authenticate_user, create_access_token
from schemas.auth import LoginRequest, LoginResponse


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Login endpoint."""
    user = authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user["email"],
            "role": user["role"],
            "full_name": user["full_name"],
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        user={
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
        }
    )