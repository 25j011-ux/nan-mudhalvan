"""
LegalEase API Routes
Defines endpoints for document generation, health verification, and exports.
"""
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from ai_core.gemini_generator import GeminiLegalGenerator
from document_generator.txt_generator import generate_txt
from document_generator.docx_generator import generate_docx
from document_generator.pdf_generator import generate_pdf

router = APIRouter(tags=["Legal Document Generation"])

# Initialize Gemini generator instance
generator = GeminiLegalGenerator()


class DocumentRequest(BaseModel):
    """
    Standard request payload for generating legal documents.
    """
    document_type: str = Field(..., description="Type of document, e.g. 'Employment Contract', 'NDA'")
    parties: Dict[str, Any] = Field(default_factory=dict, description="Contracting parties' names and addresses")
    terms: Dict[str, Any] = Field(default_factory=dict, description="Key covenants, payment, roles, and obligations")
    dates: Dict[str, Any] = Field(default_factory=dict, description="Effective dates, expiration dates, durations")
    additional_instructions: Optional[str] = Field(default="", description="Specific clauses, modifications, or requests")
    branding: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Company name, logo, typography")


class DocumentResponse(BaseModel):
    """
    Structured response payload returned to client.
    """
    success: bool
    document_type: str
    title: str
    content: str
    summary_table: Dict[str, str]
    model_used: str
    generated_at: str
    disclaimer: str


class ExportRequest(BaseModel):
    """
    Request model for document file export.
    """
    title: str
    content: str
    summary_table: Optional[Dict[str, str]] = None
    branding: Optional[Dict[str, Any]] = None


@router.get("/health", summary="Health and status check")
async def health_check():
    """
    Return API health status and whether the Gemini AI service is initialized.
    """
    configured = generator.is_configured()
    return {
        "status": "online",
        "service": "LegalEase AI Backend",
        "gemini_configured": configured,
        "mode": "Gemini AI Live Engine" if configured else "LegalEase Intelligent Built-in Engine",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/generate", response_model=DocumentResponse, summary="Generate a legal agreement")
async def generate_document(request: DocumentRequest):
    """
    Accepts contract parameters, validates inputs, invokes Gemini AI legal generator,
    and returns a structured, editable legal document.
    """
    # 1. Validation
    if not request.document_type or not request.document_type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document type is required."
        )

    if not request.parties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parties information must be provided."
        )

    try:
        # 2. Invoke Generator
        result = generator.generate_legal_document(
            document_type=request.document_type.strip(),
            parties=request.parties,
            dates=request.dates,
            terms=request.terms,
            additional_instructions=request.additional_instructions,
            branding=request.branding
        )

        return DocumentResponse(
            success=True,
            document_type=request.document_type.strip(),
            title=result.get("title", f"{request.document_type.upper()}"),
            content=result.get("content", ""),
            summary_table=result.get("summary_table", {}),
            model_used=result.get("model_used", "LegalEase AI"),
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            disclaimer=result.get("disclaimer", GeminiLegalGenerator.get_disclaimer())
        )
    except Exception as e:
        # Prevent internal exception leaks; provide clean error message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating the legal document: {str(e)}"
        )
