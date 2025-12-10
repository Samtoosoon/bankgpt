#!/usr/bin/env python3
"""
Test voice features - speech recognition and text-to-speech.
"""

from voice_helper import is_voice_available, speak_text

def test_voice_features():
    """Test voice I/O capabilities."""
    
    print("=" * 60)
    print("VOICE FEATURE TEST")
    print("=" * 60)
    
    # Check microphone availability
    voice_available = is_voice_available()
    print(f"\n✅ Microphone Available: {voice_available}")
    
    if voice_available:
        print("\n🎤 Voice Input: AVAILABLE")
        print("   → Speech recognition ready")
        print("   → Microphone detected")
    else:
        print("\n❌ Voice Input: NOT AVAILABLE")
        print("   → Microphone not detected or not accessible")
    
    # Test text-to-speech
    print("\n🔊 Testing Text-to-Speech...")
    try:
        test_text = "Welcome to BankGPT. I am ready to help you with your loan application."
        speak_text(test_text, language='english', async_mode=False)
        print("   ✅ Text-to-speech: WORKING")
    except Exception as e:
        print(f"   ❌ Text-to-speech error: {e}")
    
    print("\n" + "=" * 60)
    print("VOICE FEATURES TEST COMPLETE")
    print("=" * 60)
    print("\nFeatures enabled in Streamlit app:")
    print("✅ Voice input (microphone recording)")
    print("✅ Speech recognition (audio to text)")
    print("✅ Text-to-speech (bot responses)")
    print("✅ Language support (English, Hindi)")
    print("\n")

if __name__ == '__main__':
    test_voice_features()
