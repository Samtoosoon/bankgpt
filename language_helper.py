"""
language_helper.py - Language Detection and Response Templates
Supports English, Hindi, and Hinglish (mixed) responses
"""

from typing import Dict, Any
import re

def detect_language(text: str) -> str:
    """
    Detect language: 'english', 'hindi', or 'hinglish' (mixed)
    """
    if not text:
        return 'english'
    
    # Count Devanagari characters (Hindi)
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
    
    # Count English characters
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    total_chars = devanagari_chars + english_chars
    
    if total_chars == 0:
        return 'english'
    
    hindi_ratio = devanagari_chars / total_chars
    
    # Pure Hindi
    if hindi_ratio > 0.8:
        return 'hindi'
    # Pure English
    elif hindi_ratio < 0.2:
        return 'english'
    # Mixed (Hinglish)
    else:
        return 'hinglish'


# Phase 1: Sales Greeting Templates
PHASE_1_TEMPLATES = {
    'english': {
        'greeting': "🙏 Namaste! I am BankGPT from Tata Capital. I can help you get a personal loan in under 10 minutes. Are you looking for a loan today? (You can speak in Hindi or English)",
        'response': "🎉 Wonderful! I can offer you our **Personal Loan** at **11% interest rate**. How much amount do you need?",
    },
    'hindi': {
        'greeting': "🙏 नमस्ते! मैं BankGPT हूँ टाटा कैपिटल से। मैं आपको 10 मिनट में पर्सनल लोन दिला सकता हूँ। क्या आप आज लोन लेना चाहते हैं? (आप हिंदी या अंग्रेजी में बोल सकते हैं)",
        'response': "🎉 शानदार! मैं आपको हमारा **पर्सनल लोन** **11% ब्याज दर** पर दे सकता हूँ। आपको कितनी रकम की जरूरत है?",
    },
    'hinglish': {
        'greeting': "🙏 Namaste! Mein BankGPT hoon Tata Capital se. Main aapko 10 minute mein personal loan de sakta hoon. Kya aap aaj loan lena chahte ho? (Hindi ya English mein bol sakte ho)",
        'response': "🎉 Badhiya! Main aapko hamara **Personal Loan** **11% interest** par de sakta hoon. Aapko kitni raqam chahiye?",
    }
}

# Phase 2: Phone Verification Templates
PHASE_2_TEMPLATES = {
    'english': {
        'verify_prompt': "To check your best offer and pre-approved limit, may I have your 10-digit mobile number?",
        'invalid_phone': "⚠️ I didn't get a valid 10-digit number. Could you please repeat your phone number?",
        'phone_not_found': "I searched our system but didn't find a record for this number. Could you verify it?",
        'profile_found': "🎉 Great! I found your profile, {name}!\n\n**Your Profile:**\n• Credit Score: {credit_score} ✅\n• Monthly Income: ₹{income:,}\n• Pre-approved Limit: ₹{pre_approved_limit:,}\n\nNow, **how much amount do you need for your loan?**",
    },
    'hindi': {
        'verify_prompt': "आपका सबसे अच्छा ऑफर देखने के लिए, कृपया अपना 10-अंकीय मोबाइल नंबर दीजिए।",
        'invalid_phone': "⚠️ मुझे सही 10-अंकीय नंबर नहीं मिला। कृपया फिर से दीजिए।",
        'phone_not_found': "मुझे यह नंबर हमारे सिस्टम में नहीं मिला। कृपया वेरिफाई करें।",
        'profile_found': "🎉 बढ़िया! मुझे आपकी प्रोफाइल मिल गई, {name}!\n\n**आपकी प्रोफाइल:**\n• क्रेडिट स्कोर: {credit_score} ✅\n• मासिक आय: ₹{income:,}\n• पूर्व-अनुमोदित सीमा: ₹{pre_approved_limit:,}\n\nअब, **आपको कितनी रकम चाहिए?**",
    },
    'hinglish': {
        'verify_prompt': "Aapka best offer dekhne ke liye, apna 10-digit mobile number dije.",
        'invalid_phone': "⚠️ Mujhe sahi 10-digit number nahi mila. Dobara dije.",
        'phone_not_found': "Yeh number hamara system mein nahi mila. Verify kar lijiye.",
        'profile_found': "🎉 Badhiya! Aapki profile mil gyi, {name}!\n\n**Aapki Profile:**\n• Credit Score: {credit_score} ✅\n• Monthly Income: ₹{income:,}\n• Pre-approved Limit: ₹{pre_approved_limit:,}\n\nAb, **aapko kitni raqam chahiye?**",
    }
}

# Phase 2b: Eligibility Decision Templates
PHASE_2B_TEMPLATES = {
    'english': {
        'fast_track': "✅ Perfect! Your loan amount of ₹{amount:,} is within your pre-approved limit.\n\nYour loan is **APPROVED** at **11% interest rate**.\n\n• Monthly EMI: ₹{emi:,} (for 5 years)\n• Total Interest: ₹{total_interest:,.0f}\n\n🎉 Your sanction letter is ready! You can download it now.",
        'conditional': "⚠️ Your requested amount of ₹{amount:,} exceeds your pre-approved limit of ₹{limit:,}.\n\nNo worries! We can still process your request with additional verification.\n\n📄 **Please upload your latest Salary Slip** for quick verification.",
    },
    'hindi': {
        'fast_track': "✅ बिल्कुल! आपकी ₹{amount:,} की लोन राशि आपकी पूर्व-अनुमोदित सीमा के अंदर है।\n\nआपका लोन **अनुमोदित** है **11% ब्याज दर** पर।\n\n• मासिक EMI: ₹{emi:,} (5 साल के लिए)\n• कुल ब्याज: ₹{total_interest:,.0f}\n\n🎉 आपका स्वीकृति पत्र तैयार है! अब डाउनलोड कर सकते हैं।",
        'conditional': "⚠️ आपकी ₹{amount:,} की मांग आपकी ₹{limit:,} की सीमा से अधिक है।\n\nचिंता न करें! हम अतिरिक्त वेरिफिकेशन के साथ आपका अनुरोध प्रोसेस कर सकते हैं।\n\n📄 **अपनी नवीनतम सैलरी स्लिप अपलोड करें** तेजी से वेरिफिकेशन के लिए।",
    },
    'hinglish': {
        'fast_track': "✅ Bilkul! Aapki ₹{amount:,} ki loan amount aapki pre-approved limit ke andar hai.\n\nAapka loan **APPROVED** hai **11% interest rate** par.\n\n• Monthly EMI: ₹{emi:,} (5 saal ke liye)\n• Total Interest: ₹{total_interest:,.0f}\n\n🎉 Aapka sanction letter ready hai! Download kar sakte ho ab.",
        'conditional': "⚠️ Aapki ₹{amount:,} ki maang aapki ₹{limit:,} ki limit se zyada hai.\n\nFikr mat karo! Hum additional verification se aapka request process kar sakte hain.\n\n📄 **Apni latest Salary Slip upload karo** jaldi verification ke liye.",
    }
}

# Phase 3: Document Verification Templates
PHASE_3_TEMPLATES = {
    'english': {
        'approved': "🎉 **Excellent news!**\n\nYour Salary Slip has been verified successfully!\n\n**Your Loan Offer:**\n• Amount: ₹{amount:,}\n• Interest Rate: 11% per annum\n• EMI: ₹{emi:,}/month (60 months)\n• Status: **APPROVED** ✅\n\nYour sanction letter is ready for download!",
        'manual_review': "⚠️ We need to verify your document further.\n\nOur fraud detection flagged some items for manual review.\n\nA specialist will contact you within 24 hours. Thank you for your patience!",
    },
    'hindi': {
        'approved': "🎉 **शानदार खबर!**\n\nआपकी सैलरी स्लिप सफलतापूर्वक सत्यापित हुई!\n\n**आपका लोन ऑफर:**\n• राशि: ₹{amount:,}\n• ब्याज दर: 11% प्रति वर्ष\n• EMI: ₹{emi:,}/माह (60 महीने)\n• स्थिति: **अनुमोदित** ✅\n\nआपका स्वीकृति पत्र डाउनलोड के लिए तैयार है!",
        'manual_review': "⚠️ हमें आपके दस्तावेज़ की आगे जांच करनी है।\n\nहमारे欺fraud detection ने कुछ items को मैनुअल रिव्यू के लिए फ्लैग किया है।\n\nएक विशेषज्ञ 24 घंटे में आपसे संपर्क करेगा। आपके धैर्य के लिए धन्यवाद!",
    },
    'hinglish': {
        'approved': "🎉 **Bahut badhiya!**\n\nAapki Salary Slip successfully verify ho gyi!\n\n**Aapka Loan Offer:**\n• Amount: ₹{amount:,}\n• Interest Rate: 11% per annum\n• EMI: ₹{emi:,}/month (60 months)\n• Status: **APPROVED** ✅\n\nAapka sanction letter download ke liye ready hai!",
        'manual_review': "⚠️ Hume aapke document ki aur verification karni hai.\n\nHamara fraud detection kuch items ko manual review ke liye flag kiya hai.\n\nEk specialist 24 ghante mein aaphe contact karega. Aapke patience ke liye shukriya!",
    }
}

def get_response_template(phase: int, message_type: str, language: str, **kwargs) -> str:
    """
    Get template-based response for faster, consistent answers
    """
    templates_map = {
        1: PHASE_1_TEMPLATES,
        2: PHASE_2_TEMPLATES,
        2.5: PHASE_2B_TEMPLATES,
        3: PHASE_3_TEMPLATES,
    }
    
    if phase not in templates_map:
        return None
    
    # Ensure language exists in template
    if language not in templates_map[phase]:
        language = 'english'
    
    template = templates_map[phase].get(language, {}).get(message_type)
    
    if template is None:
        return None
    
    # Format template with provided kwargs
    try:
        return template.format(**kwargs)
    except KeyError:
        return template
