"""
=============================================================================
 HUD — Heads-Up Display for Robot Diagnostics
=============================================================================

 GAME PROGRAMMING CONCEPT: THE HUD (Heads-Up Display)
 
 A HUD is a transparent overlay that shows the player important game
 information without pausing gameplay. In our robot simulation, the HUD
 displays:
   - Core temperature gauge (visual thermometer)
   - HVAC system status (which stage is active)
   - Distance walked
   - AI chat overlay (when toggled)
   - Diagnostic log viewer (when toggled)

 RENDERING CONCEPT: LAYERED DRAWING
 The HUD draws LAST in the render pipeline, on TOP of everything else.
 Order matters: background → zones → robot → HUD
=============================================================================
"""

import pygame
import math


class HUD:
    """
    Renders all diagnostic overlays and information panels.
    
    The HUD reads telemetry data from the robot and renders it as
    visual elements using pygame.draw and pygame.font.
    """

    # --- Color Constants ---
    PANEL_BG = (10, 10, 30, 200)       # Semi-transparent dark blue
    PANEL_BORDER = (40, 40, 80)
    TEXT_PRIMARY = (220, 220, 240)
    TEXT_SECONDARY = (140, 140, 170)
    TEXT_MUTED = (90, 90, 120)
    
    CYAN = (0, 212, 255)
    GREEN = (0, 255, 136)
    ORANGE = (255, 140, 0)
    RED = (255, 51, 102)
    PURPLE = (123, 47, 247)
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize fonts and layout constants."""
        pygame.font.init()
        
        self.screen_w = screen_width
        self.screen_h = screen_height
        
        # --- Fonts ---
        try:
            self.font_title = pygame.font.SysFont("Inter", 16, bold=True)
            self.font_body = pygame.font.SysFont("Inter", 13)
            self.font_small = pygame.font.SysFont("Inter", 11)
            self.font_mono = pygame.font.SysFont("Courier", 12)
            self.font_large = pygame.font.SysFont("Inter", 20, bold=True)
        except Exception:
            self.font_title = pygame.font.Font(None, 20)
            self.font_body = pygame.font.Font(None, 16)
            self.font_small = pygame.font.Font(None, 14)
            self.font_mono = pygame.font.Font(None, 15)
            self.font_large = pygame.font.Font(None, 26)
        
        # --- Panel Dimensions ---
        self.telemetry_panel_w = 220
        self.telemetry_panel_h = 280
        self.telemetry_panel_x = screen_width - self.telemetry_panel_w - 10
        self.telemetry_panel_y = 10
        
        # --- Chat Overlay ---
        self.chat_visible = False
        self.chat_input = ""
        self.chat_panel_w = 400
        self.chat_panel_h = 300
        
        # --- Log Overlay ---
        self.log_visible = False

    def draw(self, surface: pygame.Surface, telemetry: dict, chat_history: list = None,
             log_entries: list = None, is_ai_thinking: bool = False):
        """
        Main draw method — renders all active HUD elements.
        
        Parameters:
            surface: The pygame display surface to draw on
            telemetry: Robot telemetry dict from robot.get_telemetry()
            chat_history: List of chat messages for the AI overlay
            log_entries: List of HVAC diagnostic log entries
            is_ai_thinking: Whether the AI is currently processing a query
        """
        self._draw_telemetry_panel(surface, telemetry)
        self._draw_temperature_gauge(surface, telemetry.get("core_temp", 72.0))
        self._draw_controls_hint(surface)
        
        if self.chat_visible and chat_history is not None:
            self._draw_chat_overlay(surface, chat_history, is_ai_thinking)
        
        if self.log_visible and log_entries is not None:
            self._draw_log_overlay(surface, log_entries)

    def _draw_panel_bg(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw a semi-transparent glassmorphic panel background."""
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.PANEL_BG)
        surface.blit(panel_surface, rect.topleft)
        pygame.draw.rect(surface, self.PANEL_BORDER, rect, 1, border_radius=8)

    def _draw_telemetry_panel(self, surface: pygame.Surface, telemetry: dict):
        """
        Draw the main telemetry panel in the top-right corner.
        Shows core temp, HVAC status, distance, and system stats.
        """
        rect = pygame.Rect(
            self.telemetry_panel_x, self.telemetry_panel_y,
            self.telemetry_panel_w, self.telemetry_panel_h
        )
        self._draw_panel_bg(surface, rect)
        
        x = rect.x + 12
        y = rect.y + 10
        line_h = 18
        
        # --- Title ---
        title = self.font_title.render(f"⚡ {telemetry.get('name', 'Robot')}", True, self.CYAN)
        surface.blit(title, (x, y))
        y += line_h + 6
        
        # --- Core Temperature ---
        core_temp = telemetry.get("core_temp", 72.0)
        temp_color = self._get_temp_color(core_temp)
        label = self.font_small.render("CORE TEMP", True, self.TEXT_MUTED)
        surface.blit(label, (x, y))
        y += 14
        value = self.font_large.render(f"{core_temp:.1f}°F", True, temp_color)
        surface.blit(value, (x, y))
        y += line_h + 10
        
        # --- Divider ---
        pygame.draw.line(surface, self.PANEL_BORDER, (x, y), (x + self.telemetry_panel_w - 24, y), 1)
        y += 8
        
        # --- HVAC Status ---
        hvac = telemetry.get("hvac", {})
        hvac_running = hvac.get("is_running", False)
        stage = hvac.get("current_stage", "Idle")
        stage_color = self.GREEN if hvac_running else self.TEXT_MUTED
        
        label = self.font_small.render("HVAC STATUS", True, self.TEXT_MUTED)
        surface.blit(label, (x, y))
        y += 14
        status_text = f"{'●' if hvac_running else '○'} {stage}"
        status = self.font_body.render(status_text, True, stage_color)
        surface.blit(status, (x, y))
        y += line_h + 2
        
        # Refrigerant info
        ref_text = f"Ref: {hvac.get('ref_temp', 'N/A')}°F {hvac.get('ref_pressure', '')}"
        ref = self.font_small.render(ref_text, True, self.TEXT_SECONDARY)
        surface.blit(ref, (x, y))
        y += 14
        
        ref_state = self.font_small.render(f"State: {hvac.get('ref_state', 'N/A')}", True, self.TEXT_SECONDARY)
        surface.blit(ref_state, (x, y))
        y += 14
        
        cycles_text = f"Cycles: {hvac.get('total_cycles', 0)} | Eff: {hvac.get('efficiency', 1.0):.0%}"
        cycles = self.font_small.render(cycles_text, True, self.TEXT_SECONDARY)
        surface.blit(cycles, (x, y))
        y += line_h + 4
        
        # --- Divider ---
        pygame.draw.line(surface, self.PANEL_BORDER, (x, y), (x + self.telemetry_panel_w - 24, y), 1)
        y += 8
        
        # --- Movement Stats ---
        label = self.font_small.render("MOVEMENT", True, self.TEXT_MUTED)
        surface.blit(label, (x, y))
        y += 14
        
        dist = telemetry.get("distance_walked", 0)
        dist_text = f"Distance: {dist:.0f} px"
        distance = self.font_body.render(dist_text, True, self.TEXT_PRIMARY)
        surface.blit(distance, (x, y))
        y += line_h
        
        pos = telemetry.get("position", (0, 0))
        pos_text = f"Pos: ({pos[0]:.0f}, {pos[1]:.0f})"
        position = self.font_small.render(pos_text, True, self.TEXT_SECONDARY)
        surface.blit(position, (x, y))

    def _draw_temperature_gauge(self, surface: pygame.Surface, temp: float):
        """
        Draw a vertical temperature gauge on the left side.
        
        VISUAL DESIGN: The gauge uses color gradients to show the
        temperature range from cool (blue) to critical (red).
        """
        gauge_x = 15
        gauge_y = 60
        gauge_w = 16
        gauge_h = 200
        
        # Background
        bg_rect = pygame.Rect(gauge_x - 4, gauge_y - 25, gauge_w + 8, gauge_h + 45)
        self._draw_panel_bg(surface, bg_rect)
        
        # Label
        label = self.font_small.render("TEMP", True, self.TEXT_MUTED)
        surface.blit(label, (gauge_x - 2, gauge_y - 20))
        
        # Gauge track
        track_rect = pygame.Rect(gauge_x, gauge_y, gauge_w, gauge_h)
        pygame.draw.rect(surface, (20, 20, 40), track_rect, border_radius=4)
        
        # Fill level (map temp 60-100°F to gauge height)
        fill_pct = max(0, min(1, (temp - 60) / 40))
        fill_h = int(gauge_h * fill_pct)
        
        if fill_h > 0:
            fill_rect = pygame.Rect(gauge_x, gauge_y + gauge_h - fill_h, gauge_w, fill_h)
            fill_color = self._get_temp_color(temp)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=4)
        
        # Current value
        val = self.font_small.render(f"{temp:.0f}°", True, self.TEXT_PRIMARY)
        surface.blit(val, (gauge_x - 2, gauge_y + gauge_h + 5))
        
        # Scale markers
        for t, label_text in [(60, "60"), (72, "72"), (85, "85"), (100, "100")]:
            marker_pct = (t - 60) / 40
            marker_y = gauge_y + gauge_h - int(gauge_h * marker_pct)
            pygame.draw.line(surface, self.TEXT_MUTED,
                             (gauge_x + gauge_w + 2, marker_y),
                             (gauge_x + gauge_w + 6, marker_y), 1)

    def _draw_chat_overlay(self, surface: pygame.Surface, history: list,
                            is_thinking: bool):
        """
        Draw the AI chat overlay panel.
        Shown when the player presses 'C'.
        """
        panel_x = (self.screen_w - self.chat_panel_w) // 2
        panel_y = self.screen_h - self.chat_panel_h - 20
        
        rect = pygame.Rect(panel_x, panel_y, self.chat_panel_w, self.chat_panel_h)
        self._draw_panel_bg(surface, rect)
        
        x = rect.x + 12
        y = rect.y + 10
        
        # Title
        title = self.font_title.render("🤖 AI Chat  [C to close, Enter to send]", True, self.CYAN)
        surface.blit(title, (x, y))
        y += 22
        
        # Chat history (show last few messages)
        max_messages = 6
        recent = history[-max_messages:] if history else []
        
        for msg in recent:
            role = msg.get("role", "")
            text = msg.get("text", "")
            
            if role == "user":
                prefix = self.font_small.render("YOU: ", True, self.GREEN)
            else:
                prefix = self.font_small.render("BOT: ", True, self.CYAN)
            
            surface.blit(prefix, (x, y))
            
            # Truncate long messages
            display_text = text[:60] + "..." if len(text) > 60 else text
            msg_render = self.font_small.render(display_text, True, self.TEXT_SECONDARY)
            surface.blit(msg_render, (x + 35, y))
            y += 16
        
        # Thinking indicator
        if is_thinking:
            dots = "." * (int(pygame.time.get_ticks() / 500) % 4)
            thinking = self.font_body.render(f"Thinking{dots}", True, self.ORANGE)
            surface.blit(thinking, (x, y))
            y += 18
        
        # Input field
        y = rect.y + self.chat_panel_h - 30
        input_rect = pygame.Rect(x, y, self.chat_panel_w - 24, 22)
        pygame.draw.rect(surface, (20, 20, 50), input_rect, border_radius=4)
        pygame.draw.rect(surface, self.CYAN, input_rect, 1, border_radius=4)
        
        cursor = "▌" if int(pygame.time.get_ticks() / 500) % 2 == 0 else ""
        input_text = self.font_mono.render(f"> {self.chat_input}{cursor}", True, self.TEXT_PRIMARY)
        surface.blit(input_text, (x + 6, y + 4))

    def _draw_log_overlay(self, surface: pygame.Surface, log_entries: list):
        """
        Draw the diagnostic log viewer overlay.
        Shows the last N HVAC diagnostic entries.
        """
        panel_w = 500
        panel_h = 250
        panel_x = 10
        panel_y = self.screen_h - panel_h - 20
        
        rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        self._draw_panel_bg(surface, rect)
        
        x = rect.x + 12
        y = rect.y + 10
        
        # Title
        title = self.font_title.render(f"📊 Diagnostic Log  [{len(log_entries)} entries]  [L to close]", True, self.PURPLE)
        surface.blit(title, (x, y))
        y += 22
        
        # Headers
        headers = "Cycle  Stage            Ref°F   Press  State"
        header_render = self.font_mono.render(headers, True, self.TEXT_MUTED)
        surface.blit(header_render, (x, y))
        y += 16
        
        # Show last entries
        max_entries = 12
        recent = log_entries[-max_entries:]
        
        for entry in recent:
            cycle = str(entry.get("cycle", "")).ljust(6)
            stage = str(entry.get("stage", "")).ljust(16)
            ref_temp = f"{entry.get('ref_temp', 0):.0f}".ljust(7)
            pressure = str(entry.get("ref_pressure", "")).ljust(6)
            state = str(entry.get("ref_state", ""))
            
            line = f"{cycle} {stage} {ref_temp} {pressure} {state}"
            
            # Color based on stage
            stage_name = entry.get("stage", "")
            if stage_name == "Compressor":
                color = self.ORANGE
            elif stage_name == "Evaporator":
                color = self.CYAN
            elif stage_name == "Condenser":
                color = self.GREEN
            else:
                color = self.TEXT_SECONDARY
            
            line_render = self.font_mono.render(line, True, color)
            surface.blit(line_render, (x, y))
            y += 14
            
            if y > rect.y + panel_h - 20:
                break

    def _draw_controls_hint(self, surface: pygame.Surface):
        """Draw a small controls reminder at the bottom of the screen."""
        hints = "WASD: Move  |  C: Chat  |  L: Log  |  D: Dump CSV  |  ESC: Quit"
        hint_render = self.font_small.render(hints, True, self.TEXT_MUTED)
        hint_x = (self.screen_w - hint_render.get_width()) // 2
        surface.blit(hint_render, (hint_x, self.screen_h - 20))

    def _get_temp_color(self, temp: float) -> tuple:
        """Map temperature to a color."""
        if temp <= 68:
            return (60, 120, 200)
        elif temp <= 72:
            return (60, 180, 100)
        elif temp <= 78:
            return (200, 180, 60)
        elif temp <= 85:
            return (220, 120, 40)
        else:
            return (220, 50, 50)

    def toggle_chat(self):
        """Toggle the chat overlay visibility."""
        self.chat_visible = not self.chat_visible
        if self.chat_visible:
            self.log_visible = False  # Close log when opening chat
            self.chat_input = ""

    def toggle_log(self):
        """Toggle the diagnostic log overlay visibility."""
        self.log_visible = not self.log_visible
        if self.log_visible:
            self.chat_visible = False  # Close chat when opening log
