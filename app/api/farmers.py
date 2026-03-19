"""
Farmer management API routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Farmer
from database.session import get_db

router = APIRouter(prefix="/api/farmers", tags=["Farmers"])


class FarmerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=10)
    location: str | None = None
    language: str = "en"


class FarmerResponse(BaseModel):
    id: str
    name: str
    phone: str
    location: str | None
    language: str


@router.post("/", response_model=FarmerResponse)
async def create_farmer(data: FarmerCreate, db: AsyncSession = Depends(get_db)):
    """Register a new farmer."""
    farmer = Farmer(
        name=data.name,
        phone=data.phone,
        location=data.location,
        language=data.language,
    )
    db.add(farmer)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"A farmer with phone '{data.phone}' already exists.",
        )
    await db.refresh(farmer)
    return FarmerResponse(
        id=str(farmer.id),
        name=farmer.name,
        phone=farmer.phone,
        location=farmer.location,
        language=farmer.language,
    )


@router.get("/{farmer_id}", response_model=FarmerResponse)
async def get_farmer(farmer_id: str, db: AsyncSession = Depends(get_db)):
    """Get a farmer by ID."""
    farmer = await db.get(Farmer, farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return FarmerResponse(
        id=str(farmer.id),
        name=farmer.name,
        phone=farmer.phone,
        location=farmer.location,
        language=farmer.language,
    )


@router.get("/", response_model=list[FarmerResponse])
async def list_farmers(db: AsyncSession = Depends(get_db)):
    """List all farmers."""
    result = await db.execute(select(Farmer).limit(100))
    farmers = result.scalars().all()
    return [
        FarmerResponse(
            id=str(f.id), name=f.name, phone=f.phone,
            location=f.location, language=f.language,
        )
        for f in farmers
    ]
