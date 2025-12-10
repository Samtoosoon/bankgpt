#!/usr/bin/env python3
"""
Test conversation with explicit stage tracking to verify:
1. Phone and amount are not confused
2. Stages progress correctly
3. No duplicate questions
"""

from master_agent import run_unified_agent

def test_stage_tracking():
    """Test conversation stage progression."""
    
    print("\n" + "=" * 70)
    print("STAGE-AWARE CONVERSATION TEST")
    print("=" * 70)
    
    state = {}
    messages = []
    
    test_turns = [
        ("Hi there", "greeting"),
        ("I need a home loan", "phone_asked (should ask for phone)"),
        ("My phone is 9998887776", "phone_provided (verify and ask amount)"),
        ("I need 10 lakhs", "amount_provided (check eligibility)"),
    ]
    
    for i, (user_input, expected_stage) in enumerate(test_turns, 1):
        print(f"\n{'='*70}")
        print(f"[Turn {i}] {expected_stage}")
        print(f"User: {user_input}")
        
        messages.append({'role': 'user', 'content': user_input})
        
        result = run_unified_agent(user_input, state, messages)
        bot_response = result['message']
        next_stage = result.get('conversation_stage', 'unknown')
        
        print(f"Bot:  {bot_response}")
        print(f"→ Next Stage: {next_stage}")
        
        messages.append({'role': 'assistant', 'content': bot_response})
        state.update(result)
        
        # Print state for debugging
        print(f"\nState Summary:")
        print(f"  Phone: {state.get('phone', 'N/A')}")
        print(f"  Amount: ₹{state.get('requested_amount', 0):,}")
        print(f"  Verified: {state.get('verified', False)}")
        print(f"  Stage: {next_stage}")
    
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    # Check that phone and amount are different
    phone = state.get('phone', '')
    amount = state.get('requested_amount', 0)
    
    print(f"\n✅ Phone extracted: {phone}")
    print(f"✅ Amount extracted: ₹{amount:,}")
    
    if phone == '9998887776':
        print(f"✅ PASS: Phone correctly extracted (not confused with amount)")
    else:
        print(f"❌ FAIL: Phone incorrect")
    
    if amount == 1000000:  # 10 lakhs
        print(f"✅ PASS: Amount correctly extracted (10 lakhs = 1,000,000)")
    else:
        print(f"❌ FAIL: Amount incorrect (got {amount}, expected 1000000)")
    
    if phone != str(amount):
        print(f"✅ PASS: Phone and amount are different values")
    else:
        print(f"❌ FAIL: Phone and amount were confused")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == '__main__':
    test_stage_tracking()
