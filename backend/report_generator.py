from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse
from backend.logger import logger

router = APIRouter()

# Cache to save comparison
comparison_cache = {
    "differences": [],
    "matched": []
}

@router.post("/store-differences")
async def store_differences(request: Request):
    """Saves comparison results (і differences, і matched)."""
    global comparison_cache
    data = await request.json()
    comparison_cache = {
        "differences": data.get("differences", []),
        "matched": data.get("matched", [])
    }
    logger.info(f"Saved: {len(comparison_cache['differences'])} differences, {len(comparison_cache['matched'])} comparisons")
    return {"message": "Comparison results stored"}

@router.get("/generate-pdf")
def get_pdf_report():
    """Generates a PDF report on saved results."""
    if not comparison_cache["differences"] and not comparison_cache["matched"]:
        return Response("No data available", status_code=400)

    filename = generate_pdf_report(comparison_cache)
    return FileResponse(filename, media_type="application/pdf", filename="report.pdf")

def generate_pdf_report(comparison, filename="report.pdf"):
    """Generates a PDF report."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y, "GUI Comparison Report")
    y -= 30

    # ✅ Output matched elements
    if comparison["matched"]:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y, "Matched Elements:")
        y -= 20

        c.setFont("Helvetica", 11)
        for element in comparison["matched"]:
            c.drawString(40, y, f"✔ {element}: All styles match")
            y -= 15
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 50

        y -= 10

    # ❌ Output differences
    if comparison["differences"]:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y, "Differences:")
        y -= 20

        c.setFont("Helvetica", 11)
        for diff in comparison["differences"]:
            element = diff.get("element", "Unknown element")
            issue = diff.get("issue", "Unknown issue")
            c.drawString(40, y, f"❌ {element}: {issue}")
            y -= 15

            for detail in diff.get("details", []):
                line = f" - {detail['property']}: expected {detail['expected']}, got {detail['actual']}"
                c.drawString(50, y, line)
                y -= 12

            y -= 8
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 50

    c.save()
    logger.info(f"PDF report saved as {filename}")
    return filename
