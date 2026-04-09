import os
import json
import subprocess
import requests
import google.generativeai as genai
import edge_tts
import asyncio
import urllib.parse

# --- 1. Configuration ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

async def main():
    print("🧠 Generating script with Gemini...")
    
    # --- 2. The Brain: Psychological "Anchor & Twist" Prompt ---
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
    
    response = model.generate_content(prompt)
    
    # Clean up JSON formatting if Gemini adds markdown blocks
    raw_text = response.text.strip().removeprefix('```json').removesuffix('```').strip()
    data = json.loads(raw_text)
    
    script_text = data['script_text']
    image_prompts = data['image_prompts']
    
    print("🎙️ Generating Voiceover and capturing word timestamps...")
    
    # --- 3. The Voice & Subtitle Sync ---
    voice = "en-US-ChristopherNeural" # Deep, serious tone
    communicate = edge_tts.Communicate(script_text, voice)
    
    word_boundaries = []
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

    print("✍️ Forging dynamic subtitles (.srt)...")
    with open("captions.srt", "w", encoding="utf-8") as f:
        for i, word in enumerate(word_boundaries):
            start = word["start"]
            end = start + word["duration"]
            f.write(f"{i+1}\n")
            f.write(f"{format_srt_time(start)} --> {format_srt_time(end)}\n")
            f.write(f"{word['text'].upper()}\n\n")

    print("🎨 Generating Visuals via Pollinations API...")
    
    # --- 4. The Visuals ---
    image_files = []
    # We calculate roughly how long each image should be on screen based on sentence chunks
    # For simplicity in this script, we divide total audio time by number of images
    total_audio_time = word_boundaries[-1]["start"] + word_boundaries[-1]["duration"]
    time_per_image = total_audio_time / len(image_prompts)
    
    for i, img_prompt in enumerate(image_prompts):
        # Enforcing our aesthetic and strict negative constraints
        safe_prompt = f"High-fidelity anime realism, cinematic lighting. {img_prompt}. Never include ghosts, monsters, or distorted figures."
        encoded_prompt = urllib.parse.quote(safe_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux&nologo=true"
        
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
        f.write(f"file '{image_files[-1]}'\n") # FFmpeg quirk requires last file repeated

    # --- 5. The FFmpeg Assembly ---
    # Using Liberation Sans which we will install in the GitHub Action
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
