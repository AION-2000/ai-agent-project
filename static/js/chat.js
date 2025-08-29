document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const voiceBtn = document.getElementById('voiceBtn');
    const audioPlayer = document.getElementById('audioPlayer');
    
    // Add event listener for send button
    sendBtn.addEventListener('click', sendMessage);
    
    // Add event listener for Enter key
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Function to send message
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, 'user-message');
        
        // Clear input
        userInput.value = '';
        
        // Send to server
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({message: message})
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                addMessage('Sorry, there was an error processing your request. Please try again.', 'bot-message');
                return;
            }
            
            // Add bot response to chat
            addMessage(data.text, 'bot-message');
            
            // Play audio response if available
            if (data.audio) {
                audioPlayer.src = data.audio;
                audioPlayer.play().catch(e => console.error('Audio play error:', e));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Sorry, there was an error connecting to the server. Please try again.', 'bot-message');
        });
    }
    
    // Function to add message to chat
    function addMessage(text, className) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        messageElement.textContent = text;
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Voice recognition (if supported)
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            sendMessage();
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            voiceBtn.classList.remove('listening');
        };
        
        recognition.onend = function() {
            voiceBtn.classList.remove('listening');
        };
        
        voiceBtn.addEventListener('click', function() {
            if (voiceBtn.classList.contains('listening')) {
                recognition.stop();
                voiceBtn.classList.remove('listening');
            } else {
                recognition.start();
                voiceBtn.classList.add('listening');
            }
        });
    } else {
        voiceBtn.style.display = 'none';
    }
});