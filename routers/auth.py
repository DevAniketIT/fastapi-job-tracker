"""
Authentication router for user management.

This module provides basic authentication endpoints including user registration
and login functionality. Can be extended with JWT tokens for full auth system.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime

from database import get_db, UserOperations
from models import UserCreate, UserResponse, Token

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_success_response(message: str, data=None) -> dict:
    """Create standardized success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow()
    }


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new user")
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    **Required fields:**
    - email: Valid email address
    - password: Password (minimum 6 characters)
    
    **Optional fields:**
    - full_name: User's full name
    """
    try:
        # Check if user already exists
        existing_user = UserOperations.get_user_by_email(db=db, email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = hash_password(user.password)
        db_user = UserOperations.create_user(
            db=db,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name
        )
        
        # Convert to response format
        user_response = {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at.isoformat() if db_user.created_at else None
        }
        
        return create_success_response(
            message="User registered successfully",
            data=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error registering user: {str(e)}"
        )


@router.post("/login", summary="Login user")
async def login_user(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Login user with email and password.
    
    Note: This is a simplified login endpoint. In a production environment,
    you would implement proper JWT token generation and validation.
    """
    try:
        # Get user by email
        db_user = UserOperations.get_user_by_email(db=db, email=email)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        # In a real implementation, you would create and return a JWT token here
        user_response = {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "is_active": db_user.is_active
        }
        
        return create_success_response(
            message="Login successful",
            data={
                "user": user_response,
                "token": "placeholder_token_would_be_jwt_in_production"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )


@router.get("/profile", summary="Get user profile")
async def get_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user profile information.
    
    In a production environment, you would extract user_id from JWT token
    instead of passing it as a parameter.
    """
    try:
        db_user = UserOperations.get_user_by_id(db=db, user_id=user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_response = {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at.isoformat() if db_user.created_at else None,
            "updated_at": db_user.updated_at.isoformat() if db_user.updated_at else None
        }
        
        return create_success_response(
            message="Profile retrieved successfully",
            data=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile: {str(e)}"
        )
