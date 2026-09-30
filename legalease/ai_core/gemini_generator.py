"""
LegalEase AI Core - Gemini Document Generator
Generates corporate-grade legal agreements using Google's Gemini models
with bulletproof error handling, intelligent fallback, and automatic term extraction.
"""
import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GeminiLegalGenerator:
    """
    AI-powered legal document generation engine utilizing Google Gemini.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the generator with an optional API key or retrieve from environment.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        # Clean dummy placeholder values
        if self.api_key in ["your_api_key_here", "your_gemini_api_key_here", ""]:
            self.api_key = None

        self._client_initialized = False
        self._model = None
        self._init_error = None

        if self.api_key:
            self._setup_gemini()

    def is_configured(self) -> bool:
        """Check if a valid Gemini API key is present."""
        return bool(self.api_key and self._client_initialized)

    def _setup_gemini(self):
        """Configure Google Generative AI client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            # Select appropriate model: gemini-2.5-flash / gemini-1.5-flash / gemini-pro
            available_models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
            selected_model = "gemini-1.5-flash"
            
            self._model = genai.GenerativeModel(
                model_name=selected_model,
                generation_config={
                    "temperature": 0.2, # Low temperature for legal rigor and consistency
                    "top_p": 0.95,
                    "max_output_tokens": 4096,
                }
            )
            self._client_initialized = True
            self._init_error = None
        except Exception as e:
            self._client_initialized = False
            self._init_error = str(e)

    def generate_legal_document(
        self,
        document_type: str,
        parties: Dict[str, Any],
        dates: Dict[str, Any],
        terms: Dict[str, Any],
        additional_instructions: Optional[str] = None,
        branding: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete legal document and summary table.
        
        Returns:
            dict containing:
                - title: Formal document title
                - content: Clean markdown/text legal contract
                - summary_table: Dictionary of key transaction terms
                - model_used: Name of model or generator
                - disclaimer: Mandatory legal notice
        """
        summary_table = self._build_summary_table(document_type, parties, dates, terms)
        
        # If Gemini is configured, invoke the AI model
        if self.is_configured() and self._model:
            try:
                ai_doc = self._generate_with_gemini(
                    document_type=document_type,
                    parties=parties,
                    dates=dates,
                    terms=terms,
                    additional_instructions=additional_instructions
                )
                return {
                    "success": True,
                    "title": ai_doc.get("title", f"{document_type.upper()}"),
                    "content": ai_doc.get("content", ""),
                    "summary_table": summary_table,
                    "model_used": "Google Gemini AI (gemini-1.5-flash)",
                    "disclaimer": self.get_disclaimer()
                }
            except Exception as e:
                # If Gemini API encounters rate limit, network error, or quota, gracefully fallback
                fallback_doc = self._generate_rule_based_fallback(
                    document_type=document_type,
                    parties=parties,
                    dates=dates,
                    terms=terms,
                    additional_instructions=additional_instructions
                )
                fallback_doc["summary_table"] = summary_table
                fallback_doc["model_used"] = f"LegalEase Intelligent Engine (Gemini Notice: {str(e)[:90]})"
                fallback_doc["disclaimer"] = self.get_disclaimer()
                return fallback_doc

        # If Gemini is not configured, use the intelligent legal template generator
        fallback_doc = self._generate_rule_based_fallback(
            document_type=document_type,
            parties=parties,
            dates=dates,
            terms=terms,
            additional_instructions=additional_instructions
        )
        fallback_doc["summary_table"] = summary_table
        fallback_doc["model_used"] = "LegalEase Built-in Legal Engine (Add Gemini API key in .env for custom AI generation)"
        fallback_doc["disclaimer"] = self.get_disclaimer()
        return fallback_doc

    def _generate_with_gemini(
        self,
        document_type: str,
        parties: Dict[str, Any],
        dates: Dict[str, Any],
        terms: Dict[str, Any],
        additional_instructions: Optional[str]
    ) -> Dict[str, str]:
        """Send rigorous legal drafting prompt to Gemini."""
        prompt = f"""
You are a senior legal counsel specializing in commercial contracts, corporate law, and employment law.
Draft a complete, legally robust, highly professional "{document_type}".

=== INSTRUCTIONS & CONSTRAINTS ===
1. Professional legal formatting with clear section numbers and headings (e.g., SECTION 1: DEFINITIONS, SECTION 2: SCOPE...).
2. ACCURACY: Strictly utilize the supplied party names, addresses, dates, compensation, and covenants. NEVER invent false facts or assume unstated names.
3. If essential information is missing, mark it cleanly as [TO BE INSERTED: Specific item].
4. Output format: Clean, structured markdown text.
   - Use # for Document Title
   - Use ## for Main Sections (e.g. ## SECTION 1: APPOINTMENT AND TERM)
   - Use ### for Subsections
   - Use * for itemized covenants
   - Conclude with a complete signature section:
     IN WITNESS WHEREOF, the Parties hereto have executed this Agreement as of the Effective Date.
5. Tone: Formal, unambiguous, binding, neutral, and compliant with modern contract standards.
6. DO NOT write meta-commentary, introductory remarks ("Here is your contract:"), or closing explanations. Begin directly with the Document Title.

=== CONTRACT PARAMETERS ===
Document Type: {document_type}

Parties Information:
{self._format_dict(parties)}

Dates & Duration:
{self._format_dict(dates)}

Terms, Compensation & Obligations:
{self._format_dict(terms)}

Additional Clauses / Special Instructions:
{additional_instructions or "Standard commercially reasonable terms applicable to this jurisdiction."}
"""
        response = self._model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Clean potential markdown fences
        cleaned = re.sub(r'^```(markdown)?\n', '', raw_text)
        cleaned = re.sub(r'\n```$', '', cleaned).strip()

        # Extract title from the first heading or construct one
        title_match = re.search(r'^#\s+(.+)$', cleaned, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Remove title line from body content if desired, or keep as top heading
        else:
            title = document_type.upper()

        return {
            "title": title,
            "content": cleaned
        }

    def _build_summary_table(
        self,
        document_type: str,
        parties: Dict[str, Any],
        dates: Dict[str, Any],
        terms: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate a structured summary table of key commercial terms."""
        summary = {
            "Document Type": document_type,
            "Party 1 (Primary)": parties.get("party1_name") or parties.get("employer_name") or parties.get("disclosing_party") or parties.get("landlord_name") or "Party 1",
            "Party 2 (Secondary)": parties.get("party2_name") or parties.get("employee_name") or parties.get("receiving_party") or parties.get("tenant_name") or "Party 2",
            "Effective Date": dates.get("effective_date") or dates.get("start_date") or "Upon Execution",
        }

        # Add duration/expiration
        if dates.get("expiration_date"):
            summary["Expiration Date"] = str(dates["expiration_date"])
        elif dates.get("duration"):
            summary["Term Duration"] = str(dates["duration"])

        # Add financial terms
        if terms.get("salary"):
            summary["Compensation / Salary"] = str(terms["salary"])
        elif terms.get("monthly_rent"):
            summary["Monthly Rent"] = str(terms["monthly_rent"])
        elif terms.get("compensation"):
            summary["Contract Fee"] = str(terms["compensation"])

        if terms.get("security_deposit"):
            summary["Security Deposit"] = str(terms["security_deposit"])

        # Add role or purpose
        if terms.get("job_title"):
            summary["Position / Job Title"] = str(terms["job_title"])
        elif terms.get("purpose"):
            summary["Purpose / Scope"] = str(terms["purpose"])
        elif terms.get("services"):
            summary["Scope of Services"] = str(terms["services"])[:60]

        # Location or property
        if parties.get("work_location"):
            summary["Jurisdiction / Location"] = str(parties["work_location"])
        elif parties.get("property_address"):
            summary["Premises Address"] = str(parties["property_address"])

        return summary

    def _generate_rule_based_fallback(
        self,
        document_type: str,
        parties: Dict[str, Any],
        dates: Dict[str, Any],
        terms: Dict[str, Any],
        additional_instructions: Optional[str]
    ) -> Dict[str, Any]:
        """
        Production-grade built-in legal drafting engine.
        Ensures users get complete, fully-formatted legal contracts even if offline
        or when testing prior to entering their personal Gemini API key.
        """
        doc_type_lower = document_type.lower()
        effective_date = dates.get("effective_date") or dates.get("start_date") or "October 1, 2026"
        
        # 1. EMPLOYMENT CONTRACT
        if "employment" in doc_type_lower:
            employer = parties.get("employer_name") or parties.get("party1_name") or "TechNova Solutions"
            employer_addr = parties.get("employer_address") or parties.get("address") or "Tech Park, Taramani, Chennai, Tamil Nadu, India"
            employee = parties.get("employee_name") or parties.get("party2_name") or "Rahul Kumar"
            employee_addr = parties.get("employee_address") or "No. 45, Gandhi Nagar, Chennai, Tamil Nadu, India"
            job_title = terms.get("job_title", "Software Developer")
            responsibilities = terms.get("job_responsibilities", "Software design, architecture, feature development, bug fixes, automated testing, code reviews, and technical documentation.")
            salary = terms.get("salary", "INR 6,00,000 per annum")
            pay_freq = terms.get("payment_frequency", "Monthly on or before the last working day of each calendar month")
            hours = terms.get("working_hours", "40 hours per week, Monday through Friday, standard business hours")
            location = parties.get("work_location", "Chennai, India")
            benefits = terms.get("benefits", "Comprehensive group medical insurance, paid annual leave (18 days), public holidays, and professional development allowance.")
            confidentiality = terms.get("confidentiality", "Strict confidentiality during and after the period of employment regarding proprietary algorithms, customer data, and trade secrets.")
            termination = terms.get("termination_conditions", "Thirty (30) days written notice by either party or payment in lieu thereof, subject to immediate termination for cause.")

            content = f"""# EMPLOYMENT AGREEMENT

THIS EMPLOYMENT AGREEMENT (this "Agreement") is entered into and made effective as of **{effective_date}** (the "Effective Date"), by and between:

**EMPLOYER:** **{employer}**, a corporation having its principal office and place of business at {employer_addr} (hereinafter referred to as the "Company", which expression shall include its successors and permitted assigns),

**AND**

**EMPLOYEE:** **{employee}**, residing at {employee_addr} (hereinafter referred to as the "Employee").

The Company and the Employee may collectively be referred to as the "Parties" and individually as a "Party."

---

## RECITALS

WHEREAS, the Company is engaged in business operations requiring specialized technical and operational competence; and
WHEREAS, the Company desires to employ the Employee, and the Employee desires to accept employment with the Company, subject to the terms and conditions hereinafter set forth;

NOW, THEREFORE, in consideration of the mutual covenants herein contained and other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the Parties agree as follows:

## SECTION 1: POSITION AND DUTIES
1.1 **Title & Role**: The Company hereby employs the Employee in the capacity of **{job_title}**.
1.2 **Core Responsibilities**: The Employee agrees to perform with fidelity and due diligence all duties consistent with such position, including without limitation: {responsibilities}.
1.3 **Standard of Performance**: The Employee shall devote full business time, energy, and skill exclusively to the advancement of the Company's business interests.

## SECTION 2: WORK LOCATION AND WORKING HOURS
2.1 **Location**: The Employee's primary place of work shall be at **{location}**, subject to official business travel or remote work arrangements as authorized by Company policy.
2.2 **Hours**: The standard working schedule shall consist of **{hours}**.

## SECTION 3: COMPENSATION AND BENEFITS
3.1 **Base Remuneration**: In consideration of the services rendered, the Company shall pay the Employee a remuneration of **{salary}**, payable in accordance with the Company's standard payroll schedule (**{pay_freq}**), subject to statutory tax deductions.
3.2 **Benefits**: The Employee shall be eligible to participate in Company benefit programs including: {benefits}.

## SECTION 4: CONFIDENTIALITY AND PROPRIETARY INFORMATION
4.1 **Nondisclosure**: The Employee acknowledges that during employment, the Employee will have access to confidential and proprietary information of the Company. {confidentiality}
4.2 **Return of Materials**: Upon termination of employment for any reason, the Employee shall immediately return all documents, electronic media, security tokens, and Company property.

## SECTION 5: INTELLECTUAL PROPERTY RIGHTS
5.1 **Work Made for Hire**: All inventions, software codes, designs, documentation, and improvements created, conceived, or reduced to practice by the Employee during the term of employment shall remain the sole and exclusive property of the Company.

## SECTION 6: TERM AND TERMINATION
6.1 **Term**: This Agreement shall commence on the Effective Date and continue indefinitely until terminated in accordance with this Section.
6.2 **Termination with Notice**: {termination}
6.3 **Termination for Cause**: The Company may terminate employment immediately without notice or severance in the event of gross misconduct, fraud, dishonesty, or criminal conviction.

## SECTION 7: GOVERNING LAW AND DISPUTE RESOLUTION
7.1 **Governing Law**: This Agreement shall be construed and enforced in accordance with the substantive laws applicable in {location}.
7.2 **Jurisdiction**: The courts of competent jurisdiction at {location} shall have exclusive jurisdiction over all disputes arising hereunder.

## SECTION 8: MISCELLANEOUS PROVISIONS
8.1 **Entire Agreement**: This Agreement supersedes all prior representations, communications, and understandings between the Parties regarding employment.
8.2 **Amendments**: No alteration or amendment shall be effective unless in writing and signed by both Parties.
{f"8.3 **Special Conditions**: {additional_instructions}" if additional_instructions else ""}

---

## SIGNATURE PAGE

IN WITNESS WHEREOF, the Parties hereto have duly executed and delivered this Employment Agreement as of the date first above written.

**FOR THE COMPANY:**
Name: Authorized Signatory
Title: Director / HR Head
Signature: _____________________________________
Date: {effective_date}

**FOR THE EMPLOYEE:**
Name: {employee}
Signature: _____________________________________
Date: {effective_date}
"""
            return {"title": "EMPLOYMENT AGREEMENT", "content": content}

        # 2. NON-DISCLOSURE AGREEMENT (NDA)
        elif "nda" in doc_type_lower or "non-disclosure" in doc_type_lower:
            disclosing = parties.get("disclosing_party") or parties.get("party1_name") or "Apex Innovations Inc."
            receiving = parties.get("receiving_party") or parties.get("party2_name") or "Nexus Global LLC"
            disclosing_addr = parties.get("disclosing_address") or parties.get("address") or "100 Enterprise Way, Suite 400"
            receiving_addr = parties.get("receiving_address") or "500 Horizon Boulevard"
            conf_info = terms.get("confidential_info", "Technical data, trade secrets, software architecture, business plans, financials, customer lists, and algorithms.")
            purpose = terms.get("purpose", "Evaluating and negotiating a potential strategic commercial partnership or joint technology venture.")
            duration = dates.get("duration", "Two (2) years from the Effective Date")
            exceptions = terms.get("exceptions", "Information publicly known, already known without obligation, or independently developed without reference to the Disclosing Party's Confidential Information.")

            content = f"""# MUTUAL NON-DISCLOSURE AGREEMENT

THIS NON-DISCLOSURE AGREEMENT (this "Agreement") is made effective as of **{effective_date}** (the "Effective Date"), by and between:

**DISCLOSING PARTY:** **{disclosing}**, with its principal offices at {disclosing_addr},

**AND**

**RECEIVING PARTY:** **{receiving}**, with its principal offices at {receiving_addr}.

---

## RECITALS
WHEREAS, the Parties desire to engage in confidential discussions concerning **{purpose}** (the "Authorized Purpose"); and
WHEREAS, in connection with the Authorized Purpose, each Party may disclose to the other confidential and proprietary technical and business information;

NOW, THEREFORE, the Parties agree as follows:

## SECTION 1: CONFIDENTIAL INFORMATION
1.1 **Definition**: "Confidential Information" shall mean all non-public, sensitive, or proprietary information disclosed by one Party ("Disclosing Party") to the other ("Receiving Party"), whether orally or in writing, including without limitation: {conf_info}.
1.2 **Marking**: Written materials shall be designated as "Confidential" or "Proprietary", though oral or visual disclosures shall be protected if reasonably understood as confidential.

## SECTION 2: EXCLUSIONS FROM CONFIDENTIAL INFORMATION
2.1 **Exceptions**: The obligations of confidentiality shall not apply to information which: {exceptions}.

## SECTION 3: OBLIGATIONS OF RECEIVING PARTY
3.1 **Standard of Care**: The Receiving Party agrees to protect Confidential Information with the same degree of care it exercises for its own confidential assets, but not less than reasonable care.
3.2 **Restricted Use**: The Receiving Party shall utilize Confidential Information solely for the Authorized Purpose and shall not disclose it to any third party without prior written consent.
3.3 **Need-to-Know**: Access shall be restricted strictly to officers, directors, employees, and legal advisors who have a verifiable need to know.

## SECTION 4: TERM AND SURVIVAL
4.1 **Duration**: The duty of confidentiality and non-use established hereunder shall remain in full force and effect for a period of **{duration}**.

## SECTION 5: RETURN OR DESTRUCTION OF INFORMATION
5.1 **Return**: Upon written request or termination of discussions, the Receiving Party shall promptly return or certify the secure destruction of all tangible copies of Confidential Information.

## SECTION 6: INJUNCTIVE RELIEF
6.1 **Remedies**: The Parties recognize that any breach of this Agreement may result in irreparable harm for which monetary damages alone would be inadequate. Accordingly, the Disclosing Party shall be entitled to seek injunctive relief without the necessity of posting a bond.

## SECTION 7: GOVERNING LAW AND JURISDICTION
7.1 **Law**: This Agreement shall be governed by and construed in accordance with standard commercial contract laws.
{f"7.2 **Special Stipulations**: {additional_instructions}" if additional_instructions else ""}

---

## SIGNATURE PAGE

IN WITNESS WHEREOF, the Parties have executed this Non-Disclosure Agreement as of the Effective Date.

**DISCLOSING PARTY: {disclosing}**
By: _____________________________________
Name: Authorized Representative
Date: {effective_date}

**RECEIVING PARTY: {receiving}**
By: _____________________________________
Name: Authorized Representative
Date: {effective_date}
"""
            return {"title": "NON-DISCLOSURE AGREEMENT", "content": content}

        # 3. RESIDENTIAL LEASE AGREEMENT
        elif "lease" in doc_type_lower or "rent" in doc_type_lower:
            landlord = parties.get("landlord_name") or parties.get("party1_name") or "Prime Horizon Realty"
            tenant = parties.get("tenant_name") or parties.get("party2_name") or "David Miller"
            property_addr = parties.get("property_address") or "Apartment 4B, 128 Greenfield Avenue"
            rent = terms.get("monthly_rent", "INR 35,000 / month")
            deposit = terms.get("security_deposit", "INR 70,000 (Refundable)")
            start_date = dates.get("start_date") or effective_date
            end_date = dates.get("end_date") or dates.get("expiration_date") or "September 30, 2027"
            utilities = terms.get("utilities", "Tenant is responsible for electricity, high-speed internet, and cooking gas; Landlord covers water and society maintenance.")
            maintenance = terms.get("maintenance_responsibilities", "Tenant shall maintain the interior in good repair; Landlord shall be responsible for structural and external repairs.")
            pet_policy = terms.get("pet_policy", "Pets permitted only upon prior written approval of the Landlord and payment of a pet deposit.")

            content = f"""# RESIDENTIAL LEASE AGREEMENT

THIS LEASE AGREEMENT (the "Lease") is executed on **{effective_date}**, by and between:

**LANDLORD:** **{landlord}**, having its contact address at {parties.get('landlord_address', 'Landlord Official Address')},

**AND**

**TENANT:** **{tenant}**, having contact details at {parties.get('tenant_address', 'Tenant Contact Address')}.

---

## SECTION 1: LEASED PREMISES
1.1 **Property Description**: The Landlord hereby leases to the Tenant, and the Tenant rents from the Landlord, the residential dwelling situated at **{property_addr}** (the "Premises").

## SECTION 2: TERM
2.1 **Lease Duration**: The term of this Lease shall begin on **{start_date}** and expire on **{end_date}**, unless terminated earlier in accordance with the terms herein.

## SECTION 3: RENT AND SECURITY DEPOSIT
3.1 **Monthly Rent**: The Tenant agrees to pay the Landlord a monthly rent of **{rent}**, payable in advance on or before the 5th day of each calendar month.
3.2 **Security Deposit**: Upon execution, the Tenant shall deposit with the Landlord the sum of **{deposit}**, held as security for faithful performance and returnable within 30 days of vacation less valid damage deductions.

## SECTION 4: UTILITIES AND MAINTENANCE
4.1 **Utilities**: {utilities}
4.2 **Maintenance Obligations**: {maintenance}

## SECTION 5: USE OF PREMISES AND POLICIES
5.1 **Residential Use Only**: The Premises shall be used strictly as a private residential home by the Tenant and immediate family.
5.2 **Pet Policy**: {pet_policy}
5.3 **Quiet Enjoyment**: Tenant shall not cause or permit any nuisance or unreasonable disturbance.

## SECTION 6: INSPECTION AND ACCESS
6.1 **Landlord Access**: Landlord or agents shall have the right to enter the Premises with at least 24 hours prior written notice for inspection or repairs.

## SECTION 7: DEFAULT AND TERMINATION
7.1 **Default**: Non-payment of rent for more than 15 days or breach of covenants shall entitle Landlord to terminate this Lease upon 14 days written notice.
{f"7.2 **Additional Clauses**: {additional_instructions}" if additional_instructions else ""}

---

## SIGNATURE PAGE

IN WITNESS WHEREOF, the Landlord and Tenant have signed this Residential Lease Agreement as of the Effective Date.

**LANDLORD:**
Signature: _____________________________________
Date: {effective_date}

**TENANT:**
Signature: _____________________________________
Date: {effective_date}
"""
            return {"title": "RESIDENTIAL LEASE AGREEMENT", "content": content}

        # 4. FREELANCE / SERVICE AGREEMENT / GENERAL
        else:
            party1 = parties.get("party1_name") or parties.get("client_name") or "Global Ventures Ltd."
            party2 = parties.get("party2_name") or parties.get("contractor_name") or "Creative Solutions Agency"
            title = document_type.upper()
            scope = terms.get("services") or terms.get("scope_of_work") or "Professional consulting and implementation services as agreed in Project SOW."
            fee = terms.get("compensation") or terms.get("fee") or "Milestone-based compensation agreed in Schedule A."

            content = f"""# {title}

THIS AGREEMENT (this "Agreement") is entered into as of **{effective_date}** (the "Effective Date"), by and between:

**FIRST PARTY:** **{party1}**, with offices at {parties.get('address', 'Principal Place of Business')},

**AND**

**SECOND PARTY:** **{party2}**, with offices at {parties.get('second_address', 'Operating Address')}.

---

## SECTION 1: ENGAGEMENT AND SCOPE OF SERVICES
1.1 **Scope of Services**: The Second Party agrees to perform for First Party the following services: {scope}.
1.2 **Deliverables & Milestones**: All deliverables shall conform to professional industry standards and specifications agreed between the Parties.

## SECTION 2: COMPENSATION AND PAYMENT TERMS
2.1 **Fee Structure**: First Party shall compensate Second Party in the amount of **{fee}**.
2.2 **Invoicing**: Invoices shall be payable within thirty (30) days of receipt.

## SECTION 3: INTELLECTUAL PROPERTY OWNERSHIP
3.1 **Ownership**: Upon full payment, all work product, source materials, and deliverables produced under this Agreement shall belong exclusively to First Party.

## SECTION 4: TERM AND TERMINATION
4.1 **Term**: This Agreement shall commence on {effective_date} and continue until completion of services or termination by either Party upon 15 days written notice.

## SECTION 5: CONFIDENTIALITY
5.1 **Duty of Secrecy**: Neither Party shall disclose confidential trade information belonging to the other without express written consent.

## SECTION 6: GOVERNING LAW
6.1 **Jurisdiction**: This Agreement shall be governed by and construed under the laws of the agreed jurisdiction.
{f"6.2 **Special Instructions**: {additional_instructions}" if additional_instructions else ""}

---

## SIGNATURE PAGE

IN WITNESS WHEREOF, the Parties have executed this Agreement as of the Effective Date.

**FIRST PARTY: {party1}**
Signature: _____________________________________
Date: {effective_date}

**SECOND PARTY: {party2}**
Signature: _____________________________________
Date: {effective_date}
"""
            return {"title": title, "content": content}

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Helper to format nested dictionaries into neat bullet points."""
        if not data:
            return "None specified."
        return "\n".join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in data.items() if v])

    @staticmethod
    def get_disclaimer() -> str:
        """Standard mandatory legaltech disclaimer."""
        return (
            "LegalEase generates AI-assisted legal documents for informational and drafting purposes. "
            "Users should review documents with a qualified legal professional when appropriate. "
            "LegalEase does not provide legal advice."
        )
