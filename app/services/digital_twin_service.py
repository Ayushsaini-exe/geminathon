"""
Digital Twin Visualization Engine.

Maintains a geo-spatial risk map of the farm using inputs from
disease events, soil data, weather stress, and chemical usage.
Calculates per-zone risk levels (green/yellow/red).
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.schemas.digital_twin import (
    DigitalTwinUpdateRequest,
    DigitalTwinResponse,
    DigitalTwinZoneItem,
)
from database.models import DigitalTwinZone


class DigitalTwinService:
    """Farm digital twin — geo-spatial risk visualization."""

    async def update_zone(
        self, request: DigitalTwinUpdateRequest, db: AsyncSession
    ) -> DigitalTwinResponse:
        """
        Add or update a risk zone on the farm map.
        """
        logger.info(
            f"Digital twin update: {request.zone_type} at "
            f"({request.lat}, {request.lng}) → {request.risk_level}"
        )

        zone = DigitalTwinZone(
            farmer_id=UUID(request.farmer_id),
            lat=request.lat,
            lng=request.lng,
            risk_level=request.risk_level,
            zone_type=request.zone_type,
            details=request.details,
        )
        db.add(zone)
        await db.flush()

        return await self.get_farm_map(request.farmer_id, db)

    async def get_farm_map(
        self, farmer_id: str, db: AsyncSession
    ) -> DigitalTwinResponse:
        """
        Retrieve the complete farm digital twin with all risk zones.
        """
        stmt = (
            select(DigitalTwinZone)
            .where(DigitalTwinZone.farmer_id == UUID(farmer_id))
            .order_by(DigitalTwinZone.timestamp.desc())
        )
        result = await db.execute(stmt)
        records = result.scalars().all()

        zones = [
            DigitalTwinZoneItem(
                lat=z.lat,
                lng=z.lng,
                risk_level=z.risk_level,
                zone_type=z.zone_type,
                details=z.details or {},
            )
            for z in records
        ]

        overall = self._calculate_overall_risk(zones)

        return DigitalTwinResponse(
            farmer_id=farmer_id,
            zones=zones,
            overall_risk=overall,
        )

    def _calculate_overall_risk(self, zones: list[DigitalTwinZoneItem]) -> str:
        """Determine overall farm risk from individual zone risks."""
        if not zones:
            return "green"

        risk_weights = {"red": 3, "yellow": 2, "green": 1}
        total = sum(risk_weights.get(z.risk_level, 1) for z in zones)
        avg = total / len(zones)

        if avg >= 2.5:
            return "red"
        if avg >= 1.5:
            return "yellow"
        return "green"

    async def add_disease_event(
        self,
        farmer_id: str,
        lat: float,
        lng: float,
        disease: str,
        confidence: float,
        db: AsyncSession,
    ):
        """Helper: register a disease detection as a digital twin zone."""
        risk = "red" if confidence > 0.8 else ("yellow" if confidence > 0.5 else "green")
        req = DigitalTwinUpdateRequest(
            farmer_id=farmer_id,
            lat=lat,
            lng=lng,
            zone_type="disease",
            risk_level=risk,
            details={"disease": disease, "confidence": confidence},
        )
        return await self.update_zone(req, db)

    async def add_soil_stress(
        self,
        farmer_id: str,
        lat: float,
        lng: float,
        soil_data: dict,
        db: AsyncSession,
    ):
        """Helper: register soil stress as a digital twin zone."""
        ph = soil_data.get("ph", 7.0)
        oc = soil_data.get("organic_carbon", 0.5)

        if ph < 5.5 or ph > 8.5 or oc < 0.3:
            risk = "red"
        elif ph < 6.0 or ph > 8.0 or oc < 0.5:
            risk = "yellow"
        else:
            risk = "green"

        req = DigitalTwinUpdateRequest(
            farmer_id=farmer_id,
            lat=lat,
            lng=lng,
            zone_type="soil",
            risk_level=risk,
            details=soil_data,
        )
        return await self.update_zone(req, db)
