import os
import sys
import json
import subprocess
import requests
from google import genai
import whisper
import asyncio

# --- 1. Configuration ---
client = genai.Client()

HF_TOKEN = os.environ.get('HF_TOKEN')
if not HF_TOKEN:
    print("❌ Error: HF_TOKEN is missing. Please add your Hugging Face token to GitHub Secrets.")
    sys.exit(1)

def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

async def main():
    if not os.path.exists("voiceover.wav"):
        print("❌ Error: I cannot find 'voiceover.wav'. Please upload your voiceover file to the repository before running.")
        sys.exit(1)

    print("🎧 Booting OpenAI Whisper on GitHub CPU...")
    model = whisper.load_model("base") 
    
    print("🔊 Listening to your voiceover to map exact word timestamps...")
    result = model.transcribe("voiceover.wav", word_timestamps=True)
    
    full_text = result['text'].strip()
    print(f"📝 Transcribed Audio: {full_text}")
    
    word_boundaries = []
    for segment in result['segments']:
        if 'words' in segment:
            for word in segment['words']:
                word_boundaries.append({
                    "text": word['word'].strip(),
                    "start": word['start'],
                    "duration": word['end'] - word['start']
                })

    if not word_boundaries:
        print("❌ Error: Whisper could not detect any speech in the audio file.")
        sys.exit(1)

    print("✍️ Forging dynamic subtitles (.srt)...")
    with open("captions.srt", "w", encoding="utf-8") as f:
        for i, word in enumerate(word_boundaries):
            start = word["start"]
            end = start + word["duration"]
            f.write(f"{i+1}\n")
            f.write(f"{format_srt_time(start)} --> {format_srt_time(end)}\n")
            clean_word = "".join(c for c in word['text'] if c.isalnum())
            f.write(f"{clean_word.upper()}\n\n")

    print("🧠 Asking Gemini to generate the visual storyboard based on your audio...")
    prompt = f"""
    You are an expert in dark psychology and visual storytelling. 
    Here is a transcription of a YouTube Shorts voiceover:
    "{full_text}"

    Generate exactly 4 highly detailed visual prompts that perfectly match the mood and message of this audio.
    Output JSON exactly like this:
    {{
      "image_prompts": [
        "Prompt 1",
        "Prompt 2",
        "Prompt 3",
        "Prompt 4"
      ]
    }}
    """
    
    response = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt
            )
            break 
        except Exception as e:
            print(f"⚠️ Gemini API Error - {e}. Retrying...")
            await asyncio.sleep(5)
            if attempt == 2: sys.exit(1)
            
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        lines = raw_text.split('\n')
        if len(lines) > 2:
            raw_text = '\n'.join(lines[1:-1]).strip()
            
    try:
        data = json.loads(raw_text)
    except Exception:
        print("❌ Error: Failed to parse Gemini JSON.")
        sys.exit(1)
        
    image_prompts = data.get('image_prompts', [])

    print("🎨 Generating High-Quality Visuals via Hugging Face API...")
    image_files = []
    total_audio_time = word_boundaries[-1]["start"] + word_boundaries[-1]["duration"]
    time_per_image = total_audio_time / len(image_prompts)
    
    # Using Stable Diffusion XL - The industry standard for high-res free generation
    p1 = "https://"
    p2 = "api-inference.huggingface.co"
    p3 = "/models/stabilityai/stable-diffusion-xl-base-1.0"
    HF_API_URL = p1 + p2 + p3
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    for i, img_prompt in enumerate(image_prompts):
        safe_prompt = f"High-fidelity anime realism, cinematic lighting. {img_prompt}. Never include ghosts, monsters, or distorted figures."
        payload = {"inputs": safe_prompt}
        
        img_path = f"image_{i}.jpg"
        
        # --- ROBUST HUGGING FACE DOWNLOADER ---
        for attempt in range(5):
            print(f"   -> Requesting image {i+1}/4 from Hugging Face (Attempt {attempt+1})...")
            r = requests.post(HF_API_URL, headers=headers, json=payload)
            
            if r.status_code == 200:
                with open(img_path, "wb") as f:
                    f.write(r.content)
                image_files.append(img_path)
                print(f"   ✅ Image {i+1} generated successfully.")
                break
            elif r.status_code == 503:
                # 503 means the model is currently loading into server memory.
                error_data = r.json()
                wait_time = error_data.get("estimated_time", 15.0)
                print(f"   ⏳ Model is booting up. Waiting {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time + 2) # Give it 2 extra seconds to be safe
            else:
                print(f"   ⚠️ Hugging Face Error {r.status_code}: {r.text}")
                await asyncio.sleep(5)
                if attempt == 4:
                    print(f"❌ Fatal Error: Could not fetch image {i+1} from Hugging Face.")
                    sys.exit(1)

    print("🎞️ Assembling final sequence...")
    with open("images.txt", "w") as f:
        for img in image_files:
            f.write(f"file '{img}'\n")
            f.write(f"duration {time_per_image}\n")
        f.write(f"file '{image_files[-1]}'\n")

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', 'images.txt',
        '-i', 'voiceover.wav',
        '-vf', "subtitles=captions.srt:force_style='Fontname=Liberation Sans,Fontsize=24,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,Outline=2,Alignment=10'",
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        'final_video.mp4'
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)
    print("✅ Video generated successfully: final_video.mp4")

if __name__ == "__main__":
    asyncio.run(main())
