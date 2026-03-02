"""
Sustainability Report Generator.

Compiles a farmer's full sustainability history into a
downloadable PDF with QR verification code.
"""

import io
import json
import os
import uuid as uuid_mod
from datetime import datetime

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas.report import ReportRequest, ReportResponse
from database.models import (
    Farmer,
    SoilProfile,
    CropEvent,
    PesticideRecord,
    ESGScore,
    DiseaseDetection,
    SustainabilityReport,
)


class ReportService:
    """Generates comprehensive sustainability reports as PDFs with QR codes."""

    def __init__(self):
        self.output_dir = os.path.join(".", "reports")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate(
        self, request: ReportRequest, db: AsyncSession
    ) -> ReportResponse:
        """
        1. Fetch all relevant data for the farmer
        2. Compile into structured report
        3. Generate PDF
        4. Generate QR verification code
        5. Store report record
        """
        logger.info(f"Generating sustainability report for farmer {request.farmer_id}")

        # 1. Gather data
        report_data = await self._gather_data(request.farmer_id, db)

        # 2. Generate QR code
        report_id = str(uuid_mod.uuid4())
        qr_data = json.dumps({
            "report_id": report_id,
            "farmer_id": request.farmer_id,
            "generated_at": datetime.utcnow().isoformat(),
            "verification_url": f"https://agrofix.verify/{report_id}",
        })
        qr_image_path = self._generate_qr(qr_data, report_id)

        # 3. Generate PDF
        pdf_path = self._generate_pdf(
            report_data, report_id, qr_image_path, request.include_sections
        )

        # 4. Store record
        report_record = SustainabilityReport(
            farmer_id=request.farmer_id,
            pdf_url=pdf_path,
            qr_data=qr_data,
            report_data=report_data,
        )
        db.add(report_record)
        await db.flush()

        return ReportResponse(
            farmer_id=request.farmer_id,
            pdf_url=pdf_path,
            qr_code_data=qr_data,
            report_summary={
                "report_id": report_id,
                "sections": request.include_sections,
                "total_events": len(report_data.get("crop_events", [])),
                "esg_score": report_data.get("latest_esg", {}).get("score", "N/A"),
            },
        )

    async def _gather_data(self, farmer_id: str, db: AsyncSession) -> dict:
        """Fetch all farmer data for the report."""
        fid = farmer_id
        data = {}

        # Farmer profile
        farmer = await db.get(Farmer, fid)
        if farmer:
            data["farmer"] = {
                "name": farmer.name,
                "phone": farmer.phone,
                "location": farmer.location,
            }

        # Soil profiles
        result = await db.execute(
            select(SoilProfile).where(SoilProfile.farmer_id == fid).order_by(SoilProfile.fetched_at.desc()).limit(5)
        )
        soils = result.scalars().all()
        data["soil_profiles"] = [
            {"shc_id": s.shc_id, "N": s.nitrogen, "P": s.phosphorus, "K": s.potassium,
             "pH": s.ph, "OC": s.organic_carbon, "date": s.fetched_at.isoformat()}
            for s in soils
        ]

        # Crop events
        result = await db.execute(
            select(CropEvent).where(CropEvent.farmer_id == fid).order_by(CropEvent.timestamp.desc()).limit(20)
        )
        events = result.scalars().all()
        data["crop_events"] = [
            {"type": e.event_type, "details": e.details, "date": e.timestamp.isoformat()}
            for e in events
        ]

        # Disease detections
        result = await db.execute(
            select(DiseaseDetection).where(DiseaseDetection.farmer_id == fid).order_by(DiseaseDetection.timestamp.desc()).limit(10)
        )
        diseases = result.scalars().all()
        data["diseases"] = [
            {"disease": d.disease, "confidence": d.confidence, "treatment": d.treatment, "date": d.timestamp.isoformat()}
            for d in diseases
        ]

        # Pesticide records
        result = await db.execute(
            select(PesticideRecord).where(PesticideRecord.farmer_id == fid).order_by(PesticideRecord.timestamp.desc()).limit(10)
        )
        pesticides = result.scalars().all()
        data["chemical_logs"] = [
            {"batch_id": p.batch_id, "product": p.product_name, "verified": p.verified, "date": p.timestamp.isoformat()}
            for p in pesticides
        ]

        # Latest ESG score
        result = await db.execute(
            select(ESGScore).where(ESGScore.farmer_id == fid).order_by(ESGScore.timestamp.desc()).limit(1)
        )
        esg = result.scalar_one_or_none()
        if esg:
            data["latest_esg"] = {
                "score": esg.score, "environmental": esg.environmental,
                "social": esg.social, "governance": esg.governance,
            }

        return data

    def _generate_qr(self, data: str, report_id: str) -> str:
        """Generate a QR code image and save to disk."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        path = os.path.join(self.output_dir, f"qr_{report_id}.png")
        img.save(path)
        return path

    def _generate_pdf(
        self,
        data: dict,
        report_id: str,
        qr_path: str,
        sections: list[str],
    ) -> str:
        """Generate the sustainability report PDF."""
        pdf_path = os.path.join(self.output_dir, f"report_{report_id}.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            textColor=colors.HexColor("#2E7D32"),
        )
        story.append(Paragraph("🌾 AgroFix Sustainability Report", title_style))
        story.append(Spacer(1, 0.3 * inch))

        # Farmer info
        farmer = data.get("farmer", {})
        story.append(Paragraph(f"<b>Farmer:</b> {farmer.get('name', 'N/A')}", styles["Normal"]))
        story.append(Paragraph(f"<b>Location:</b> {farmer.get('location', 'N/A')}", styles["Normal"]))
        story.append(Paragraph(f"<b>Report ID:</b> {report_id}", styles["Normal"]))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
        story.append(Spacer(1, 0.3 * inch))

        # Soil section
        if "soil" in sections and data.get("soil_profiles"):
            story.append(Paragraph("🧪 Soil Health Data", styles["Heading2"]))
            soil_table_data = [["SHC ID", "N", "P", "K", "pH", "OC", "Date"]]
            for s in data["soil_profiles"]:
                soil_table_data.append([
                    s["shc_id"], str(s["N"]), str(s["P"]), str(s["K"]),
                    str(s["pH"]), str(s["OC"]), s["date"][:10],
                ])
            t = Table(soil_table_data)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.2 * inch))

        # Chemical logs
        if "chemicals" in sections and data.get("chemical_logs"):
            story.append(Paragraph("🛡 Chemical Usage Log", styles["Heading2"]))
            chem_data = [["Batch ID", "Product", "Verified", "Date"]]
            for c in data["chemical_logs"]:
                chem_data.append([
                    c["batch_id"], c["product"] or "Unknown",
                    "✅" if c["verified"] else "❌", c["date"][:10],
                ])
            t = Table(chem_data)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FF9800")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.2 * inch))

        # ESG Score
        if "esg" in sections and data.get("latest_esg"):
            story.append(Paragraph("📊 ESG Sustainability Score", styles["Heading2"]))
            esg = data["latest_esg"]
            story.append(Paragraph(f"<b>Overall Score:</b> {esg['score']}/100", styles["Normal"]))
            story.append(Paragraph(f"Environmental: {esg['environmental']} | Social: {esg['social']} | Governance: {esg['governance']}", styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))

        # QR Code
        story.append(Paragraph("🔗 Verification QR Code", styles["Heading2"]))
        try:
            qr_img = RLImage(qr_path, width=1.5 * inch, height=1.5 * inch)
            story.append(qr_img)
        except Exception as e:
            logger.warning(f"Could not embed QR image: {e}")
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("Scan to verify this report's authenticity.", styles["Normal"]))

        doc.build(story)
        logger.info(f"PDF report generated: {pdf_path}")
        return pdf_path
