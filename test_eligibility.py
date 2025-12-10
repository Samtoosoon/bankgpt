# test_eligibility.py - Quick test of eligibility routing logic

from eligibility import check_eligibility

# Test cases
test_cases = [
    {
        "name": "Fast Track (within limit)",
        "user": {"pre_approved_limit": 1000000, "credit_score": 780},
        "amount": 500000,
        "expected": "FAST_TRACK"
    },
    {
        "name": "Conditional Review (2x limit)",
        "user": {"pre_approved_limit": 500000, "credit_score": 680},
        "amount": 900000,
        "expected": "CONDITIONAL_REVIEW"
    },
    {
        "name": "Conditional Review (high score, high amount)",
        "user": {"pre_approved_limit": 500000, "credit_score": 750},
        "amount": 1200000,
        "expected": "CONDITIONAL_REVIEW"
    },
    {
        "name": "Hard Rejection (too high amount)",
        "user": {"pre_approved_limit": 500000, "credit_score": 680},
        "amount": 1500000,
        "expected": "HARD_REJECTION"
    },
    {
        "name": "Hard Rejection (low score)",
        "user": {"pre_approved_limit": 500000, "credit_score": 600},
        "amount": 400000,
        "expected": "HARD_REJECTION"
    },
]

print("Testing Eligibility Logic\n" + "="*50)

for test in test_cases:
    result = check_eligibility(test["amount"], test["user"])
    status = "✅ PASS" if result == test["expected"] else "❌ FAIL"
    print(f"{status} | {test['name']}")
    print(f"  → Amount: {test['amount']:,}, Limit: {test['user']['pre_approved_limit']:,}, Score: {test['user']['credit_score']}")
    print(f"  → Expected: {test['expected']}, Got: {result}\n")
