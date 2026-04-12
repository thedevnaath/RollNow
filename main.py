import json
import textwrap
from manim import *

# Vertical Shorts Configuration (9:16)
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.background_color = BLACK

def wrap_text(text, width=38):
    """Automatically wraps text so it never breaks the screen boundaries."""
    return "\n".join(textwrap.wrap(text, width=width))

class DailyShort(Scene):
    def construct(self):
        # Load the AI-generated content
        with open("content.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        FONT = "Liberation Sans"
        TITLE_COLOR = "#FFC000"  
        BOX_COLOR = "#1C1C1E"    
        TEXT_COLOR = WHITE
        
        # ---------------------------------------------------------
        # PHASE 1: The Hook
        # ---------------------------------------------------------
        hook_text = Text(
            wrap_text(data["hook"], width=25), 
            font=FONT,
            font_size=48, 
            color=TEXT_COLOR, 
            line_spacing=1.2,
            weight=BOLD
        ).move_to(ORIGIN)
        
        if hook_text.width > 8.5:
            hook_text.width = 8.5
            
        self.play(FadeIn(hook_text, shift=UP*0.5), run_time=1.5)
        self.wait(2.5)
        self.play(FadeOut(hook_text, shift=UP*0.5), run_time=1)
        self.wait(0.5)
        
        # ---------------------------------------------------------
        # PHASE 2: The Main Content Structure
        # ---------------------------------------------------------
        content_box = RoundedRectangle(
            corner_radius=0.4, 
            width=8.0, 
            height=9.5, 
            color=BOX_COLOR, 
            fill_color=BOX_COLOR, 
            fill_opacity=1,
            stroke_width=0
        ).shift(DOWN * 0.5)
        
        title = Text(data["title"], font=FONT, font_size=50, color=TITLE_COLOR, weight=BOLD)
        title.next_to(content_box, UP, buff=0.8)
        
        if title.width > 8.5:
            title.width = 8.5
            
        # Dynamically generate bullet points from AI data
        bullet_mobjects = []
        for bullet_text in data["bullets"]:
            wrapped = wrap_text("• " + bullet_text, width=36)
            # Indent subsequent lines of a bullet point
            indented = wrapped.replace("\n", "\n  ") 
            b_mob = Text(indented, font=FONT, font_size=34, color=TEXT_COLOR, line_spacing=1.2)
            bullet_mobjects.append(b_mob)
        
        bullets = VGroup(*bullet_mobjects)
        bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.7)
        
        # Responsive padding
        if bullets.width > content_box.width - 1.2:
            bullets.width = content_box.width - 1.2
        if bullets.height > content_box.height - 1.2:
            bullets.height = content_box.height - 1.2
            
        bullets.move_to(content_box.get_center())
        
        # ---------------------------------------------------------
        # PHASE 3: The Animation Sequence
        # ---------------------------------------------------------
        self.play(FadeIn(title, shift=DOWN*0.5), FadeIn(content_box), run_time=1)
        self.wait(0.5)
        
        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT*0.5), run_time=0.8)
            self.wait(2.0) # slightly longer wait to read the powerful text
            
        self.wait(4)
