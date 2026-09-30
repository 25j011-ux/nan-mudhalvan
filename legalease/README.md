# LegalEase – AI-Powered Legal Document Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-4285F4.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**LegalEase** is an enterprise-grade AI legal drafting platform that empowers founders, HR leaders, lawyers, landlords, and contractors to generate, customize, edit, and export corporate-grade legal agreements in minutes.

Backed by **Google Gemini AI** and a built-in intelligent legal drafting engine, LegalEase strictly adheres to contract parameters, eliminates factual hallucinations, and provides instant exports in **TXT**, **DOCX (Word)**, and **PDF** formats.

---

## 🌟 Key Features

* **⚡ Intelligent Multi-Type Contract Drafting:**
  * Employment Contracts (remuneration, roles, benefits, IP assignment, restrictive covenants)
  * Mutual & Unilateral Non-Disclosure Agreements (NDAs)
  * Residential Lease Agreements (rent, deposits, utilities, maintenance, pet policy)
  * Freelance & Independent Contractor Agreements (deliverables, milestones, IP handover)
  * Master Service Agreements (B2B MSAs, SLAs, liability limitations)
  * Custom Commercial Agreements with bespoke prompts
* **🔍 Automatic Key Terms Table:** Automatically parses parties, dates, compensation, and covenants into an executive summary table displayed before the full contract text.
* **✏️ Real-Time Editable Preview:** Review drafted agreements side-by-side with an integrated live editor allowing manual clause tweaking prior to export.
* **🎨 White-Label Document Customization:** Embed your law firm or company logo, select preferred typography (Calibri, Arial, Times New Roman, Garamond), and customize running headers and footers.
* **📥 Multi-Format Export:**
  * **TXT:** Clean, human-readable ASCII/UTF-8 format.
  * **DOCX:** Formatted Word document with corporate palettes, tables, and dual-party signature blocks.
  * **PDF:** Crisp, publication-grade PDF with running headers, footers, page numbering, and signature seals.
* **🛡️ Built-in Offline Fallback Engine:** Works seamlessly out of the box even before configuring a Gemini API key or during network downtime.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | [Streamlit](https://streamlit.io/) | Interactive, modern SaaS UI with custom CSS, dynamic forms, and real-time state management |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance asynchronous REST API with Pydantic validation & CORS |
| **AI Intelligence** | [Google Gemini AI](https://ai.google.dev/) | Structured few-shot legal drafting prompts via `gemini-1.5-flash` |
| **Document Processing** | `python-docx`, `fpdf2`, `Pillow` | Native binary generation for Word, PDF, and high-DPI image assets |
| **Environment** | `python-dotenv` | Zero API key exposure; secure variable loading |

---

## 📁 Project Structure

```text
LegalEase/
│
├── main.py                       # FastAPI application entry point & CORS configuration
├── routes.py                     # API routing, Pydantic schemas (DocumentRequest), /generate
├── streamlit_app.py              # Modern Streamlit UI with multi-tab navigation & editor
├── requirements.txt              # Production dependency specifications
├── .env                          # Local secrets configuration (GEMINI_API_KEY)
├── .env.example                  # Template configuration file
├── README.md                     # Comprehensive project documentation
│
├── ai_core/
│   ├── __init__.py               # AI module exports
│   └── gemini_generator.py       # Google Gemini AI legal drafting class & fallback engine
│
├── document_generator/
│   ├── __init__.py               # Document generator exports
│   ├── docx_generator.py         # Microsoft Word DOCX styling with tables & branding
│   ├── pdf_generator.py          # Corporate PDF generator with running headers/footers
│   └── txt_generator.py          # Structured plain text export
│
├── assets/
│   └── logo.png                  # High-resolution legal-tech branding emblem
│
└── generated_documents/          # Storage directory for compiled contracts
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
* Python 3.10, 3.11, or 3.12 installed on your machine.
* A free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Installation

Clone or navigate to the repository directory:

```bash
cd LegalEase
```

Create a virtual environment and install dependencies:

```bash
# Using standard Python venv
python -m venv .venv
source .venv/bin/activate       # On Linux/macOS
.venv\Scripts\activate          # On Windows

# Install packages
pip install -r requirements.txt
```

*(Optional: If you use [uv](https://github.com/astral-sh/uv), run `uv pip install -r requirements.txt`)*

### 3. Environment Variable Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Open `.env` and paste your Gemini API key:

```env
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
BACKEND_URL=http://127.0.0.1:8000
```

> **Note:** Even without an API key, LegalEase includes a built-in intelligent legal drafting engine for immediate testing and demonstration!

---

## 🖥️ Running the Application

LegalEase is architected as a decoupled frontend and backend. Run both components in separate terminal windows:

### Terminal 1: Run FastAPI Backend
```bash
uvicorn main:app --reload --port 8000
```
* Backend API will be available at: `http://127.0.0.1:8000`
* Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### Terminal 2: Run Streamlit Frontend
```bash
streamlit run streamlit_app.py
```
* Frontend Web App will open automatically in your browser at: `http://localhost:8501`

---

## 🧪 Sample Test Run

To test the application end-to-end:

1. Open `http://localhost:8501`.
2. Go to **Create Document**.
3. Click the **⚡ Load Sample Test Data (Employment Contract)** button at the top of the form.
4. This pre-fills:
   * **Employer:** TechNova Solutions (Chennai, India)
   * **Employee:** Rahul Kumar
   * **Job Title:** Software Developer
   * **Remuneration:** ₹6,00,000 per year
   * **Start Date:** 01/10/2026
5. Click **⚡ Generate Legal Document**.
6. View the **Summary of Key Contract Terms** table and the full **Employment Agreement**.
7. Edit clauses in the **✏️ Live Document Editor** tab or download directly via **Download TXT**, **Download DOCX**, or **Download PDF**.

---

## 📡 REST API Documentation

### Root Endpoint
`GET /`  
Returns service health, versioning, and supported document types.

### Health Endpoint
`GET /health`  
Returns backend status and whether Google Gemini AI is initialized:
```json
{
  "status": "online",
  "service": "LegalEase AI Backend",
  "gemini_configured": true,
  "mode": "Gemini AI Live Engine",
  "timestamp": "2026-09-30T14:45:00"
}
```

### Document Generation Endpoint
`POST /generate`

**Sample Request Body:**
```json
{
  "document_type": "Employment Contract",
  "parties": {
    "employer_name": "TechNova Solutions",
    "employer_address": "Tech Park, Taramani, Chennai",
    "employee_name": "Rahul Kumar",
    "work_location": "Chennai, India"
  },
  "dates": {
    "start_date": "01/10/2026"
  },
  "terms": {
    "job_title": "Software Developer",
    "salary": "INR 6,00,000 per year",
    "payment_frequency": "Monthly"
  },
  "additional_instructions": "Include standard non-compete clause for 6 months."
}
```

**Sample Response Body:**
```json
{
  "success": true,
  "document_type": "Employment Contract",
  "title": "EMPLOYMENT AGREEMENT",
  "content": "# EMPLOYMENT AGREEMENT\n\nTHIS EMPLOYMENT AGREEMENT...",
  "summary_table": {
    "Document Type": "Employment Contract",
    "Party 1 (Primary)": "TechNova Solutions",
    "Party 2 (Secondary)": "Rahul Kumar",
    "Effective Date": "01/10/2026",
    "Compensation / Salary": "INR 6,00,000 per year",
    "Position / Job Title": "Software Developer",
    "Jurisdiction / Location": "Chennai, India"
  },
  "model_used": "Google Gemini AI (gemini-1.5-flash)",
  "generated_at": "2026-09-30 14:45:00 UTC",
  "disclaimer": "LegalEase generates AI-assisted legal documents for informational and drafting purposes..."
}
```

---

## 🚢 Deployment Guide

### A. Deploy to Streamlit Community Cloud (Frontend Only or Combined)
1. Push this repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io) and link your repository.
3. Set the Main file path to `streamlit_app.py`.
4. In Advanced Settings, add `GEMINI_API_KEY` under Secrets.
5. Deploy! Streamlit will automatically run the app with direct Gemini generation.

### B. Deploy Backend to Render / Railway
1. **Render:**
   * Create a new **Web Service** from your GitHub repo.
   * Runtime: `Python 3`
   * Build Command: `pip install -r requirements.txt`
   * Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   * Add Environment Variable: `GEMINI_API_KEY`
2. **Railway:**
   * Deploy from GitHub repo.
   * Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   * Add Variables: `GEMINI_API_KEY`

### C. Docker Deployment
A single container or docker-compose setup can run both services:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
```

---

## ⚖️ Legal Disclaimer

> **IMPORTANT NOTICE:** LegalEase generates AI-assisted legal documents for informational and drafting purposes only.
> LegalEase does not provide legal advice, and using this application does not establish an attorney-client relationship.
> Laws vary substantially across jurisdictions; always consult a licensed attorney or legal professional before executing any legal agreement.

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).
