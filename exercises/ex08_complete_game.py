#!/usr/bin/env python3
"""
=============================================================================
 EXERCISE 08 — Complete Game: Robot + HVAC + AI + Zones
=============================================================================

 PYTHON CONCEPTS: Full integration — classes, composition, game loop,
                  event handling, overlays, file I/O, optional AI,
                  state machines, collision detection, particle effects

 HVAC CONCEPTS:   Multi-zone thermal environments, heat sources,
                  zone-based HVAC (VAV systems), equipment monitoring,
                  diagnostic logging, AI-assisted field troubleshooting

 GOAL: Combine EVERYTHING from exercises 01-07 into one complete game:
       - Visual robot with WASD movement (ex07)
       - HVAC refrigeration cycle (ex02)
       - CSV diagnostic logging (ex03)
       - OOP classes (ex04)
       - Optional Gemini AI chat (ex05)
       - Anomaly dashboard (ex06)
       - Pygame rendering (ex07)

 CONTROLS:
   WASD / Arrows — Move robot
   C             — Toggle AI chat overlay
   L             — Toggle diagnostic log view
   D             — Dump current data to CSV file
   ESC           — Quit

 PREREQUISITES:
   pip install pygame
   (Optional) pip install google-genai + set GEMINI_API_KEY
=============================================================================
"""

import sys
import os
import math
import csv
import time
import random

# ─────────────────────────────────────────────────────────────────────────────
# SAFE IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
try:
    import pygame
except ImportError:
    print("❌ Pygame required: pip install pygame")
    sys.exit(1)

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 960, 640
FPS = 60

# Color palette
C_BG          = (18, 20, 28)
C_GRID        = (30, 33, 45)
C_TEXT        = (200, 210, 230)
C_ACCENT      = (0, 200, 255)
C_GREEN       = (100, 220, 100)
C_YELLOW      = (255, 200, 50)
C_RED         = (255, 60, 60)
C_BLUE        = (50, 120, 255)
C_COOL_ZONE   = (30, 50, 120, 60)
C_HOT_ZONE    = (120, 40, 30, 60)
C_NORM_ZONE   = (50, 55, 70, 40)
C_OVERLAY_BG  = (10, 12, 20, 220)
C_HEAD        = (180, 190, 210)
C_EYE         = (0, 255, 180)

# Robot
ROBOT_SPEED   = 3.5
BODY_W, BODY_H = 36, 44
HEAD_R        = 16
HEAT_PER_PX   = 0.009
COOL_RATE     = 0.04
AC_ON_TEMP    = 110.0
AC_OFF_TEMP   = 98.6
OVERHEAT      = 155.0

GRID_SIZE     = 50


# ─────────────────────────────────────────────────────────────────────────────
# MAP ZONES — Different thermal environments
# ─────────────────────────────────────────────────────────────────────────────

class Zone:
    """
    A rectangular area with a specific thermal characteristic.

    HVAC LESSON — ZONING:
      Commercial buildings are divided into ZONES, each with its own
      thermostat and VAV box (Variable Air Volume).  Zones have different
      loads: server rooms are hot, lobbies are mild, freezer rooms are cold.
      The HVAC system must treat each zone independently.
    """
    def __init__(self, rect: tuple, zone_type: str, name: str,
                 temp_modifier: float):
        self.rect = pygame.Rect(*rect)
        self.zone_type = zone_type  # "hot", "cold", "normal"
        self.name = name
        self.temp_modifier = temp_modifier  # °F added per frame while inside

    def contains(self, x: float, y: float) -> bool:
        return self.rect.collidepoint(int(x), int(y))

    def get_color(self) -> tuple:
        if self.zone_type == "hot":
            return C_HOT_ZONE
        elif self.zone_type == "cold":
            return C_COOL_ZONE
        else:
            return C_NORM_ZONE


# Pre-defined map zones
MAP_ZONES = [
    Zone((50, 50, 200, 150), "hot", "Server Room", 0.05),
    Zone((50, 250, 180, 160), "hot", "Boiler Room", 0.08),
    Zone((700, 50, 210, 200), "cold", "Freezer", -0.06),
    Zone((300, 420, 250, 170), "cold", "Cold Storage", -0.04),
    Zone((350, 100, 250, 200), "normal", "Office Space", 0.0),
    Zone((700, 350, 210, 240), "hot", "Kitchen", 0.06),
]

# Heat sources (small hot spots within zones)
HEAT_SOURCES = [
    {"x": 120, "y": 120, "radius": 30, "intensity": 0.12, "name": "Server Rack"},
    {"x": 110, "y": 350, "radius": 25, "intensity": 0.15, "name": "Boiler"},
    {"x": 800, "y": 450, "radius": 28, "intensity": 0.10, "name": "Oven"},
]


# ─────────────────────────────────────────────────────────────────────────────
# AIR CONDITIONER CLASS
# ─────────────────────────────────────────────────────────────────────────────

class AirConditioner:
    """AC unit with full refrigeration cycle tracking."""

    def __init__(self, unit_id: str = "AC-001"):
        self.unit_id = unit_id
        self.running = False
        self.cycle_count = 0
        self.total_btus_removed = 0.0

        # Refrigerant state for logging
        self.suction_psi = 68.0
        self.discharge_psi = 231.0
        self.superheat_f = 10.0
        self.subcooling_f = 10.0

    def update(self, current_temp: float) -> float:
        """Thermostat logic + cooling. Returns new temp."""
        if current_temp > AC_ON_TEMP and not self.running:
            self.running = True
            self.cycle_count += 1
            # Simulate pressure changes on startup
            self.suction_psi = round(random.uniform(65, 75), 1)
            self.discharge_psi = round(random.uniform(220, 250), 1)

        if current_temp <= AC_OFF_TEMP and self.running:
            self.running = False
            self.suction_psi = 0.0
            self.discharge_psi = 0.0

        if self.running:
            cooling = COOL_RATE
            self.total_btus_removed += cooling * 50  # Simplified BTU calc
            return current_temp - cooling

        return current_temp

    def get_log_dict(self, cycle: int, temp: float) -> dict:
        """Return a dict suitable for CSV logging."""
        return {
            "timestamp": time.strftime("%H:%M:%S"),
            "cycle": cycle,
            "core_temp_f": round(temp, 1),
            "ac_running": self.running,
            "suction_psi": self.suction_psi,
            "discharge_psi": self.discharge_psi,
            "superheat_f": self.superheat_f,
            "subcooling_f": self.subcooling_f,
            "total_btus": round(self.total_btus_removed, 0),
        }


# ─────────────────────────────────────────────────────────────────────────────
# AI BRAIN (Optional Gemini)
# ─────────────────────────────────────────────────────────────────────────────

class AIBrain:
    """Optional Gemini AI for HVAC chat — graceful offline fallback."""

    SYSTEM_PROMPT = (
        "You are an HVAC expert AI inside a walking robot game. "
        "Answer HVAC questions concisely. Relate answers to the game "
        "when possible. Keep responses under 100 words."
    )

    def __init__(self):
        self.online = False
        self.client = None
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if GENAI_AVAILABLE and api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.online = True
            except Exception:
                pass

    def ask(self, question: str, context: str = "") -> str:
        if self.online:
            try:
                prompt = f"Game context: {context}\n\nQuestion: {question}"
                resp = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config={
                        "system_instruction": self.SYSTEM_PROMPT,
                        "temperature": 0.5,
                        "max_output_tokens": 200,
                    }
                )
                return resp.text
            except Exception as e:
                return f"AI Error: {e}"

        # Offline fallback
        q = question.lower()
        if "superheat" in q:
            return ("Superheat = suction line temp minus saturation temp. "
                    "Target 8-14°F. In the game, high superheat means "
                    "the AC needs more refrigerant charge.")
        elif "zone" in q:
            return ("The map has hot zones (server rooms, kitchens) and "
                    "cold zones (freezers). Your robot heats up faster in "
                    "hot zones — just like real HVAC zoning challenges.")
        elif "compressor" in q:
            return ("The compressor is the heart of the AC. It raises "
                    "pressure and temperature so heat can be rejected "
                    "outdoors. Watch your discharge pressure on the HUD.")
        return ("I'm in offline mode. Set GEMINI_API_KEY for AI chat. "
                "I know about: superheat, zones, compressors, subcooling.")


# ─────────────────────────────────────────────────────────────────────────────
# ROBOT CLASS — Full game entity
# ─────────────────────────────────────────────────────────────────────────────

class GameRobot:
    """Complete game robot with AC, AI, movement, and thermal physics."""

    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
        self.core_temp_f = 98.6
        self.distance_px = 0.0
        self.dx, self.dy = 0.0, 0.0
        self.moving = False
        self.current_zone = "Open Area"
        self.blink_timer = 0

        self.ac = AirConditioner("ROBOT-AC")
        self.brain = AIBrain()

        # Diagnostic log (in-memory)
        self.log_entries = []
        self.log_frame_counter = 0

    def handle_input(self, keys):
        self.dx, self.dy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    self.dy = -ROBOT_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:   self.dy = ROBOT_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:   self.dx = -ROBOT_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:  self.dx = ROBOT_SPEED

        if self.dx and self.dy:
            f = ROBOT_SPEED / math.sqrt(self.dx**2 + self.dy**2)
            self.dx *= f
            self.dy *= f
        self.moving = (self.dx != 0 or self.dy != 0)

    def update(self):
        # Move
        self.x = max(BODY_W//2, min(SCREEN_W - BODY_W//2, self.x + self.dx))
        self.y = max(HEAD_R + BODY_H//2,
                     min(SCREEN_H - BODY_H//2, self.y + self.dy))

        # Movement heat
        if self.moving:
            dist = math.sqrt(self.dx**2 + self.dy**2)
            self.distance_px += dist
            self.core_temp_f += dist * HEAT_PER_PX

        # Zone effects
        self.current_zone = "Open Area"
        for zone in MAP_ZONES:
            if zone.contains(self.x, self.y):
                self.current_zone = zone.name
                self.core_temp_f += zone.temp_modifier
                break

        # Heat sources (proximity-based)
        for hs in HEAT_SOURCES:
            dist = math.sqrt((self.x - hs["x"])**2 + (self.y - hs["y"])**2)
            if dist < hs["radius"] * 2:
                falloff = max(0, 1 - dist / (hs["radius"] * 2))
                self.core_temp_f += hs["intensity"] * falloff

        # Natural dissipation
        if self.core_temp_f > 75:
            self.core_temp_f -= 0.003

        # AC
        self.core_temp_f = self.ac.update(self.core_temp_f)
        self.core_temp_f = max(40.0, min(200.0, self.core_temp_f))

        # Periodic logging
        self.log_frame_counter += 1
        if self.log_frame_counter % 60 == 0:  # Every second
            self.log_entries.append(
                self.ac.get_log_dict(self.ac.cycle_count, self.core_temp_f)
            )
            # Keep last 300 entries (5 min at 1/sec)
            if len(self.log_entries) > 300:
                self.log_entries = self.log_entries[-300:]

        self.blink_timer = (self.blink_timer + 1) % 200

    def get_body_color(self) -> tuple:
        t = self.core_temp_f
        if t < 98.6:
            r = max(0, min(255, int(50 + (t - 40) * 0.85)))
            return (r, min(255, int(150 + (98.6 - t))), 255)
        elif t < AC_ON_TEMP:
            ratio = (t - 98.6) / (AC_ON_TEMP - 98.6)
            return (int(100 + 155 * ratio), int(220 - 120 * ratio), int(100 - 50 * ratio))
        else:
            ratio = min(1, (t - AC_ON_TEMP) / (OVERHEAT - AC_ON_TEMP))
            return (255, int(100 - 70 * ratio), int(50 - 20 * ratio))

    def draw(self, surface):
        bc = self.get_body_color()
        bx = int(self.x - BODY_W//2)
        by = int(self.y - BODY_H//2)

        # Shadow
        pygame.draw.rect(surface, (8, 8, 12),
                         (bx+3, by+3, BODY_W, BODY_H), border_radius=5)
        # Body
        pygame.draw.rect(surface, bc,
                         (bx, by, BODY_W, BODY_H), border_radius=5)
        pygame.draw.rect(surface, (255,255,255),
                         (bx, by, BODY_W, BODY_H), 2, border_radius=5)

        # Head
        hx, hy = int(self.x), int(self.y - BODY_H//2 - HEAD_R + 3)
        pygame.draw.circle(surface, C_HEAD, (hx, hy), HEAD_R)
        pygame.draw.circle(surface, (255,255,255), (hx, hy), HEAD_R, 2)

        # Eyes
        if self.blink_timer < 190:
            ec = C_RED if self.core_temp_f > OVERHEAT else C_EYE
            pygame.draw.circle(surface, ec, (hx-6, hy-1), 3)
            pygame.draw.circle(surface, ec, (hx+6, hy-1), 3)
            pygame.draw.circle(surface, (0,0,0), (hx-6, hy-1), 1)
            pygame.draw.circle(surface, (0,0,0), (hx+6, hy-1), 1)

        # Antenna
        pygame.draw.line(surface, C_ACCENT,
                         (hx, hy - HEAD_R), (hx, hy - HEAD_R - 10), 2)
        ant_color = C_BLUE if self.ac.running else C_ACCENT
        pygame.draw.circle(surface, ant_color, (hx, hy - HEAD_R - 10), 3)

        # AC snowflake indicator
        if self.ac.running:
            sx = bx + BODY_W + 6
            sy = by + 8
            for a in [0, 60, 120]:
                r = math.radians(a)
                pygame.draw.line(surface, C_BLUE,
                    (int(sx+5*math.cos(r)), int(sy+5*math.sin(r))),
                    (int(sx-5*math.cos(r)), int(sy-5*math.sin(r))), 2)

    def dump_csv(self, filepath: str) -> int:
        """Dump diagnostic log to CSV. Returns number of rows."""
        if not self.log_entries:
            return 0
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.log_entries[0].keys())
            writer.writeheader()
            writer.writerows(self.log_entries)
        return len(self.log_entries)


# ─────────────────────────────────────────────────────────────────────────────
# DRAWING FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def draw_grid(surface):
    for x in range(0, SCREEN_W, GRID_SIZE):
        pygame.draw.line(surface, C_GRID, (x, 0), (x, SCREEN_H))
    for y in range(0, SCREEN_H, GRID_SIZE):
        pygame.draw.line(surface, C_GRID, (0, y), (SCREEN_W, y))


def draw_zones(surface, font):
    """Draw colored zone rectangles with labels."""
    for zone in MAP_ZONES:
        # Semi-transparent zone fill
        zone_surf = pygame.Surface(
            (zone.rect.width, zone.rect.height), pygame.SRCALPHA)
        zone_surf.fill(zone.get_color())
        surface.blit(zone_surf, zone.rect.topleft)
        # Border
        border_color = C_RED if zone.zone_type == "hot" else (
            C_BLUE if zone.zone_type == "cold" else (80, 85, 100))
        pygame.draw.rect(surface, border_color, zone.rect, 1, border_radius=2)
        # Label
        label = font.render(zone.name, True, C_TEXT)
        surface.blit(label, (zone.rect.x + 5, zone.rect.y + 3))

    # Heat sources (glowing circles)
    for hs in HEAT_SOURCES:
        hs_surf = pygame.Surface((hs["radius"]*4, hs["radius"]*4), pygame.SRCALPHA)
        pygame.draw.circle(hs_surf, (255, 80, 30, 40),
                           (hs["radius"]*2, hs["radius"]*2), hs["radius"]*2)
        pygame.draw.circle(hs_surf, (255, 120, 50, 80),
                           (hs["radius"]*2, hs["radius"]*2), hs["radius"])
        surface.blit(hs_surf, (hs["x"] - hs["radius"]*2,
                               hs["y"] - hs["radius"]*2))


def draw_hud(surface, robot, font, sfont):
    """Draw the main HUD panel."""
    # Panel background
    panel = pygame.Surface((230, 210), pygame.SRCALPHA)
    panel.fill((10, 12, 20, 190))
    surface.blit(panel, (8, 8))
    pygame.draw.rect(surface, C_ACCENT, (8, 8, 230, 210), 1, border_radius=4)

    y = 14
    surface.blit(font.render("HVAC ROBOT MONITOR", True, C_ACCENT), (16, y))
    y += 22

    # Temp with color
    t = robot.core_temp_f
    tc = C_RED if t > OVERHEAT else C_YELLOW if t > AC_ON_TEMP else (
         C_GREEN if t < 105 else (255, 180, 80))
    surface.blit(font.render(f"Core: {t:.1f}°F", True, tc), (16, y))
    y += 18

    # Temp bar
    bar_w = 200
    fill = min(1, max(0, (t - 40) / 160))
    pygame.draw.rect(surface, (40, 42, 55), (16, y, bar_w, 8), border_radius=3)
    if int(bar_w * fill) > 0:
        pygame.draw.rect(surface, robot.get_body_color(),
                         (16, y, int(bar_w * fill), 8), border_radius=3)
    y += 14

    # Stats
    dm = robot.distance_px / 30.0
    stats = [
        f"Zone    : {robot.current_zone}",
        f"Distance: {dm:.1f} m",
        f"AC      : {'ON ❄' if robot.ac.running else 'STANDBY'}",
        f"Cycles  : {robot.ac.cycle_count}",
        f"BTUs    : {robot.ac.total_btus_removed:.0f}",
        f"Suction : {robot.ac.suction_psi:.0f} PSI",
        f"Dischrg : {robot.ac.discharge_psi:.0f} PSI",
        f"AI      : {'ONLINE' if robot.brain.online else 'OFFLINE'}",
    ]
    for s in stats:
        surface.blit(sfont.render(s, True, C_TEXT), (16, y))
        y += 15

    # Controls bar at bottom
    controls = "WASD:Move  C:Chat  L:Log  D:CSV Dump  ESC:Quit"
    surface.blit(sfont.render(controls, True, (90, 95, 110)),
                 (SCREEN_W//2 - 180, SCREEN_H - 22))


def draw_chat_overlay(surface, font, sfont, chat_history, input_text, robot):
    """Draw the AI chat overlay (toggle with C key)."""
    ow, oh = 420, 350
    ox = SCREEN_W - ow - 15
    oy = 15

    # Background
    overlay = pygame.Surface((ow, oh), pygame.SRCALPHA)
    overlay.fill((10, 12, 20, 230))
    surface.blit(overlay, (ox, oy))
    pygame.draw.rect(surface, C_ACCENT, (ox, oy, ow, oh), 1, border_radius=4)

    # Title
    ai_status = "🟢 AI ONLINE" if robot.brain.online else "🔴 OFFLINE MODE"
    surface.blit(font.render(f"HVAC AI CHAT — {ai_status}", True, C_ACCENT),
                 (ox + 10, oy + 6))

    # Chat history (scrollable area)
    cy = oy + 28
    max_lines = 18
    visible = chat_history[-max_lines:] if len(chat_history) > max_lines else chat_history
    for entry in visible:
        color = C_ACCENT if entry.startswith("You:") else C_GREEN
        # Word wrap
        words = entry.split()
        line = ""
        for w in words:
            test = line + " " + w if line else w
            if len(test) > 48:
                surface.blit(sfont.render(line, True, color), (ox + 10, cy))
                cy += 14
                line = w
            else:
                line = test
        if line:
            surface.blit(sfont.render(line, True, color), (ox + 10, cy))
            cy += 14
        cy += 2

    # Input area
    input_y = oy + oh - 26
    pygame.draw.rect(surface, (30, 33, 45),
                     (ox + 8, input_y, ow - 16, 20), border_radius=3)
    display_input = input_text if input_text else "Type question, Enter to send..."
    input_color = C_TEXT if input_text else (80, 85, 100)
    surface.blit(sfont.render(f"> {display_input[-40:]}", True, input_color),
                 (ox + 12, input_y + 3))


def draw_log_overlay(surface, font, sfont, robot):
    """Draw the diagnostic log overlay (toggle with L key)."""
    ow, oh = 460, 300
    ox = (SCREEN_W - ow) // 2
    oy = (SCREEN_H - oh) // 2

    overlay = pygame.Surface((ow, oh), pygame.SRCALPHA)
    overlay.fill((10, 12, 20, 235))
    surface.blit(overlay, (ox, oy))
    pygame.draw.rect(surface, C_YELLOW, (ox, oy, ow, oh), 1, border_radius=4)

    surface.blit(font.render("DIAGNOSTIC LOG (Last 15 entries)", True, C_YELLOW),
                 (ox + 10, oy + 6))

    # Column headers
    header = f"{'Time':<10s} {'Cyc':>3s} {'Temp':>7s} {'AC':>4s} {'Suct':>6s} {'Dsch':>6s} {'BTUs':>7s}"
    surface.blit(sfont.render(header, True, C_ACCENT), (ox + 10, oy + 28))

    entries = robot.log_entries[-15:] if len(robot.log_entries) > 15 else robot.log_entries
    ly = oy + 44
    for e in entries:
        ac_str = "ON" if e.get("ac_running") else "OFF"
        line = (f"{e.get('timestamp',''):<10s} "
                f"{e.get('cycle', 0):>3} "
                f"{e.get('core_temp_f', 0):>7.1f} "
                f"{ac_str:>4s} "
                f"{e.get('suction_psi', 0):>6.1f} "
                f"{e.get('discharge_psi', 0):>6.1f} "
                f"{e.get('total_btus', 0):>7.0f}")
        color = C_RED if e.get("ac_running") else C_TEXT
        surface.blit(sfont.render(line, True, color), (ox + 10, ly))
        ly += 16

    if not entries:
        surface.blit(sfont.render("No data yet — move around to generate logs.",
                                  True, (100, 105, 120)), (ox + 10, oy + 50))


# ─────────────────────────────────────────────────────────────────────────────
# NOTIFICATION SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

class Notification:
    """Brief on-screen notification message."""
    def __init__(self, text: str, duration: int = 120, color=C_GREEN):
        self.text = text
        self.frames_left = duration
        self.color = color

    def update(self) -> bool:
        self.frames_left -= 1
        return self.frames_left > 0

    def draw(self, surface, font, y_offset: int):
        alpha = min(255, self.frames_left * 4)
        txt = font.render(self.text, True, self.color)
        surface.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, 50 + y_offset))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN GAME LOOP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """
    Complete game — Robot + HVAC + Zones + AI Chat + Diagnostic Logs.

    PYTHON LESSON — STATE MANAGEMENT:
      show_chat, show_log are boolean flags that toggle overlays.
      The game manages multiple UI states simultaneously.
      This is a simple state machine — the foundation of all game UIs.

    HVAC LESSON — INTEGRATED BUILDING MANAGEMENT:
      This game mirrors a real BMS (Building Management System):
        - Zone monitoring (thermal zones on the map)
        - Equipment status (AC HUD)
        - Alarms/notifications (overheat warnings)
        - Diagnostic logging (L key / D key)
        - AI troubleshooting (C key chat)
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("HVAC Robot — Complete Game (Exercise 08)")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("monospace", 14, bold=True)
    sfont = pygame.font.SysFont("monospace", 12)

    # Create robot at center
    robot = GameRobot(SCREEN_W // 2, SCREEN_H // 2)

    # UI State
    show_chat = False
    show_log = False
    chat_history = ["AI: Welcome! Ask me HVAC questions. (C to toggle)"]
    chat_input = ""
    notifications = []

    script_dir = os.path.dirname(os.path.abspath(__file__))

    running = True
    while running:
        # ── 1. EVENTS ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_c:
                    show_chat = not show_chat
                    if show_chat:
                        show_log = False  # Close log if opening chat

                elif event.key == pygame.K_l:
                    show_log = not show_log
                    if show_log:
                        show_chat = False

                elif event.key == pygame.K_d:
                    # Dump CSV
                    path = os.path.join(script_dir, "game_diagnostic_dump.csv")
                    count = robot.dump_csv(path)
                    if count > 0:
                        notifications.append(
                            Notification(f"📝 Saved {count} records to CSV", 150, C_GREEN))
                    else:
                        notifications.append(
                            Notification("No data to dump yet!", 90, C_YELLOW))

                # Chat input handling
                elif show_chat:
                    if event.key == pygame.K_RETURN and chat_input.strip():
                        question = chat_input.strip()
                        chat_history.append(f"You: {question}")
                        context = (f"Robot temp: {robot.core_temp_f:.1f}°F, "
                                   f"Zone: {robot.current_zone}, "
                                   f"AC: {'ON' if robot.ac.running else 'OFF'}")
                        answer = robot.brain.ask(question, context)
                        chat_history.append(f"AI: {answer}")
                        chat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        chat_input += event.unicode

        # ── 2. UPDATE ──
        if not show_chat:  # Don't move while typing
            keys = pygame.key.get_pressed()
            robot.handle_input(keys)
        else:
            robot.dx, robot.dy, robot.moving = 0, 0, False

        robot.update()

        # Overheat notification
        if robot.core_temp_f > OVERHEAT:
            if not any(n.text.startswith("🔥") for n in notifications):
                notifications.append(
                    Notification("🔥 OVERHEAT WARNING! Find a cold zone!", 180, C_RED))

        # Update notifications
        notifications = [n for n in notifications if n.update()]

        # ── 3. DRAW ──
        screen.fill(C_BG)
        draw_grid(screen)
        draw_zones(screen, sfont)
        robot.draw(screen)
        draw_hud(screen, robot, font, sfont)

        if show_chat:
            draw_chat_overlay(screen, font, sfont, chat_history,
                              chat_input, robot)
        if show_log:
            draw_log_overlay(screen, font, sfont, robot)

        # Notifications
        for i, n in enumerate(notifications):
            n.draw(screen, font, i * 22)

        # ── 4. FLIP ──
        pygame.display.flip()
        clock.tick(FPS)

    # ── SHUTDOWN ──
    pygame.quit()

    print()
    print("=" * 64)
    print(" EXERCISE 08 — COMPLETE GAME FINISHED")
    print("=" * 64)
    print(f"""
 FINAL STATS:
   Core Temperature  : {robot.core_temp_f:.1f} °F
   Total Distance    : {robot.distance_px / 30:.1f} m
   AC Cycles         : {robot.ac.cycle_count}
   Total BTUs Removed: {robot.ac.total_btus_removed:.0f}
   Log Entries       : {len(robot.log_entries)}
   AI Brain          : {'ONLINE' if robot.brain.online else 'OFFLINE'}

 WHAT YOU LEARNED (FULL PROGRAM):
   Python — Classes, composition, game loops, event handling,
            overlays/state machines, file I/O, optional imports,
            try/except, list management, color math, dictionaries,
            f-strings, CSV logging, API integration, modular design

   HVAC  — Multi-zone thermal environments, VAV zoning, heat sources,
           auto-thermostat control, refrigeration cycle, diagnostic
           logging, BMS dashboards, AI-assisted troubleshooting,
           fault detection, pressure-temperature relationships

 🎉 CONGRATULATIONS! You've completed the Python HVAC Game Training!
""")


if __name__ == "__main__":
    main()
