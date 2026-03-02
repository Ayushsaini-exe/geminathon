"""
Pesticide Authenticity Verification Service.

Uses EasyOCR to extract batch IDs from bottle images,
then cross-checks against a mock CIBRC database.
"""

import base64
import io
import re
from uuid import UUID

from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.schemas.pesticide import PesticideVerifyRequest, PesticideVerifyResponse
from database.models import PesticideRecord


# Mock CIBRC (Central Insecticides Board & Registration Committee) database
MOCK_CIBRC_DB: dict[str, dict] = {
    "BATCH-2024-001": {
        "product_name": "Imidacloprid 17.8% SL",
        "manufacturer": "Bayer CropScience",
        "registration_no": "CIR-9(1)-354",
        "status": "registered",
    },
    "BATCH-2024-002": {
        "product_name": "Chlorpyrifos 20% EC",
        "manufacturer": "UPL Limited",
        "registration_no": "CIR-9(1)-128",
        "status": "registered",
    },
    "BATCH-2024-003": {
        "product_name": "Mancozeb 75% WP",
        "manufacturer": "Indofil Industries",
        "registration_no": "CIR-9(1)-097",
        "status": "registered",
    },
    "BATCH-2024-004": {
        "product_name": "Cypermethrin 25% EC",
        "manufacturer": "Dhanuka Agritech",
        "registration_no": "CIR-9(1)-445",
        "status": "registered",
    },
    "BATCH-2024-005": {
        "product_name": "Neem Oil 1500 PPM",
        "manufacturer": "Parry Nutraceuticals",
        "registration_no": "CIR-9(1)-512",
        "status": "registered",
    },
}


class PesticideVerificationService:
    """OCR-based pesticide batch verification against CIBRC registry."""

    def __init__(self):
        self._reader = None

    def _get_ocr_reader(self):
        """Lazy-load EasyOCR reader to avoid startup overhead."""
        if self._reader is None:
            try:
                import easyocr
                self._reader = easyocr.Reader(["en"], gpu=False)
                logger.info("EasyOCR reader initialized")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                raise
        return self._reader

    async def verify(
        self, request: PesticideVerifyRequest, db: AsyncSession
    ) -> PesticideVerifyResponse:
        """
        1. Extract batch ID from image (OCR) or use manually provided ID
        2. Cross-check against mock CIBRC database
        3. Store record and return verification result
        """
        batch_id = request.batch_id
        ocr_text = None

        # Step 1: OCR extraction if image provided
        if request.image_base64 and not batch_id:
            batch_id, ocr_text = self._extract_batch_id(request.image_base64)

        if not batch_id:
            return PesticideVerifyResponse(
                batch_id="UNKNOWN",
                verified=False,
                status="unknown",
                message="Could not extract or determine batch ID.",
                ocr_extracted_text=ocr_text,
            )

        # Step 2: Cross-check with CIBRC database
        cibrc_record = MOCK_CIBRC_DB.get(batch_id.upper())

        if cibrc_record:
            verified = True
            status = "verified"
            message = (
                f"✅ Product VERIFIED: {cibrc_record['product_name']} by "
                f"{cibrc_record['manufacturer']} (Reg: {cibrc_record['registration_no']})"
            )
            product_name = cibrc_record["product_name"]
            manufacturer = cibrc_record["manufacturer"]
        else:
            verified = False
            status = "counterfeit"
            message = (
                f"⚠️ COUNTERFEIT WARNING: Batch ID '{batch_id}' not found in CIBRC registry. "
                f"This product may be fake or unregistered."
            )
            product_name = None
            manufacturer = None

        # Step 3: Store record
        record = PesticideRecord(
            farmer_id=UUID(request.farmer_id),
            batch_id=batch_id,
            product_name=product_name,
            manufacturer=manufacturer,
            verified=verified,
            raw_ocr_text=ocr_text,
        )
        db.add(record)
        await db.flush()

        logger.info(f"Pesticide verification: {batch_id} → {status}")

        return PesticideVerifyResponse(
            batch_id=batch_id,
            product_name=product_name,
            manufacturer=manufacturer,
            verified=verified,
            status=status,
            message=message,
            ocr_extracted_text=ocr_text,
        )

    def _extract_batch_id(self, image_base64: str) -> tuple[str | None, str | None]:
        """Use EasyOCR to extract batch ID from a bottle image."""
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))

            reader = self._get_ocr_reader()
            results = reader.readtext(image)

            full_text = " ".join([r[1] for r in results])
            logger.info(f"OCR extracted text: {full_text[:200]}")

            # Try to find batch ID pattern
            batch_pattern = r"BATCH[-\s]?\d{4}[-\s]?\d{3}"
            match = re.search(batch_pattern, full_text, re.IGNORECASE)

            if match:
                batch_id = re.sub(r"\s+", "-", match.group().upper())
                return batch_id, full_text

            return None, full_text

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return None, None
