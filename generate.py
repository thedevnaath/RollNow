import os
import json
import google.generativeai as genai

def generate_content():
    # You will store this key securely in GitHub Secrets
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
        
    genai.configure(api_key=api_key)
    
    # We use Gemini 1.5 Flash - it is lightning fast and great at JSON
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    You are an elite behavioral psychologist and viral copywriter. 
    Your goal is to teach human development, stoicism, or cognitive behavioral therapy in a dark, "glitch in the matrix" aesthetic. 
    It must be highly positive and life-improving, but framed as a "secret hack" or "psychological glitch".
    
    Generate a new, unique topic (do NOT repeat 'The Spotlight Illusion').
    Keep the sentences brutally powerful, simple, and short. Every point should feel like a goldmine.
    
    Output strictly in the following JSON format:
    {
        "hook": "A 1-sentence hook to start the video. Max 8 words.",
        "title": "A 2-4 word title in ALL CAPS.",
        "bullets": [
            "Bullet 1: Brutally powerful truth.",
            "Bullet 2: Mindset shift.",
            "Bullet 3: Practical reality.",
            "Bullet 4: Empowering conclusion."
        ]
    }
    """
    
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
        )
    )
    
    data = json.loads(response.text)
    
    # Save the generated content to a file for Manim to read
    with open("content.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    print("✅ Content generated successfully!")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    generate_content()
