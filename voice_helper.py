# voice_helper.py - Speech recognition and text-to-speech utilities
"""
Handles voice input (speech-to-text) and voice output (text-to-speech).
Uses SpeechRecognition for input and pyttsx3 for output.
"""

import speech_recognition as sr
import pyttsx3
import threading
from typing import Optional, Tuple

# Initialize TTS engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Speaking rate
tts_engine.setProperty('volume', 0.9)  # Volume (0-1)


def speak_text(text: str, language: str = 'english', async_mode: bool = True) -> None:
    """
    Convert text to speech and play it.
    
    Args:
        text: Text to speak
        language: Language for speech output
        async_mode: If True, speak in background thread
    """
    try:
        # Set language-specific voice
        voices = tts_engine.getProperty('voices')
        if language == 'hindi':
            # Try to find Hindi voice, fallback to default
            tts_engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
        else:
            # Use default English voice
            tts_engine.setProperty('voice', voices[0].id if voices else None)
        
        # Queue the text
        tts_engine.say(text)
        
        # Speak
        if async_mode:
            # Run in background thread
            thread = threading.Thread(target=tts_engine.runAndWait)
            thread.daemon = True
            thread.start()
        else:
            # Block until done
            tts_engine.runAndWait()
    
    except Exception as e:
        print(f"TTS Error: {e}")


def recognize_speech() -> Optional[str]:
    """
    Capture audio from microphone and convert to text.
    
    Returns:
        Recognized text or None if failed
    """
    recognizer = sr.Recognizer()
    
    try:
        # Use default microphone
        with sr.Microphone() as source:
            print("🎤 Listening...")
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)
            # Listen for audio (up to 10 seconds)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
        
        # Try to recognize using Google Speech Recognition API
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    
    except sr.UnknownValueError:
        print("❌ Could not understand audio. Please speak clearly.")
        return None
    except sr.RequestError as e:
        print(f"❌ Speech recognition service error: {e}")
        return None
    except Exception as e:
        print(f"❌ Voice input error: {e}")
        return None


def is_voice_available() -> bool:
    """Check if voice input/output is available."""
    try:
        # Check if we can access microphone
        with sr.Microphone() as source:
            pass
        return True
    except:
        return False
