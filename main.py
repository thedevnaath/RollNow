from manim import *
import numpy as np

# Global Configuration for 1080p60 16:9 Landscape
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_width = 16.0
config.frame_height = 9.0
config.background_color = "#5B6C5D"
E_COLOR = "#F3EDE2"

# ---------------------------------------------------------
# SERVER 1 (0:00 - 1:00) : The Loop and The Clarity
# ---------------------------------------------------------
class Phase1(Scene):
    def construct(self):
        lines = VGroup(*[Line(LEFT*10 + UP*y, RIGHT*10 + UP*y, color=E_COLOR, stroke_opacity=0.3) for y in np.arange(-6, 6, 0.4)])
        vertical_lines = VGroup(*[Line(DOWN*6 + RIGHT*x, UP*6 + RIGHT*x, color=E_COLOR, stroke_opacity=0.3) for x in np.arange(-10, 10, 0.4)])
        grid = VGroup(lines, vertical_lines)
        
        self.play(Create(grid, lag_ratio=0.1), run_time=15)
        
        wave_grid = grid.copy().apply_function(lambda p: p + np.array([np.sin(p[1]), np.cos(p[0]), 0]) * 0.5)
        self.play(Transform(grid, wave_grid), run_time=25, rate_func=there_and_back)
        
        clarity_point = Dot(radius=0.5, color=E_COLOR)
        self.play(Transform(grid, clarity_point), run_time=20)


# ---------------------------------------------------------
# SERVER 2 (1:00 - 2:00) : The First Breath
# ---------------------------------------------------------
class Phase2(Scene):
    def construct(self):
        # Visually connect to the exact frame Phase 1 ended on
        grid = Dot(radius=0.5, color=E_COLOR)
        self.add(grid)
        
        breathing_circles = VGroup(*[Circle(radius=r, color=E_COLOR, stroke_width=2) for r in np.arange(0.5, 8.0, 0.5)])
        self.play(Transform(grid, breathing_circles), run_time=20)
        
        self.play(grid.animate.scale(1.3), run_time=20, rate_func=smooth)
        self.play(grid.animate.scale(1/1.3), run_time=20, rate_func=smooth)


# ---------------------------------------------------------
# SERVER 3 (2:00 - 3:00) : The Real Reset
# ---------------------------------------------------------
class Phase3(Scene):
    def construct(self):
        # Connect to Phase 2 end frame
        grid = VGroup(*[Circle(radius=r, color=E_COLOR, stroke_width=2) for r in np.arange(0.5, 8.0, 0.5)])
        self.add(grid)
        
        knot = ParametricFunction(
            lambda t: np.array([np.sin(t) + 2 * np.sin(2 * t), np.cos(t) - 2 * np.cos(2 * t), 0]) * 1.5,
            t_range=[0, TAU], color=E_COLOR, stroke_width=4
        )
        self.play(Transform(grid, knot), run_time=20)
        self.play(Rotate(grid, angle=PI*2), run_time=20, rate_func=linear)
        
        reset_line = Line(LEFT*8, RIGHT*8, color=E_COLOR, stroke_width=4)
        self.play(Transform(grid, reset_line), run_time=20)


# ---------------------------------------------------------
# SERVER 4 (3:00 - 4:00) : Who You Become
# ---------------------------------------------------------
class Phase4(Scene):
    def construct(self):
        # Connect to Phase 3 end frame
        grid = Line(LEFT*8, RIGHT*8, color=E_COLOR, stroke_width=4)
        self.add(grid)
        
        eye_top = ArcBetweenPoints(LEFT*4, RIGHT*4, angle=-PI/2, color=E_COLOR)
        eye_bottom = ArcBetweenPoints(LEFT*4, RIGHT*4, angle=PI/2, color=E_COLOR)
        eye = VGroup(eye_top, eye_bottom)
        
        self.play(Transform(grid, eye), run_time=20)
        
        mandala = VGroup()
        for i in range(12):
            petal = eye_top.copy().rotate(i * PI / 6, about_point=ORIGIN)
            mandala.add(petal)
            
        self.play(Transform(grid, mandala), run_time=20)
        self.play(Rotate(grid, angle=PI), run_time=20, rate_func=linear)


# ---------------------------------------------------------
# SERVER 5 (4:00 - 5:00) : The Loop You Never Consented To
# ---------------------------------------------------------
class Phase5(Scene):
    def construct(self):
        # Connect to Phase 4 end frame (Mandala rotated PI)
        eye_top = ArcBetweenPoints(LEFT*4, RIGHT*4, angle=-PI/2, color=E_COLOR)
        grid = VGroup()
        for i in range(12):
            petal = eye_top.copy().rotate(i * PI / 6, about_point=ORIGIN)
            grid.add(petal)
        grid.rotate(PI)
        self.add(grid)
        
        spiral = ParametricFunction(
            lambda t: np.array([t * np.cos(t * 5), t * np.sin(t * 5), 0]) * 0.4,
            t_range=[0, 15], color=E_COLOR, stroke_width=3
        )
        
        self.play(Transform(grid, spiral), run_time=20)
        
        tracker = ValueTracker(0)
        grid.add_updater(lambda m: m.set_opacity(0.8 + 0.2*np.sin(tracker.get_value())))
        self.play(Rotate(grid, angle=PI*4), tracker.animate.set_value(10), run_time=20, rate_func=linear)
        grid.clear_updaters()
        
        # The final disappearance
        self.play(grid.animate.scale(50).set_opacity(0), run_time=20, rate_func=rush_into)

