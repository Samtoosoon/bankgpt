# eligibility.py - Check eligibility and route to fast track, conditional, or rejection
from typing import Dict, Any, Literal


def check_eligibility(
    requested_amount: float,
    user: Dict[str, Any]
) -> Literal["FAST_TRACK", "CONDITIONAL_REVIEW", "HARD_REJECTION"]:
    """
    Determine eligibility path based on amount, pre-approved limit, and credit score.
    
    Logic:
    1. If credit score < 650: HARD_REJECTION (hard gate)
    2. FAST_TRACK: requested_amount <= pre_approved_limit AND score >= 700
    3. CONDITIONAL_REVIEW: (requested_amount <= 2*limit) OR (score >= 700 and amount reasonable)
    4. HARD_REJECTION: all other cases
    
    Args:
        requested_amount: Loan amount requested (float)
        user: Dict with 'pre_approved_limit' and 'credit_score' keys
    
    Returns:
        One of: "FAST_TRACK", "CONDITIONAL_REVIEW", "HARD_REJECTION"
    """
    limit = user.get('pre_approved_limit', 0) or user.get('approved_amount', 0)
    score = user.get('credit_score', 0)
    
    # Hard gate: credit score below minimum
    if score < 650:
        return "HARD_REJECTION"
    
    # Fast track: within limit AND good score
    if requested_amount <= limit and score >= 700:
        return "FAST_TRACK"
    
    # Conditional review: borderline cases
    # - Amount up to 2x limit (any score >= 650)
    # - OR excellent score allows more flexible borrowing
    if requested_amount <= (2 * limit) or score >= 750:
        return "CONDITIONAL_REVIEW"
    
    # Hard rejection: everything else
    return "HARD_REJECTION"
