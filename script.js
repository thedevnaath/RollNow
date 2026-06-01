// Import the official Google Gemini Web SDK
import { GoogleGenerativeAI } from "https://esm.run/@google/generative-ai";

// GitHub Actions will replace this string during deployment
const API_KEY = "INJECT_API_KEY_HERE"; 
const genAI = new GoogleGenerativeAI(API_KEY);

// Set up the specific model and system instructions for a customer service agent
const model = genAI.getGenerativeModel({ 
    model: "gemini-1.5-flash", // Lightning fast for live chat
    systemInstruction: "You are an elite customer service agent for an experimental AI SaaS company. Be concise, helpful, and polite. Keep your answers under 3 sentences."
});

// Start a chat session to remember history
const chat = model.startChat({
    history: [],
});

// UI Elements
const chatToggle = document.getElementById('chat-toggle');
const chatWidget = document.getElementById('chat-widget');
const closeChat = document.getElementById('close-chat');
const sendBtn = document.getElementById('send-btn');
const chatInput = document.getElementById('chat-input');
const chatHistory = document.getElementById('chat-history');

// Toggle Chat Window
chatToggle.addEventListener('click', () => chatWidget.classList.add('open'));
closeChat.addEventListener('click', () => chatWidget.classList.remove('open'));

// Append messages to the UI
function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('msg', sender);
    msgDiv.textContent = text;
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight; // Auto-scroll to bottom
}

// Handle sending messages
async function handleSend() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Show user message
    addMessage(text, 'user');
    chatInput.value = '';

    // Show temporary "Typing..." state
    const typingId = "typing-" + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('msg', 'ai');
    typingDiv.id = typingId;
    typingDiv.textContent = "Typing...";
    chatHistory.appendChild(typingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    try {
        // Send to Gemini
        const result = await chat.sendMessage(text);
        const responseText = result.response.text();
        
        // Replace typing state with actual response
        document.getElementById(typingId).textContent = responseText;
    } catch (error) {
        document.getElementById(typingId).textContent = "Error: Could not connect to API.";
        console.error(error);
    }
}

// Listen for Enter key or Button click
sendBtn.addEventListener('click', handleSend);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
});
