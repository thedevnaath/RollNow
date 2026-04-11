import os
import sys
import subprocess
import glob

def main():
    # --- 1. The Vector Generator: Writing the Manim architecture ---
    print("📐 Generating 5-Minute Mathematical Vector Geometry (Manim)...")
    
    # We write the Manim script directly to a file
    manim_code = """
from manim import *
import numpy as np

# Long-form 16:9 Landscape Video
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_width = 16.0
config.frame_height = 9.0
config.background_color = "#5B6C5D"

class PsychologyLongForm(Scene):
    def construct(self):
        E_COLOR = "#F3EDE2"
        
        # We need to fill exactly 5 minutes (300 seconds). 
        # The pacing is extremely slow, deliberate, and hypnotic.
        
        # ---------------------------------------------------------
        # PHASE 1: The Loop and The Clarity (0:00 - 0:45)
        # "The moment you see this clearly... stop mid-scroll..."
        # ---------------------------------------------------------
        # Create a chaotic, overwhelming grid representing the mental loop/routine
        lines = VGroup(*[
            Line(LEFT*10 + UP*y, RIGHT*10 + UP*y, color=E_COLOR, stroke_opacity=0.3)
            for y in np.arange(-6, 6, 0.4)
        ])
        vertical_lines = VGroup(*[
            Line(DOWN*6 + RIGHT*x, UP*6 + RIGHT*x, color=E_COLOR, stroke_opacity=0.3)
            for x in np.arange(-10, 10, 0.4)
        ])
        grid = VGroup(lines, vertical_lines)
        
        self.play(Create(grid, lag_ratio=0.1), run_time=15)
        
        # The grid distorts into chaotic waves
        wave_grid = grid.copy().apply_function(
            lambda p: p + np.array([np.sin(p[1]), np.cos(p[0]), 0]) * 0.5
        )
        self.play(Transform(grid, wave_grid), run_time=15, rate_func=there_and_back)
        
        # Collapse into absolute, terrifying clarity (a single glowing point)
        clarity_point = Dot(radius=0.5, color=E_COLOR)
        self.play(Transform(grid, clarity_point), run_time=15)


        # ---------------------------------------------------------
        # PHASE 2: The First Breath (0:45 - 1:30)
        # "That moment is the beginning. The first real breath..."
        # ---------------------------------------------------------
        # The point expands into concentric, breathing circles
        breathing_circles = VGroup(*[
            Circle(radius=r, color=E_COLOR, stroke_width=2) 
            for r in np.arange(0.5, 8.0, 0.5)
        ])
        
        self.play(Transform(grid, breathing_circles), run_time=15)
        
        # Simulate a deep, 30-second breath in and out using scale
        self.play(grid.animate.scale(1.3), run_time=15, rate_func=smooth)
        self.play(grid.animate.scale(1/1.3), run_time=15, rate_func=smooth)


        # ---------------------------------------------------------
        # PHASE 3: The Real Reset (1:30 - 2:15)
        # "Not motivation that fades... A real reset."
        # ---------------------------------------------------------
        # Circles collapse into a tangled, complex knot (fleeting motivation)
        knot = ParametricFunction(
            lambda t: np.array([
                np.sin(t) + 2 * np.sin(2 * t),
                np.cos(t) - 2 * np.cos(2 * t),
                0
            ]) * 1.5,
            t_range=[0, TAU],
            color=E_COLOR,
            stroke_width=4
        )
        self.play(Transform(grid, knot), run_time=15)
        
        # The knot twists and pulses rapidly
        self.play(Rotate(grid, angle=PI*2), run_time=15, rate_func=linear)
        
        # The "Real Reset" - the knot smoothly untangles into a single straight line
        reset_line = Line(LEFT*8, RIGHT*8, color=E_COLOR, stroke_width=4)
        self.play(Transform(grid, reset_line), run_time=15)


        # ---------------------------------------------------------
        # PHASE 4: Who You Become (2:15 - 3:15)
        # "Starts in how you see yourself... ends in who you become."
        # ---------------------------------------------------------
        # The line curves into an abstract eye
        eye_top = ArcBetweenPoints(LEFT*4, RIGHT*4, angle=-PI/2, color=E_COLOR)
        eye_bottom = ArcBetweenPoints(LEFT*4, RIGHT*4, angle=PI/2, color=E_COLOR)
        eye = VGroup(eye_top, eye_bottom)
        
        self.play(Transform(grid, eye), run_time=20)
        
        # The eye morphs into a complex, fully realized geometric mandala
        mandala = VGroup()
        for i in range(12):
            petal = eye_top.copy().rotate(i * PI / 6, about_point=ORIGIN)
            mandala.add(petal)
            
        self.play(Transform(grid, mandala), run_time=20)
        self.play(Rotate(grid, angle=PI), run_time=20, rate_func=linear)


        # ---------------------------------------------------------
        # PHASE 5: The Loop You Never Consented To (3:15 - 4:15)
        # "Inside your own brain... quietly... in a loop."
        # ---------------------------------------------------------
        # The mandala is swallowed by an infinite, hypnotic spiral
        spiral = ParametricFunction(
            lambda t: np.array([
                t * np.cos(t * 5),
                t * np.sin(t * 5),
                0
            ]) * 0.4,
            t_range=[0, 15],
            color=E_COLOR,
            stroke_width=3
        )
        
        self.play(Transform(grid, spiral), run_time=20)
        
        # The spiral rotates endlessly, pulling the viewer in
        tracker = ValueTracker(0)
        grid.add_updater(lambda m: m.set_opacity(0.8 + 0.2*np.sin(tracker.get_value())))
        
        self.play(
            Rotate(grid, angle=PI*4), 
            tracker.animate.set_value(10),
            run_time=40, 
            rate_func=linear
        )
        grid.clear_updaters()


        # ---------------------------------------------------------
        # PHASE 6: Seeing The Mechanism (4:15 - 5:00)
        # "Once you see the mechanism... you cannot unsee it."
        # ---------------------------------------------------------
        # The fluid spiral snaps into rigid, mechanical interlocking gears
        gear1 = RegularPolygon(n=12, color=E_COLOR).scale(3)
        gear2 = RegularPolygon(n=12, color=E_COLOR).scale(3).shift(RIGHT*6)
        gear3 = RegularPolygon(n=12, color=E_COLOR).scale(3).shift(LEFT*6)
        mechanism = VGroup(gear1, gear2, gear3)
        
        self.play(Transform(grid, mechanism), run_time=15)
        
        # The gears grind together
        self.play(
            Rotate(grid[0], angle=PI/2),
            Rotate(grid[1], angle=-PI/2),
            Rotate(grid[2], angle=-PI/2),
            run_time=15,
            rate_func=linear
        )
        
        # Dive into the center of the mechanism to end the video
        self.play(
            grid.animate.scale(50).set_opacity(0), 
            run_time=15, 
            rate_func=ease_in_expo
        )
        
        self.wait(5)
"""
    with open("scene.py", "w") as f:
        f.write(manim_code)

    # --- 2. Execute Manim Engine (1080p 60FPS) ---
    print("🎥 Rendering 5-Minute Cinematic Vector Animation on GitHub CPU...")
    # This will take a few minutes to render. It computes thousands of frames.
    subprocess.run(['manim', '-qh', 'scene.py', 'PsychologyLongForm'], check=True)

    print("🔍 Locating rendered video...")
    video_files = glob.glob("media/**/*.mp4", recursive=True)
    
    if not video_files:
        print("❌ Fatal Error: Manim finished, but no MP4 file was found.")
        sys.exit(1)
        
    video_path = video_files[0]
    print(f"✅ Found pure visual video at: {video_path}")

        # --- 3. Final Assembly ---
    os.rename(video_path, "final_video.mp4")
    print("✅ Silent cinematic video generated successfully: final_video.mp4")


if __name__ == "__main__":
    main()
