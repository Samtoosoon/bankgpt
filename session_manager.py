# session_manager.py - Manages Streamlit session state for conversation flow

import streamlit as st
from typing import Dict, Any, List, Optional


def init_session():
    """Initialize all session state keys for the conversation flow."""
    
    if 'conversation_state' not in st.session_state:
        st.session_state['conversation_state'] = {
            'phase': 1,  # 1=Sales, 2=Underwriting, 3=Conditional, 4=Sanction
            'phone': None,
            'credit_score': None,
            'pre_approved_limit': 0,
            'requested_amount': 0,
            'eligibility_path': None,
            'fraud_status': 'Pending',
            'decision': 'Pending',
            'decision_reason': '',
            'salary_slip_uploaded': False,
            'income': 0,
            'verified': False,
            'voice_enabled': False,
            'language': 'English'
        }
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [
            {
                "role": "assistant",
                "content": "Namaste! 🙏 I am BankGPT. I can help you get a personal loan in under 10 minutes. Are you looking for a loan today? (You can speak in Hindi or English)"
            }
        ]


def get_conversation_state() -> Dict[str, Any]:
    """Get the current conversation state."""
    return st.session_state.get('conversation_state', {})


def update_conversation_state(updates: Dict[str, Any]):
    """Update conversation state with new values."""
    if 'conversation_state' not in st.session_state:
        init_session()
    st.session_state['conversation_state'].update(updates)


def add_message(role: str, content: str):
    """Add a message to the chat history."""
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    st.session_state['messages'].append({
        "role": role,
        "content": content
    })


def get_messages() -> List[Dict[str, str]]:
    """Get all messages from conversation history."""
    return st.session_state.get('messages', [])


def reset_session():
    """Reset all session state to initial values."""
    if 'conversation_state' in st.session_state:
        del st.session_state['conversation_state']
    if 'messages' in st.session_state:
        del st.session_state['messages']
    init_session()


def get_session_summary() -> Dict[str, Any]:
    """Get a summary of the current session state."""
    state = get_conversation_state()
    return {
        'phase': state.get('phase'),
        'applicant_phone': state.get('phone'),
        'credit_score': state.get('credit_score'),
        'pre_approved_limit': state.get('pre_approved_limit'),
        'requested_amount': state.get('requested_amount'),
        'eligibility_path': state.get('eligibility_path'),
        'fraud_status': state.get('fraud_status'),
        'decision': state.get('decision'),
        'total_messages': len(get_messages())
    }
