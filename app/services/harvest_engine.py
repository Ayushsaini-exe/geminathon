"""
Harvest Window Arbitrage Engine.

Simulates 72-hour harvest scenarios using weather forecasts,
mandi prices, and transport costs to recommend optimal harvest timing.
"""

import json
import random
from datetime import datetime, timedelta
from uuid import UUID

import httpx
from google import genai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas.harvest import (
    HarvestRequest,
    HarvestResponse,
    HarvestScenarioItem,
)
from database.models import HarvestScenario


class HarvestEngine:
    """Economic decision support for harvest timing optimization."""

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"
        self.weather_api_key = settings.OPENWEATHER_API_KEY

    async def analyze(
        self, request: HarvestRequest, db: AsyncSession
    ) -> HarvestResponse:
        """
        1. Fetch 3-day weather forecast
        2. Fetch mock mandi prices
        3. Simulate harvest scenarios (today, +2d, +3d)
        4. Calculate net profit per scenario
        5. AI recommendation
        """
        logger.info(
            f"Harvest analysis for farmer {request.farmer_id}, crop: {request.crop}"
        )

        # 1. Weather forecast
        weather = await self._fetch_weather(request.location)

        # 2. Mock mandi prices
        prices = self._mock_agmarknet_prices(request.crop)

        # 3. Simulate scenarios
        scenarios = self._simulate_scenarios(
            request.crop,
            request.current_maturity_pct,
            weather,
            prices,
        )

        # 4. AI recommendation
        recommendation, best = await self._generate_recommendation(
            request.crop, scenarios
        )

        # 5. Store in DB
        scenario_record = HarvestScenario(
            farmer_id=UUID(request.farmer_id),
            crop=request.crop,
            scenarios=[s.model_dump() for s in scenarios],
            recommendation=recommendation,
        )
        db.add(scenario_record)
        await db.flush()

        return HarvestResponse(
            crop=request.crop,
            scenarios=scenarios,
            recommendation=recommendation,
            recommended_scenario=best,
        )

    async def _fetch_weather(self, location: str) -> list[dict]:
        """Fetch 3-day weather forecast from OpenWeatherMap."""
        try:
            if not self.weather_api_key:
                return self._mock_weather()

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.openweathermap.org/data/2.5/forecast",
                    params={
                        "q": location,
                        "appid": self.weather_api_key,
                        "units": "metric",
                        "cnt": 8,  # ~3 days of 3-hour intervals
                    },
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()

                forecasts = []
                for item in data.get("list", [])[:3]:
                    forecasts.append({
                        "date": item["dt_txt"],
                        "temp": item["main"]["temp"],
                        "humidity": item["main"]["humidity"],
                        "weather": item["weather"][0]["main"],
                        "rain_prob": item.get("pop", 0) * 100,
                    })
                return forecasts
        except Exception as e:
            logger.warning(f"Weather API failed, using mock: {e}")
            return self._mock_weather()

    def _mock_weather(self) -> list[dict]:
        """Mock 3-day weather forecast."""
        base = datetime.utcnow()
        return [
            {
                "date": (base + timedelta(days=i)).strftime("%Y-%m-%d"),
                "temp": round(random.uniform(25, 38), 1),
                "humidity": random.randint(40, 85),
                "weather": random.choice(["Clear", "Clouds", "Rain"]),
                "rain_prob": round(random.uniform(0, 70), 1),
            }
            for i in range(3)
        ]

    def _mock_agmarknet_prices(self, crop: str) -> dict:
        """
        Mock Agmarknet mandi prices.
        In production, scrape agmarknet.gov.in or use their API.
        """
        base_prices = {
            "rice": 2200,
            "wheat": 2275,
            "maize": 1962,
            "cotton": 6620,
            "soybean": 4600,
            "sugarcane": 315,
            "tomato": 1500,
            "potato": 800,
            "onion": 1200,
        }
        base = base_prices.get(crop.lower(), 2000)
        return {
            "current_price": base,
            "price_trend": random.choice(["rising", "stable", "falling"]),
            "nearby_mandis": [
                {"name": "Mandi A", "price": base + random.randint(-200, 200), "distance_km": 15},
                {"name": "Mandi B", "price": base + random.randint(-200, 200), "distance_km": 35},
                {"name": "Mandi C", "price": base + random.randint(-200, 200), "distance_km": 60},
            ],
        }

    def _simulate_scenarios(
        self,
        crop: str,
        maturity_pct: float,
        weather: list[dict],
        prices: dict,
    ) -> list[HarvestScenarioItem]:
        """Generate 3 harvest timing scenarios with economic analysis."""
        scenarios = []
        base_yield = round(random.uniform(15, 30), 1)  # quintals
        base_price = prices["current_price"]

        for i, (label, day_offset) in enumerate([
            ("Harvest Today", 0),
            ("Harvest +2 Days", 2),
            ("Harvest +3 Days", 3),
        ]):
            weather_day = weather[min(i, len(weather) - 1)]
            rain_risk = weather_day["rain_prob"]

            # Calculate quality/yield adjustments
            if day_offset == 0:
                quality_loss = 0
                yield_adj = base_yield * (maturity_pct / 100)
            else:
                maturity_gain = min(100, maturity_pct + day_offset * 3)
                quality_loss = rain_risk * 0.05 if rain_risk > 50 else 0
                yield_adj = base_yield * (maturity_gain / 100) * (1 - quality_loss / 100)

            # Price adjustment based on trend
            price_adj = base_price + (day_offset * random.randint(-50, 100))

            # Transport cost (nearest mandi)
            nearest = min(prices["nearby_mandis"], key=lambda m: m["distance_km"])
            transport = nearest["distance_km"] * 15  # ₹15/km

            net_profit = round(yield_adj * price_adj - transport, 2)

            weather_risk = "low" if rain_risk < 30 else ("medium" if rain_risk < 60 else "high")

            harvest_date = (datetime.utcnow() + timedelta(days=day_offset)).strftime("%Y-%m-%d")

            scenarios.append(
                HarvestScenarioItem(
                    label=label,
                    harvest_day=harvest_date,
                    weather_risk=weather_risk,
                    mandi_price_per_quintal=round(price_adj, 2),
                    transport_cost=round(transport, 2),
                    estimated_yield_quintal=round(yield_adj, 2),
                    net_profit=net_profit,
                    quality_loss_pct=round(quality_loss, 2),
                )
            )

        return scenarios

    async def _generate_recommendation(
        self, crop: str, scenarios: list[HarvestScenarioItem]
    ) -> tuple[str, str]:
        """Use Gemini to generate a natural-language recommendation."""
        try:
            table = json.dumps([s.model_dump() for s in scenarios], indent=2)
            prompt = f"""You are an agricultural economist helping an Indian farmer decide when to harvest {crop}.

Here are the simulated scenarios:
{table}

Analyze the scenarios considering:
1. Net profit
2. Weather risk
3. Quality loss
4. Price trends

Provide a clear, concise recommendation (2-3 sentences) on which scenario is best and why.
Also state which scenario label you recommend (e.g., "Harvest Today", "Harvest +2 Days", or "Harvest +3 Days")."""

            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt
            )

            text = response.text
            # Determine best scenario
            best = max(scenarios, key=lambda s: s.net_profit).label
            return text, best

        except Exception as e:
            logger.error(f"Harvest recommendation failed: {e}")
            best = max(scenarios, key=lambda s: s.net_profit)
            return f"Based on profit analysis, {best.label} is recommended.", best.label
