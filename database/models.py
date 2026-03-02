"""
SQLAlchemy ORM models for the AgroFix platform.

Covers: Farmers, Soil Profiles, Chat History, Crop Events,
Disease Detection, Pesticide Records, ESG Scores, Harvest Scenarios,
Digital Twin Zones, and Sustainability Reports.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    Integer,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Farmer(Base):
    """Farmer profile — the central entity."""
    __tablename__ = "farmers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    location = Column(String(512), nullable=True)
    language = Column(String(50), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    soil_profiles = relationship("SoilProfile", back_populates="farmer", lazy="selectin")
    chat_history = relationship("ChatHistory", back_populates="farmer", lazy="selectin")
    crop_events = relationship("CropEvent", back_populates="farmer", lazy="selectin")
    disease_detections = relationship("DiseaseDetection", back_populates="farmer", lazy="selectin")
    pesticide_records = relationship("PesticideRecord", back_populates="farmer", lazy="selectin")
    esg_scores = relationship("ESGScore", back_populates="farmer", lazy="selectin")
    harvest_scenarios = relationship("HarvestScenario", back_populates="farmer", lazy="selectin")
    digital_twin_zones = relationship("DigitalTwinZone", back_populates="farmer", lazy="selectin")
    sustainability_reports = relationship("SustainabilityReport", back_populates="farmer", lazy="selectin")


class SoilProfile(Base):
    """Soil Health Card (SHC) data for a farmer."""
    __tablename__ = "soil_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    shc_id = Column(String(100), nullable=False)
    nitrogen = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    organic_carbon = Column(Float, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="soil_profiles")


class ChatHistory(Base):
    """Context memory — stores conversation history per farmer."""
    __tablename__ = "chat_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant | system
    message = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="chat_history")


class CropEvent(Base):
    """Tracks crop lifecycle events (planting, fertilizing, harvesting, etc.)."""
    __tablename__ = "crop_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="crop_events")


class DiseaseDetection(Base):
    """Vision model disease detection results."""
    __tablename__ = "disease_detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    image_url = Column(String(1024), nullable=True)
    disease = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    treatment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="disease_detections")


class PesticideRecord(Base):
    """Pesticide batch verification records."""
    __tablename__ = "pesticide_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    batch_id = Column(String(255), nullable=False)
    product_name = Column(String(255), nullable=True)
    manufacturer = Column(String(255), nullable=True)
    verified = Column(Boolean, default=False)
    raw_ocr_text = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="pesticide_records")


class ESGScore(Base):
    """Environmental, Social, and Governance sustainability score."""
    __tablename__ = "esg_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    score = Column(Float, nullable=False)
    environmental = Column(Float, default=0.0)
    social = Column(Float, default=0.0)
    governance = Column(Float, default=0.0)
    breakdown = Column(JSON, nullable=True)
    action = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="esg_scores")


class HarvestScenario(Base):
    """Harvest window simulation results and recommendation."""
    __tablename__ = "harvest_scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    crop = Column(String(100), nullable=True)
    scenarios = Column(JSON, nullable=False)  # list of scenario dicts
    recommendation = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="harvest_scenarios")


class DigitalTwinZone(Base):
    """Geo-spatial risk zones for the digital twin farm map."""
    __tablename__ = "digital_twin_zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # green | yellow | red
    zone_type = Column(String(100), nullable=True)  # disease | soil | weather | chemical
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="digital_twin_zones")


class SustainabilityReport(Base):
    """Generated sustainability PDF reports with QR verification."""
    __tablename__ = "sustainability_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    pdf_url = Column(String(1024), nullable=True)
    qr_data = Column(Text, nullable=True)
    report_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="sustainability_reports")
