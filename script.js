const API_KEY = "INJECT_API_KEY_HERE";
const HOST = "generativelanguage.googleapis.com";
const WS_URL = `wss://${HOST}/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=${API_KEY}`;

let ws;
let audioCtx;
let mediaStream;
let audioProcessor;
let cameraStream;
let visionInterval;

let isVoiceActive = false;
let isVisionActive = false;

// UI Selection
const statusTag = document.getElementById('status-tag');
const chatStream = document.getElementById('chat-stream');
const textInput = document.getElementById('text-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const visionBtn = document.getElementById('vision-btn');
const videoPreview = document.getElementById('video-preview');

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('bubble', sender);
    div.textContent = text;
    chatStream.appendChild(div);
    chatStream.scrollTop = chatStream.scrollHeight;
}

// 1. Establish the Live Session Pipeline
function startLiveSession() {
    return new Promise((resolve) => {
        if (ws && ws.readyState === WebSocket.OPEN) return resolve();

        ws = new WebSocket(WS_URL);
        ws.onopen = () => {
            statusTag.textContent = "🟢 Live Connected";
            
            // Registered Exact Model from Dashboard
            ws.send(JSON.stringify({
                setup: {
                    model: "models/gemini-3-flash-live",
                    generationConfig: {
                        responseModalities: ["AUDIO", "TEXT"]
                    },
                    systemInstruction: {
                        parts: [{ text: "You are the live counter clerk at 'The Golden Whisk Bakery'. You can interact with text, listen to the customer's voice, and visually see their camera feed. Assist them with menu prices, ingredients, and checkout politely." }]
                    }
                }
            }));
            resolve();
        };

        ws.onmessage = async (e) => {
            let data = e.data instanceof Blob ? JSON.parse(await e.data.text()) : JSON.parse(e.data);
            if (data.serverContent?.modelTurn?.parts) {
                for (let part of data.serverContent.modelTurn.parts) {
                    if (part.text) addMessage(part.text, 'ai');
                    if (part.inlineData?.data) playAudioData(part.inlineData.data);
                }
            }
        };

        ws.onclose = () => {
            statusTag.textContent = "🔴 Offline";
            disconnectAll();
        };
    });
}

// 2. Real-time Audio Output Player
function playAudioData(base64) {
    if (!audioCtx) return;
    const binary = window.atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    
    const pcm16 = new Int16Array(bytes.buffer);
    const float32 = new Float32Array(pcm16.length);
    for (let i = 0; i < pcm16.length; i++) float32[i] = pcm16[i] / 32768.0;
    
    const buffer = audioCtx.createBuffer(1, float32.length, 24000);
    buffer.getChannelData(0).set(float32);
    const src = audioCtx.createBufferSource();
    src.buffer = buffer;
    src.connect(audioCtx.destination);
    src.start();
}

// 3. Real-time Text Component
async function sendText() {
    const val = textInput.value.trim();
    if (!val) return;
    await startLiveSession();
    addMessage(val, 'user');
    textInput.value = '';

    ws.send(JSON.stringify({
        clientContent: {
            turns: [{ role: "user", parts: [{ text: val }] }],
            turnComplete: true
        }
    }));
}
sendBtn.addEventListener('click', sendText);
textInput.addEventListener('keypress', (e) => { if(e.key === 'Enter') sendText(); });

// 4. Real-time Voice Component (Input 16kHz PCM stream)
async function toggleVoice() {
    if (isVoiceActive) { stopVoice(); return; }
    await startLiveSession();
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const src = audioCtx.createMediaStreamSource(mediaStream);
        audioProcessor = audioCtx.createScriptProcessor(4096, 1, 1);
        
        src.connect(audioProcessor);
        audioProcessor.connect(audioCtx.destination);
        
        audioProcessor.onaudioprocess = (e) => {
            const input = e.inputBuffer.getChannelData(0);
            const pcm16 = new Int16Array(input.length);
            for(let i=0; i<input.length; i++) pcm16[i] = Math.max(-1, Math.min(1, input[i])) * 32767;
            
            const u8 = new Uint8Array(pcm16.buffer);
            let bin = '';
            for(let i=0; i<u8.byteLength; i++) bin += String.fromCharCode(u8[i]);
            
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    realtimeInput: { mediaChunks: [{ mimeType: "audio/pcm;rate=16000", data: window.btoa(bin) }] }
                }));
            }
        };
        isVoiceActive = true;
        voiceBtn.textContent = "⏹️ Stop Audio Listening";
        voiceBtn.classList.add('active');
    } catch (err) { addMessage("Mic error: " + err.message, "ai"); }
}

function stopVoice() {
    if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
    if (audioProcessor) audioProcessor.disconnect();
    isVoiceActive = false;
    voiceBtn.textContent = "🎙️ Connect Live Audio (Talk)";
    voiceBtn.classList.remove('active');
}

// 5. Mobile Camera Component (Uses Back-Facing Camera)
async function toggleVision() {
    if (isVisionActive) { stopVision(); return; }
    await startLiveSession();
    
    try {
        // Request the device's back-facing camera instead of screen share
        cameraStream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: "environment", width: { ideal: 640 }, height: { ideal: 480 } } 
        });
        videoPreview.srcObject = cameraStream;
        videoPreview.style.display = "block";
        
        const track = cameraStream.getVideoTracks()[0];
        const capture = new ImageCapture(track);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        // Capture 1 JPEG snapshot per second
        visionInterval = setInterval(async () => {
            if (ws.readyState !== WebSocket.OPEN) return;
            try {
                const bitmap = await capture.grabFrame();
                canvas.width = bitmap.width;
                canvas.height = bitmap.height;
                ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
                
                canvas.toBlob((blob) => {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64 = reader.result.split(',')[1];
                        ws.send(JSON.stringify({
                            realtimeInput: { mediaChunks: [{ mimeType: "image/jpeg", data: base64 }] }
                        }));
                    };
                    reader.readAsDataURL(blob);
                }, 'image/jpeg', 0.6); 
            } catch (e) { console.log("Frame dropped: ", e); }
        }, 1000);

        isVisionActive = true;
        visionBtn.textContent = "⏹️ Stop Camera Vision";
        visionBtn.classList.add('active');
    } catch (err) { addMessage("Camera error: " + err.message, "ai"); }
}

function stopVision() {
    clearInterval(visionInterval);
    if (cameraStream) cameraStream.getTracks().forEach(t => t.stop());
    videoPreview.style.display = "none";
    isVisionActive = false;
    visionBtn.textContent = "📷 Open Camera for AI";
    visionBtn.classList.remove('active');
}

function disconnectAll() { stopVoice(); stopVision(); }
voiceBtn.addEventListener('click', toggleVoice);
visionBtn.addEventListener('click', toggleVision);
