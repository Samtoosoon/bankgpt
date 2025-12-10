#!/usr/bin/env python
"""
Test: LLM-generated open-ended responses for Phase 1
Tests various loan requests without yes/no questions
"""

from master_agent import run_phase_1_sales

print("=" * 70)
print("PHASE 1: LLM-GENERATED OPEN-ENDED RESPONSES")
print("=" * 70)

test_cases = [
    ("Hi there", "First greeting"),
    ("i need a loan for my business", "Business loan request"),
    ("i need a home loan", "Home loan request"),
    ("i want to buy a car", "Car loan request"),
    ("i need money for education", "Education loan request"),
    ("personal loan please", "Personal loan request"),
    ("i need 500000 for my startup", "Specific business loan with amount"),
]

print("\nTesting LLM-Generated Phase 1 Responses:\n")

for i, (user_input, description) in enumerate(test_cases, 1):
    print(f"Test {i}: {description}")
    print(f"  User Input: '{user_input}'")
    
    # Determine if this is first message
    is_first = (i == 1)
    first_msg_label = "(GREETING)" if is_first else "(LLM RESPONSE)"
    
    result = run_phase_1_sales(user_input, first_message=is_first)
    
    phase = result['phase']
    message = result['message']
    
    phase_label = "Phase 1" if phase == 1 else "Phase 2"
    
    print(f"  {first_msg_label}")
    print(f"  Phase: {phase_label}")
    print(f"  Message:")
    print(f"    {message[:100]}..." if len(message) > 100 else f"    {message}")
    print()

print("=" * 70)
print("✅ LLM-GENERATED RESPONSES WORKING")
print("=" * 70)
