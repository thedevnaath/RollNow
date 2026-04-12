from manim import *
import numpy as np

# Global Configuration for 1080p60 16:9 Landscape
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_width = 16.0
config.frame_height = 9.0
config.background_color = BLACK
E_COLOR = "#F3EDE2"

# ---------------------------------------------------------
# SERVER 1 (0:00 - 1:00) : The Reactive Pinball
# ---------------------------------------------------------
class Phase1(Scene):
    def construct(self):
        # "You woke up today. You checked your phone..."
        phone = RoundedRectangle(corner_radius=0.5, height=6, width=3.5, color=E_COLOR, stroke_width=4)
        dot = Dot(radius=0.15, color=E_COLOR)
        self.play(Create(phone), FadeIn(dot), run_time=5)
        
        # "You scrolled through things that didn't matter..."
        self.play(dot.animate.shift(UP*2), run_time=5, rate_func=there_and_back_with_pause)
        self.play(dot.animate.shift(DOWN*2.5), run_time=5, rate_func=there_and_back)
        
        # "Most people are not living... reacting. An app sends a notification..."
        self.play(FadeOut(phone), dot.animate.scale(2), run_time=5)
        
        # The dot gets pushed around violently by external walls (Reaction)
        walls = VGroup(
            Line(LEFT*2, RIGHT*2, color=E_COLOR).shift(UP*3),
            Line(UP*2, DOWN*2, color=E_COLOR).shift(RIGHT*4),
            Line(LEFT*2, RIGHT*2, color=E_COLOR).shift(DOWN*3),
            Line(UP*2, DOWN*2, color=E_COLOR).shift(LEFT*4),
        )
        self.play(Create(walls), run_time=5)
        
        # Bouncing (Reacting to life)
        self.play(dot.animate.move_to(walls[0].get_center() + DOWN*0.2), run_time=3, rate_func=rush_into)
        self.play(dot.animate.move_to(walls[1].get_center() + LEFT*0.2), run_time=3, rate_func=rush_from)
        self.play(dot.animate.move_to(walls[2].get_center() + UP*0.2), run_time=3, rate_func=rush_into)
        self.play(dot.animate.move_to(walls[3].get_center() + RIGHT*0.2), run_time=3, rate_func=rush_from)
        self.play(dot.animate.move_to(ORIGIN), run_time=3)
        
        # "When was the last time you actually chose?"
        circle_trap = Circle(radius=1.5, color=E_COLOR, stroke_width=4)
        self.play(Transform(walls, circle_trap), run_time=15)
        self.wait(5)

# ---------------------------------------------------------
# SERVER 2 (1:00 - 2:00) : The Handed-Down Mold
# ---------------------------------------------------------
class Phase2(Scene):
    def construct(self):
        # Connect to Phase 1 end frame
        dot = Dot(radius=0.3, color=E_COLOR)
        circle_trap = Circle(radius=1.5, color=E_COLOR, stroke_width=4)
        self.add(dot, circle_trap)
        
        # "The life you are living... you did not design it. It was handed to you piece by piece..."
        slab_top = Rectangle(height=1, width=4, color=E_COLOR, fill_color=BLACK, fill_opacity=1).shift(UP*5)
        slab_bottom = Rectangle(height=1, width=4, color=E_COLOR, fill_color=BLACK, fill_opacity=1).shift(DOWN*5)
        slab_left = Rectangle(height=4, width=1, color=E_COLOR, fill_color=BLACK, fill_opacity=1).shift(LEFT*5)
        slab_right = Rectangle(height=4, width=1, color=E_COLOR, fill_color=BLACK, fill_opacity=1).shift(RIGHT*5)
        
        # Parents, School, Friends, Social Media closing in
        self.play(slab_top.animate.shift(DOWN*3.5), run_time=5)
        self.play(slab_bottom.animate.shift(UP*3.5), run_time=5)
        self.play(slab_left.animate.shift(RIGHT*3.5), run_time=5)
        self.play(slab_right.animate.shift(LEFT*3.5), run_time=5)
        
        # Encased in the heavy "normal" mold
        heavy_box = Square(side_length=3, color=E_COLOR, stroke_width=8)
        self.play(
            FadeOut(slab_top), FadeOut(slab_bottom), FadeOut(slab_left), FadeOut(slab_right),
            FadeOut(circle_trap), FadeOut(dot),
            Create(heavy_box), run_time=10
        )
        
        # "There is a word for this... Autopilot."
        ground_line = Line(LEFT*10, RIGHT*10, color=E_COLOR).shift(DOWN*1.5)
        self.play(heavy_box.animate.shift(DOWN*0.0), Create(ground_line), run_time=5)
        
        # The rigid box rolls on autopilot
        self.play(Rotate(heavy_box, angle=-PI/2, about_point=heavy_box.get_corner(DR)), run_time=5, rate_func=linear)
        self.play(Rotate(heavy_box, angle=-PI/2, about_point=heavy_box.get_corner(DR)), run_time=5, rate_func=linear)
        self.play(Rotate(heavy_box, angle=-PI/2, about_point=heavy_box.get_corner(DR)), run_time=5, rate_func=linear)
        
        # Stop rolling for the end of the phase
        self.play(heavy_box.animate.move_to(UP*0.5), run_time=10)

# ---------------------------------------------------------
# SERVER 3 (2:00 - 3:00) : The Shattering
# ---------------------------------------------------------
class Phase3(Scene):
    def construct(self):
        # Connect to Phase 2 end frame
        heavy_box = Square(side_length=3, color=E_COLOR, stroke_width=8).shift(UP*0.5)
        ground_line = Line(LEFT*10, RIGHT*10, color=E_COLOR).shift(DOWN*1.5)
        self.add(heavy_box, ground_line)
        
        # "I want you to actually think... Because there is a version of you that chooses."
        pulse = Square(side_length=0.5, color=E_COLOR).shift(UP*0.5)
        self.play(FadeIn(pulse), run_time=5)
        
        self.play(pulse.animate.scale(3), run_time=5, rate_func=there_and_back)
        self.play(pulse.animate.scale(4), run_time=5, rate_func=there_and_back)
        
        # The awakening: Shattering the rigid autopilot box
        shards = VGroup(*[Line(ORIGIN, UP*np.random.random()*2, color=E_COLOR).rotate(np.random.random()*TAU).shift(heavy_box.get_center() + np.array([np.random.uniform(-1.5,1.5), np.random.uniform(-1.5,1.5), 0])) for _ in range(30)])
        
        self.play(ReplacementTransform(heavy_box, shards), ReplacementTransform(pulse, shards), FadeOut(ground_line), run_time=5, rate_func=rush_into)
        self.play(shards.animate.scale(2).set_opacity(0), run_time=5)
        
        # "This is about becoming conscious. Truly awake."
        # An organic, free-flowing wave representing the true self
        wave = ParametricFunction(
            lambda t: np.array([t, np.sin(t*2) * 1.5, 0]),
            t_range=[-6, 6], color=E_COLOR, stroke_width=5
        )
        self.play(Create(wave), run_time=15)
        
        # The wave breathes and moves freely
        wave_breathe = ParametricFunction(
            lambda t: np.array([t, np.sin(t*3) * 2, 0]),
            t_range=[-6, 6], color=E_COLOR, stroke_width=5
        )
        self.play(Transform(wave, wave_breathe), run_time=20, rate_func=there_and_back)

# ---------------------------------------------------------
# SERVER 4 (3:00 - 4:00) : Breaking the Herd
# ---------------------------------------------------------
class Phase4(Scene):
    def construct(self):
        # Connect to Phase 3 end frame
        wave = ParametricFunction(
            lambda t: np.array([t, np.sin(t*2) * 1.5, 0]),
            t_range=[-6, 6], color=E_COLOR, stroke_width=5
        )
        self.add(wave)
        
        # "You have been living on borrowed terms... following the movement..."
        straight_line = Line(LEFT*8, RIGHT*8, color=E_COLOR, stroke_width=3)
        self.play(Transform(wave, straight_line), run_time=5)
        
        # The Herd: A massive block of identical lines moving mindlessly
        herd = VGroup(*[Line(LEFT*8, RIGHT*8, color=E_COLOR, stroke_width=2, stroke_opacity=0.3).shift(UP*y) for y in np.arange(-4, 4.5, 0.5)])
        herd.add(wave)
        self.play(Create(herd), run_time=10)
        
        # Infinite scroll effect representing blind forward movement
        self.play(herd.animate.shift(RIGHT*2), run_time=10, rate_func=linear)
        
        # "The moment you see this clearly... stop mid-scroll or mid-routine."
        self.play(herd.animate.shift(RIGHT*0.1), run_time=2, rate_func=rush_from) # Sudden halt
        
        # "Wait, this isn't really mine..." The center line breaks away
        self.play(herd.animate.set_opacity(0.1), wave.animate.set_color(WHITE).set_stroke(width=6), run_time=5)
        
        # Charting its own complex, intentional path
        star = Star(n=7, outer_radius=3, inner_radius=1.5, color=E_COLOR, stroke_width=5)
        self.play(FadeOut(herd), Transform(wave, star), run_time=15)
        self.play(Rotate(wave, angle=PI/2), run_time=13, rate_func=smooth)

# ---------------------------------------------------------
# SERVER 5 (4:00 - 5:00) : The Mechanism
# ---------------------------------------------------------
class Phase5(Scene):
    def construct(self):
        # Connect to Phase 4 end frame
        star = Star(n=7, outer_radius=3, inner_radius=1.5, color=E_COLOR, stroke_width=5).rotate(PI/2)
        self.add(star)
        
        # "But before we can talk about how to take your life back..."
        # Melt the star into the distinct lobes of a human brain
        left_lobe = Arc(radius=2, angle=PI, color=E_COLOR, stroke_width=5).rotate(PI/2).shift(LEFT*1)
        right_lobe = Arc(radius=2, angle=PI, color=E_COLOR, stroke_width=5).rotate(-PI/2).shift(RIGHT*1)
        brain = VGroup(left_lobe, right_lobe)
        
        self.play(Transform(star, brain), run_time=15)
        
        # "Inside your own brain... quietly... in a loop you never consented to."
        # The brain distorts into a tight, inescapable Ouroboros loop
        loop = ParametricFunction(
            lambda t: np.array([np.sin(t) + 2 * np.sin(2 * t), np.cos(t) - 2 * np.cos(2 * t), 0]),
            t_range=[0, TAU], color=E_COLOR, stroke_width=5
        )
        self.play(Transform(star, loop), run_time=15)
        self.play(Rotate(star, angle=PI), run_time=10, rate_func=linear)
        
        # "Once you actually see the mechanism, you cannot unsee it."
        # The fluid loop snaps into rigid, massive interlocking gears
        gear1 = RegularPolygon(n=10, color=E_COLOR, stroke_width=6).scale(2.5).shift(LEFT*2.5)
        gear2 = RegularPolygon(n=10, color=E_COLOR, stroke_width=6).scale(2.5).shift(RIGHT*2.5)
        mechanism = VGroup(gear1, gear2)
        
        self.play(Transform(star, mechanism), run_time=10)
        
        # The gears grind together
        self.play(Rotate(star[0], angle=PI/5), Rotate(star[1], angle=-PI/5), run_time=5, rate_func=linear)
        
        # "That is where we are going next." (Dive into the dark center of the gears)
        self.play(star.animate.scale(20).set_opacity(0), run_time=5, rate_func=rush_into)
        self.wait(5)
