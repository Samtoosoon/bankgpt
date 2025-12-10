#!/usr/bin/env python
"""
Verification: The exact scenario from user request
"""

from master_agent import run_phase_1_sales

print("=" * 60)
print("VERIFICATION: USER REQUEST SCENARIO")
print("=" * 60)

# The exact scenario from user request
print("\nScenario from User Request:")
print('User Input: "i need a home loan"')

result = run_phase_1_sales('i need a home loan', first_message=False)

print(f'Bot Phase: {result["phase"]} (expected: 2 - underwriting)')
print(f'Bot Message:\n{result["message"]}')

print("\n" + "=" * 60)
if result['phase'] == 2:
    print("✅ SUCCESS!")
    print("\nThe exact request from user now works:")
    print('  User: "i need a home loan"')
    print('  Bot: Moves to Phase 2 (underwriting)')
    print('  Result: Asks for phone number to proceed')
else:
    print("❌ Issue detected")

print("=" * 60)
