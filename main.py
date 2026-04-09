import os
import sys
import json
import subprocess
import requests
import re
from google import genai
import edge_tts
import asyncio
import urllib.parse

# --- 1. Configuration ---
client = genai.Client() 

def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

async def main():
    print("🧠 Generating script with Gemini...")
    
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
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    # --- Robust JSON Parsing ---
    raw_text = response.text.strip()
    # Strip out any markdown code blocks using regex
    raw_text = re.sub(r'^
http://googleusercontent.com/immersive_entry_chip/0
