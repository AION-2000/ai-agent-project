import os
import sys
import json
import base64
import io
from flask import Flask, render_template, request, jsonify

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Starting Flask app...")

# Initialize Flask app
app = Flask(__name__)

# Set template and static folders
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')

app.template_folder = template_dir
app.static_folder = static_dir

print(f"Template directory: {template_dir}")
print(f"Static directory: {static_dir}")
print(f"Template dir exists: {os.path.exists(template_dir)}")
print(f"Static dir exists: {os.path.exists(static_dir)}")

@app.route('/')
def index():
    try:
        print("Attempting to render index.html...")
        index_path = os.path.join(app.template_folder, 'index.html')
        print(f"Index template path: {index_path}")
        print(f"Index template exists: {os.path.exists(index_path)}")
        
        if not os.path.exists(index_path):
            return create_fallback_index()
            
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering index: {e}")
        return create_fallback_index()

@app.route('/chat')
def chat_page():
    try:
        print("Attempting to render chat.html...")
        chat_path = os.path.join(app.template_folder, 'chat.html')
        print(f"Chat template path: {chat_path}")
        print(f"Chat template exists: {os.path.exists(chat_path)}")
        
        if not os.path.exists(chat_path):
            return create_fallback_chat()
            
        return render_template('chat.html')
    except Exception as e:
        print(f"Error rendering chat: {e}")
        return create_fallback_chat()

@app.route('/static/<path:filename>')
def static_files(filename):
    try:
        print(f"Serving static file: {filename}")
        file_path = os.path.join(app.static_folder, filename)
        print(f"Static file path: {file_path}")
        print(f"Static file exists: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determine content type
            if filename.endswith('.css'):
                content_type = 'text/css'
            elif filename.endswith('.js'):
                content_type = 'text/javascript'
            elif filename.endswith('.png'):
                content_type = 'image/png'
            elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                content_type = 'image/jpeg'
            else:
                content_type = 'text/plain'
            
            return content, 200, {'Content-Type': content_type}
        else:
            return "File not found", 404
            
    except Exception as e:
        print(f"Error serving static file {filename}: {e}")
        return "Error serving file", 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        print("Chat API called...")
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        
        user_message = data.get('message', '')
        print(f"User message: {user_message}")
        
        # Simple response for now
        response_text = f"You said: {user_message}. This is a test response from AIOVerse!"
        
        # Try to generate audio (fallback if gTTS fails)
        try:
            from gtts import gTTS
            tts = gTTS(text=response_text, lang='en')
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            audio_base64 = base64.b64encode(mp3_fp.read()).decode('utf-8')
            print("Audio generated successfully")
        except Exception as audio_error:
            print(f"Audio generation failed: {audio_error}")
            audio_base64 = ""
        
        return jsonify({
            'text': response_text,
            'audio': f"data:audio/mp3;base64,{audio_base64}" if audio_base64 else ""
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Chat service temporarily unavailable"}), 500

def create_fallback_index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AIOVerse - AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #0f0f23, #1a1a2e); color: white; margin: 0; padding: 20px; min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; text-align: center; padding: 50px 20px; }
            h1 { font-size: 3rem; color: #00d4ff; margin-bottom: 20px; }
            p { font-size: 1.2rem; margin-bottom: 30px; color: rgba(255,255,255,0.8); }
            .btn { background: linear-gradient(45deg, #00d4ff, #0099cc); color: white; padding: 15px 30px; border: none; border-radius: 25px; font-size: 1.1rem; text-decoration: none; display: inline-block; transition: transform 0.3s; }
            .btn:hover { transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AIOVerse</h1>
            <p>Welcome to AIOVerse - Your AI Assistant with Voice & Text</p>
            <p>Experience the future of AI assistants with seamless text and voice interactions</p>
            <a href="/chat" class="btn">Start Chat</a>
        </div>
    </body>
    </html>
    '''

def create_fallback_chat():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AIOVerse Chat</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #0f0f23, #1a1a2e); color: white; margin: 0; height: 100vh; display: flex; flex-direction: column; }
            .header { padding: 20px; background: rgba(0,0,0,0.3); border-bottom: 1px solid rgba(255,255,255,0.1); }
            .header h1 { margin: 0; color: #00d4ff; }
            .chat-area { flex: 1; padding: 20px; overflow-y: auto; }
            .message { margin: 10px 0; padding: 10px 15px; border-radius: 15px; max-width: 70%; }
            .user-message { background: linear-gradient(45deg, #00d4ff, #0099cc); margin-left: auto; }
            .bot-message { background: rgba(255,255,255,0.1); }
            .input-area { padding: 20px; background: rgba(0,0,0,0.3); display: flex; gap: 10px; }
            input { flex: 1; padding: 15px; border: none; border-radius: 25px; background: rgba(255,255,255,0.1); color: white; font-size: 16px; }
            input::placeholder { color: rgba(255,255,255,0.5); }
            button { padding: 15px 20px; border: none; border-radius: 25px; background: linear-gradient(45deg, #00d4ff, #0099cc); color: white; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 AIOVerse Chat</h1>
            <p>Type a message to start chatting!</p>
        </div>
        <div class="chat-area" id="chatArea">
            <div class="message bot-message">Hello! I'm AIOVerse. How can I help you today?</div>
        </div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Type your message...">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const chatArea = document.getElementById('chatArea');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Add user message
                chatArea.innerHTML += `<div class="message user-message">${message}</div>`;
                input.value = '';
                chatArea.scrollTop = chatArea.scrollHeight;
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    chatArea.innerHTML += `<div class="message bot-message">${data.text}</div>`;
                    
                    if (data.audio) {
                        const audio = new Audio(data.audio);
                        audio.play().catch(e => console.log('Audio play failed:', e));
                    }
                } catch (error) {
                    chatArea.innerHTML += `<div class="message bot-message">Sorry, I encountered an error. Please try again.</div>`;
                }
                
                chatArea.scrollTop = chatArea.scrollHeight;
            }
            
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    '''

# Vercel handler function
def handler(event, context):
    try:
        print(f"Handler called with event: {json.dumps(event, indent=2)}")
        
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        print(f"Processing: {method} {path}")
        
        with app.test_client() as client:
            if method == 'GET':
                response = client.get(path)
            elif method == 'POST':
                body = event.get('body', '{}')
                if event.get('isBase64Encoded', False):
                    body = base64.b64decode(body).decode('utf-8')
                
                response = client.post(
                    path,
                    data=body,
                    content_type='application/json'
                )
            else:
                return {
                    'statusCode': 405,
                    'body': 'Method Not Allowed'
                }
            
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        print(f"Handler error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": f"Server error: {str(e)}"})
        }

# For local development
if __name__ == '__main__':
    print("Running in local development mode...")
    app.run(debug=True, port=5000)