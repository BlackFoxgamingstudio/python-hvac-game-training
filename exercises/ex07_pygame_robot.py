#!/usr/bin/env python3
"""
=============================================================================
 EXERCISE 07 — Pygame Robot: Visual HVAC Simulation
=============================================================================

 PYTHON CONCEPTS: pygame library, game loop, event handling, drawing
                  primitives, keyboard input, color manipulation, delta
                  time, frame rate, HUD rendering, state machines

 HVAC CONCEPTS:   Heat generation from work, visual temperature feedback,
                  automatic cooling systems, thermal management,
                  real-time monitoring dashboards

 GOAL: Create a visual robot that moves with WASD/arrow keys, generates
       heat as it moves, changes color based on temperature, and has
       an auto-cooling AC system.  A HUD displays live sensor data.

 PREREQUISITES:
   pip install pygame

 CONTROLS:
   WASD / Arrow Keys — Move the robot
   ESC               — Quit
=============================================================================
"""

import sys
import math
import time

# ─────────────────────────────────────────────────────────────────────────────
# SAFE PYGAME IMPORT
# ─────────────────────────────────────────────────────────────────────────────
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("=" * 60)
    print(" ❌ Pygame is not installed!")
    print(" Run: pip install pygame")
    print("=" * 60)
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
# Window dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60  # Target frames per second

# Colors (R, G, B)
# PYTHON LESSON — TUPLES:
#   Colors in Pygame are (Red, Green, Blue) tuples, each 0-255.
#   Tuples are immutable — once created, they can't be changed.
#   This is good for constants that shouldn't accidentally change.
COLOR_BG = (20, 22, 30)          # Dark background
COLOR_GRID = (35, 38, 50)        # Subtle grid lines
COLOR_HUD_BG = (15, 17, 25, 200) # Semi-transparent HUD background
COLOR_TEXT = (200, 210, 230)      # Light text
COLOR_ACCENT = (0, 200, 255)     # Cyan accent
COLOR_WARNING = (255, 200, 50)   # Yellow warning
COLOR_DANGER = (255, 60, 60)     # Red danger
COLOR_COOL = (50, 150, 255)      # Blue — cool
COLOR_NORMAL = (100, 220, 100)   # Green — normal temp
COLOR_HOT = (255, 100, 50)       # Orange — hot
COLOR_OVERHEAT = (255, 30, 30)   # Red — overheating
COLOR_HEAD = (180, 190, 210)     # Robot head color
COLOR_EYE = (0, 255, 180)        # Robot eye glow

# Robot settings
ROBOT_SPEED = 3.0          # Pixels per frame when moving
ROBOT_BODY_W = 40          # Body width
ROBOT_BODY_H = 50          # Body height
ROBOT_HEAD_RADIUS = 18     # Head circle radius
HEAT_PER_PIXEL = 0.008     # Temperature rise per pixel moved
COOL_RATE = 0.03           # Degrees cooled per frame when AC is on
AC_TRIGGER_TEMP = 110.0    # AC turns on above this temp
AC_TARGET_TEMP = 98.6      # AC cools down to this temp
OVERHEAT_TEMP = 150.0      # Danger zone!

# Grid settings
GRID_SPACING = 50          # Pixels between grid lines


# ─────────────────────────────────────────────────────────────────────────────
# ROBOT CLASS
# ─────────────────────────────────────────────────────────────────────────────

class VisualRobot:
    """
    A robot that moves on screen, generates heat, and self-cools.

    PYTHON LESSON — GAME OBJECTS:
      In game development, each entity (player, enemy, item) is usually
      a class.  The class holds position, velocity, state — everything
      the game loop needs to update and draw the entity each frame.

    HVAC LESSON:
      This robot is a thermal system.  Moving = doing work = generating
      heat.  The AC kicks in automatically when temperature exceeds a
      threshold — exactly like a real thermostat-controlled system.
    """

    def __init__(self, x: float, y: float):
        # Position (center of the robot)
        self.x = x
        self.y = y

        # Thermal state
        self.core_temp_f = 98.6      # Starting temperature
        self.ac_running = False       # Is the AC currently cooling?
        self.ac_cycles = 0            # Total AC activations

        # Movement tracking
        self.total_distance_px = 0.0  # Total pixels traveled
        self.moving = False           # Is the robot moving this frame?
        self.dx = 0.0                 # Velocity X
        self.dy = 0.0                 # Velocity Y

        # Visual
        self.eye_blink_timer = 0      # For eye blink animation

    def handle_input(self, keys) -> None:
        """
        Process keyboard input for movement.

        PYTHON LESSON — PYGAME KEY STATE:
          pygame.key.get_pressed() returns a list of booleans.
          keys[pygame.K_w] is True if W is held down RIGHT NOW.
          This is different from event-based input (key pressed/released).
          Continuous checking = smooth movement.
        """
        self.dx = 0.0
        self.dy = 0.0

        # WASD and Arrow keys
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.dy = -ROBOT_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.dy = ROBOT_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.dx = -ROBOT_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.dx = ROBOT_SPEED

        # Diagonal movement should not be faster (normalize)
        if self.dx != 0 and self.dy != 0:
            factor = ROBOT_SPEED / math.sqrt(self.dx**2 + self.dy**2)
            self.dx *= factor
            self.dy *= factor

        self.moving = (self.dx != 0 or self.dy != 0)

    def update(self) -> None:
        """
        Update robot state each frame.

        PYTHON LESSON — UPDATE PATTERN:
          Games separate INPUT → UPDATE → DRAW into distinct phases.
          Update changes the data.  Draw reads the data and renders.
          This separation keeps code clean and testable.

        HVAC LESSON:
          Each frame simulates a tiny time step.  Heat accumulates
          from movement.  The AC removes heat when it's running.
          This is a simplified thermal model: Q_in - Q_out = ΔT.
        """
        # Move the robot
        self.x += self.dx
        self.y += self.dy

        # Keep robot on screen (boundary clamping)
        self.x = max(ROBOT_BODY_W // 2,
                     min(SCREEN_WIDTH - ROBOT_BODY_W // 2, self.x))
        self.y = max(ROBOT_HEAD_RADIUS + ROBOT_BODY_H // 2,
                     min(SCREEN_HEIGHT - ROBOT_BODY_H // 2, self.y))

        # Track distance
        if self.moving:
            dist = math.sqrt(self.dx**2 + self.dy**2)
            self.total_distance_px += dist

            # Generate heat from movement
            self.core_temp_f += dist * HEAT_PER_PIXEL

        # Natural heat dissipation (very slow)
        if self.core_temp_f > 75.0:
            self.core_temp_f -= 0.005

        # AC auto-control (thermostat logic!)
        if self.core_temp_f > AC_TRIGGER_TEMP and not self.ac_running:
            self.ac_running = True
            self.ac_cycles += 1
        elif self.core_temp_f <= AC_TARGET_TEMP and self.ac_running:
            self.ac_running = False

        # AC cooling
        if self.ac_running:
            self.core_temp_f -= COOL_RATE

        # Clamp temperature
        self.core_temp_f = max(70.0, min(200.0, self.core_temp_f))

        # Eye blink timer
        self.eye_blink_timer = (self.eye_blink_timer + 1) % 180

    def get_body_color(self) -> tuple:
        """
        Calculate robot body color based on temperature.

        PYTHON LESSON — COLOR INTERPOLATION:
          We smoothly blend between blue (cool) → green (normal) →
          orange (hot) → red (overheating) based on a value.
          This is called "linear interpolation" or "lerp."
        """
        t = self.core_temp_f

        if t < 98.6:
            # Cool range: blue to green
            ratio = max(0, (t - 70) / (98.6 - 70))
            r = int(COLOR_COOL[0] + (COLOR_NORMAL[0] - COLOR_COOL[0]) * ratio)
            g = int(COLOR_COOL[1] + (COLOR_NORMAL[1] - COLOR_COOL[1]) * ratio)
            b = int(COLOR_COOL[2] + (COLOR_NORMAL[2] - COLOR_COOL[2]) * ratio)
        elif t < AC_TRIGGER_TEMP:
            # Normal to warm: green to orange
            ratio = (t - 98.6) / (AC_TRIGGER_TEMP - 98.6)
            r = int(COLOR_NORMAL[0] + (COLOR_HOT[0] - COLOR_NORMAL[0]) * ratio)
            g = int(COLOR_NORMAL[1] + (COLOR_HOT[1] - COLOR_NORMAL[1]) * ratio)
            b = int(COLOR_NORMAL[2] + (COLOR_HOT[2] - COLOR_NORMAL[2]) * ratio)
        else:
            # Hot to overheating: orange to red
            ratio = min(1, (t - AC_TRIGGER_TEMP) / (OVERHEAT_TEMP - AC_TRIGGER_TEMP))
            r = int(COLOR_HOT[0] + (COLOR_OVERHEAT[0] - COLOR_HOT[0]) * ratio)
            g = int(COLOR_HOT[1] + (COLOR_OVERHEAT[1] - COLOR_HOT[1]) * ratio)
            b = int(COLOR_HOT[2] + (COLOR_OVERHEAT[2] - COLOR_HOT[2]) * ratio)

        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the robot on the screen.

        PYTHON LESSON — PYGAME DRAWING:
          pygame.draw.rect(surface, color, (x, y, width, height))
          pygame.draw.circle(surface, color, (cx, cy), radius)

          The coordinate system starts at top-left (0,0).
          X increases rightward, Y increases downward.
        """
        body_color = self.get_body_color()
        bx = int(self.x - ROBOT_BODY_W // 2)
        by = int(self.y - ROBOT_BODY_H // 2)

        # Shadow (subtle depth effect)
        shadow_rect = pygame.Rect(bx + 3, by + 3, ROBOT_BODY_W, ROBOT_BODY_H)
        pygame.draw.rect(surface, (10, 10, 15), shadow_rect, border_radius=6)

        # Body (rounded rectangle)
        body_rect = pygame.Rect(bx, by, ROBOT_BODY_W, ROBOT_BODY_H)
        pygame.draw.rect(surface, body_color, body_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 255, 255, 60), body_rect,
                         width=2, border_radius=6)

        # Head (circle above body)
        head_cx = int(self.x)
        head_cy = int(self.y - ROBOT_BODY_H // 2 - ROBOT_HEAD_RADIUS + 4)
        pygame.draw.circle(surface, COLOR_HEAD, (head_cx, head_cy),
                           ROBOT_HEAD_RADIUS)
        pygame.draw.circle(surface, (255, 255, 255, 80), (head_cx, head_cy),
                           ROBOT_HEAD_RADIUS, width=2)

        # Eyes (two small circles, blink occasionally)
        if self.eye_blink_timer < 170:  # Open most of the time
            eye_y = head_cy - 2
            eye_color = COLOR_DANGER if self.core_temp_f > OVERHEAT_TEMP else COLOR_EYE
            pygame.draw.circle(surface, eye_color, (head_cx - 7, eye_y), 4)
            pygame.draw.circle(surface, eye_color, (head_cx + 7, eye_y), 4)
            # Eye pupils
            pygame.draw.circle(surface, (0, 0, 0), (head_cx - 7, eye_y), 2)
            pygame.draw.circle(surface, (0, 0, 0), (head_cx + 7, eye_y), 2)

        # Antenna
        pygame.draw.line(surface, COLOR_ACCENT,
                         (head_cx, head_cy - ROBOT_HEAD_RADIUS),
                         (head_cx, head_cy - ROBOT_HEAD_RADIUS - 12), 2)
        pygame.draw.circle(surface, COLOR_ACCENT,
                           (head_cx, head_cy - ROBOT_HEAD_RADIUS - 12), 3)

        # AC indicator (snowflake when cooling)
        if self.ac_running:
            ac_x = bx + ROBOT_BODY_W + 8
            ac_y = by + 10
            # Simple snowflake: 3 crossed lines
            for angle in [0, 60, 120]:
                rad = math.radians(angle)
                x1 = int(ac_x + 6 * math.cos(rad))
                y1 = int(ac_y + 6 * math.sin(rad))
                x2 = int(ac_x - 6 * math.cos(rad))
                y2 = int(ac_y - 6 * math.sin(rad))
                pygame.draw.line(surface, COLOR_COOL, (x1, y1), (x2, y2), 2)


# ─────────────────────────────────────────────────────────────────────────────
# HUD (Heads-Up Display)
# ─────────────────────────────────────────────────────────────────────────────

def draw_hud(surface: pygame.Surface, robot: VisualRobot,
             font: pygame.font.Font, small_font: pygame.font.Font) -> None:
    """
    Draw the heads-up display with sensor readings.

    PYTHON LESSON — SURFACE BLITTING:
      font.render() creates a new Surface with the text drawn on it.
      surface.blit() pastes that text Surface onto the main screen.
      This is how ALL text rendering works in Pygame.

    HVAC LESSON:
      This HUD mirrors what you'd see on a building management system
      (BMS) dashboard — real-time sensor readings, status indicators,
      and alarm states.
    """
    # HUD background panel
    hud_rect = pygame.Rect(10, 10, 240, 180)
    hud_surface = pygame.Surface((240, 180), pygame.SRCALPHA)
    hud_surface.fill((15, 17, 25, 180))
    surface.blit(hud_surface, (10, 10))
    pygame.draw.rect(surface, COLOR_ACCENT, hud_rect, width=1, border_radius=4)

    # Title
    title = font.render("ROBOT HVAC MONITOR", True, COLOR_ACCENT)
    surface.blit(title, (20, 15))

    # Temperature with color indicator
    temp = robot.core_temp_f
    if temp > OVERHEAT_TEMP:
        temp_color = COLOR_DANGER
        temp_status = "OVERHEAT!"
    elif temp > AC_TRIGGER_TEMP:
        temp_color = COLOR_WARNING
        temp_status = "HOT"
    elif temp > 100:
        temp_color = COLOR_HOT
        temp_status = "WARM"
    else:
        temp_color = COLOR_NORMAL
        temp_status = "NORMAL"

    temp_text = font.render(f"Core Temp: {temp:.1f}°F", True, temp_color)
    surface.blit(temp_text, (20, 42))

    status_text = small_font.render(f"Status: {temp_status}", True, temp_color)
    surface.blit(status_text, (20, 62))

    # Distance
    dist_m = robot.total_distance_px / 30.0  # Convert px to "meters"
    dist_text = small_font.render(f"Distance: {dist_m:.1f} m", True, COLOR_TEXT)
    surface.blit(dist_text, (20, 85))

    # Position
    pos_text = small_font.render(
        f"Position: ({robot.x:.0f}, {robot.y:.0f})", True, COLOR_TEXT)
    surface.blit(pos_text, (20, 105))

    # AC Status
    ac_status = "ON ❄️" if robot.ac_running else "STANDBY"
    ac_color = COLOR_COOL if robot.ac_running else COLOR_TEXT
    ac_text = small_font.render(f"AC: {ac_status}", True, ac_color)
    surface.blit(ac_text, (20, 125))

    ac_cycles = small_font.render(
        f"AC Cycles: {robot.ac_cycles}", True, COLOR_TEXT)
    surface.blit(ac_cycles, (20, 145))

    # Temperature bar (visual gauge)
    bar_x, bar_y = 20, 168
    bar_w, bar_h = 210, 10
    # Background
    pygame.draw.rect(surface, (40, 42, 55),
                     (bar_x, bar_y, bar_w, bar_h), border_radius=3)
    # Fill based on temperature (70-200 range)
    fill_ratio = min(1, max(0, (temp - 70) / (200 - 70)))
    fill_w = int(bar_w * fill_ratio)
    bar_color = robot.get_body_color()
    if fill_w > 0:
        pygame.draw.rect(surface, bar_color,
                         (bar_x, bar_y, fill_w, bar_h), border_radius=3)

    # Controls help (bottom of screen)
    help_text = small_font.render(
        "WASD/Arrows: Move  |  ESC: Quit", True, (100, 105, 120))
    surface.blit(help_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 25))


# ─────────────────────────────────────────────────────────────────────────────
# GRID BACKGROUND
# ─────────────────────────────────────────────────────────────────────────────

def draw_grid(surface: pygame.Surface) -> None:
    """
    Draw a subtle grid floor pattern.

    HVAC LESSON:
      Grids represent the floor plan of a building.  In HVAC design,
      the floor plan determines zone layout, duct routing, and where
      to place supply/return air registers.
    """
    for x in range(0, SCREEN_WIDTH, GRID_SPACING):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SPACING):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN GAME LOOP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """
    The main game loop.

    PYTHON LESSON — THE GAME LOOP:
      Every game follows this pattern:
        1. PROCESS EVENTS (keyboard, mouse, quit)
        2. UPDATE state (move objects, check collisions, physics)
        3. DRAW everything to the screen
        4. Wait for the next frame (clock.tick)

      This loop runs 60 times per second (60 FPS).  Each pass through
      the loop is one "frame."

    HVAC LESSON:
      This is exactly how a PLC (Programmable Logic Controller) works
      in HVAC:
        1. Read inputs (sensors)
        2. Execute logic (thermostat decisions)
        3. Write outputs (turn equipment on/off)
        4. Wait for next scan cycle
    """
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("HVAC Robot Simulator — Exercise 07")
    clock = pygame.time.Clock()

    # Fonts
    font = pygame.font.SysFont("monospace", 16, bold=True)
    small_font = pygame.font.SysFont("monospace", 14)

    # Create the robot at center of screen
    robot = VisualRobot(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Game loop
    running = True
    while running:
        # ── 1. PROCESS EVENTS ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # ── 2. UPDATE ──
        keys = pygame.key.get_pressed()
        robot.handle_input(keys)
        robot.update()

        # ── 3. DRAW ──
        screen.fill(COLOR_BG)       # Clear screen
        draw_grid(screen)            # Draw background grid
        robot.draw(screen)           # Draw the robot
        draw_hud(screen, robot, font, small_font)  # Draw HUD

        # ── 4. FLIP & TICK ──
        pygame.display.flip()        # Show the frame
        clock.tick(FPS)              # Maintain 60 FPS

    # Cleanup
    pygame.quit()
    print()
    print("=" * 60)
    print(" EXERCISE 07 COMPLETE")
    print("=" * 60)
    print(f"""
 FINAL STATS:
   Core Temperature : {robot.core_temp_f:.1f} °F
   Total Distance   : {robot.total_distance_px / 30:.1f} m
   AC Cycles        : {robot.ac_cycles}

 WHAT YOU LEARNED:
   Python — pygame basics, game loop pattern, event handling,
            keyboard state, drawing primitives (rect, circle, line),
            color interpolation, HUD rendering, frame rate control

   HVAC  — Real-time thermal monitoring, auto-thermostat logic,
           visual temperature feedback, sensor dashboards,
           PLC scan cycle analogy, building floor plan grids

 NEXT: Exercise 08 — Complete Game (all systems combined!)
""")


if __name__ == "__main__":
    main()
