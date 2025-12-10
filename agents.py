import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from fpdf import FPDF

DATA_PATH = Path('data/mock_db.json')


def load_db() -> Dict[str, Any]:
    if not DATA_PATH.exists():
        return {}
    with DATA_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


def verification_agent(phone: str, db: Dict[str, Any]) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Look up phone in mock DB."""
    record = db.get(phone)
    if record:
        return "Verified in mock DB", record
    return "Not found in mock DB", None


def fraud_agent(record: Optional[Dict[str, Any]]) -> str:
    if not record:
        return "No record to check"
    if record.get('blacklisted'):
        return "Blacklisted"
    return "Clear"


def underwriting_agent(credit_score: Optional[int], income: Optional[float]) -> tuple[str, str]:
    """Return decision and reason string for XAI panel."""
    if credit_score is None or income is None:
        return "Needs docs", "Missing credit score or income"

    if credit_score < 650:
        return "Reject", "Credit score < 650"
    if credit_score < 700:
        return "Conditional @ 15%", "Score between 650-699 triggers conditional review"

    if income < 30000:
        return "Reject", "Income below 30k"
    if credit_score >= 750 and income >= 50000:
        return "Approved @ 10.5%", "High score and income >= 50k"

    return "Approved @ 13.5%", "Standard rate for mid-tier profile"


def sales_agent(amount: float, rate: float, tenure_years: int, pre_limit: float, credit_score: Optional[int]) -> str:
    """Craft a persuasive pitch focusing on savings and speed."""
    headline = "Let's lock a great personal loan offer for you today."
    limit_hint = f"You are pre-approved up to INR {pre_limit:,.0f}." if pre_limit else "We can pre-approve you instantly."
    score_hint = f" Your credit score of {credit_score} helps you qualify faster." if credit_score else " Share your credit score for an even sharper rate."  # noqa: E501
    return (
        f"{headline} {limit_hint} "
        f"Proposed: INR {amount:,.0f} at {rate:.1f}% for {tenure_years} yrs."
        f" Pay only while you benefit, and we finalize in minutes once checks pass." + score_hint
    )


def sanction_agent(applicant_name: str, amount: float, output_dir: Path = Path('outputs')) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"sanction_{applicant_name.replace(' ', '_')}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Loan Sanction Letter", ln=True, align='C')
    pdf.ln(10)
    # Use ASCII-friendly text to avoid latin-1 encoding issues in fpdf
    pdf.cell(200, 10, txt=f"Applicant: {applicant_name}", ln=True)
    pdf.cell(200, 10, txt=f"Approved Amount: INR {amount:,.0f}", ln=True)
    pdf.cell(200, 10, txt="Status: Conditional Approval", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt="This is a system-generated document for demo purposes.")

    pdf.output(str(pdf_path))
    return pdf_path
