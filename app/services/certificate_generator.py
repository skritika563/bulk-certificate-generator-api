import math
from datetime import datetime
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

# Pre-calculate output directory and page dimensions
OUTPUT_DIR = Path("generated_certificates")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)

# Colour Palette
NAVY = colors.HexColor("#171E5D")
DARK_GREEN = colors.HexColor("#245747")
GOLD = colors.HexColor("#E38A37")
PALE_GOLD = colors.HexColor("#F7F0DD")
CREAM = colors.HexColor("#FFFEFA")
GREY = colors.HexColor("#6A788B")
LIGHT_BORDER = colors.HexColor("#D9C38B")


def fit_font_size(text: str, font_name: str, max_size: int, min_size: int, max_width: float) -> int:
    """Calculate target font size directly in O(1) time using linear ratio scaling."""
    current_width = stringWidth(str(text), font_name, max_size)
    if current_width <= max_width or current_width == 0:
        return max_size
    return max(min_size, int(max_size * (max_width / current_width)))


def draw_corner_accents(pdf: canvas.Canvas, width: float, height: float) -> None:
    """Draw decorative navy and gold diagonal ribbons on all four corners."""
    corners = [
        (0, height, -45),       # Top-Left
        (width, height, -135),  # Top-Right
        (width, 0, 135),        # Bottom-Right (Fixed angle: 135 deg)
        (0, 0, 45),             # Bottom-Left
    ]

    for tx, ty, angle in corners:
        pdf.saveState()
        pdf.translate(tx, ty)
        pdf.rotate(angle)
        
        pdf.setFillColor(NAVY)
        pdf.rect(-20, -35, 180, 35, fill=1, stroke=0)
        
        pdf.setFillColor(GOLD)
        pdf.rect(-20, -35, 180, 7, fill=1, stroke=0)
        pdf.restoreState()


def draw_gold_seal(pdf: canvas.Canvas, cx: float, cy: float, outer_r: float = 22) -> None:
    """Draw a decorative gold award seal emblem with serrated edges and star center."""
    pdf.saveState()
    
    # Outer serrated starburst edge
    num_teeth = 36
    path = pdf.beginPath()
    for i in range(num_teeth * 2):
        angle = math.radians(i * (360 / (num_teeth * 2)))
        r = outer_r if i % 2 == 0 else outer_r - 3
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.close()
    pdf.setFillColor(GOLD)
    pdf.drawPath(path, fill=1, stroke=0)
    
    # Inner circles
    pdf.setFillColor(PALE_GOLD)
    pdf.circle(cx, cy, outer_r - 5, fill=1, stroke=0)
    
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1)
    pdf.circle(cx, cy, outer_r - 7, fill=0, stroke=1)
    
    # Center star badge
    path_star = pdf.beginPath()
    for i in range(10):
        angle = math.radians(90 + i * 36)
        r = (outer_r - 11) if i % 2 == 0 else (outer_r - 16)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        if i == 0:
            path_star.moveTo(x, y)
        else:
            path_star.lineTo(x, y)
    path_star.close()
    pdf.setFillColor(NAVY)
    pdf.drawPath(path_star, fill=1, stroke=0)
    
    pdf.restoreState()

def safe_filename_part(value: str) -> str:
    """Convert text into a safe filename component."""

    value = value.strip()
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", value)
    value = re.sub(r"\s+", "_", value)
    value = value.strip("._")

    return value or "Certificate"

def generate_certificate(
    certificate_id: int,
    recipient_name: str,
    event_name: str,
    event_date: str,
    organization: str,
    issue_date: str | None = None,
) -> str:
    """Generate an optimized certificate PDF named as RecipientName_EventName.pdf."""
    recipient_part = safe_filename_part(recipient_name)
    event_part = safe_filename_part(event_name)

    filename = f"{recipient_part}_{event_part}.pdf"
    file_path = OUTPUT_DIR / filename

    if file_path.exists():
        filename = f"{recipient_part}_{event_part}_{certificate_id}.pdf"
        file_path = OUTPUT_DIR / filename

    formatted_issue_date = issue_date or datetime.now().strftime("%d %b %Y")

    pdf = canvas.Canvas(str(file_path), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    pdf.setTitle(f"Certificate - {recipient_name}")
    pdf.setAuthor(organization)

    # Background
    pdf.setFillColor(CREAM)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    # Double Outer & Inner Borders
    margin = 25
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(2)
    pdf.rect(margin, margin, PAGE_WIDTH - 2 * margin, PAGE_HEIGHT - 2 * margin, fill=0, stroke=1)

    pdf.setStrokeColor(LIGHT_BORDER)
    pdf.setLineWidth(0.7)
    pdf.rect(margin + 7, margin + 7, PAGE_WIDTH - 2 * (margin + 7), PAGE_HEIGHT - 2 * (margin + 7), fill=0, stroke=1)

    # Decorative 4-Corner Ribbons
    draw_corner_accents(pdf, PAGE_WIDTH, PAGE_HEIGHT)

    center_x = PAGE_WIDTH / 2

    # Organization Name & Top Line
    pdf.setFillColor(DARK_GREEN)
    pdf.setFont("Times-Bold", 17)
    pdf.drawCentredString(center_x, PAGE_HEIGHT - 65, organization)

    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1.3)
    pdf.line(center_x - 90, PAGE_HEIGHT - 77, center_x + 90, PAGE_HEIGHT - 77)

    # Certificate Title Header
    pdf.setFillColor(NAVY)
    pdf.setFont("Times-Bold", 31)
    pdf.drawCentredString(center_x, PAGE_HEIGHT - 119, "CERTIFICATE")

    pdf.setFillColor(GOLD)
    pdf.setFont("Times-Bold", 15)
    pdf.drawCentredString(center_x, PAGE_HEIGHT - 145, "O F   A C H I E V E M E N T")

    # Introductory Line
    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(center_x, PAGE_HEIGHT - 177, "THIS CERTIFICATE IS PROUDLY PRESENTED TO")

    # Recipient Name
    name_size = fit_font_size(recipient_name, "Times-Bold", 29, 17, PAGE_WIDTH - 150)
    pdf.setFillColor(DARK_GREEN)
    pdf.setFont("Times-Bold", name_size)
    pdf.drawCentredString(center_x, PAGE_HEIGHT - 215, recipient_name)

    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1)
    pdf.line(center_x - 145, PAGE_HEIGHT - 226, center_x + 145, PAGE_HEIGHT - 226)

    # Body Text
    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(center_x, PAGE_HEIGHT - 251, "in recognition of successful participation in")

    event_size = fit_font_size(event_name, "Times-Bold", 20, 12, PAGE_WIDTH - 150)
    pdf.setFillColor(NAVY)
    pdf.setFont("Times-Bold", event_size)
    pdf.drawCentredString(center_x, PAGE_HEIGHT - 279, event_name)

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(center_x, PAGE_HEIGHT - 301, f"Organised by {organization} on {event_date}")

    pdf.setFillColor(DARK_GREEN)
    pdf.setFont("Times-Italic", 11)
    pdf.drawCentredString(center_x, PAGE_HEIGHT - 330, "Celebrating your commitment to learning, growth and achievement.")

    # Gold Award Seal
    draw_gold_seal(pdf, center_x, 125, outer_r=22)

    # Date of Issue Block
    date_line_y = 68

    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(center_x, date_line_y + 7, formatted_issue_date)

    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1.0)
    pdf.line(center_x - 85, date_line_y, center_x + 85, date_line_y)

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(center_x, date_line_y - 12, "DATE OF ISSUE")

    # Certificate ID (Safe margin offset)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(margin + 105, margin + 17, f"Certificate ID: {certificate_id}")

    pdf.showPage()
    pdf.save()

    return str(file_path)