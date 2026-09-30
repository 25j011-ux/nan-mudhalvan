"""
LegalEase PDF Generator
Builds publication-quality PDF legal documents using FPDF2 with custom branding,
table formatting, running headers/footers, and page numbering.
"""
import os
import io
import re
from typing import Optional, Dict, Any

try:
    from fpdf import FPDF
except ImportError:
    from fpdf2 import FPDF


def _sanitize_for_latin1(text: str) -> str:
    """
    Sanitize text for standard PDF fonts (Helvetica/Times/Courier) to avoid Latin-1 encoding errors.
    Replaces common legal/currency unicode characters with ASCII/Latin-1 equivalents.
    """
    replacements = {
        "\u2018": "'",   # Left single quote
        "\u2019": "'",   # Right single quote
        "\u201c": '"',   # Left double quote
        "\u201d": '"',   # Right double quote
        "\u2014": " -- ", # Em dash
        "\u2013": " - ",  # En dash
        "\u2022": "*",    # Bullet
        "\u2026": "...",  # Ellipsis
        "\u20b9": "INR ", # Indian Rupee symbol
        "\u00a0": " ",    # Non-breaking space
        "\u2122": "(TM)", # Trademark
        "\u00a9": "(C)",  # Copyright
        "\u00ae": "(R)",  # Registered
        "\u00a7": "Sec. ", # Section sign
        "\u20ac": "EUR ", # Euro
        "\u00a3": "GBP ", # British Pound
        "\u00a5": "JPY ", # Yen
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
        
    # Any remaining character beyond latin-1 range (0-255) is safely replaced with ascii
    safe_chars = []
    for ch in text:
        if ord(ch) < 256:
            safe_chars.append(ch)
        else:
            safe_chars.append("?")
    return "".join(safe_chars)


class LegalDocumentPDF(FPDF):
    """Custom FPDF subclass tailored for elegant legal documents."""
    
    def __init__(
        self,
        company_name: str = "LegalEase AI Legal Drafting",
        header_text: str = "",
        footer_text: str = "Confidential Legal Document -- Generated with LegalEase",
        logo_path: Optional[str] = None,
        font_family: str = "Helvetica"
    ):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.company_name = _sanitize_for_latin1(company_name)
        self.header_text = _sanitize_for_latin1(header_text or company_name)
        self.footer_text = _sanitize_for_latin1(footer_text)
        self.logo_path = logo_path if (logo_path and os.path.exists(logo_path)) else None
        
        # Safe font family fallback
        f_lower = font_family.lower()
        if "times" in f_lower or "roman" in f_lower or "garamond" in f_lower:
            self.doc_font = "Times"
        elif "courier" in f_lower or "mono" in f_lower:
            self.doc_font = "Courier"
        else:
            self.doc_font = "Helvetica"
            
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(auto=True, margin=22)

    def header(self):
        # Header on every page
        if self.page_no() == 1 and self.logo_path:
            try:
                # Add logo on top left of first page
                self.image(self.logo_path, x=20, y=14, w=35)
                self.set_y(15)
                self.set_font(self.doc_font, "B", 9)
                self.set_text_color(11, 37, 69) # Deep Navy
                self.cell(0, 5, self.header_text.upper(), align="R", ln=1)
                self.ln(12)
                return
            except Exception:
                pass

        self.set_y(12)
        self.set_font(self.doc_font, "I", 8)
        self.set_text_color(100, 116, 139) # Muted Slate
        self.cell(0, 5, self.header_text.upper(), align="R", ln=1)
        self.set_draw_color(226, 232, 240)
        self.line(20, 18, 190, 18)
        self.ln(6)

    def footer(self):
        # Position 15 mm from bottom
        self.set_y(-16)
        self.set_draw_color(226, 232, 240)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(2)
        self.set_font(self.doc_font, "", 8)
        self.set_text_color(100, 116, 139)
        self.cell(120, 5, self.footer_text, align="L")
        self.cell(50, 5, f"Page {self.page_no()}", align="R")


def generate_pdf(
    title: str,
    content: str,
    summary_table: Optional[Dict[str, str]] = None,
    output_path: Optional[str] = None,
    branding: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Generate a professional PDF legal agreement.
    """
    branding = branding or {}
    company_name = branding.get("company_name", "LegalEase AI Document Drafting")
    header_text = branding.get("header_text", company_name)
    footer_text = branding.get("footer_text", "Confidential Legal Document -- Generated with LegalEase")
    logo_path = branding.get("logo_path")
    font_family = branding.get("font_family", "Helvetica")
    include_signatures = branding.get("include_signatures", True)

    pdf = LegalDocumentPDF(
        company_name=company_name,
        header_text=header_text,
        footer_text=footer_text,
        logo_path=logo_path,
        font_family=font_family
    )
    pdf.add_page()
    doc_font = pdf.doc_font

    # Title Section
    safe_title = _sanitize_for_latin1(title.strip().upper())
    pdf.set_y(pdf.get_y() + 6)
    pdf.set_font(doc_font, "B", 18)
    pdf.set_text_color(11, 37, 69) # Deep Navy
    pdf.multi_cell(170, 9, safe_title, align="C")
    
    # Elegant Underline
    pdf.ln(2)
    y_line = pdf.get_y()
    pdf.set_draw_color(11, 37, 69)
    pdf.set_line_width(0.6)
    pdf.line(65, y_line, 145, y_line)
    pdf.set_line_width(0.2)
    pdf.ln(6)

    # Automatic Key Terms Summary Table (if provided)
    if summary_table and len(summary_table) > 0:
        pdf.set_font(doc_font, "B", 10.5)
        pdf.set_text_color(11, 37, 69)
        pdf.cell(170, 7, "SUMMARY OF KEY COVENANTS & TERMS", ln=1)
        pdf.ln(1)

        # Table Header
        pdf.set_font(doc_font, "B", 9)
        pdf.set_fill_color(11, 37, 69)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(55, 7, "  Term / Clause", border=1, fill=True)
        pdf.cell(115, 7, "  Agreed Details", border=1, ln=1, fill=True)

        # Table Rows
        pdf.set_font(doc_font, "", 8.5)
        is_alt = False
        for k, v in summary_table.items():
            if is_alt:
                pdf.set_fill_color(248, 250, 252) # Light slate
            else:
                pdf.set_fill_color(255, 255, 255)

            safe_k = _sanitize_for_latin1(str(k))
            safe_v = _sanitize_for_latin1(str(v))

            pdf.set_text_color(15, 23, 42)
            pdf.cell(55, 6.5, f"  {safe_k[:32]}", border="LRB", fill=True)
            pdf.cell(115, 6.5, f"  {safe_v[:75]}", border="LRB", ln=1, fill=True)
            is_alt = not is_alt

        pdf.ln(6)

    # Document Body Processing
    cleaned_content = content.replace("```markdown", "").replace("```", "").strip()
    raw_lines = cleaned_content.split("\n")

    in_signature_section = False

    for raw_line in raw_lines:
        line = _sanitize_for_latin1(raw_line.strip())
        if not line:
            pdf.ln(2.5)
            continue

        # Signature page check
        if any(keyword in line.upper() for keyword in ["IN WITNESS WHEREOF", "SIGNATURE PAGE", "EXECUTED AS AN AGREEMENT"]):
            in_signature_section = True
            pdf.ln(6)
            pdf.set_font(doc_font, "B", 10.5)
            pdf.set_text_color(11, 37, 69)
            pdf.multi_cell(170, 6, line)
            pdf.ln(3)
            continue

        # Major Article / Heading 1
        if line.startswith("# ") or (line.isupper() and len(line) < 60 and ("ARTICLE" in line or "SECTION" in line or "AGREEMENT" in line)):
            h_text = line.lstrip("# ").strip()
            pdf.ln(4)
            pdf.set_font(doc_font, "B", 11.5)
            pdf.set_text_color(11, 37, 69)
            pdf.cell(170, 6.5, h_text, ln=1)
            pdf.set_draw_color(203, 213, 225)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(2)
            continue

        # Subheading 2
        if line.startswith("## ") or line.startswith("### "):
            sub_text = line.lstrip("# ").strip()
            pdf.ln(3)
            pdf.set_font(doc_font, "B", 10)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(170, 5.5, sub_text, ln=1)
            pdf.ln(1)
            continue

        # Bullet point
        if line.startswith("* ") or line.startswith("- ") or line.startswith("• "):
            bullet_text = line[2:].strip()
            clean_b = re.sub(r'\*\*(.*?)\*\*', r'\1', bullet_text)
            pdf.set_font(doc_font, "", 9)
            pdf.set_text_color(51, 65, 85)
            # Indented bullet
            pdf.set_x(25)
            pdf.multi_cell(165, 4.8, f"-  {clean_b}")
            continue

        # Regular legal paragraph
        clean_para = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
        pdf.set_font(doc_font, "", 9)
        pdf.set_text_color(30, 41, 59)
        pdf.multi_cell(170, 4.8, clean_para, align="J")
        pdf.ln(1.5)

    # Optional signature boxes if not already in content
    if include_signatures and not in_signature_section:
        if pdf.get_y() > 220:
            pdf.add_page()
            
        pdf.ln(8)
        pdf.set_font(doc_font, "B", 10)
        pdf.set_text_color(11, 37, 69)
        pdf.cell(170, 6, "IN WITNESS WHEREOF, the Parties have executed this Agreement as of the Effective Date:", ln=1)
        pdf.ln(6)

        # Dual signature boxes
        col_w = 80
        start_y = pdf.get_y()
        
        # Column 1
        pdf.set_xy(20, start_y)
        pdf.set_font(doc_font, "B", 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(col_w, 5, "FOR: DISCLOSING / EMPLOYING PARTY", ln=1)
        pdf.set_font(doc_font, "", 8.5)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(col_w, 7, "Signature: ___________________________", ln=1)
        pdf.cell(col_w, 6, "Printed Name: ________________________", ln=1)
        pdf.cell(col_w, 6, "Title: _______________________________", ln=1)
        pdf.cell(col_w, 6, "Date: ________________________________", ln=1)

        # Column 2
        pdf.set_xy(110, start_y)
        pdf.set_font(doc_font, "B", 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(col_w, 5, "FOR: RECEIVING / SECOND PARTY", ln=1)
        pdf.set_font(doc_font, "", 8.5)
        pdf.set_text_color(71, 85, 105)
        pdf.set_x(110)
        pdf.cell(col_w, 7, "Signature: ___________________________", ln=1)
        pdf.set_x(110)
        pdf.cell(col_w, 6, "Printed Name: ________________________", ln=1)
        pdf.set_x(110)
        pdf.cell(col_w, 6, "Title: _______________________________", ln=1)
        pdf.set_x(110)
        pdf.cell(col_w, 6, "Date: ________________________________", ln=1)

    # Return bytes and/or save
    pdf_bytes = pdf.output()

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes
