import json
import random
import base64
import io
from gtts import gTTS

class VoiceAgent:
    def __init__(self, responses_path='responses.json'):
        with open(responses_path, 'r') as f:
            self.responses = json.load(f)
    
    def get_response(self, user_input):
        user_input = user_input.lower()
        
        # Check greetings
        for pattern, responses in self.responses.get('greetings', {}).items():
            if pattern in user_input:
                return random.choice(responses)
        
        # Check other categories
        for category, patterns in self.responses.get('categories', {}).items():
            for pattern, responses in patterns.items():
                if pattern in user_input:
                    return random.choice(responses)
        
        # Fallback
        return random.choice(self.responses.get('fallback', ["I don't understand. Please try again."]))
    
    def get_audio_response(self, text):
        tts = gTTS(text=text, lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
        return audio_base64