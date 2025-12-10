#!/usr/bin/env python
"""Debug LLM response selection"""

from gemini_integration import GeminiClient

client = GeminiClient()

test_cases = [
    "i need a home loan",
    "yes",
    "tell me more",
    "absolutely, let's do this",
    "no thanks"
]

print("=" * 60)
print("LLM RESPONSE SELECTION TEST")
print("=" * 60)

for user_input in test_cases:
    print(f"\nUser input: '{user_input}'")
    
    response_options = {
        'positive': "🎉 Wonderful! I can offer you our **Personal Loan** at **11% interest rate**. How much amount do you need?",
        'neutral': "I'm here to help! Are you interested in a personal loan?",
        'greeting': "🙏 Namaste! I am BankGPT from Tata Capital. Are you looking for a loan today?"
    }
    
    prompt = f"""
You are a helpful loan sales assistant. The user has responded to "Are you looking for a loan today?".

User's response: "{user_input}"

Based on the user's response, select the BEST response from these options:

1. POSITIVE: "{response_options['positive']}"
2. NEUTRAL: "{response_options['neutral']}"
3. GREETING: "{response_options['greeting']}"

Respond with ONLY the number (1, 2, or 3) of the best response.
"""
    
    try:
        response = client.generate_text(prompt)
        print(f"LLM Response: '{response.strip()}'")
        
        if '1' in str(response):
            print("→ Selected: POSITIVE (Phase 2)")
        elif '2' in str(response):
            print("→ Selected: NEUTRAL (Phase 1)")
        elif '3' in str(response):
            print("→ Selected: GREETING (Phase 1)")
        else:
            print(f"→ Unrecognized: {response}")
    except Exception as e:
        print(f"Error: {e}")
