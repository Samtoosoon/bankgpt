from pathlib import Path
from typing import Any, Dict, Optional

from agents import (
    load_db,
    verification_agent,
    fraud_agent,
    underwriting_agent,
    sanction_agent,
    sales_agent,
)


def run_pipeline(
    applicant_name: str,
    phone: str,
    requested_amount: float,
    monthly_income: Optional[float],
    credit_score: Optional[int],
    rate: float,
    tenure_years: int,
    query_text: str = "",
) -> Dict[str, Any]:
    """Execute the multi-agent flow and return a decision bundle.

    Implements the flowchart:
    - Fast lane if amount <= pre-approved limit and fraud is clear.
    - Hard rejection if amount > 2x limit or credit score < 700.
    - Conditional review path with salary slip request and fraud check.
    - Manual review when record is missing or fraud is flagged.
    """

    db = load_db()
    ver_status, record = verification_agent(phone, db)
    pre_limit = record.get("approved_amount", 0) if record else 0
    income_used = monthly_income or (record.get("income") if record else None)
    credit_used = credit_score if credit_score is not None else (record.get("credit_score") if record else None)

    uw_status, uw_reason = underwriting_agent(credit_used, income_used)
    fraud_status = fraud_agent(record)

    doc_status = "Not Requested"
    decision = "Pending"
    reason = ""

    manual_review = False
    if not record:
        manual_review = True
        reason = "Customer not found in CRM"

    amount_ok = bool(pre_limit) and requested_amount <= pre_limit
    hard_condition = False
    if pre_limit:
        hard_condition = requested_amount > (pre_limit * 2)
    if credit_used is not None and credit_used < 700:
        hard_condition = True

    # Hard rejection path
    if hard_condition:
        decision = "Rejected"
        reason = "Hard rejection: amount > 2x pre-approved or credit score < 700"
        doc_status = "Not Requested"
    # Fast lane (within limit and verified)
    elif amount_ok and not manual_review:
        if fraud_status == "Blacklisted":
            decision = "Manual Review"
            reason = "Fraud flagged"
        else:
            decision = "Approved"
            reason = "Within pre-approved limit; fraud clear"
    else:
        # Conditional review path
        doc_status = "Salary slip requested"
        if fraud_status == "Blacklisted":
            decision = "Manual Review"
            reason = "Fraud flagged during conditional review"
        elif uw_status.startswith("Reject"):
            decision = "Rejected"
            reason = uw_reason
        else:
            decision = "Conditional Approval"
            reason = uw_reason or "Conditional review passed"

    if manual_review and decision == "Pending":
        decision = "Manual Review"
        reason = reason or "Record missing; needs human review"

    sanction_path: Optional[Path] = None
    if decision in ("Approved", "Conditional Approval"):
        sanction_path = sanction_agent(applicant_name or "Applicant", requested_amount)

    sales_pitch = sales_agent(requested_amount, rate, tenure_years, pre_limit, credit_used)

    return {
        "verification": ver_status,
        "fraud": fraud_status,
        "underwriting": uw_status,
        "underwriting_reason": uw_reason,
        "documents": doc_status,
        "decision": decision,
        "reason": reason,
        "sanction_file": str(sanction_path.name) if sanction_path else None,
        "sanction_path": str(sanction_path) if sanction_path else None,
        "sales_pitch": sales_pitch,
        "credit_used": credit_used,
        "income_used": income_used,
        "preapproved_limit": pre_limit,
        "requested_amount": requested_amount,
        "rate": rate,
        "tenure_years": tenure_years,
        "query": query_text,
    }
