"""
gemini_integration.py - Google Gemini API integration for dynamic responses
Generates contextual loan offers and conversation based on applicant profile
"""

import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use gemini-2.5-flash (latest stable model with best performance/cost ratio)
    MODEL = genai.GenerativeModel('gemini-2.5-flash')
else:
    MODEL = None


class GeminiClient:
    """Wrapper for Gemini API interactions."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if Gemini API is configured."""
        return MODEL is not None
    
    @staticmethod
    def generate_sales_pitch(
        applicant_name: str,
        credit_score: Optional[int] = None,
        income: Optional[float] = None,
        pre_approved_limit: Optional[float] = None
    ) -> str:
        """Generate personalized sales pitch using Gemini."""
        
        if not GeminiClient.is_available():
            return GeminiClient._fallback_sales_pitch()
        
        profile_info = f"Applicant: {applicant_name}"
        if credit_score:
            profile_info += f", Credit Score: {credit_score}"
        if income:
            profile_info += f", Income: ₹{income:,}/month"
        if pre_approved_limit:
            profile_info += f", Pre-approved Limit: ₹{pre_approved_limit:,}"
        
        prompt = f"""
        You are BankGPT, a persuasive and friendly personal loan assistant.
        
        {profile_info}
        
        Generate a warm, encouraging sales pitch (2-3 sentences) offering a personal loan at 11% interest rate.
        Make the applicant feel valued and highlight how quickly we can process their loan.
        Use appropriate emojis and Indian rupee symbols.
        """
        
        try:
            response = MODEL.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return GeminiClient._fallback_sales_pitch()
    
    @staticmethod
    def generate_eligibility_response(
        applicant_name: str,
        credit_score: int,
        income: float,
        pre_approved_limit: float,
        requested_amount: float
    ) -> str:
        """Generate eligibility decision message using Gemini."""
        
        if not GeminiClient.is_available():
            return GeminiClient._fallback_eligibility_response(
                applicant_name, credit_score, pre_approved_limit, requested_amount
            )
        
        prompt = f"""
        You are BankGPT, a professional loan processor.
        
        Applicant: {applicant_name}
        Credit Score: {credit_score}
        Monthly Income: ₹{income:,}
        Pre-approved Limit: ₹{pre_approved_limit:,}
        Requested Amount: ₹{requested_amount:,}
        
        Generate a professional response (2-3 sentences) explaining their eligibility status.
        If requested_amount <= pre_approved_limit: Congratulate them on approval and show EMI.
        If requested_amount > pre_approved_limit: Explain the amount exceeds limit and ask for documents.
        Use appropriate emojis and financial terminology.
        """
        
        try:
            response = MODEL.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return GeminiClient._fallback_eligibility_response(
                applicant_name, credit_score, pre_approved_limit, requested_amount
            )
    
    @staticmethod
    def generate_approval_message(
        applicant_name: str,
        loan_amount: float,
        emi: float,
        tenure_months: int = 60
    ) -> str:
        """Generate approval message with EMI details using Gemini."""
        
        if not GeminiClient.is_available():
            return GeminiClient._fallback_approval_message(applicant_name, loan_amount, emi)
        
        prompt = f"""
        You are BankGPT, delivering good news to a loan applicant.
        
        Applicant: {applicant_name}
        Approved Loan Amount: ₹{loan_amount:,}
        Monthly EMI: ₹{emi:,}
        Tenure: {tenure_months} months
        
        Generate an enthusiastic approval message (2-3 sentences) celebrating their approval.
        Include the loan amount and EMI clearly.
        Mention that their sanction letter is ready for download.
        Use celebratory emojis like 🎉 ✅
        """
        
        try:
            response = MODEL.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return GeminiClient._fallback_approval_message(applicant_name, loan_amount, emi)
    
    @staticmethod
    def generate_document_verification_response(
        applicant_name: str,
        fraud_status: str,
        loan_amount: float
    ) -> str:
        """Generate document verification response using Gemini."""
        
        if not GeminiClient.is_available():
            return GeminiClient._fallback_document_response(
                applicant_name, fraud_status, loan_amount
            )
        
        is_approved = fraud_status == "Clear"
        prompt = f"""
        You are BankGPT, verifying an applicant's salary slip.
        
        Applicant: {applicant_name}
        Document Status: {'Verified ✅' if is_approved else 'Requires Manual Review ⚠️'}
        Loan Amount: ₹{loan_amount:,}
        
        Generate a response {'celebrating their approval' if is_approved else 'explaining the review process'} (2-3 sentences).
        If approved, mention their sanction letter is ready.
        If not approved, explain that a specialist will contact them within 24 hours.
        """
        
        try:
            response = MODEL.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return GeminiClient._fallback_document_response(
                applicant_name, fraud_status, loan_amount
            )
    
    # Fallback messages when Gemini is not available
    @staticmethod
    def _fallback_sales_pitch() -> str:
        return (
            "🎉 That's wonderful! I am BankGPT, your personal loan assistant powered by AI. "
            "I can get you a loan approval in under 10 minutes!\n\n"
            "Based on your needs, I can offer you our **Special Personal Loan** at a competitive rate of **11% per annum**.\n\n"
            "To check your best offer and pre-approved limit, **may I have your 10-digit mobile number**?"
        )
    
    @staticmethod
    def _fallback_eligibility_response(
        name: str,
        score: int,
        limit: float,
        amount: float
    ) -> str:
        if amount <= limit:
            return (
                f"✅ Perfect! Your loan amount of ₹{amount:,} is within your pre-approved limit.\n\n"
                f"Your loan is **APPROVED** at **11% interest rate**.\n\n"
                f"🎉 Your sanction letter is ready!"
            )
        else:
            return (
                f"⚠️ Your requested amount of ₹{amount:,} exceeds your pre-approved limit of ₹{limit:,}.\n\n"
                f"📄 **Please upload your latest Salary Slip** for quick verification."
            )
    
    @staticmethod
    def _fallback_approval_message(name: str, amount: float, emi: float) -> str:
        return (
            f"🎉 **Excellent news!**\n\n"
            f"Your Loan of ₹{amount:,} is **APPROVED** at **11% per annum**!\n\n"
            f"• Monthly EMI: ₹{emi:,}\n"
            f"• Your sanction letter is ready for download!"
        )
    
    @staticmethod
    def _fallback_document_response(name: str, fraud_status: str, amount: float) -> str:
        if fraud_status == "Clear":
            return (
                f"🎉 **Excellent news!**\n\n"
                f"Your Salary Slip has been verified successfully!\n\n"
                f"Loan of ₹{amount:,} is **APPROVED**! ✅"
            )
        else:
            return (
                f"⚠️ We need to verify your document further.\n\n"
                f"A specialist will contact you within 24 hours. Thank you for your patience!"
            )
