import math
from langdetect import detect_langs

LANG_MAP = {
    'en': 'en',
    'hi': 'hi',
    'gu': 'gu',
    'mr': 'mr',
    'pa': 'pa',
    'bn': 'bn'
}


def compute_emi(principal: float, annual_rate_percent: float, tenure_months: int) -> float:
    r = annual_rate_percent / 100.0 / 12.0
    n = tenure_months
    if r == 0:
        return principal / n
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return emi


def compute_foir(monthly_income: float, existing_emis_total: float, new_emi: float) -> float:
    fixed_obligations = existing_emis_total + new_emi
    if monthly_income == 0:
        return 999.0
    return (fixed_obligations / monthly_income) * 100.0


def eligibility_band(foir_percent: float, credit_score: int = None):
    # If credit score exists and is below threshold
    if credit_score is not None and credit_score < 650:
        return 'High Risk (credit score under threshold)'
    
    if foir_percent <= 40:
        return 'Likely Eligible'
    if foir_percent <= 50:
        return 'Borderline'
    return 'Likely Ineligible'


def detect_language(text: str, fallback='en') -> str:
    try:
        langs = detect_langs(text)
        if not langs:
            return fallback
        
        top = langs[0]
        code = top.lang

        # Map if possible
        if code in LANG_MAP:
            return LANG_MAP[code]
        return code
    except Exception:
        return fallback
