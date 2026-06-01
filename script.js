const API_KEY = "INJECT_API_KEY_HERE"; 
const HOST = "generativelanguage.googleapis.com";
// 1. Updated to the official v1beta BidiGenerateContent endpoint
const WS_URL = `wss://${HOST}/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=${API_KEY}`;

let ws;
let audioCtx;
let mediaStream;
let audioProcessor;
let isCalling = false;

// UI Elements
const chatToggle = document.getElementById('chat-toggle');
const chatWidget = document.getElementById('chat-widget');
const closeChat = document.getElementById('close-chat');
const sendBtn = document.getElementById('send-btn');
const callBtn = document.getElementById('call-btn');
const chatInput = document.getElementById('chat-input');
const chatHistory = document.getElementById('chat-history');
const statusIndicator = document.getElementById('status-indicator');

// Toggle UI
chatToggle.addEventListener('click', () => chatWidget.classList.add('open'));
closeChat.addEventListener('click', () => chatWidget.classList.remove('open'));

function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('msg', sender);
    msgDiv.textContent = text;
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Initialize WebSocket Connection
function connectWebSocket() {
    return new Promise((resolve) => {
        ws = new WebSocket(WS_URL);
        
        ws.onopen = () => {
            statusIndicator.textContent = "🟢 Connected";
            
            // 2. Initializing Gemini 3.1 Flash Live Preview
            ws.send(JSON.stringify({
                setup: { 
                    model: "models/gemini-3.1-flash-live-preview",
                    generationConfig: {
                        responseModalities: ["AUDIO"] // Forces the AI to reply natively in audio
                    },
                    systemInstruction: {
                        parts: [{ text: "You are an elite customer service agent. Be concise, helpful, and polite. Keep your answers short." }]
                    }
                }
            }));
            resolve();
        };

        ws.onmessage = async (evt) => {
            let msg;
            try {
                if (evt.data instanceof Blob) {
                    const text = await evt.data.text();
                    msg = JSON.parse(text);
                } else {
                    msg = JSON.parse(evt.data);
                }
                handleServerMessage(msg);
            } catch (e) { console.error("Error parsing message", e); }
        };

        ws.onclose = () => {
            statusIndicator.textContent = "🔴 Disconnected";
            stopVoiceCall();
        };
    });
}

// Handle incoming Audio and Text from Gemini
function handleServerMessage(msg) {
    if (msg.serverContent && msg.serverContent.modelTurn) {
        const parts = msg.serverContent.modelTurn.parts;
        for (const part of parts) {
            // If the model sends Text
            if (part.text) {
                addMessage(part.text, 'ai');
            }
            // If the model sends Audio (Base64 PCM)
            if (part.inlineData && part.inlineData.data) {
                playAudioChunk(part.inlineData.data);
            }
        }
    }
}

// Decode Base64 Audio and play it natively in browser
function playAudioChunk(base64Str) {
    if (!audioCtx) return;
    
    const binaryString = window.atob(base64Str);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    
    // Convert PCM16 to Float32 for Web Audio API
    const pcm16 = new Int16Array(bytes.buffer);
    const float32 = new Float32Array(pcm16.length);
    for (let i = 0; i < pcm16.length; i++) {
        float32[i] = pcm16[i] / 32768.0;
    }
    
    // Gemini Live API returns audio at 24kHz
    const buffer = audioCtx.createBuffer(1, float32.length, 24000);
    buffer.getChannelData(0).set(float32);
    
    const source = audioCtx.createBufferSource();
    source.buffer = buffer;
    source.connect(audioCtx.destination);
    source.start();
}

// Send Text to the Live API
async function sendTextMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        await connectWebSocket();
    }
    
    addMessage(text, 'user');
    chatInput.value = '';

    ws.send(JSON.stringify({
        clientContent: {
            turns: [{ role: "user", parts: [{ text: text }] }],
            turnComplete: true
        }
    }));
}

sendBtn.addEventListener('click', sendTextMessage);
chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendTextMessage(); });

// Capture Microphone and stream 16kHz PCM to Live API
async function startVoiceCall() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        await connectWebSocket();
    }
    
    // Force AudioContext to 16kHz (Required by Gemini Live API input)
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const source = audioCtx.createMediaStreamSource(mediaStream);
        
        // ScriptProcessor is used for raw PCM extraction
        audioProcessor = audioCtx.createScriptProcessor(4096, 1, 1);
        source.connect(audioProcessor);
        audioProcessor.connect(audioCtx.destination);
        
        audioProcessor.onaudioprocess = (e) => {
            const float32 = e.inputBuffer.getChannelData(0);
            const pcm16 = new Int16Array(float32.length);
            for(let i=0; i<float32.length; i++) {
                pcm16[i] = Math.max(-1, Math.min(1, float32[i])) * 32767;
            }
            
            // Convert to Base64
            const uint8 = new Uint8Array(pcm16.buffer);
            let binary = '';
            for (let i = 0; i < uint8.byteLength; i++) {
                binary += String.fromCharCode(uint8[i]);
            }
            const base64 = window.btoa(binary);
            
            // Stream audio chunk to Gemini
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    realtimeInput: {
                        mediaChunks: [{ mimeType: "audio/pcm;rate=16000", data: base64 }]
                    }
                }));
            }
        };
        
        isCalling = true;
        callBtn.textContent = "⏹️ End Call";
        callBtn.classList.add("active");
        addMessage("Voice call started. Speak into your microphone.", "ai");
        
    } catch (err) {
        console.error("Microphone access denied", err);
        addMessage("Error: Please allow microphone permissions.", "ai");
    }
}

function stopVoiceCall() {
    if (mediaStream) mediaStream.getTracks().forEach(track => track.stop());
    if (audioProcessor) audioProcessor.disconnect();
    isCalling = false;
    callBtn.textContent = "🎙️ Connect Voice Call";
    callBtn.classList.remove("active");
}

callBtn.addEventListener('click', () => {
    if (isCalling) {
        stopVoiceCall();
    } else {
        startVoiceCall();
    }
});
