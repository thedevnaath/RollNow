import os
import sys
import subprocess
import whisper
import asyncio

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
    
    raw_words = []
    for segment in result['segments']:
        if 'words' in segment:
            for word in segment['words']:
                raw_words.append({
                    "text": word['word'].strip(),
                    "start": word['start'],
                    "duration": word['end'] - word['start']
                })

    if not raw_words:
        print("❌ Error: Whisper could not detect any speech.")
        sys.exit(1)

    # --- THE SUBTITLE FIX: Grouping words into 3-word chunks ---
    print("🧠 Forging grouped, readable subtitles...")
    chunks = []
    current_chunk = []
    chunk_start = 0

    for i, word in enumerate(raw_words):
        if not current_chunk:
            chunk_start = word['start']
        
        current_chunk.append(word['text'])
        chunk_end = word['start'] + word['duration']
        
        # Close the chunk if it has 3 words, is the last word, or there's a pause in speech
        next_word_start = raw_words[i+1]['start'] if i+1 < len(raw_words) else chunk_end
        pause_duration = next_word_start - chunk_end
        
        if len(current_chunk) >= 3 or i == len(raw_words) - 1 or pause_duration > 0.4:
            chunks.append({
                "text": " ".join(current_chunk),
                "start": chunk_start,
                "duration": chunk_end - chunk_start
            })
            current_chunk = []

    with open("captions.srt", "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            start = chunk["start"]
            end = start + chunk["duration"]
            f.write(f"{i+1}\n")
            f.write(f"{format_srt_time(start)} --> {format_srt_time(end)}\n")
            # Strip weird punctuation for bold visual text
            clean_text = "".join(c for c in chunk['text'] if c.isalnum() or c.isspace() or c in "!?.,'")
            f.write(f"{clean_text.upper()}\n\n")

    total_audio_time = raw_words[-1]["start"] + raw_words[-1]["duration"]
    step_time = total_audio_time / 4.0

    # --- THE VECTOR GENERATOR: Writing the Manim animation script on the fly ---
    print("📐 Generating Mathematical Vector Geometry (Manim)...")
    manim_code = f"""
from manim import *
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.background_color = BLACK

class PsychologyVisual(Scene):
    def construct(self):
        step_time = {step_time}

        # Step 1: The Anchor (A rigid line of control)
        shape = Line(DOWN * 6, UP * 6, color=WHITE).set_stroke(width=5)
        self.play(Create(shape), run_time=step_time)

        # Step 2: The Action (Distorting into a manipulative frequency)
        wave = FunctionGraph(lambda x: np.sin(x * 3) * 2, x_range=[-4, 4], color=WHITE).set_stroke(width=5).rotate(PI/2)
        self.play(Transform(shape, wave), run_time=step_time)

        # Step 3: The Twist (The psychological trap)
        circles = VGroup(*[Circle(radius=r, color=WHITE).set_stroke(width=3) for r in np.arange(0.5, 4.5, 0.5)])
        self.play(Transform(shape, circles), run_time=step_time)

        # Step 4: The Truth (A sharp, striking realization)
        poly = RegularPolygon(n=3, color=WHITE).scale(3).set_stroke(width=5)
        self.play(Transform(shape, poly), run_time=step_time * 0.7)
        self.play(FadeOut(shape), run_time=step_time * 0.3)
"""
    with open("scene.py", "w") as f:
        f.write(manim_code)

    # Execute the Manim render command (High Quality, 1080p60)
    print("🎥 Rendering 1080p60 Vector Animation on GitHub CPU...")
    subprocess.run(['manim', '-qh', 'scene.py', 'PsychologyVisual'], check=True)

    # Manim saves files to a specific output folder structure
    video_path = "media/videos/scene/1080p60/PsychologyVisual.mp4"

    # --- FINAL ASSEMBLY ---
    print("🎞️ Merging Vector Animation, Audio, and Subtitles...")
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', 'voiceover.wav',
        '-vf', "subtitles=captions.srt:force_style='Fontname=Liberation Sans,Fontsize=22,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,Outline=2,Alignment=10'",
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        'final_video.mp4'
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)
    print("✅ Premium Vector Video generated successfully: final_video.mp4")

if __name__ == "__main__":
    asyncio.run(main())
