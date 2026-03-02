"""
Soil Health Card (SHC) Integration Service.

Fetches soil parameters from government API (mocked),
stores structured soil profiles, and generates fertilizer advice.
"""

import json
import random

from google import genai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas.shc import SHCRequest, SHCResponse, SoilParameters
from database.models import SoilProfile


class SHCService:
    """Soil Health Card integration — mock API + AI fertilizer advice."""

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"

    async def fetch_soil_profile(
        self, request: SHCRequest, db: AsyncSession
    ) -> SHCResponse:
        """
        1. Call mock SHC API to get soil parameters
        2. Store in database
        3. Generate fertilizer advice via Gemini
        """
        logger.info(f"Fetching SHC data for ID: {request.shc_id}")

        # 1. Mock SHC API call
        soil_params = self._mock_shc_api(request.shc_id)

        # 2. Store soil profile
        profile = SoilProfile(
            farmer_id=request.farmer_id,
            shc_id=request.shc_id,
            nitrogen=soil_params.nitrogen,
            phosphorus=soil_params.phosphorus,
            potassium=soil_params.potassium,
            ph=soil_params.ph,
            organic_carbon=soil_params.organic_carbon,
        )
        db.add(profile)
        await db.flush()

        # 3. Generate fertilizer advice
        advice = await self._generate_fertilizer_advice(soil_params)

        return SHCResponse(
            shc_id=request.shc_id,
            farmer_id=request.farmer_id,
            soil_parameters=soil_params,
            fertilizer_advice=advice,
        )

    def _mock_shc_api(self, shc_id: str) -> SoilParameters:
        """
        Simulate Government SHC API response.
        In production, replace with actual API call to soilhealth.dac.gov.in.
        """
        # Deterministic randomness seeded by SHC ID for reproducibility
        seed = sum(ord(c) for c in shc_id)
        rng = random.Random(seed)

        return SoilParameters(
            N=round(rng.uniform(100, 350), 1),
            P=round(rng.uniform(10, 80), 1),
            K=round(rng.uniform(80, 400), 1),
            ph=round(rng.uniform(5.5, 8.5), 2),
            organic_carbon=round(rng.uniform(0.2, 1.5), 2),
        )

    async def _generate_fertilizer_advice(self, params: SoilParameters) -> str:
        """Use Gemini to generate personalized fertilizer recommendations."""
        try:
            prompt = f"""You are an agricultural soil scientist. Based on the following soil test results,
provide specific fertilizer recommendations for Indian farming conditions.

Soil Parameters:
- Nitrogen (N): {params.nitrogen} kg/ha
- Phosphorus (P): {params.phosphorus} kg/ha
- Potassium (K): {params.potassium} kg/ha
- pH: {params.ph}
- Organic Carbon: {params.organic_carbon}%

Provide:
1. Soil health assessment (good/moderate/poor)
2. Specific fertilizer recommendations with quantities
3. Organic amendments suggested
4. Crops best suited for this soil

Keep response concise and practical for a farmer."""

            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini fertilizer advice failed: {e}")
            return "Unable to generate advice. Please consult your local agricultural officer."
