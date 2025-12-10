# xai_helper.py - Explainability text generation for decision rationale

def explain_decision(decision: str, reason: str, context: dict) -> str:
    """
    Generate human-readable explanation for loan decision.
    
    Args:
        decision: "Approved", "Conditional Approval", "Rejected", "Manual Review", etc.
        reason: Brief reason from agent
        context: Dict with credit_score, income, amount, limit, fraud_status, etc.
    
    Returns:
        Detailed explanation text for XAI panel
    """
    
    credit_score = context.get('credit_score')
    income = context.get('income')
    amount = context.get('requested_amount')
    limit = context.get('pre_approved_limit', 0)
    fraud_status = context.get('fraud_status', 'Unknown')
    
    if decision == "Approved":
        text = f"✅ **Approved**: Your loan of INR {amount:,.0f} has been approved."
        if limit:
            text += f"\n- Amount is within your pre-approved limit of INR {limit:,.0f}."
        if credit_score and credit_score >= 750:
            text += f"\n- Excellent credit score ({credit_score}) qualifies you for our best rates."
        if fraud_status == "Clear":
            text += "\n- Fraud screening: Clear."
        return text
    
    elif decision == "Conditional Approval":
        text = f"⚠️ **Conditional Approval**: Your request for INR {amount:,.0f} requires verification."
        if amount and limit and amount > limit:
            text += f"\n- Amount exceeds pre-approved limit (INR {limit:,.0f}), but your profile is strong."
        if credit_score and 700 <= credit_score < 750:
            text += f"\n- Credit score ({credit_score}) is good; salary verification needed."
        if income:
            text += f"\n- Declared income: INR {income:,.0f}/month. Please upload latest salary slip to confirm."
        return text + "\n- **Next step**: Upload salary slip for faster processing."
    
    elif decision == "Rejected":
        text = f"❌ **Rejected**: We cannot approve your request at this time."
        if credit_score and credit_score < 650:
            text += f"\n- Credit score ({credit_score}) is below minimum threshold (650)."
        if amount and limit and amount > (2 * limit):
            text += f"\n- Requested amount (INR {amount:,.0f}) exceeds 2x pre-approved limit (INR {limit:,.0f})."
        if fraud_status == "Blacklisted":
            text += "\n- Account flagged for fraud concerns. Please contact support."
        return text
    
    elif decision == "Manual Review":
        text = f"🔍 **Under Manual Review**: Your application requires specialist review."
        if fraud_status == "Blacklisted":
            text += "\n- Fraud screening raised a concern. Our team will contact you within 24 hours."
        elif not context.get('verified_in_crm'):
            text += "\n- We need to verify some details from our system. Please check your email."
        else:
            text += f"\n- Reason: {reason}"
        return text
    
    else:
        return f"📋 **Status**: {decision}\n- {reason}"


def explain_agent_decision(agent_name: str, decision: str, score: float = None, threshold: float = None) -> str:
    """
    Generate explanation for individual agent decisions (verification, underwriting, fraud, etc.)
    
    Args:
        agent_name: 'verification', 'fraud', 'underwriting', etc.
        decision: Agent's decision/status
        score: Numeric score if applicable
        threshold: Threshold used by agent
    
    Returns:
        Explanation text
    """
    
    if agent_name == "verification":
        if decision == "Verified in mock DB":
            return "✅ Phone verified against our records."
        else:
            return "⚠️ Phone not found in our system. Manual verification may be required."
    
    elif agent_name == "underwriting":
        if decision.startswith("Approved"):
            rate = decision.split("@")[-1].strip() if "@" in decision else "standard"
            return f"✅ Underwriting approved at rate: {rate}."
        elif decision.startswith("Conditional"):
            rate = decision.split("@")[-1].strip() if "@" in decision else "standard"
            return f"⚠️ Conditional approval at rate: {rate}. Salary slip required."
        else:
            return f"❌ Underwriting declined: {decision}."
    
    elif agent_name == "fraud":
        if decision == "Clear":
            return "✅ Fraud screening passed. No concerns found."
        elif decision == "Blacklisted":
            return "❌ Account is on our blacklist. Manual review required."
        else:
            return f"⚠️ Fraud screening: {decision}."
    
    elif agent_name == "verification_docs":
        if decision == "Approved":
            return "✅ Documents verified successfully."
        elif decision == "Salary slip requested":
            return "⏳ Awaiting salary slip upload for verification."
        else:
            return f"📋 Document status: {decision}."
    
    else:
        return f"ℹ️ {agent_name}: {decision}"
