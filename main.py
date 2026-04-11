import os
import sys
import json
import subprocess
import requests
from google import genai
import whisper
import asyncio
from PIL import Image
import io

# --- 1. Configuration ---
client = genai.Client()

CF_ACCOUNT_ID = os.environ.get('CF_ACCOUNT_ID')
CF_API_TOKEN = os.environ.get('CF_API_TOKEN')

if not CF_ACCOUNT_ID or not CF_API_TOKEN:
    print("❌ Error: Cloudflare credentials missing. Please add CF_ACCOUNT_ID and CF_API_TOKEN to GitHub Secrets.")
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

    print("🎨 Generating Cinematic Visuals via Cloudflare Enterprise AI...")
    image_files = []
    total_audio_time = word_boundaries[-1]["start"] + word_boundaries[-1]["duration"]
    time_per_image = total_audio_time / len(image_prompts)
    
    # Using Stable Diffusion XL on Cloudflare Infrastructure
    CF_API_URL = f"[https://api.cloudflare.com/client/v4/accounts/](https://api.cloudflare.com/client/v4/accounts/){CF_ACCOUNT_ID}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}
    
    for i, img_prompt in enumerate(image_prompts):
        safe_prompt = f"Cinematic lighting, high-fidelity anime realism, dark atmosphere. {img_prompt}. Never include ghosts, monsters, or distorted figures."
        img_path = f"image_{i}.jpg"
        
        # We request a 9:16 vertical resolution safe for SDXL memory limits
        payload = {
            "prompt": safe_prompt,
            "height": 1024,
            "width": 576,
            "num_steps": 20
        }
        
        for attempt in range(3):
            print(f"   -> Requesting image {i+1}/4 from Cloudflare (Attempt {attempt+1})...")
            try:
                r = requests.post(CF_API_URL, headers=headers, json=payload)
                
                if r.status_code == 200:
                    # Cloudflare hands back raw image bytes. 
                    # We load it into PIL and perfectly upscale it to 1080x1920 for YouTube Shorts
                    image = Image.open(io.BytesIO(r.content))
                    resized_image = image.resize((1080, 1920), Image.Resampling.LANCZOS)
                    resized_image.save(img_path, "JPEG", quality=95)
                    
                    image_files.append(img_path)
                    print(f"   ✅ Image {i+1} generated and upscaled successfully.")
                    break
                else:
                    print(f"   ⚠️ Cloudflare API Error {r.status_code}: {r.text}")
                    await asyncio.sleep(5)
                    if attempt == 2:
                        print(f"❌ Fatal Error: Could not fetch image {i+1} from Cloudflare.")
                        sys.exit(1)
            except Exception as e:
                print(f"   ⚠️ Request Error: {e}")
                await asyncio.sleep(5)
                if attempt == 2: sys.exit(1)

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
