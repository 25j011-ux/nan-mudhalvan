"""
LegalEase TXT Generator
Formats and exports legal documents as clean, structured plain text.
"""
import os
import re
from typing import Optional, Dict


def generate_txt(
    title: str,
    content: str,
    summary_table: Optional[Dict[str, str]] = None,
    output_path: Optional[str] = None,
    branding: Optional[dict] = None
) -> bytes:
    """
    Generate a clean UTF-8 text file from legal document content and terms.
    
    Args:
        title: Document title (e.g. 'EMPLOYMENT CONTRACT')
        content: Main body text of the legal agreement
        summary_table: Key terms dictionary for quick reference table
        output_path: Optional path to save on disk
        branding: Optional branding configuration
        
    Returns:
        bytes: Encoded text bytes
    """
    lines = []
    divider = "=" * 78
    subdivider = "-" * 78
    
    company_name = branding.get("company_name", "LEGALEASE AI LEGAL DRAFTING") if branding else "LEGALEASE AI LEGAL DRAFTING"

    # Header
    lines.append(divider)
    lines.append(f"{company_name.center(78)}")
    lines.append(divider)
    lines.append("")
    lines.append(f"{title.strip().upper().center(78)}")
    lines.append("")

    # Automatic Term Summary Table if provided
    if summary_table:
        lines.append(subdivider)
        lines.append("SUMMARY OF KEY TERMS".center(78))
        lines.append(subdivider)
        max_key_len = max([len(str(k)) for k in summary_table.keys()] + [15])
        for key, val in summary_table.items():
            lines.append(f"  {str(key).ljust(max_key_len)} :  {str(val)}")
        lines.append(subdivider)
        lines.append("")

    # Clean body content (strip excessive markdown artifacts for text view if any)
    cleaned_content = content.replace("```markdown", "").replace("```", "").strip()
    lines.append(cleaned_content)
    lines.append("")
    lines.append(divider)
    lines.append("CONFIDENTIAL & PRIVILEGED LEGAL DOCUMENT".center(78))
    lines.append("Generated with LegalEase AI (Verify with qualified legal counsel)".center(78))
    lines.append(divider)

    full_text = "\n".join(lines)
    text_bytes = full_text.encode("utf-8")

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(text_bytes)

    return text_bytes
