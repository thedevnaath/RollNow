from manim import *

# Vertical Shorts Configuration (9:16)
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.background_color = BLACK

class SpotlightIllusion(Scene):
    def construct(self):
        # Fonts and Colors matching your screenshot
        FONT = "Liberation Sans"
        TITLE_COLOR = "#FFC000"  # The bold yellow/gold
        BOX_COLOR = "#1C1C1E"    # The dark grey background of the text box
        TEXT_COLOR = WHITE
        
        # ---------------------------------------------------------
        # PHASE 1: The Hook
        # ---------------------------------------------------------
        hook_text = Text(
            "The psychological glitch\nmaking you socially anxious.", 
            font=FONT,
            font_size=52, 
            color=TEXT_COLOR, 
            line_spacing=1.2,
            weight=BOLD
        ).move_to(ORIGIN)
        
        # Fade in the hook, let them read it, fade it out
        self.play(FadeIn(hook_text, shift=UP*0.5), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(hook_text, shift=UP*0.5), run_time=1)
        self.wait(0.5)
        
        # ---------------------------------------------------------
        # PHASE 2: The Main Content Structure
        # ---------------------------------------------------------
        
        # The Title
        title = Text("THE SPOTLIGHT ILLUSION", font=FONT, font_size=55, color=TITLE_COLOR, weight=BOLD)
        title.to_edge(UP, buff=3)
        
        # The Dark Grey Box - NOW WITH CURVED EDGES
        content_box = RoundedRectangle(
            corner_radius=0.3, # This gives it that smooth, Apple-style UI curve
            width=8.0, 
            height=9.0, 
            color=BOX_COLOR, 
            fill_color=BOX_COLOR, 
            fill_opacity=1,
            stroke_width=0
        )
        content_box.next_to(title, DOWN, buff=0.8)
        
        # The Bullets (Formatted to fit inside the box perfectly)
        b1 = Text("• Your brain overestimates how\n  much people notice you by 50%.", font=FONT, font_size=36, color=TEXT_COLOR, line_spacing=1.2)
        b2 = Text("• Everyone around you is trapped\n  in their own first-person\n  simulation.", font=FONT, font_size=36, color=TEXT_COLOR, line_spacing=1.2)
        b3 = Text("• When you mess up, they aren't\n  judging you. They are thinking\n  about themselves.", font=FONT, font_size=36, color=TEXT_COLOR, line_spacing=1.2)
        b4 = Text("• True freedom starts the exact\n  moment you realize you are\n  invisible.", font=FONT, font_size=36, color=TEXT_COLOR, line_spacing=1.2)
        
        bullets = VGroup(b1, b2, b3, b4)
        bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.8)
        bullets.move_to(content_box.get_center())
        
        # ---------------------------------------------------------
        # PHASE 3: The Animation Sequence
        # ---------------------------------------------------------
        
        # Pop in the Title and the Box
        self.play(FadeIn(title, shift=DOWN*0.5), FadeIn(content_box), run_time=1)
        self.wait(0.5)
        
        # Fade in Bullets one by one for pacing
        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT*0.5), run_time=0.8)
            self.wait(1.5) 
            
        # Hold the final frame so the viewer can read/screenshot
        self.wait(4)
