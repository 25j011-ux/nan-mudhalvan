"""
LegalEase – AI-Powered Legal Document Generator
FastAPI Backend Application Entry Point
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import router

# Load environment configuration
load_dotenv()

app = FastAPI(
    title="LegalEase API",
    description="Intelligent AI-Powered Legal Document Generator Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure Cross-Origin Resource Sharing (CORS) for Streamlit frontend and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)


@app.get("/", summary="API Root & Service Overview")
async def root():
    """
    Root endpoint providing service metadata and navigation links.
    """
    return {
        "service": "LegalEase – AI-Powered Legal Document Generator",
        "status": "operational",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "generate_endpoint": "POST /generate",
        "supported_documents": [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Residential Lease Agreement",
            "Freelance Agreement",
            "Service Agreement",
            "Custom Legal Document"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
