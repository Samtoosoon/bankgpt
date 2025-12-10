"""
test_conversation_flow.py - Test the 4-phase conversation flow without Streamlit
Tests: Phase 1 (Sales) → Phase 2 (Underwriting) → Phase 3 (Conditional) → Phase 4 (Sanction)
"""

import sys
import io
from pathlib import Path
from master_agent import run_phase_1_sales, run_phase_2_underwriting, run_phase_3_conditional, run_phase_4_sanction
from session_manager import (
    init_session, get_conversation_state, update_conversation_state, 
    add_message, get_messages, reset_session
)

# Fix Unicode encoding for Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Mock state object (simulating Streamlit's st.session_state)
class MockSessionState(dict):
    """Simple dict to simulate Streamlit session state."""
    pass


def test_phase_1_sales():
    """Test Phase 1: Sales Agent - Warm greeting and response."""
    print("\n" + "="*60)
    print("TEST PHASE 1: SALES AGENT")
    print("="*60)
    
    # First message: Show greeting
    result = run_phase_1_sales("Hi", first_message=True)
    print(f"✅ ASSISTANT (Greeting): {result['message'][:80]}...")
    print(f"   Phase: {result['phase']}")
    assert result['phase'] == 1, "Should stay in Phase 1 after greeting"
    print("✅ Greeting shown!")
    
    # Second message: User responds with loan intent
    result = run_phase_1_sales("Yes, I need a home loan", first_message=False)
    print(f"✅ ASSISTANT (Response): {result['message'][:80]}...")
    print(f"   Next Phase: {result['phase']}")
    assert result['phase'] == 2, "Phase 1 should transition to Phase 2 when user confirms"
    print("✅ Phase 1 test passed!")
    return result


def test_phase_2_phone_verification():
    """Test Phase 2 Step 1: Phone number verification."""
    print("\n" + "="*60)
    print("TEST PHASE 2 STEP 1: PHONE VERIFICATION")
    print("="*60)
    
    state = {
        'phone': None,
        'phase': 2
    }
    
    # FIRST CALL: Bot asks for phone number
    result = run_phase_2_underwriting("yes", state)
    print(f"✅ ASSISTANT: {result['message'][:100]}...")
    assert "mobile number" in result['message'].lower(), "Should ask for phone number"
    assert result.get('phone') is None, "Phone should still be None"
    assert result.get('asked_for_phone') == True, "Flag should indicate phone was asked"
    print("✅ Phone prompt test passed!")
    
    # SECOND CALL: User provides phone number
    state = result
    result = run_phase_2_underwriting("9876543210", state)
    print(f"✅ ASSISTANT: {result['message'][:100]}...")
    print(f"   Phone Verified: {result.get('verified')}")
    print(f"   Credit Score: {result.get('credit_score')}")
    if result.get('pre_approved_limit'):
        print(f"   Pre-Approved Limit: ₹{result.get('pre_approved_limit'):,}")
    
    assert result.get('verified') == True, "Phone should be verified"
    assert result.get('credit_score') == 780, "Credit score should be 780 for this phone"
    assert result.get('pre_approved_limit') == 1200000, "Pre-approved limit should match mock DB"
    print("✅ Phone verification test passed!")
    return result


def test_phase_2_amount_within_limit():
    """Test Phase 2 Step 2: Amount within pre-approved limit (Fast Track)."""
    print("\n" + "="*60)
    print("TEST PHASE 2 STEP 2: AMOUNT WITHIN LIMIT (FAST TRACK)")
    print("="*60)
    
    state = {
        'phone': '9876543210',
        'credit_score': 780,
        'pre_approved_limit': 1200000,
        'phase': 2,
        'asked_for_phone': True
    }
    
    result = run_phase_2_underwriting("500000", state)
    print(f"✅ ASSISTANT: {result['message'][:100]}...")
    if result.get('requested_amount'):
        print(f"   Requested Amount: ₹{result.get('requested_amount'):,}")
    print(f"   Eligibility Path: {result.get('eligibility_path')}")
    print(f"   Next Phase: {result.get('phase')}")
    
    assert result.get('eligibility_path') == 'FAST_TRACK', "Should be FAST_TRACK"
    assert result.get('phase') == 4, "Should transition to Phase 4 (Sanction)"
    print("✅ Fast track test passed!")
    return result


def test_phase_2_amount_exceeds_limit():
    """Test Phase 2 Step 2: Amount exceeds pre-approved limit (Conditional Review)."""
    print("\n" + "="*60)
    print("TEST PHASE 2 STEP 2: AMOUNT EXCEEDS LIMIT (CONDITIONAL REVIEW)")
    print("="*60)
    
    state = {
        'phone': '9876543210',
        'credit_score': 780,
        'pre_approved_limit': 1200000,
        'phase': 2,
        'asked_for_phone': True
    }
    
    result = run_phase_2_underwriting("1500000", state)
    print(f"✅ ASSISTANT: {result['message'][:100]}...")
    if result.get('requested_amount'):
        print(f"   Requested Amount: ₹{result.get('requested_amount'):,}")
    print(f"   Eligibility Path: {result.get('eligibility_path')}")
    print(f"   Next Phase: {result.get('phase')}")
    
    assert result.get('eligibility_path') == 'CONDITIONAL_REVIEW', "Should be CONDITIONAL_REVIEW"
    assert result.get('phase') == 3, "Should transition to Phase 3 (Conditional Review)"
    print("✅ Conditional review trigger test passed!")
    return result


def test_phase_3_conditional_review():
    """Test Phase 3: Conditional Review - Document verification."""
    print("\n" + "="*60)
    print("TEST PHASE 3: CONDITIONAL REVIEW")
    print("="*60)
    
    state = {
        'phone': '9876543210',
        'credit_score': 780,
        'requested_amount': 1500000,
        'phase': 3
    }
    
    # Mock uploaded file
    class MockFile:
        name = "salary_slip.pdf"
    
    result = run_phase_3_conditional(state, MockFile())
    print(f"✅ ASSISTANT: {result['message'][:100]}...")
    print(f"   Decision: {result.get('decision')}")
    print(f"   Fraud Status: {result.get('fraud_status')}")
    
    assert result.get('decision') in ['Approved', 'Manual Review'], "Decision should be clear"
    assert result.get('fraud_status') in ['Clear', 'Blacklisted'], "Fraud status should be known"
    print("✅ Conditional review test passed!")
    return result


def test_phase_4_sanction():
    """Test Phase 4: Sanction - Generate sanction letter."""
    print("\n" + "="*60)
    print("TEST PHASE 4: SANCTION")
    print("="*60)
    
    state = {
        'phone': '9876543210',
        'requested_amount': 500000,
        'phase': 4
    }
    
    pdf_path = run_phase_4_sanction(state)
    print(f"✅ Sanction Letter Generated: {pdf_path}")
    
    assert pdf_path is not None, "PDF path should be generated"
    assert Path(pdf_path).exists(), f"PDF file should exist at {pdf_path}"
    print("✅ Sanction test passed!")
    return pdf_path


def test_invalid_phone():
    """Test error handling for invalid phone."""
    print("\n" + "="*60)
    print("TEST ERROR HANDLING: INVALID PHONE")
    print("="*60)
    
    state = {'phone': None, 'phase': 2, 'asked_for_phone': True}
    
    result = run_phase_2_underwriting("abc123", state)
    print(f"⚠️ ASSISTANT: {result['message']}")
    print(f"   Phone Verified: {result.get('phone')}")
    
    assert result.get('phone') is None, "Invalid phone should not verify"
    print("✅ Invalid phone handling test passed!")


def test_phone_not_in_db():
    """Test handling for phone not in CRM."""
    print("\n" + "="*60)
    print("TEST ERROR HANDLING: PHONE NOT IN CRM")
    print("="*60)
    
    state = {'phone': None, 'phase': 2, 'asked_for_phone': True}
    
    result = run_phase_2_underwriting("1111111111", state)
    print(f"⚠️ ASSISTANT: {result['message']}")
    print(f"   Verified: {result.get('verified')}")
    
    assert result.get('verified') == False, "Phone not in DB should not verify"
    print("✅ Phone not in CRM handling test passed!")


def run_all_tests():
    """Run all conversation flow tests."""
    print("\n" + "█"*60)
    print("█  BankGPT CONVERSATION FLOW TEST SUITE")
    print("█"*60)
    
    try:
        # Phase 1
        test_phase_1_sales()
        
        # Phase 2
        test_phase_2_phone_verification()
        test_phase_2_amount_within_limit()
        test_phase_2_amount_exceeds_limit()
        
        # Phase 3
        test_phase_3_conditional_review()
        
        # Phase 4
        test_phase_4_sanction()
        
        # Error Handling
        test_invalid_phone()
        test_phone_not_in_db()
        
        print("\n" + "█"*60)
        print("█  ✅ ALL TESTS PASSED!")
        print("█"*60)
        print("\n🎉 The conversation flow is working correctly.")
        print("   Start the app with: streamlit run app.py")
        print()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
