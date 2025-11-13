// AI Chatbot for E-Argo
class EArgoChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.createChatbotHTML();
        this.attachEventListeners();
        this.addWelcomeMessage();
    }

    createChatbotHTML() {
        const container = document.createElement('div');
        container.className = 'chatbot-container';
        container.innerHTML = `
            <button class="chatbot-toggle" id="chatbotToggle">💬</button>
            <div class="chatbot-window" id="chatbotWindow">
                <div class="chatbot-header">
                    <h3>🌾 E-Argo AI Assistant</h3>
                    <button class="chatbot-close" id="chatbotClose">×</button>
                </div>
                <div class="chatbot-messages" id="chatbotMessages"></div>
                <div class="chatbot-input-area">
                    <input type="text" class="chatbot-input" id="chatbotInput" placeholder="Ask me anything about agriculture...">
                    <button class="chatbot-send" id="chatbotSend">➤</button>
                </div>
            </div>
        `;
        document.body.appendChild(container);
    }

    attachEventListeners() {
        document.getElementById('chatbotToggle').addEventListener('click', () => this.toggleChat());
        document.getElementById('chatbotClose').addEventListener('click', () => this.toggleChat());
        document.getElementById('chatbotSend').addEventListener('click', () => this.sendMessage());
        document.getElementById('chatbotInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const window = document.getElementById('chatbotWindow');
        if (this.isOpen) {
            window.classList.add('active');
            document.getElementById('chatbotInput').focus();
        } else {
            window.classList.remove('active');
        }
    }

    addWelcomeMessage() {
        this.addMessage('bot', '👋 Hi! I\'m your AI agricultural assistant. I can help you with:\n\n🌾 Crop recommendations\n🦠 Disease detection\n💊 Fertilizer advice\n🌤️ Weather information\n\nAsk me anything!');
    }

    addMessage(sender, text) {
        const messagesContainer = document.getElementById('chatbotMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}`;
        
        if (sender === 'bot') {
            messageDiv.innerHTML = `
                <div class="chatbot-avatar">🌾</div>
                <div class="message-bubble">${this.formatMessage(text)}</div>
            `;
        } else {
            messageDiv.innerHTML = `<div class="message-bubble">${text}</div>`;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    formatMessage(text) {
        // Convert newlines to <br>
        return text.replace(/\n/g, '<br>');
    }

    showTyping() {
        const messagesContainer = document.getElementById('chatbotMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chatbot-message bot';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="chatbot-avatar">🌾</div>
            <div class="message-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTyping() {
        const typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();
    }

    async sendMessage() {
        const input = document.getElementById('chatbotInput');
        const message = input.value.trim();
        
        if (!message) return;

        this.addMessage('user', message);
        input.value = '';
        this.showTyping();

        // Simulate AI response (replace with actual API call)
        setTimeout(() => {
            this.hideTyping();
            const response = this.generateResponse(message);
            this.addMessage('bot', response);
        }, 1000 + Math.random() * 1000);
    }

    generateResponse(userMessage) {
        const message = userMessage.toLowerCase();
        
        // Crop recommendation queries
        if (message.includes('crop') || message.includes('plant') || message.includes('grow')) {
            return '🌾 For crop recommendations, I need:\n\n• Nitrogen (N) level\n• Phosphorous (P) level\n• Potassium (K) level\n• pH level\n• Rainfall\n• Your city name\n\nVisit the Crop Recommendation page to get personalized suggestions!';
        }
        
        // Disease detection queries
        if (message.includes('disease') || message.includes('sick') || message.includes('leaf')) {
            return '🦠 I can help detect plant diseases! Upload a photo of your plant leaf on the Disease Detection page. I can identify 38+ different diseases and provide treatment recommendations.';
        }
        
        // Fertilizer queries
        if (message.includes('fertilizer') || message.includes('nutrient') || message.includes('soil')) {
            return '💊 For fertilizer recommendations, I need:\n\n• Your crop type\n• Current Nitrogen (N) level\n• Current Phosphorous (P) level\n• Current Potassium (K) level\n\nCheck out the Fertilizer Recommendation page for expert advice!';
        }
        
        // Weather queries
        if (message.includes('weather') || message.includes('temperature') || message.includes('rain')) {
            return '🌤️ Weather data is automatically fetched from OpenWeatherMap API when you use crop recommendations. Just enter your city name and I\'ll get the latest temperature and humidity data!';
        }
        
        // Greeting
        if (message.includes('hi') || message.includes('hello') || message.includes('hey')) {
            return '👋 Hello! I\'m here to help with all your agricultural needs. What would you like to know?';
        }
        
        // Help
        if (message.includes('help') || message.includes('what can you do')) {
            return '🤖 I can help you with:\n\n✅ Crop recommendations based on soil conditions\n✅ Plant disease detection from images\n✅ Fertilizer suggestions for your crops\n✅ Weather information for your location\n\nJust ask me anything about agriculture!';
        }
        
        // Default response
        const responses = [
            'That\'s interesting! Can you tell me more about what you need help with?',
            'I\'m here to help with crop recommendations, disease detection, and fertilizer advice. What would you like to know?',
            'Great question! For specific recommendations, try using our Crop Recommendation or Disease Detection features.',
            'I can help you with agricultural decisions. Would you like to know about crops, diseases, or fertilizers?'
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    new EArgoChatbot();
});

