"""
LegalEase – AI-Powered Legal Document Generator
Streamlit Frontend Application
"""
import os
import sys
from datetime import datetime, date
import requests
import streamlit as st
from PIL import Image

# Import local generators for fallback or direct compilation
try:
    from ai_core.gemini_generator import GeminiLegalGenerator
    from document_generator.txt_generator import generate_txt
    from document_generator.docx_generator import generate_docx
    from document_generator.pdf_generator import generate_pdf
except ImportError:
    # Ensure root path is added
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ai_core.gemini_generator import GeminiLegalGenerator
    from document_generator.txt_generator import generate_txt
    from document_generator.docx_generator import generate_docx
    from document_generator.pdf_generator import generate_pdf

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LegalEase – AI Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# GLOBAL CONSTANTS & PATHS
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_documents")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# -----------------------------------------------------------------------------
# CUSTOM SAAS CSS
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1E293B;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Header Nav Bar Styling */
    .legalease-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1.5rem;
        background: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(11, 37, 69, 0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 2rem;
    }
    .legalease-nav-links {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }
    .legalease-nav-link {
        font-size: 0.95rem;
        font-weight: 600;
        color: #475569;
        text-decoration: none;
        transition: color 0.2s;
    }
    .legalease-nav-link:hover {
        color: #1E40AF;
    }

    /* Hero Section */
    .hero-card {
        background: linear-gradient(135deg, #0A192F 0%, #0F2A4A 60%, #173863 100%);
        color: #FFFFFF;
        padding: 3.5rem 3rem;
        border-radius: 20px;
        box-shadow: 0 16px 36px rgba(11, 37, 69, 0.25);
        margin-bottom: 2.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(37, 99, 235, 0.35);
        border: 1px solid rgba(147, 197, 253, 0.4);
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #93C5FD;
        margin-bottom: 1.25rem;
    }
    .hero-title {
        font-size: 2.75rem;
        font-weight: 800;
        line-height: 1.2;
        color: #FFFFFF;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        line-height: 1.6;
        color: #CBD5E1;
        max-width: 650px;
        margin-bottom: 2rem;
    }

    /* Feature Cards */
    .feature-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.75rem 1.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(11, 37, 69, 0.08);
        border-color: #93C5FD;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        font-size: 0.9rem;
        color: #64748B;
        line-height: 1.5;
    }

    /* Doc Type Selection Cards */
    .doctype-card {
        background: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 1rem;
    }
    .doctype-card:hover {
        border-color: #2563EB;
        background-color: #F8FAFC;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.12);
        transform: translateY(-2px);
    }
    .doctype-selected {
        border-color: #2563EB !important;
        background: #EFF6FF !important;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.16) !important;
    }

    /* Summary Term Table */
    .term-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
        background: #FFFFFF;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    .term-table th {
        background: #0B2545;
        color: #FFFFFF;
        padding: 0.9rem 1.25rem;
        font-weight: 600;
        font-size: 0.9rem;
        text-align: left;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .term-table td {
        padding: 0.85rem 1.25rem;
        font-size: 0.92rem;
        border-bottom: 1px solid #F1F5F9;
        color: #1E293B;
    }
    .term-table tr:nth-child(even) {
        background-color: #F8FAFC;
    }
    .term-table tr:hover {
        background-color: #EFF6FF;
    }

    /* Trust & Security Badge */
    .trust-banner {
        background: #F8FAFC;
        border-left: 4px solid #059669;
        border-radius: 0 10px 10px 0;
        padding: 0.9rem 1.25rem;
        margin: 1.5rem 0;
        font-size: 0.88rem;
        color: #334155;
    }

    /* Legal Disclaimer Footer */
    .disclaimer-box {
        background: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        font-size: 0.82rem;
        color: #991B1B;
        line-height: 1.5;
        margin-top: 2.5rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

if "selected_doc_type" not in st.session_state:
    st.session_state["selected_doc_type"] = "Employment Contract"

if "generated_doc" not in st.session_state:
    st.session_state["generated_doc"] = None

if "edited_content" not in st.session_state:
    st.session_state["edited_content"] = ""

if "active_sample_loaded" not in st.session_state:
    st.session_state["active_sample_loaded"] = False

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS & BRANDING
# -----------------------------------------------------------------------------
with st.sidebar:
    # Logo Display
    if os.path.exists(LOGO_PATH):
        try:
            logo_img = Image.open(LOGO_PATH)
            st.image(logo_img, use_container_width=True)
        except Exception:
            st.title("⚖️ LegalEase")
    else:
        st.title("⚖️ LegalEase")

    st.markdown("<p style='font-size:0.85rem; color:#64748B; font-weight:600;'>AI LEGAL DRAFTING SUITE</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Main Navigation
    nav_choice = st.radio(
        "Navigation",
        ["Home", "Create Document", "Templates", "About", "Help"],
        index=["Home", "Create Document", "Templates", "About", "Help"].index(st.session_state["current_page"]),
        key="sidebar_nav"
    )
    if nav_choice != st.session_state["current_page"]:
        st.session_state["current_page"] = nav_choice
        st.rerun()

    st.markdown("---")

    # System Status & Gemini Health
    st.markdown("### 🔌 System Connectivity")
    
    # Check Backend status
    backend_online = False
    gemini_active = False
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=1.5)
        if resp.status_code == 200:
            backend_online = True
            data = resp.json()
            gemini_active = data.get("gemini_configured", False)
    except Exception:
        backend_online = False

    if backend_online:
        st.success(f"FastAPI Backend: **Online** ({BACKEND_URL})")
    else:
        st.info("FastAPI Backend: **Standby** (Direct Engine active)")

    # API Key Configuration
    with st.expander("🔑 Gemini API Settings", expanded=False):
        env_key = os.getenv("GEMINI_API_KEY", "")
        has_env_key = bool(env_key and env_key not in ["your_api_key_here", "your_gemini_api_key_here"])
        
        custom_key = st.text_input(
            "Gemini API Key (Optional Override)",
            type="password",
            value=st.session_state.get("gemini_key_override", ""),
            help="Enter your Google Gemini API key if not configured in .env"
        )
        if custom_key:
            st.session_state["gemini_key_override"] = custom_key
            st.success("Custom Gemini Key applied for this session!")
        elif has_env_key:
            st.success("API Key detected from `.env`")
        else:
            st.warning("No API Key detected. LegalEase will use the built-in intelligent legal engine.")

    # Custom Document Branding
    st.markdown("### 🎨 Document Branding")
    with st.expander("Custom Export Settings", expanded=False):
        brand_company = st.text_input("Company / Law Firm Name", value="LegalEase Drafted Documents")
        brand_font = st.selectbox("Document Typography", ["Calibri", "Arial", "Times New Roman", "Garamond", "Georgia"])
        brand_header = st.text_input("Custom Running Header", value="CONFIDENTIAL COMMERCIAL DOCUMENT")
        brand_footer = st.text_input("Custom Running Footer", value="LegalEase AI Document Drafting -- All Rights Reserved")
        include_sig = st.checkbox("Include Signature Section", value=True)
        uploaded_logo = st.file_uploader("Upload Company Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

        logo_file_path = None
        if uploaded_logo:
            temp_logo_path = os.path.join(OUTPUT_DIR, f"temp_logo_{uploaded_logo.name}")
            with open(temp_logo_path, "wb") as f:
                f.write(uploaded_logo.getbuffer())
            logo_file_path = temp_logo_path
            st.image(uploaded_logo, width=120, caption="Uploaded Logo Preview")
        elif os.path.exists(LOGO_PATH):
            logo_file_path = LOGO_PATH

    branding_config = {
        "company_name": brand_company,
        "font_family": brand_font,
        "header_text": brand_header,
        "footer_text": brand_footer,
        "include_signatures": include_sig,
        "logo_path": logo_file_path
    }

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def trigger_generation(doc_type, parties, dates, terms, additional_inst, branding):
    """
    Coordinates document generation via FastAPI backend or local fallback.
    """
    payload = {
        "document_type": doc_type,
        "parties": parties,
        "dates": dates,
        "terms": terms,
        "additional_instructions": additional_inst,
        "branding": branding
    }

    # First attempt: FastAPI Backend
    try:
        response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=60)
        if response.status_code == 200:
            return response.json()
    except Exception:
        # Fallback to in-process direct generator if backend is not actively running
        pass

    # Direct generator fallback
    active_key = st.session_state.get("gemini_key_override") or os.getenv("GEMINI_API_KEY")
    generator = GeminiLegalGenerator(api_key=active_key)
    res = generator.generate_legal_document(
        document_type=doc_type,
        parties=parties,
        dates=dates,
        terms=terms,
        additional_instructions=additional_inst,
        branding=branding
    )
    return {
        "success": True,
        "document_type": doc_type,
        "title": res.get("title", doc_type.upper()),
        "content": res.get("content", ""),
        "summary_table": res.get("summary_table", {}),
        "model_used": res.get("model_used", "LegalEase Intelligent Engine"),
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "disclaimer": res.get("disclaimer", GeminiLegalGenerator.get_disclaimer())
    }


# =============================================================================
# PAGE 1: LANDING PAGE
# =============================================================================
if st.session_state["current_page"] == "Home":
    # Hero Section
    st.markdown("""
    <div class="hero-card">
        <span class="hero-badge">AI-POWERED CONTRACT INTELLIGENCE</span>
        <h1 class="hero-title">Create Professional Legal Documents with AI</h1>
        <p class="hero-subtitle">
            Generate customizable, editable, and professionally formatted legal contracts in minutes.
            Powered by Google Gemini AI with high-precision clauses, custom branding, and instant DOCX/PDF export.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Hero Action Buttons
    col_btn1, col_btn2, col_btn_empty = st.columns([1.6, 1.6, 4])
    with col_btn1:
        if st.button("🚀 Create Document", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "Create Document"
            st.rerun()
    with col_btn2:
        if st.button("📚 Explore Templates", use_container_width=True):
            st.session_state["current_page"] = "Templates"
            st.rerun()

    st.markdown("<div style='margin-bottom: 2.5rem;'></div>", unsafe_allow_html=True)

    # Trust & Standards Banner
    st.markdown("""
    <div class="trust-banner">
        🛡️ <strong>Bank-Grade Legal Drafting:</strong> All templates adhere to standard commercial contract law standards.
        Features rigorous clause structures, indemnification warranties, confidentiality provisions, and dual signature blocks.
    </div>
    """, unsafe_allow_html=True)

    # Key Value Props
    st.markdown("### Why Choose LegalEase?")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Instant Generation</div>
            <div class="feature-desc">Generate complete 8-12 section commercial contracts in under 5 seconds with zero boilerplate hassle.</div>
        </div>
        """, unsafe_allow_html=True)

    with f_col2:
        f_title = "Tailored Precision"
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">⚖️</div>
            <div class="feature-title">{f_title}</div>
            <div class="feature-desc">Dynamic forms adapt automatically to employment contracts, NDAs, leases, and freelance agreements.</div>
        </div>
        """, unsafe_allow_html=True)

    with f_col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📑</div>
            <div class="feature-title">Multi-Format Export</div>
            <div class="feature-desc">Export instantly to clean TXT, corporate Word DOCX, and publication-ready PDF with running headers and page numbers.</div>
        </div>
        """, unsafe_allow_html=True)

    with f_col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <div class="feature-title">Custom Branding</div>
            <div class="feature-desc">Upload your organization logo, select your preferred typography, and personalize running headers and footers.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 3rem;'></div>", unsafe_allow_html=True)

    # Document Types Overview Section
    st.markdown("### Supported Legal Documents")
    dt1, dt2, dt3 = st.columns(3)
    with dt1:
        st.markdown("""
        **1. Employment Contract**  
        Full-time/part-time employment agreements with compensation, benefits, IP assignment, and termination clauses.
        
        **2. Non-Disclosure Agreement (NDA)**  
        Unilateral or mutual confidentiality agreements covering proprietary data, trade secrets, and non-circumvention.
        """)
    with dt2:
        st.markdown("""
        **3. Residential Lease Agreement**  
        Complete tenancy agreements detailing monthly rent, security deposits, maintenance responsibilities, and pet rules.
        
        **4. Freelance Agreement**  
        Milestone-based independent contractor contracts with IP transfer, deliverable specifications, and warranties.
        """)
    with dt3:
        st.markdown("""
        **5. Service Agreement**  
        Comprehensive B2B master service agreements (MSA) with SLAs, liability caps, and termination rights.
        
        **6. Custom Legal Document**  
        Draft bespoke agreements with arbitrary clauses, commercial covenants, and unique legal instructions.
        """)

# =============================================================================
# PAGE 2: CREATE DOCUMENT
# =============================================================================
elif st.session_state["current_page"] == "Create Document":
    st.markdown("## 📝 Create Your Legal Document")
    st.markdown("Select an agreement type below, review or customize the parameters, and click **Generate Document**.")

    # 1. Document-Type Cards
    doc_options = [
        ("Employment Contract", "💼", "Full-time / part-time employment with salary, roles & IP terms."),
        ("Non-Disclosure Agreement", "🔒", "Protect proprietary data, trade secrets & business discussions."),
        ("Residential Lease Agreement", "🏠", "Residential tenancy terms, rent, security deposit & property rules."),
        ("Freelance Agreement", "💻", "Independent contractor agreements with project milestones & IP assignment."),
        ("Service Agreement", "🤝", "Professional B2B service contracts, scope of work & SLAs."),
        ("Custom Legal Document", "📜", "Create tailored commercial agreements with custom covenants.")
    ]

    st.markdown("#### Step 1: Select Document Type")
    card_cols = st.columns(3)
    for idx, (doc_name, icon, desc) in enumerate(doc_options):
        col = card_cols[idx % 3]
        is_selected = (st.session_state["selected_doc_type"] == doc_name)
        border_color = "#2563EB" if is_selected else "#E2E8F0"
        bg_color = "#EFF6FF" if is_selected else "#FFFFFF"

        with col:
            st.markdown(f"""
            <div style="background:{bg_color}; border:2px solid {border_color}; border-radius:14px; padding:1.15rem; margin-bottom:0.75rem; box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                <div style="font-size:1.6rem; margin-bottom:0.4rem;">{icon}</div>
                <div style="font-weight:700; font-size:1.05rem; color:#0F172A; margin-bottom:0.25rem;">{doc_name}</div>
                <div style="font-size:0.83rem; color:#64748B; line-height:1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select {doc_name}", key=f"btn_select_{idx}", use_container_width=True):
                st.session_state["selected_doc_type"] = doc_name
                st.rerun()

    selected_doc = st.session_state["selected_doc_type"]
    st.markdown(f"**Active Selection:** `{selected_doc}`")
    st.markdown("---")

    # Sample Test Quick-Loader
    sample_col1, sample_col2 = st.columns([2.5, 3.5])
    with sample_col1:
        if st.button("⚡ Load Sample Test Data (Employment Contract)", help="Pre-fills official test data for quick evaluation"):
            st.session_state["selected_doc_type"] = "Employment Contract"
            st.session_state["active_sample_loaded"] = True
            st.rerun()
    with sample_col2:
        if st.session_state.get("active_sample_loaded"):
            st.success("Sample data loaded: TechNova Solutions / Rahul Kumar (Software Developer, ₹6,00,000/yr, Chennai)!")

    # 2. Dynamic Input Forms
    st.markdown(f"#### Step 2: Enter Details for {selected_doc}")
    
    with st.form("contract_form"):
        # Common Document Title
        doc_title = st.text_input(
            "Document Title",
            value=f"{selected_doc.upper()}",
            help="Formal title displayed at the top of the contract"
        )

        parties_data = {}
        dates_data = {}
        terms_data = {}

        # -------------------------------------------------------------
        # A. EMPLOYMENT CONTRACT FORM
        # -------------------------------------------------------------
        if selected_doc == "Employment Contract":
            is_sample = st.session_state.get("active_sample_loaded", False)

            c1, c2 = st.columns(2)
            with c1:
                parties_data["employer_name"] = st.text_input("Employer / Company Name*", value="TechNova Solutions" if is_sample else "")
                parties_data["employer_address"] = st.text_input("Employer Address", value="Tech Park, Taramani, Chennai, Tamil Nadu, India" if is_sample else "")
                parties_data["employer_email"] = st.text_input("Employer Contact Email", value="hr@technova.com" if is_sample else "")
                parties_data["work_location"] = st.text_input("Work Location / Jurisdiction*", value="Chennai, India" if is_sample else "")
            with c2:
                parties_data["employee_name"] = st.text_input("Employee Name*", value="Rahul Kumar" if is_sample else "")
                parties_data["employee_address"] = st.text_input("Employee Address", value="No. 45, Gandhi Nagar, Chennai, Tamil Nadu, India" if is_sample else "")
                parties_data["employee_email"] = st.text_input("Employee Email", value="rahul.kumar@example.com" if is_sample else "")
                parties_data["phone"] = st.text_input("Employee Phone Number", value="+91 98765 43210" if is_sample else "")

            st.markdown("##### Job & Compensation Details")
            c3, c4 = st.columns(2)
            with c3:
                terms_data["job_title"] = st.text_input("Job Title*", value="Software Developer" if is_sample else "")
                terms_data["salary"] = st.text_input("Annual Remuneration / Salary*", value="₹6,00,000 per year" if is_sample else "")
                terms_data["payment_frequency"] = st.selectbox("Payment Frequency", ["Monthly on the last working day", "Bi-weekly", "Weekly"])
                terms_data["working_hours"] = st.text_input("Working Hours", value="40 hours per week (Mon - Fri, 9:00 AM - 6:00 PM)")
            with c4:
                dates_data["start_date"] = st.text_input("Commencement / Start Date*", value="01/10/2026" if is_sample else date.today().strftime("%d/%m/%Y"))
                terms_data["job_responsibilities"] = st.text_area(
                    "Job Responsibilities",
                    value="Software design, architecture, feature development, bug fixes, automated testing, code reviews, and technical documentation." if is_sample else "General software development and technical duties assigned by engineering management.",
                    height=95
                )

            st.markdown("##### Governance & Terms")
            c5, c6 = st.columns(2)
            with c5:
                terms_data["benefits"] = st.text_area("Benefits Package", value="Comprehensive medical insurance coverage, 18 days paid annual leave, public holidays, and professional development allowance.", height=80)
                terms_data["confidentiality"] = st.text_area("Confidentiality Requirements", value="Strict protection of proprietary algorithms, technical codebases, customer information, and trade secrets during and after employment.", height=80)
            with c6:
                terms_data["termination_conditions"] = st.text_area("Termination Conditions", value="Thirty (30) days written notice by either party or compensation in lieu thereof; immediate termination for cause or gross misconduct.", height=80)
                add_clauses = st.text_area("Additional Terms / Special Covenants", value="Non-compete clause valid for 6 months post-employment within the domestic territory.", height=80)

        # -------------------------------------------------------------
        # B. NON-DISCLOSURE AGREEMENT (NDA) FORM
        # -------------------------------------------------------------
        elif selected_doc == "Non-Disclosure Agreement":
            c1, c2 = st.columns(2)
            with c1:
                parties_data["disclosing_party"] = st.text_input("Disclosing Party Name*", value="TechNova Innovations Ltd.")
                parties_data["disclosing_address"] = st.text_input("Disclosing Party Address", value="100 Innovation Way, Cyber City")
                parties_data["disclosing_email"] = st.text_input("Disclosing Party Email", value="legal@technova.com")
            with c2:
                parties_data["receiving_party"] = st.text_input("Receiving Party Name*", value="Vertex Analytics Inc.")
                parties_data["receiving_address"] = st.text_input("Receiving Party Address", value="500 Venture Boulevard, Suite 300")
                parties_data["receiving_email"] = st.text_input("Receiving Party Email", value="contact@vertexanalytics.com")

            c3, c4 = st.columns(2)
            with c3:
                dates_data["effective_date"] = st.text_input("Effective Date*", value=date.today().strftime("%d/%m/%Y"))
                dates_data["duration"] = st.text_input("Confidentiality Duration*", value="Two (2) years from the Effective Date")
                terms_data["purpose"] = st.text_input("Authorized Purpose*", value="Evaluating a strategic commercial partnership and technical integration.")
            with c4:
                terms_data["confidential_info"] = st.text_area(
                    "Scope of Confidential Information",
                    value="All non-public proprietary information including source code, customer records, technical specifications, financial forecasts, and trade secrets.",
                    height=100
                )
                terms_data["exceptions"] = st.text_input("Exceptions to Confidentiality", value="Information publicly known, already possessed without restriction, or independently developed.")
            add_clauses = st.text_area("Additional Terms & Injunction Clauses", value="Injunctive relief permitted without posting a bond in case of unauthorized disclosure.", height=70)

        # -------------------------------------------------------------
        # C. RESIDENTIAL LEASE AGREEMENT FORM
        # -------------------------------------------------------------
        elif selected_doc == "Residential Lease Agreement":
            c1, c2 = st.columns(2)
            with c1:
                parties_data["landlord_name"] = st.text_input("Landlord / Property Owner*", value="Suresh Ramanathan")
                parties_data["landlord_address"] = st.text_input("Landlord Address", value="No. 12, Green Park Avenue, Chennai")
                parties_data["landlord_email"] = st.text_input("Landlord Contact Email", value="suresh.r@example.com")
                parties_data["property_address"] = st.text_input("Leased Property Address*", value="Flat 4B, Emerald Heights, OMR Road, Chennai - 600096")
            with c2:
                parties_data["tenant_name"] = st.text_input("Tenant Name*", value="Ananya Sharma")
                parties_data["tenant_address"] = st.text_input("Tenant Current Address", value="Flat 2A, Rosewood Apartments, Bangalore")
                parties_data["tenant_email"] = st.text_input("Tenant Email", value="ananya.sharma@example.com")
                parties_data["tenant_phone"] = st.text_input("Tenant Phone", value="+91 98401 23456")

            c3, c4 = st.columns(2)
            with c3:
                terms_data["monthly_rent"] = st.text_input("Monthly Rent Amount*", value="₹35,000 per month")
                terms_data["security_deposit"] = st.text_input("Security Deposit (Refundable)*", value="₹1,00,000")
                dates_data["start_date"] = st.text_input("Lease Start Date*", value="01/11/2026")
                dates_data["end_date"] = st.text_input("Lease End Date*", value="31/10/2027")
            with c4:
                terms_data["utilities"] = st.text_area("Utilities Responsibility", value="Tenant pays electricity, cooking gas, and internet; Landlord covers water and society maintenance charges.", height=75)
                terms_data["maintenance_responsibilities"] = st.text_area("Maintenance Obligations", value="Tenant shall maintain fixtures and minor repairs under ₹1,000; Landlord handles structural and plumbing repairs.", height=75)
                terms_data["pet_policy"] = st.text_input("Pet Policy", value="One domestic cat or dog allowed subject to ₹10,000 refundable pet deposit.")
            add_clauses = st.text_area("Additional Terms & Lock-in Period", value="6 months lock-in period. 1 month advance notice required for vacation.", height=70)

        # -------------------------------------------------------------
        # D. FREELANCE / SERVICE / CUSTOM FORM
        # -------------------------------------------------------------
        else:
            c1, c2 = st.columns(2)
            with c1:
                parties_data["party1_name"] = st.text_input("Client / First Party Name*", value="Apex Media Corp")
                parties_data["address"] = st.text_input("Client Address", value="12 Enterprise Plaza, Level 4")
                parties_data["email"] = st.text_input("Client Email", value="billing@apexmedia.com")
            with c2:
                parties_data["party2_name"] = st.text_input("Contractor / Second Party Name*", value="DevStudio Solutions")
                parties_data["second_address"] = st.text_input("Contractor Address", value="78 Digital Hub, Suite 10")
                parties_data["contractor_email"] = st.text_input("Contractor Email", value="contact@devstudio.io")

            c3, c4 = st.columns(2)
            with c3:
                terms_data["services"] = st.text_area("Scope of Services / Deliverables*", value="Design, frontend development, and API integration for the e-commerce mobile web application.", height=85)
                terms_data["compensation"] = st.text_input("Remuneration / Fee Structure*", value="₹2,50,000 payable upon milestone completion")
            with c4:
                dates_data["effective_date"] = st.text_input("Effective Date*", value=date.today().strftime("%d/%m/%Y"))
                dates_data["duration"] = st.text_input("Target Completion Date / Term", value="Three (3) months from execution")
                terms_data["ip_ownership"] = st.text_input("Intellectual Property", value="Full assignment of all IP and work product to Client upon payment.")

            add_clauses = st.text_area("Special Instructions / Additional Clauses", value="Contractor provides 30 days of complimentary bug-fixing support after deployment.", height=70)

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        generate_clicked = st.form_submit_button("⚡ Generate Legal Document", type="primary", use_container_width=True)

    # 3. Document Generation Logic
    if generate_clicked:
        # Validate essential names
        p1 = parties_data.get("employer_name") or parties_data.get("disclosing_party") or parties_data.get("landlord_name") or parties_data.get("party1_name")
        p2 = parties_data.get("employee_name") or parties_data.get("receiving_party") or parties_data.get("tenant_name") or parties_data.get("party2_name")

        if not p1 or not p2:
            st.error("Please fill in both party names before generating the document.")
        else:
            with st.spinner("⚖️ LegalEase AI is drafting your professional agreement with verified clauses..."):
                result = trigger_generation(
                    doc_type=selected_doc,
                    parties=parties_data,
                    dates=dates_data,
                    terms=terms_data,
                    additional_inst=add_clauses,
                    branding=branding_config
                )
                if result and result.get("success"):
                    st.session_state["generated_doc"] = result
                    st.session_state["edited_content"] = result.get("content", "")
                    st.success("✅ Document generated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to generate document. Please check input parameters or backend connectivity.")

    # 4. Document Preview & Term Table Section
    if st.session_state.get("generated_doc"):
        doc_result = st.session_state["generated_doc"]
        st.markdown("---")
        st.markdown("### 📋 Document Review & Customization")

        # Engine Badge
        engine_used = doc_result.get("model_used", "LegalEase AI")
        st.caption(f"Drafted via: **{engine_used}** | Timestamp: `{doc_result.get('generated_at', '')}`")

        # Automatic Term Table (Requirement 10)
        summary = doc_result.get("summary_table", {})
        if summary:
            st.markdown("#### 🔍 Summary of Key Contract Terms")
            # Render structured HTML table
            table_html = "<table class='term-table'><thead><tr><th>Term / Covenant</th><th>Agreed Specifications</th></tr></thead><tbody>"
            for k, v in summary.items():
                table_html += f"<tr><td style='font-weight:600;'>{k}</td><td>{v}</td></tr>"
            table_html += "</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)

        # Tabbed Preview: Formatted Markdown View vs Editable Text Editor
        tab_preview, tab_editor = st.tabs(["👁️ Formatted Preview", "✏️ Live Document Editor"])

        with tab_preview:
            st.markdown(
                f"<div style='background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:2rem 2.5rem; box-shadow:0 4px 12px rgba(0,0,0,0.04);'>"
                f"{st.session_state['edited_content']}"
                f"</div>",
                unsafe_allow_html=True
            )

        with tab_editor:
            st.info("💡 You can freely edit any clause below. Your edits will be saved and exported to TXT, DOCX, and PDF.")
            updated_text = st.text_area(
                "Contract Text Editor",
                value=st.session_state["edited_content"],
                height=480,
                key="doc_editor_textarea"
            )
            if updated_text != st.session_state["edited_content"]:
                st.session_state["edited_content"] = updated_text

        # Regenerate Section
        with st.expander("🔄 Need to modify? Regenerate with AI instructions", expanded=False):
            re_instructions = st.text_input("Specific modifications (e.g., 'Increase probation period to 6 months', 'Add IP confidentiality clause')")
            if st.button("Regenerate Document"):
                with st.spinner("Re-drafting document with updated instructions..."):
                    reg_result = trigger_generation(
                        doc_type=selected_doc,
                        parties=parties_data,
                        dates=dates_data,
                        terms=terms_data,
                        additional_inst=f"{add_clauses}\nModification Request: {re_instructions}",
                        branding=branding_config
                    )
                    if reg_result and reg_result.get("success"):
                        st.session_state["generated_doc"] = reg_result
                        st.session_state["edited_content"] = reg_result.get("content", "")
                        st.success("Document updated successfully!")
                        st.rerun()

        # Export System (Requirement 8)
        st.markdown("#### 📥 Export & Download")
        st.write("Download your finalized agreement in your preferred corporate format:")

        clean_filename = f"{selected_doc.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        doc_final_title = doc_result.get("title", selected_doc.upper())
        final_content = st.session_state["edited_content"]

        exp_col1, exp_col2, exp_col3 = st.columns(3)

        # 1. TXT Export
        with exp_col1:
            txt_bytes = generate_txt(
                title=doc_final_title,
                content=final_content,
                summary_table=summary,
                branding=branding_config
            )
            st.download_button(
                label="📄 Download TXT",
                data=txt_bytes,
                file_name=f"{clean_filename}.txt",
                mime="text/plain",
                use_container_width=True
            )

        # 2. DOCX Export
        with exp_col2:
            docx_bytes = generate_docx(
                title=doc_final_title,
                content=final_content,
                summary_table=summary,
                branding=branding_config
            )
            st.download_button(
                label="📘 Download DOCX (Word)",
                data=docx_bytes,
                file_name=f"{clean_filename}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        # 3. PDF Export
        with exp_col3:
            pdf_bytes = generate_pdf(
                title=doc_final_title,
                content=final_content,
                summary_table=summary,
                branding=branding_config
            )
            st.download_button(
                label="📕 Download PDF",
                data=pdf_bytes,
                file_name=f"{clean_filename}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # Mandatory LegalTech Disclaimer (Requirement 11)
    st.markdown("""
    <div class="disclaimer-box">
        <strong>⚖️ Legal Disclaimer:</strong> LegalEase generates AI-assisted legal documents for informational and drafting purposes.
        Users should review documents with a qualified legal professional when appropriate. LegalEase does not provide legal advice.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGE 3: TEMPLATES LIBRARY
# =============================================================================
elif st.session_state["current_page"] == "Templates":
    st.markdown("## 📚 LegalEase Template Library")
    st.markdown("Browse our curated, lawyer-approved contract templates. Click **Use Template** to customize and generate.")

    templates = [
        {
            "name": "Employment Contract",
            "category": "Corporate & HR",
            "icon": "💼",
            "desc": "Standard corporate employment agreement covering role specifications, remuneration, medical benefits, restrictive covenants, and termination policies.",
            "target": "Employment Contract"
        },
        {
            "name": "Mutual Non-Disclosure Agreement (NDA)",
            "category": "Intellectual Property",
            "icon": "🔒",
            "desc": "Two-way confidentiality contract safeguarding proprietary technical architecture, business financials, algorithms, and strategic discussions.",
            "target": "Non-Disclosure Agreement"
        },
        {
            "name": "Residential Lease Agreement",
            "category": "Real Estate",
            "icon": "🏠",
            "desc": "Thorough residential tenancy agreement defining monthly rental amounts, security deposit escrow, utility allocations, and pet covenants.",
            "target": "Residential Lease Agreement"
        },
        {
            "name": "Freelance Services Contract",
            "category": "Independent Contractor",
            "icon": "💻",
            "desc": "Milestone-driven contractor agreement protecting intellectual property transfer, milestone deliverables, and non-solicitation.",
            "target": "Freelance Agreement"
        },
        {
            "name": "Master Service Agreement (MSA)",
            "category": "Commercial B2B",
            "icon": "🤝",
            "desc": "Comprehensive B2B service agreement specifying service level standards (SLA), invoicing timelines, and liability limitations.",
            "target": "Service Agreement"
        },
        {
            "name": "Custom Legal Document",
            "category": "General Drafting",
            "icon": "📜",
            "desc": "Flexible drafting canvas enabling prompt-driven legal agreements tailored to your specific commercial requirements.",
            "target": "Custom Legal Document"
        }
    ]

    t_col1, t_col2 = st.columns(2)
    for idx, t in enumerate(templates):
        target_col = t_col1 if idx % 2 == 0 else t_col2
        with target_col:
            st.markdown(f"""
            <div class="feature-card" style="margin-bottom:1.25rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                    <span style="font-size:1.75rem;">{t['icon']}</span>
                    <span style="background:#E2E8F0; color:#334155; font-size:0.75rem; font-weight:700; padding:0.25rem 0.6rem; border-radius:999px;">
                        {t['category']}
                    </span>
                </div>
                <div class="feature-title">{t['name']}</div>
                <div class="feature-desc" style="margin-bottom:1rem;">{t['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Use {t['name']}", key=f"use_t_{idx}", use_container_width=True):
                st.session_state["selected_doc_type"] = t["target"]
                st.session_state["current_page"] = "Create Document"
                st.rerun()


# =============================================================================
# PAGE 4: ABOUT
# =============================================================================
elif st.session_state["current_page"] == "About":
    st.markdown("## 🏛️ About LegalEase")
    st.markdown("""
    **LegalEase** is an enterprise-grade legal document generation platform designed to eliminate the friction,
    high legal costs, and tedious drafting hours associated with routine commercial contracts.
    
    ### 🎯 Our Mission
    To empower founders, business owners, landlords, freelancers, and legal counsels with instant,
    lawyer-crafted legal documentation that strictly honors user inputs, never hallucinates facts,
    and exports seamlessly to clean Word (.docx) and PDF documents.

    ### 🛠️ Architecture & Tech Stack
    - **Frontend:** Streamlit with customized SaaS styling and responsive cards
    - **Backend:** FastAPI with Pydantic contract validation and asynchronous request handling
    - **AI Core:** Google Gemini AI models (`gemini-1.5-flash`) with structured prompts & zero meta-commentary
    - **Document Engines:** `python-docx` for Word formatting, `fpdf2` for publication PDFs, and custom UTF-8 text writers
    - **Security:** Environment variable management via `python-dotenv`, filename sanitization, and no client-side API key leakage.
    """)

    st.markdown("""
    <div class="trust-banner">
        🔒 <strong>Data Privacy Guarantee:</strong> LegalEase does not store your private contract data or party details on remote servers.
        Generated files remain local to your session.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGE 5: HELP & FAQ
# =============================================================================
elif st.session_state["current_page"] == "Help":
    st.markdown("## ❓ Help & Frequently Asked Questions")

    with st.expander("How do I connect my Google Gemini API Key?", expanded=True):
        st.markdown("""
        1. Obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
        2. Open the `.env` file in the project directory and set:
           ```bash
           GEMINI_API_KEY=your_actual_key_here
           ```
        3. Alternatively, expand the **🔑 Gemini API Settings** in the left sidebar and paste your key directly for the active session.
        """)

    with st.expander("Can I edit the generated document before downloading?", expanded=False):
        st.markdown("""
        **Yes!** After generating the document, click on the **✏️ Live Document Editor** tab.
        You can modify clauses, change names, or add additional terms. Any edits you make in the text editor
        will be instantly included when you click **Download TXT**, **Download DOCX**, or **Download PDF**.
        """)

    with st.expander("How do I run both FastAPI backend and Streamlit frontend?", expanded=False):
        st.markdown("""
        **Terminal 1 (Backend):**
        ```bash
        uvicorn main:app --reload --port 8000
        ```
        **Terminal 2 (Frontend):**
        ```bash
        streamlit run streamlit_app.py
        ```
        The Streamlit application automatically connects to `http://127.0.0.1:8000`. If the backend is offline,
        LegalEase smoothly operates using its built-in engine.
        """)

    with st.expander("Is LegalEase a replacement for legal counsel?", expanded=False):
        st.markdown("""
        LegalEase generates AI-assisted legal documents for drafting and informational purposes.
        While templates follow standard commercial contract conventions, you should review sensitive agreements
        with qualified legal counsel in your respective jurisdiction.
        """)
