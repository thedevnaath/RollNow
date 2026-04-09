import os
import sys
import json
import subprocess
import requests
import urllib.parse
from google import genai
import edge_tts
import asyncio

# --- 1. Configuration ---
client = genai.Client() 

def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

async def main():
    print("🧠 Generating script with Gemini 1.5 Flash...")
    
    prompt = """
    You are an expert in human behavior and dark psychology. Generate a 30-second YouTube Shorts script designed to provoke deep self-reflection.
    Follow this structure:
    1. The Anchor: A relatable, mundane physical object or habit.
    2. The Action: Why people accept this mundane thing.
    3. The Twist: Compare this to a toxic psychological flaw or self-sabotage.
    4. The Truth: A harsh, paradigm-shifting conclusion.
    
    Output JSON exactly like this:
    {
      "script_text": "Sentence 1. Sentence 2. Sentence 3. Sentence 4.",
      "image_prompts": [
        "Prompt for sentence 1",
        "Prompt for sentence 2",
        "Prompt for sentence 3",
        "Prompt for sentence 4"
      ]
    }
    Make sure there is exactly one image prompt for every sentence. The script_text must be one continuous string.
    """
    
    # --- Robust Retry Loop using stable gemini-1.5-flash ---
    response = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt
            )
            break 
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1}: Gemini API Error - {e}")
            if attempt < 2:
                print("Retrying in 10 seconds...")
                await asyncio.sleep(10)
            else:
                print("❌ Fatal Error: Gemini API failed after 3 attempts.")
                sys.exit(1)
    
    # --- Bulletproof JSON Parsing ---
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        lines = raw_text.split('\n')
        if len(lines) > 2:
            raw_text = '\n'.join(lines[1:-1]).strip()
    
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse Gemini's response as JSON.\nRaw Response: {response.text}")
        sys.exit(1)
    
    script_text = data.get('script_text', '')
    image_prompts = data.get('image_prompts', [])
    
    if not script_text:
        print("❌ Error: Gemini returned an empty script.")
        sys.exit(1)
        
    print("🎙️ Generating Voiceover and capturing word timestamps...")
    
    # --- EXTREME Text Sanitization ---
    clean_text = script_text.replace('&', 'and').replace('\n', ' ').replace('\r', '')
    valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?"
    clean_text = "".join(c for c in clean_text if c in valid_chars)
    clean_text = " ".join(clean_text.split()) 
    
    print(f"Speaking: {clean_text}")

    voice = "en-US-ChristopherNeural" 
    word_boundaries = []
    
    # --- Robust Retry Loop for TTS ---
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(clean_text, voice)
            with open("voiceover.mp3", "wb") as audio_file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        word_boundaries.append({
                            "text": chunk["text"],
                            "start": chunk["offset"] / 10000000,
                            "duration": chunk["duration"] / 10000000
                        })
            
            if word_boundaries:
                break 
            else:
                print(f"⚠️ Attempt {attempt + 1}: TTS returned empty stream. Retrying in 2 seconds...")
                await asyncio.sleep(2)
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed with error: {e}. Retrying in 2 seconds...")
            await asyncio.sleep(2)

    if not word_boundaries:
        print("❌ Error: Edge TTS failed after 3 attempts.")
        print("🚨 Note: If you see this error, Microsoft has temporarily blocked the GitHub Actions Server IP. You will need to wait an hour, or run this Python script locally on your own computer.")
        sys.exit(1)

    print("✍️ Forging dynamic subtitles (.srt)...")
    with open("captions.srt", "w", encoding="utf-8") as f:
        for i, word in enumerate(word_boundaries):
            start = word["start"]
            end = start + word["duration"]
            f.write(f"{i+1}\n")
            f.write(f"{format_srt_time(start)} --> {format_srt_time(end)}\n")
            f.write(f"{word['text'].upper()}\n\n")

    print("🎨 Generating Visuals via Pollinations API...")
    
    image_files = []
    total_audio_time = word_boundaries[-1]["start"] + word_boundaries[-1]["duration"]
    time_per_image = total_audio_time / len(image_prompts)
    
    for i, img_prompt in enumerate(image_prompts):
        safe_prompt = f"High-fidelity anime realism, cinematic lighting. {img_prompt}. Never include ghosts, monsters, or distorted figures."
        encoded_prompt = urllib.parse.quote(safe_prompt)
        
        # --- Clean, Functional URL (No markdown links) ---
        url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){encoded_prompt}?width=1080&height=1920&model=flux&nologo=true"
        
        r = requests.get(url)
        img_path = f"image_{i}.png"
        with open(img_path, "wb") as f:
            f.write(r.content)
        image_files.append(img_path)

    print("🎞️ Assembling final sequence...")
    
    with open("images.txt", "w") as f:
        for img in image_files:
            f.write(f"file '{img}'\n")
            f.write(f"duration {time_per_image}\n")
        f.write(f"file '{image_files[-1]}'\n")

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', 'images.txt',
        '-i', 'voiceover.mp3',
        '-vf', "subtitles=captions.srt:force_style='Fontname=Liberation Sans,Fontsize=24,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,Outline=2,Alignment=10'",
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',
        '-shortest',
        'final_video.mp4'
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)
    print("✅ Video generated successfully: final_video.mp4")

if __name__ == "__main__":
    asyncio.run(main())
