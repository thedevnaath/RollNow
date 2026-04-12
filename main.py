from manim import *

# Vertical Shorts Configuration (9:16)
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.background_color = BLACK

class SpotlightIllusion(Scene):
    def construct(self):
        # Fonts and Colors
        FONT = "Liberation Sans"
        TITLE_COLOR = "#FFC000"  
        BOX_COLOR = "#1C1C1E"    
        TEXT_COLOR = WHITE
        
        # ---------------------------------------------------------
        # PHASE 1: The Hook
        # ---------------------------------------------------------
        hook_text = Text(
            "The psychological glitch\nmaking you socially anxious.", 
            font=FONT,
            font_size=48, 
            color=TEXT_COLOR, 
            line_spacing=1.2,
            weight=BOLD
        ).move_to(ORIGIN)
        
        # Ensure hook doesn't overflow screen width
        if hook_text.width > 8.5:
            hook_text.width = 8.5
            
        self.play(FadeIn(hook_text, shift=UP*0.5), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(hook_text, shift=UP*0.5), run_time=1)
        self.wait(0.5)
        
        # ---------------------------------------------------------
        # PHASE 2: The Main Content Structure (Responsive Layout)
        # ---------------------------------------------------------
        
        # 1. Anchor the Box to the center (shifted slightly down for the title)
        content_box = RoundedRectangle(
            corner_radius=0.4, 
            width=8.0, 
            height=9.5, 
            color=BOX_COLOR, 
            fill_color=BOX_COLOR, 
            fill_opacity=1,
            stroke_width=0
        ).shift(DOWN * 0.5)
        
        # 2. Anchor the Title relative to the Box
        title = Text("THE SPOTLIGHT ILLUSION", font=FONT, font_size=50, color=TITLE_COLOR, weight=BOLD)
        title.next_to(content_box, UP, buff=0.8)
        
        # Ensure title fits on screen
        if title.width > 8.5:
            title.width = 8.5
            
        # 3. Create Bullets with optimized line breaks
        b1 = Text("• Your brain overestimates how much\n  people notice you by 50%.", font=FONT, font_size=34, color=TEXT_COLOR, line_spacing=1.2)
        b2 = Text("• Everyone around you is trapped in\n  their own first-person simulation.", font=FONT, font_size=34, color=TEXT_COLOR, line_spacing=1.2)
        b3 = Text("• When you mess up, they aren't\n  judging you. They are thinking\n  about themselves.", font=FONT, font_size=34, color=TEXT_COLOR, line_spacing=1.2)
        b4 = Text("• True freedom starts the exact\n  moment you realize you are\n  invisible.", font=FONT, font_size=34, color=TEXT_COLOR, line_spacing=1.2)
        
        bullets = VGroup(b1, b2, b3, b4)
        bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.7)
        
        # 4. THE FIX: Force bullets to fit inside the box with a 1.2 unit margin padding
        if bullets.width > content_box.width - 1.2:
            bullets.width = content_box.width - 1.2
            
        if bullets.height > content_box.height - 1.2:
            bullets.height = content_box.height - 1.2
            
        # 5. Center the perfectly sized text block inside the box
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
            
        # Hold the final frame
        self.wait(4)
