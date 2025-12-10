# master_agent.py - Unified LLM-Driven Conversation Agent
"""
Single, continuous conversation flow powered by LLM.
No phases - one natural conversation that handles:
- Greeting and loan understanding
- Phone verification and profile lookup
- Loan amount and eligibility
- Document verification if needed
- Approval and sanction

Language-aware responses (English, Hindi, Hinglish)
Smart context tracking to avoid duplicate questions
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from agents import load_db, verification_agent, fraud_agent, underwriting_agent, sanction_agent
from language_helper import detect_language
from groq_integration import GroqClient

DATA_PATH = Path('data/mock_db.json')


def load_mock_db():
    """Load mock CRM database."""
    if DATA_PATH.exists():
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def run_unified_agent(user_input: str, state: Dict[str, Any], conversation_history: list) -> Dict[str, Any]:
    """
    Unified conversation agent - handles entire loan application flow in one natural conversation.
    
    Conversation Stages:
    1. greeting: First message - bot greets
    2. loan_type: Bot asking about loan type
    3. phone_asked: Bot asked for phone number
    4. phone_provided: User provided phone, verified
    5. amount_asked: Bot asked for amount
    6. amount_provided: User provided amount
    7. eligibility_check: Checking eligibility
    8. approved: Loan approved
    9. document_needed: Document verification required
    10. document_uploaded: Document verified
    11. completed: Loan sanctioned
    
    Flow:
    1. First turn: Show greeting, set stage to phone_asked
    2. Subsequent turns: Use LLM with conversation history and stage to:
       - Understand loan needs and amount
       - Extract phone number when in phone_asked stage
       - Look up customer profile
       - Determine eligibility
       - Request documents if needed
       - Generate approval
    
    Args:
        user_input: User's message
        state: Conversation state tracking (phone, amount, verification status, stage, etc.)
        conversation_history: List of previous messages for context
        
    Returns:
        Dict with message and updated state info
    """
    
    detected_language = detect_language(user_input)
    
    # Determine current conversation stage
    current_stage = _determine_conversation_stage(state, conversation_history)
    
    # FIRST TURN: Show greeting
    if not conversation_history:
        greeting = _get_greeting(detected_language)
        return {
            'message': greeting,
            'detected_language': detected_language,
            'conversation_stage': 'phone_asked'  # Next stage: ask for phone
        }
    
    # SUBSEQUENT TURNS: Use LLM to drive conversation naturally
    try:
        client = GroqClient()
        
        # Build conversation context from history
        history_context = _build_history_context(conversation_history, detected_language)
        
        # Build current state context with stage awareness
        state_context = _build_state_context_with_stage(state, current_stage, detected_language)
        
        # System prompt that guides the conversation based on stage
        system_prompt = _get_stage_aware_system_prompt(detected_language, state, current_stage)
        
        # Build the full prompt
        full_prompt = f"""{system_prompt}

CONVERSATION STAGE: {current_stage.upper()}

CONVERSATION HISTORY:
{history_context}

CURRENT STATE:
{state_context}

Customer's latest message: "{user_input}"

Based on the conversation stage, history, and current state, generate the next response.

STAGE-SPECIFIC INSTRUCTIONS for stage '{current_stage}':
{_get_stage_instructions(current_stage)}

Your response should:
1. Be natural and conversational
2. Acknowledge the customer's input
3. Move to the next stage appropriately
4. Keep responses under 150 words
5. Be warm and professional

Generate only the bot's response, no explanations or meta-commentary."""
        
        # Generate response with Groq LLM
        response = GroqClient.generate_text(full_prompt, max_tokens=300)
        
        if not response or len(response.strip()) < 5:
            response = "I'm having trouble processing that. Could you please rephrase?"
        
        # Extract structured information from user input and state
        extracted_info = _extract_information(user_input, state, conversation_history, detected_language)
        
        # Determine next stage
        next_stage = _determine_next_stage(current_stage, extracted_info, state)
        
        return {
            'message': response.strip(),
            'detected_language': detected_language,
            'conversation_stage': next_stage,
            **extracted_info  # Include phone, amount, eligibility_path, etc.
        }
    
    except Exception as e:
        # Fallback response
        return {
            'message': "I'm having trouble processing your request. Could you please try again?",
            'detected_language': detected_language,
            'error': str(e),
            'conversation_stage': current_stage
        }


def _get_greeting(language: str) -> str:
    """Get language-specific greeting."""
    greetings = {
        'hindi': (
            "🙏 नमस्ते! मैं BankGPT हूँ टाटा कैपिटल से। "
            "आप अपने लिए कौन सा लोन ढूंढ रहे हैं?"
        ),
        'hinglish': (
            "🙏 Namaste! Main BankGPT hoon Tata Capital se. "
            "Aap apne liye kaunsa loan dhundh rahe ho?"
        ),
        'english': (
            "🙏 Namaste! I am BankGPT from Tata Capital. "
            "What kind of loan are you looking for?"
        )
    }
    return greetings.get(language, greetings['english'])


def _determine_conversation_stage(state: Dict[str, Any], conversation_history: list) -> str:
    """Determine current conversation stage based on state and history."""
    
    # If no history, we're at greeting stage
    if not conversation_history:
        return 'greeting'
    
    # Check what information we have
    has_phone = bool(state.get('phone'))
    has_amount = bool(state.get('requested_amount'))
    phone_verified = state.get('verified', False)
    
    # Determine stage based on what we have
    if has_phone and phone_verified and has_amount:
        # We have both phone and amount - check eligibility
        amount = state.get('requested_amount', 0)
        limit = state.get('pre_approved_limit', 0)
        
        if amount <= limit:
            return 'approved'
        else:
            return 'document_needed'
    
    elif has_phone and phone_verified:
        # We have phone but no amount - ask for amount
        return 'amount_asked'
    
    elif has_phone and not phone_verified:
        # Phone provided but not yet verified
        return 'phone_provided'
    
    else:
        # No phone yet - ask for it
        return 'phone_asked'


def _determine_next_stage(current_stage: str, extracted_info: Dict[str, Any], state: Dict[str, Any]) -> str:
    """Determine next conversation stage."""
    
    has_new_phone = bool(extracted_info.get('phone'))
    has_new_amount = bool(extracted_info.get('requested_amount'))
    
    stage_flow = {
        'greeting': 'phone_asked',
        'phone_asked': 'phone_provided' if has_new_phone else 'phone_asked',
        'phone_provided': 'amount_asked' if state.get('verified') else 'phone_provided',
        'amount_asked': 'amount_provided' if has_new_amount else 'amount_asked',
        'amount_provided': 'eligibility_check',
        'eligibility_check': 'approved' if (state.get('requested_amount', 0) <= state.get('pre_approved_limit', 0)) else 'document_needed',
        'approved': 'completed',
        'document_needed': 'document_uploaded',
        'document_uploaded': 'completed',
        'completed': 'completed',
        'loan_type': 'phone_asked'
    }
    
    return stage_flow.get(current_stage, current_stage)


def _get_stage_instructions(stage: str) -> str:
    """Get specific instructions for each conversation stage."""
    
    instructions = {
        'greeting': "You've already greeted the customer. Now ask about their loan needs and what type of loan they want.",
        'phone_asked': "The customer has NOT given their phone number yet. Ask for their 10-digit phone number to verify their identity.",
        'phone_provided': "The customer just provided their phone number. Acknowledge it and tell them you're verifying their profile.",
        'amount_asked': "The customer has provided their phone and been verified. Now ask how much loan amount they need.",
        'amount_provided': "The customer just told you the amount they need. Acknowledge it and say you're checking their eligibility.",
        'eligibility_check': "Check if the amount is within their pre-approved limit. Tell them the result.",
        'approved': "The amount is within their limit. Congratulate them on approval and provide EMI details.",
        'document_needed': "The amount exceeds their pre-approved limit. Ask them to upload their salary slip for verification.",
        'document_uploaded': "They've uploaded the document. Verify it and give them the final decision.",
        'completed': "The loan has been approved or the application is complete. Offer next steps or ask if they need anything else."
    }
    
    return instructions.get(stage, "Continue the conversation naturally based on the context provided.")


def _build_state_context_with_stage(state: Dict[str, Any], stage: str, language: str) -> str:
    """Build current state summary with stage awareness."""
    lines = []
    
    lines.append(f"CONVERSATION STAGE: {stage}")
    lines.append("")
    
    # What we know
    lines.append("VERIFIED INFORMATION:")
    if state.get('phone'):
        lines.append(f"  ✓ Phone: {state['phone']} (verified)")
    else:
        lines.append(f"  ✗ Phone: NOT YET PROVIDED")
    
    if state.get('customer_name'):
        lines.append(f"  ✓ Name: {state['customer_name']}")
    
    if state.get('credit_score'):
        lines.append(f"  ✓ Credit Score: {state['credit_score']}")
    
    if state.get('pre_approved_limit'):
        lines.append(f"  ✓ Pre-approved Limit: ₹{state['pre_approved_limit']:,}")
    
    if state.get('requested_amount'):
        lines.append(f"  ✓ Requested Amount: ₹{state['requested_amount']:,}")
    else:
        lines.append(f"  ✗ Requested Amount: NOT YET PROVIDED")
    
    if state.get('verified'):
        lines.append(f"  ✓ Identity: VERIFIED")
    else:
        lines.append(f"  ✗ Identity: NOT YET VERIFIED")
    
    # Eligibility
    if state.get('phone') and state.get('requested_amount'):
        amount = state.get('requested_amount', 0)
        limit = state.get('pre_approved_limit', 0)
        
        lines.append("")
        lines.append("ELIGIBILITY STATUS:")
        if amount <= limit:
            lines.append(f"  ✓ APPROVED - Amount ₹{amount:,} is within limit ₹{limit:,}")
        else:
            lines.append(f"  ⚠ NEEDS REVIEW - Amount ₹{amount:,} exceeds limit ₹{limit:,}")
    
    return "\n".join(lines)



def _build_history_context(conversation_history: list, language: str) -> str:
    """Build conversation history for LLM context."""
    if not conversation_history:
        return "No previous conversation yet."
    
    lines = []
    for msg in conversation_history[-6:]:  # Last 6 messages for context
        role = "Customer" if msg['role'] == 'user' else "BankGPT"
        lines.append(f"{role}: {msg['content'][:100]}")
    
    return "\n".join(lines)


def _build_state_context(state: Dict[str, Any], language: str) -> str:
    """Build current state summary for LLM context."""
    lines = []
    
    if state.get('phone'):
        lines.append(f"- Phone verified: {state['phone']}")
    
    if state.get('customer_name'):
        lines.append(f"- Customer name: {state['customer_name']}")
    
    if state.get('credit_score'):
        lines.append(f"- Credit score: {state['credit_score']}")
    
    if state.get('pre_approved_limit'):
        lines.append(f"- Pre-approved limit: ₹{state['pre_approved_limit']:,}")
    
    if state.get('requested_amount'):
        lines.append(f"- Requested amount: ₹{state['requested_amount']:,}")
    
    if state.get('eligibility_path'):
        lines.append(f"- Eligibility path: {state['eligibility_path']}")
    
    if state.get('document_uploaded'):
        lines.append(f"- Document status: {state['document_uploaded']}")
    
    if not lines:
        lines.append("- No customer information captured yet")
    
    return "\n".join(lines)


def _get_stage_aware_system_prompt(language: str, state: Dict[str, Any], stage: str) -> str:
    """Get language-specific system prompt with stage awareness."""
    
    base_prompt = f"""You are BankGPT, a professional and friendly loan officer at Tata Capital.
Your current task: You are in the '{stage}' stage of the loan application process.

CRITICAL RULES:
1. Only ask for information that is NOT yet in the VERIFIED INFORMATION section
2. DO NOT re-ask questions - check what's already been provided
3. Use verified data as facts - don't question or recalculate
4. Stay focused on the current stage
5. When moving to next stage, acknowledge progress

STAGE CONTEXT:
- phone_asked: Customer has NOT given phone number - ASK FOR IT
- phone_provided: Phone just given - VERIFY and LOOKUP PROFILE
- amount_asked: Customer has verified phone - ASK FOR AMOUNT
- amount_provided: Amount just given - CHECK ELIGIBILITY
- eligibility_check: Both phone and amount available - DETERMINE IF APPROVED
- approved: Amount within limit - CONGRATULATE and PROVIDE EMI
- document_needed: Amount exceeds limit - REQUEST SALARY SLIP
- completed: Application complete - PROVIDE NEXT STEPS

IMPORTANT:
- Phone number is ALWAYS 10 digits - never confuse with amounts
- Amounts are in RUPEES - can be "5 lakhs", "500000", etc
- Only look at verified information in the state - ignore user's rephrasing of old info
- BE CONVERSATIONAL but PRECISE
- Acknowledge customer's current message but act based on current stage

When in '{stage}' stage:
- Do NOT ask about information from earlier stages
- Focus ONLY on what this stage needs
- Use the stage instructions provided separately"""
    
    if language == 'hindi':
        return f"""{base_prompt}

LANGUAGE: Hindi/Hinglish
Always respond in the language the customer is using.
Keep professional tone but use warm, conversational Hindi.
Use rupee amounts like "पाँच लाख" or "5 लाख"."""
    elif language == 'hinglish':
        return f"""{base_prompt}

LANGUAGE: Hinglish (Hindi + English mix)
Match the customer's language preference.
Use simple, conversational Hinglish.
Say amounts like "5 lakhs" or "five lakhs"."""
    else:
        return f"""{base_prompt}

LANGUAGE: English
Use clear, professional English.
Say amounts like "5 lakhs" or "500,000 rupees"."""


def _extract_information(user_input: str, state: Dict[str, Any], 
                         conversation_history: list, language: str) -> Dict[str, Any]:
    """
    Extract structured information from user input.
    Updates state with phone, amount, and other details.
    """
    import re
    extracted = {}
    
    # Extract phone number (10 digits) - but only if we haven't already got it
    if not state.get('phone'):
        # Look for 10 consecutive digits (phone number pattern)
        phone_matches = re.findall(r'\b\d{10}\b', user_input)
        
        if phone_matches:
            phone = phone_matches[0]  # Take first 10-digit match
            
            # Verify phone in database
            db = load_mock_db()
            ver_status, record = verification_agent(phone, db)
            
            if record:
                extracted['phone'] = phone
                extracted['customer_name'] = record.get('name', '')
                extracted['credit_score'] = record.get('credit_score', 700)
                extracted['pre_approved_limit'] = record.get('approved_amount', 500000)
                extracted['income'] = record.get('income', 50000)
                extracted['verified'] = True
    
    # Extract loan amount - only if we haven't already got it
    if not state.get('requested_amount'):
        user_lower = user_input.lower()
        
        # Pattern 1: "X lakhs" or "X lakh" or "X lac"
        lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac)', user_lower)
        if lakh_match:
            amount_value = float(lakh_match.group(1))
            extracted['requested_amount'] = int(amount_value * 100000)
        
        # Pattern 2: "X crore" (if mentioned)
        crore_match = re.search(r'(\d+(?:\.\d+)?)\s*crore', user_lower)
        if crore_match and 'requested_amount' not in extracted:
            amount_value = float(crore_match.group(1))
            extracted['requested_amount'] = int(amount_value * 10000000)
        
        # Pattern 3: Large 6-7 digit numbers (like 500000 for 5 lakhs)
        if 'requested_amount' not in extracted:
            large_numbers = re.findall(r'\b(\d{6,7})\b', user_input)
            
            # Filter to reasonable loan amounts (10K to 1 Crore)
            for num_str in large_numbers:
                num = int(num_str)
                if 100000 <= num <= 100000000:  # Between 1 lakh and 1 crore
                    extracted['requested_amount'] = num
                    break
    
    # Determine eligibility path if we have both phone and amount

    if state.get('phone') and extracted.get('requested_amount'):
        pre_approved = state.get('pre_approved_limit', extracted.get('pre_approved_limit', 0))
        requested = extracted['requested_amount']
        
        if requested <= pre_approved:
            extracted['eligibility_path'] = 'FAST_TRACK'
        else:
            extracted['eligibility_path'] = 'CONDITIONAL_REVIEW'
    
    return extracted


def calculate_emi(principal: float, rate: float, tenure_months: int) -> float:
    """Simple EMI calculation."""
    r = rate / 100.0 / 12.0
    n = tenure_months
    if r == 0:
        return principal / n
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return emi


# Deprecated phase functions - kept for backward compatibility
def run_phase_1_sales(user_input: str, first_message: bool = True) -> Dict[str, Any]:
    """Deprecated - use run_unified_agent instead."""
    if first_message:
        return {'message': _get_greeting('english'), 'phase': 1}
    return {'message': "Please tell me about your loan needs.", 'phase': 1}


def run_phase_2_underwriting(user_input: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Deprecated - use run_unified_agent instead."""
    return {'message': "How can I help you?", 'phase': 2}


def run_phase_3_conditional(state: Dict[str, Any], uploaded_file) -> Dict[str, Any]:
    """Deprecated - use run_unified_agent instead."""
    return {'message': "Document received.", 'decision': 'Pending'}


def run_phase_4_sanction(state: Dict[str, Any]) -> Optional[str]:
    """Deprecated - use run_unified_agent instead."""
    return None
