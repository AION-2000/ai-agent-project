import os
import sys
import json
import random
import base64
import io
from flask import Flask, render_template, request, jsonify
from gtts import gTTS

# Initialize the Flask app
app = Flask(__name__)

# Define the VoiceAgent class directly in app.py to avoid import issues
class VoiceAgent:
    def __init__(self):
        # Define responses directly in the class to avoid file path issues
        self.responses = {
            "greetings": {
                "hello": ["Hello! I'm AIOVerse, your AI assistant. How can I help you today?", "Hi there! I'm AIOVerse. What can I do for you?"],
                "hi": ["Hi! I'm AIOVerse. How are you?", "Hello! I'm AIOVerse. Nice to meet you."],
                "hey": ["Hey! I'm AIOVerse. What's up?", "Hey! I'm AIOVerse. How can I assist you?"]
            },
            "categories": {
                "about": {
                    "what are you": ["I am AIOVerse, an AI assistant designed to help with your questions.", "I'm AIOVerse, a virtual assistant here to assist you."],
                    "what can you do": ["I can answer questions, provide information, and have conversations with you.", "I can help with a variety of tasks including answering questions and providing recommendations."]
                },
                "help": {
                    "help": ["I'm here to help! What do you need assistance with?", "Sure, I can help. What do you need?"],
                    "how do you work": ["Just type or speak your question, and I'll do my best to answer it.", "I use natural language processing to understand and respond to your queries."]
                }
            },
            "fallback": [
                "I'm not sure how to respond to that.",
                "Could you please rephrase that?",
                "I don't have an answer for that right now.",
                "That's beyond my current capabilities."
            ]
        }
    
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
        try:
            tts = gTTS(text=text, lang='en')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
            return audio_base64
        except Exception as e:
            print(f"Error generating audio: {e}")
            return ""

# Initialize the agent
agent = VoiceAgent()

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error rendering index template: {str(e)}", 500

@app.route('/chat')
def chat_page():
    try:
        return render_template('chat.html')
    except Exception as e:
        return f"Error rendering chat template: {str(e)}", 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        
        user_message = data.get('message', '')
        response_text = agent.get_response(user_message)
        audio_base64 = agent.get_audio_response(response_text)
        
        return jsonify({
            'text': response_text,
            'audio': f"data:audio/mp3;base64,{audio_base64}"
        })
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# Vercel serverless function handler
def handler(event, context):
    # Simple request handler for Vercel
    try:
        # Extract path from the event
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        # Handle favicon.ico requests
        if path == '/favicon.ico':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'image/x-icon'},
                'body': ''
            }
        
        # Handle different routes
        if path == '/':
            # Render index page
            with app.test_client() as client:
                response = client.get('/')
                return {
                    'statusCode': response.status_code,
                    'headers': dict(response.headers),
                    'body': response.get_data(as_text=True)
                }
        elif path == '/chat':
            if method == 'GET':
                # Render chat page
                with app.test_client() as client:
                    response = client.get('/chat')
                    return {
                        'statusCode': response.status_code,
                        'headers': dict(response.headers),
                        'body': response.get_data(as_text=True)
                    }
            elif method == 'POST':
                # Handle chat POST request
                body = event.get('body', '{}')
                headers = event.get('headers', {})
                
                with app.test_client() as client:
                    response = client.post(
                        '/chat',
                        data=body,
                        headers=headers,
                        content_type=headers.get('content-type', 'application/json')
                    )
                    return {
                        'statusCode': response.status_code,
                        'headers': dict(response.headers),
                        'body': response.get_data(as_text=True)
                    }
        
        # Default response for other routes
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>404 Not Found</h1>'
        }
    except Exception as e:
        print(f"Error in handler: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>500 Internal Server Error</h1><p>{str(e)}</p>'
        }

# For local development
if __name__ == '__main__':
    app.run(debug=True)