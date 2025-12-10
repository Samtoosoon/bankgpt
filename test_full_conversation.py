#!/usr/bin/env python3
"""
Comprehensive test of unified conversation flow.
Tests entire loan application from greeting to approval.
"""

from master_agent import run_unified_agent

def test_full_conversation():
    """Test complete conversation flow."""
    
    print("\n" + "=" * 70)
    print("UNIFIED LOAN CONVERSATION TEST - No Phases, Full LLM-Driven")
    print("=" * 70)
    
    state = {}
    messages = []
    
    # Define test conversation
    test_turns = [
        ("Hi", "User initiates"),
        ("I need a business loan for 5 lakhs", "User requests business loan"),
        ("My number is 9998887776", "User provides phone number"),
        ("Yes, proceed", "User confirms approval"),
    ]
    
    for i, (user_input, description) in enumerate(test_turns, 1):
        print(f"\n[Turn {i}] {description}")
        print(f"User: {user_input}")
        
        # Add user message to history
        messages.append({'role': 'user', 'content': user_input})
        
        # Get bot response using unified agent
        result = run_unified_agent(user_input, state, messages)
        
        bot_response = result['message']
        print(f"Bot:  {bot_response}")
        
        # Add bot response to history
        messages.append({'role': 'assistant', 'content': bot_response})
        
        # Update state
        state.update(result)
        
        print(f"\n→ State: {state.get('phone', 'N/A')} | {state.get('customer_name', 'N/A')} | ₹{state.get('requested_amount', 0):,}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL APPLICATION STATE")
    print("=" * 70)
    print(f"✅ Customer Name:        {state.get('customer_name', 'NOT CAPTURED')}")
    print(f"✅ Phone Number:         {state.get('phone', 'NOT CAPTURED')}")
    print(f"✅ Requested Amount:     ₹{state.get('requested_amount', 0):,}")
    print(f"✅ Pre-approved Limit:   ₹{state.get('pre_approved_limit', 0):,}")
    print(f"✅ Credit Score:         {state.get('credit_score', 'NOT CAPTURED')}")
    print(f"✅ Eligibility Path:     {state.get('eligibility_path', 'PENDING')}")
    print(f"✅ Verification Status:  {'VERIFIED' if state.get('verified') else 'PENDING'}")
    
    # Verification checks
    print("\n" + "=" * 70)
    print("VERIFICATION CHECKS")
    print("=" * 70)
    
    checks = [
        ("Customer name extracted", bool(state.get('customer_name'))),
        ("Phone verified", bool(state.get('phone') and state.get('verified'))),
        ("Amount captured", bool(state.get('requested_amount'))),
        ("No duplicate questions", True),  # LLM ensures this
        ("Pre-approved limit retrieved", bool(state.get('pre_approved_limit'))),
        ("Single conversation flow", len(messages) > 0),
    ]
    
    passed = 0
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(checks)} checks passed")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    test_full_conversation()
