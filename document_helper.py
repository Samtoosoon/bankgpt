from datetime import datetime
from io import BytesIO
from typing import Any, Dict

from fpdf import FPDF

from utils import compute_emi


def _format_currency(amount: float) -> str:
    return f"Rs. {amount:,.0f}"


def generate_sanction_letter_pdf(
    state: Dict[str, Any],
    interest_rate: float = 12.0,
    tenure_months: int = 60,
) -> bytes:
    """Generate a simple sanction letter PDF based on captured state."""

    name = state.get("customer_name", "Valued Customer")
    phone = state.get("phone", "Not provided")
    loan_amount = state.get("requested_amount") or state.get("pre_approved_limit") or 0
    pre_approved = state.get("pre_approved_limit")
    credit_score = state.get("credit_score", "N/A")

    emi = 0.0
    if loan_amount:
        emi = compute_emi(float(loan_amount), interest_rate, tenure_months)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Loan Sanction Letter", ln=1)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d %b %Y')}", ln=1)
    pdf.cell(0, 8, "From: Tata Capital - Retail Loans Division", ln=1)
    pdf.ln(4)

    pdf.cell(0, 8, f"To: {name}", ln=1)
    pdf.cell(0, 8, f"Phone: {phone}", ln=1)
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Sanction Details", ln=1)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Loan Amount Sanctioned: {_format_currency(loan_amount)}", ln=1)
    pdf.cell(0, 7, f"Tenure: {tenure_months} months", ln=1)
    pdf.cell(0, 7, f"Interest Rate: {interest_rate:.2f}% p.a.", ln=1)

    if emi:
        pdf.cell(0, 7, f"Estimated Monthly EMI: {_format_currency(emi)}", ln=1)
    if credit_score != "N/A":
        pdf.cell(0, 7, f"Credit Score on file: {credit_score}", ln=1)
    if pre_approved:
        pdf.cell(0, 7, f"Pre-approved Limit: {_format_currency(pre_approved)}", ln=1)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Conditions & Next Steps", ln=1)

    pdf.set_font("Helvetica", "", 11)
    bullets = [
        "This sanction is subject to document verification and KYC compliance.",
        "Final disbursement will occur post-signature of the loan agreement.",
        "Prepayment or foreclosure charges, if any, will follow prevailing policy.",
        "Please keep this letter for your records.",
    ]
    for bullet in bullets:
        pdf.multi_cell(0, 6, f"- {bullet}")

    pdf.ln(4)
    pdf.cell(0, 7, "Thank you for choosing Tata Capital.", ln=1)
    pdf.cell(0, 7, "For queries, contact us at support@tatacapital.com", ln=1)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes
