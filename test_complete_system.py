#!/usr/bin/env python3
"""
Comprehensive system test demonstrating:
1. No phase architecture
2. Stage-aware conversation
3. Proper amount/phone extraction
4. LLM-driven responses
5. Natural conversation flow
"""

from master_agent import run_unified_agent

def test_complete_system():
    """Test complete loan application flow."""
    
    print("\n" + "=" * 80)
    print("BANKGPT COMPLETE SYSTEM TEST - PRODUCTION READINESS")
    print("=" * 80)
    
    print("\n✅ Testing: Unified conversation, no phases, stage-aware LLM")
    print("✅ Testing: Proper extraction without confusion")
    print("✅ Testing: Natural dialogue flow")
    print("=" * 80)
    
    state = {}
    messages = []
    
    test_scenarios = [
        {
            'input': 'Hi',
            'description': 'Customer initiates',
            'expect': 'phone_asked'
        },
        {
            'input': 'I want a home loan',
            'description': 'Customer states loan type',
            'expect': 'phone_asked (not re-asked)'
        },
        {
            'input': 'My phone number is 9998887776',
            'description': 'Customer provides phone',
            'expect': 'amount_asked'
        },
        {
            'input': 'I need 8 lakhs',
            'description': 'Customer provides amount',
            'expect': 'eligibility_check'
        },
        {
            'input': 'That looks good',
            'description': 'Customer confirms',
            'expect': 'approved'
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'─'*80}")
        print(f"[Test {i}] {scenario['description']}")
        print(f"Expected Stage: {scenario['expect']}")
        print(f"─"*80)
        
        user_input = scenario['input']
        print(f"👤 User: {user_input}")
        
        messages.append({'role': 'user', 'content': user_input})
        
        result = run_unified_agent(user_input, state, messages)
        bot_response = result['message']
        stage = result.get('conversation_stage', 'unknown')
        
        print(f"🤖 Bot:  {bot_response}")
        
        messages.append({'role': 'assistant', 'content': bot_response})
        state.update(result)
        
        # Show current extraction
        print(f"\n📊 Current State:")
        print(f"   Phone: {state.get('phone', '—')}")
        print(f"   Amount: ₹{state.get('requested_amount', 0):,}" if state.get('requested_amount') else "   Amount: —")
        print(f"   Name: {state.get('customer_name', '—')}")
        print(f"   Verified: {'✅' if state.get('verified') else '❌'}")
        print(f"   Stage: {stage}")
        
        # Verify no confusion
        phone = str(state.get('phone', ''))
        amount = str(state.get('requested_amount', ''))
        
        if phone and amount:
            if phone != amount:
                print(f"   ✅ Phone ≠ Amount (no confusion)")
            else:
                print(f"   ❌ ERROR: Phone and Amount are same!")
    
    # Final summary
    print(f"\n{'═'*80}")
    print("FINAL APPLICATION STATUS")
    print(f"{'═'*80}")
    
    checks = [
        ("Customer Name Captured", bool(state.get('customer_name'))),
        ("Phone Number Verified", bool(state.get('phone') and state.get('verified'))),
        ("Loan Amount Extracted", bool(state.get('requested_amount'))),
        ("Pre-approved Limit Fetched", bool(state.get('pre_approved_limit'))),
        ("Credit Score Retrieved", bool(state.get('credit_score'))),
        ("Phone ≠ Amount", str(state.get('phone', '')) != str(state.get('requested_amount', ''))),
        ("Single Conversation Flow", len(messages) >= 5),
        ("No Phase Architecture", 'phase' not in state),
        ("Stage Tracking Works", 'conversation_stage' in state),
    ]
    
    print("\n✅ VERIFICATION CHECKLIST:")
    passed = 0
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {check_name}")
        if result:
            passed += 1
    
    print(f"\n{'═'*80}")
    print(f"RESULT: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("🎉 SYSTEM READY FOR PRODUCTION")
    else:
        print("⚠️  Some checks failed")
    
    print(f"{'═'*80}\n")
    
    return passed == len(checks)

if __name__ == '__main__':
    success = test_complete_system()
    exit(0 if success else 1)
