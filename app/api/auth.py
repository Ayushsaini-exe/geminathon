"""
Authentication API routes — register, login, and profile.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password, verify_password, create_access_token, get_current_user
from database.models import User, Farmer
from database.session import get_db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6)
    role: str = Field("farmer", description="farmer or manager")
    name: str = Field("", description="Full name (required for farmers)")
    phone: str = Field("", description="Phone number (required for farmers)")
    location: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserProfile(BaseModel):
    id: str
    email: str
    role: str
    farmer_id: str | None = None
    name: str | None = None
    phone: str | None = None
    location: str | None = None


@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user (and create Farmer profile if role=farmer)."""
    # Check if email already exists
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    farmer_id = None

    # If farmer, create a Farmer profile first
    if data.role == "farmer":
        if not data.name or not data.phone:
            raise HTTPException(status_code=400, detail="Name and phone are required for farmer registration")

        farmer = Farmer(
            name=data.name,
            phone=data.phone,
            location=data.location,
        )
        db.add(farmer)
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=409, detail=f"Phone '{data.phone}' already registered")
        farmer_id = farmer.id

    # Create user
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        farmer_id=farmer_id,
    )
    db.add(user)
    await db.flush()

    token = create_access_token({"sub": user.id, "role": user.role})

    return AuthResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "farmer_id": farmer_id,
            "name": data.name if data.role == "farmer" else None,
        },
    )


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and return a JWT token."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.id, "role": user.role})

    farmer_name = None
    farmer_phone = None
    farmer_location = None
    if user.farmer:
        farmer_name = user.farmer.name
        farmer_phone = user.farmer.phone
        farmer_location = user.farmer.location

    return AuthResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "farmer_id": user.farmer_id,
            "name": farmer_name,
            "phone": farmer_phone,
            "location": farmer_location,
        },
    )


@router.get("/me", response_model=UserProfile)
async def get_profile(user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return UserProfile(
        id=user.id,
        email=user.email,
        role=user.role,
        farmer_id=user.farmer_id,
        name=user.farmer.name if user.farmer else None,
        phone=user.farmer.phone if user.farmer else None,
        location=user.farmer.location if user.farmer else None,
    )
