#!/usr/bin/env python3
"""
Test unified conversation flow without phases.
Verify: No duplicate questions, smooth natural conversation.
"""

import sys
sys.path.insert(0, '/root')

from master_agent import run_unified_agent
from session_manager import get_conversation_state

# Simulate conversation
def test_unified_conversation():
    """Test unified agent conversation flow."""
    
    print("=" * 60)
    print("Testing Unified Conversation Flow (No Phases)")
    print("=" * 60)
    
    state = {}
    messages = []
    
    # Turn 1: Bot greeting
    print("\n[Turn 1] Bot initiates conversation")
    result = run_unified_agent("Hi", state, messages)
    print(f"Bot: {result['message']}\n")
    messages.append({'role': 'assistant', 'content': result['message']})
    state.update(result)
    
    # Turn 2: User requests business loan
    print("[Turn 2] User: I need a business loan for 5 lakhs")
    user_msg = "I need a business loan for 5 lakhs"
    messages.append({'role': 'user', 'content': user_msg})
    result = run_unified_agent(user_msg, state, messages)
    print(f"Bot: {result['message']}\n")
    messages.append({'role': 'assistant', 'content': result['message']})
    state.update(result)
    
    # Turn 3: User provides phone
    print("[Turn 3] User: My number is 9998887776")
    user_msg = "My number is 9998887776"
    messages.append({'role': 'user', 'content': user_msg})
    result = run_unified_agent(user_msg, state, messages)
    print(f"Bot: {result['message']}\n")
    messages.append({'role': 'assistant', 'content': result['message']})
    state.update(result)
    
    # Check extracted information
    print("=" * 60)
    print("EXTRACTED STATE:")
    print(f"  Phone: {state.get('phone', 'N/A')}")
    print(f"  Customer: {state.get('customer_name', 'N/A')}")
    print(f"  Amount: ₹{state.get('requested_amount', 0):,}")
    print(f"  Pre-approved Limit: ₹{state.get('pre_approved_limit', 0):,}")
    print(f"  Eligibility: {state.get('eligibility_path', 'N/A')}")
    print("=" * 60)
    
    # Verify no duplicate amount question
    conversation_text = ' '.join([msg['content'].lower() for msg in messages])
    
    amount_asks = (
        conversation_text.count('how much amount') +
        conversation_text.count('how much') +
        conversation_text.count('what amount')
    )
    
    print(f"\n✅ TEST RESULTS:")
    print(f"   - Total messages: {len(messages)}")
    print(f"   - Amount questions asked: {amount_asks}")
    
    if amount_asks <= 1:
        print("   ✅ PASS: No duplicate amount questions")
    else:
        print("   ❌ FAIL: Amount question asked more than once")
    
    if state.get('phone'):
        print("   ✅ PASS: Phone extracted and verified")
    else:
        print("   ❌ FAIL: Phone not extracted")
    
    if state.get('requested_amount'):
        print("   ✅ PASS: Amount extracted")
    else:
        print("   ❌ FAIL: Amount not extracted")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_unified_conversation()
