import os
import whisper
from manim import *

# Horizontal Long-Form Configuration (16:9)
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_width = 16.0
config.frame_height = 9.0
config.background_color = "#5B6C5D"

class KineticTypography(Scene):
    def construct(self):
        audio_path = "voiceover.wav"
        
        if not os.path.exists(audio_path):
            print(f"❌ Error: {audio_path} not found in the repository.")
            return

        # 1. Bind the audio track to the video timeline
        self.add_sound(audio_path)

        # 2. Run AI Transcription
        print("🧠 AI is listening and extracting millisecond timestamps...")
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, word_timestamps=True)
        
        words = []
        for segment in result['segments']:
            for word in segment['words']:
                words.append({
                    "text": word["word"].strip().upper(),
                    "start": word["start"],
                    "end": word["end"]
                })

        if not words:
            print("❌ No words detected. Check the audio file.")
            return

        # 3. Kinetic Typography Setup
        FONT = "Liberation Sans"
        BASE_COLOR = "#F3EDE2"
        HIGHLIGHT_COLOR = "#FFFFFF" 
        
        # We process the text in 4-word "phrases" to keep the screen minimal and focused
        chunk_size = 4 
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
        
        # The master clock strictly prevents floating-point audio drift over long videos
        master_time = 0.0
        
        def sync_time(target):
            nonlocal master_time
            if target > master_time:
                self.wait(target - master_time)
                master_time = target

        # 4. The Animation Engine
        for chunk in chunks:
            phrase_group = VGroup(*[
                Text(w["text"], font=FONT, font_size=72, color=BASE_COLOR, weight=BOLD)
                for w in chunk
            ]).arrange(RIGHT, buff=0.4).move_to(ORIGIN)

            # Ensure phrase never breaks screen bounds
            if phrase_group.width > 14:
                phrase_group.width = 14

            chunk_start = chunk[0]["start"]
            sync_time(chunk_start)

            # Snap phrase onto the screen
            self.play(FadeIn(phrase_group, shift=UP*0.5, scale=0.9), run_time=0.2, rate_func=rush_into)
            master_time += 0.2

            # Word-by-word active highlighting
            for i, w in enumerate(chunk):
                word_mob = phrase_group[i]
                w_start = w["start"]
                w_end = w["end"]
                
                sync_time(w_start)

                duration = w_end - w_start
                punch_time = 0.1
                
                # Prevent micro-glitches for words spoken extremely fast
                if duration < 0.2:
                    duration = 0.2

                # PUNCH UP: Word scales toward the camera
                self.play(
                    word_mob.animate.set_color(HIGHLIGHT_COLOR).scale(1.2),
                    run_time=punch_time,
                    rate_func=rush_into
                )
                master_time += punch_time

                # HOLD: Wait for the speaker to finish the word
                hold_time = duration - punch_time
                if hold_time > 0:
                    self.wait(hold_time)
                    master_time += hold_time

                # SNAP DOWN: Returns to base scale but retains the white highlight
                self.play(
                    word_mob.animate.scale(1 / 1.2),
                    run_time=0.1,
                    rate_func=rush_from
                )
                master_time += 0.1

            # Snap the phrase off the screen
            self.play(FadeOut(phrase_group, shift=UP*0.5, scale=1.1), run_time=0.2, rate_func=rush_from)
            master_time += 0.2
