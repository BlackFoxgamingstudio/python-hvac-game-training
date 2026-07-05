"""
=============================================================================
 Main Game — Python Systems Thinking: The Complete Robot Simulation
=============================================================================

 GAME PROGRAMMING CONCEPT: THE GAME LOOP
 
 Every video game, from Pong to AAA titles, runs on the same fundamental
 pattern — the GAME LOOP:
 
     while game_is_running:
         1. HANDLE EVENTS   — Read keyboard, mouse, window events
         2. UPDATE           — Apply physics, AI, game logic
         3. DRAW             — Render everything to the screen
         4. TICK             — Wait for the next frame (60 FPS)
 
 This is remarkably similar to how an HVAC Building Management System works:
 
     while building_is_occupied:
         1. READ SENSORS     — Temperature, humidity, CO2 levels
         2. PROCESS LOGIC    — PID control, setpoint comparison
         3. ACTUATE          — Turn on/off compressors, fans, dampers
         4. LOG & WAIT       — Record data, wait for next scan interval

 The game integrates ALL concepts from the training:
   - Python fundamentals (variables, loops, functions)
   - HVAC simulation (real thermodynamic model)
   - OOP (Robot, HVACSystem, RobotBrain, HUD as separate classes)
   - AI integration (Gemini chat overlay)
   - Diagnostic logging (CSV dump, live log viewer)
   - Game programming (game loop, input, rendering, zones)
=============================================================================
"""

import sys
import pygame
from .robot import Robot
from .hvac_system import HVACSystem
from .ai_brain import RobotBrain
from .hud import HUD


class Zone:
    """
    Represents a temperature zone in the game world.
    
    HVAC CONCEPT: ZONE CONTROL
    In commercial buildings, different areas have different thermal loads.
    A server room needs more cooling than a lobby. Zone control allows
    the BMS to manage each area independently.
    
    In our game, zones are colored rectangles with different outdoor
    temperatures that affect the robot's HVAC efficiency.
    """
    
    def __init__(self, rect: pygame.Rect, outdoor_temp: float,
                 name: str, color: tuple):
        self.rect = rect
        self.outdoor_temp = outdoor_temp
        self.name = name
        self.color = color  # (R, G, B, A) for semi-transparent fill


class Game:
    """
    The main game class — orchestrates everything.
    
    OOP CONCEPT: THE GOD OBJECT (Controller)
    The Game class is the top-level controller. It creates all other
    objects, runs the main loop, and coordinates between subsystems.
    In real game engines, this is often called the "Engine" or "Application".
    """

    # --- Screen Configuration ---
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    FPS = 60
    TITLE = "🤖 Python Systems Thinking — Robot HVAC Simulator"
    
    # --- Color Constants ---
    BG_COLOR = (12, 12, 28)
    GRID_COLOR = (22, 22, 45)
    GRID_SPACING = 40

    def __init__(self):
        """
        Initialize Pygame and create all game objects.
        
        GAME PROGRAMMING: INITIALIZATION PHASE
        Before the game loop starts, we must:
        1. Initialize the graphics engine (pygame.init)
        2. Create the display window
        3. Set up the clock for frame rate control
        4. Create all game objects (Robot, HUD, Zones)
        """
        pygame.init()
        
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(self.TITLE)
        
        # --- Frame Rate Controller ---
        # GAME CONCEPT: The clock ensures consistent frame timing.
        # tick(60) means "run at most 60 frames per second."
        self.clock = pygame.time.Clock()
        self.running = True
        
        # --- Create Game Objects ---
        self.robot = Robot(
            x=self.SCREEN_WIDTH // 2,
            y=self.SCREEN_HEIGHT // 2,
            name="RoboMech-V2"
        )
        
        self.brain = RobotBrain(bot_name="RoboMech-V2")
        
        self.hud = HUD(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # --- Create Temperature Zones ---
        self.zones = self._create_zones()
        
        # --- Game State ---
        self.current_outdoor_temp = 85.0  # Default outdoor temp
        self.play_bounds = pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Enable HVAC logging for the diagnostic viewer
        self.robot.hvac.log_enabled = True

    def _create_zones(self) -> list:
        """
        Define the temperature zones on the map.
        
        Each zone represents a different thermal environment.
        Walking through a hot zone increases the cooling challenge.
        Cold zones make the HVAC's job easier.
        """
        zones = [
            # Hot zone — like a server room or south-facing glass wall
            Zone(
                rect=pygame.Rect(750, 100, 200, 200),
                outdoor_temp=110.0,
                name="Hot Zone (110°F)",
                color=(180, 40, 40, 50)
            ),
            Zone(
                rect=pygame.Rect(50, 500, 180, 180),
                outdoor_temp=105.0,
                name="Heat Source (105°F)",
                color=(200, 60, 20, 40)
            ),
            # Cold zone — like a walk-in cooler or night time
            Zone(
                rect=pygame.Rect(400, 50, 200, 150),
                outdoor_temp=40.0,
                name="Cold Zone (40°F)",
                color=(40, 80, 180, 50)
            ),
            Zone(
                rect=pygame.Rect(100, 200, 150, 150),
                outdoor_temp=50.0,
                name="Cool Area (50°F)",
                color=(40, 100, 160, 40)
            ),
            # Normal zone — standard conditions
            Zone(
                rect=pygame.Rect(450, 400, 250, 200),
                outdoor_temp=85.0,
                name="Standard (85°F)",
                color=(60, 60, 80, 30)
            ),
        ]
        return zones

    def handle_events(self):
        """
        Process all pygame events.
        
        GAME PROGRAMMING: EVENT HANDLING
        Pygame collects all input events (key presses, mouse clicks,
        window close) into a queue. We process them one by one.
        
        We separate KEY DOWN events (single presses for toggles) from
        KEY STATE (held keys for continuous movement).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # --- Single-press key actions ---
                
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_c:
                    # Toggle AI chat overlay
                    self.hud.toggle_chat()
                
                elif event.key == pygame.K_l:
                    # Toggle diagnostic log overlay
                    self.hud.toggle_log()
                
                elif event.key == pygame.K_d:
                    # Dump diagnostic CSV
                    self.robot.hvac.dump_csv("robot_hvac_diagnostic.csv")
                
                # --- Chat Input Handling ---
                elif self.hud.chat_visible:
                    if event.key == pygame.K_RETURN:
                        # Send the chat message to the AI brain
                        if self.hud.chat_input.strip():
                            telemetry = self.robot.get_telemetry()
                            self.brain.ask(self.hud.chat_input.strip(), telemetry)
                            self.hud.chat_input = ""
                    
                    elif event.key == pygame.K_BACKSPACE:
                        self.hud.chat_input = self.hud.chat_input[:-1]
                    
                    else:
                        # Append typed character to chat input
                        if event.unicode and event.unicode.isprintable():
                            if len(self.hud.chat_input) < 80:
                                self.hud.chat_input += event.unicode

    def update(self, dt: float):
        """
        Update all game objects for this frame.
        
        GAME PROGRAMMING: THE UPDATE STEP
        This is where all game logic happens:
        1. Read current keyboard state for movement
        2. Determine which zone the robot is in
        3. Update the robot (physics, heat, HVAC)
        """
        # --- 1. Handle continuous keyboard input (if chat is NOT active) ---
        if not self.hud.chat_visible:
            keys = pygame.key.get_pressed()
            self.robot.handle_input(keys)
        else:
            # Freeze robot movement while typing
            self.robot.vx = 0
            self.robot.vy = 0
            self.robot.is_moving = False
        
        # --- 2. Determine outdoor temp based on robot's zone ---
        robot_rect = self.robot.get_rect()
        self.current_outdoor_temp = 85.0  # Default
        
        for zone in self.zones:
            if robot_rect.colliderect(zone.rect):
                self.current_outdoor_temp = zone.outdoor_temp
                # Heat sources also directly heat the robot
                if zone.outdoor_temp > 100:
                    self.robot.internal_core_temp += 0.02 * dt * (zone.outdoor_temp - 85)
                break
        
        # --- 3. Update Robot ---
        self.robot.update(dt, self.current_outdoor_temp, self.play_bounds)

    def draw(self):
        """
        Render everything to the screen.
        
        GAME PROGRAMMING: THE DRAW STEP
        Drawing order matters! We draw back-to-front:
        1. Background (grid floor)
        2. Zones (colored areas)
        3. Robot (the player character)
        4. HUD (information overlay — always on top)
        """
        # --- 1. Clear screen with background color ---
        self.screen.fill(self.BG_COLOR)
        
        # --- 2. Draw grid floor ---
        for x in range(0, self.SCREEN_WIDTH, self.GRID_SPACING):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                             (x, 0), (x, self.SCREEN_HEIGHT), 1)
        for y in range(0, self.SCREEN_HEIGHT, self.GRID_SPACING):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                             (0, y), (self.SCREEN_WIDTH, y), 1)
        
        # --- 3. Draw zones ---
        for zone in self.zones:
            # Semi-transparent zone fill
            zone_surface = pygame.Surface(
                (zone.rect.width, zone.rect.height), pygame.SRCALPHA
            )
            zone_surface.fill(zone.color)
            self.screen.blit(zone_surface, zone.rect.topleft)
            
            # Zone border
            border_color = tuple(min(255, c + 40) for c in zone.color[:3])
            pygame.draw.rect(self.screen, border_color, zone.rect, 1, border_radius=4)
            
            # Zone label
            try:
                font = pygame.font.SysFont("Inter", 11)
            except Exception:
                font = pygame.font.Font(None, 14)
            label = font.render(zone.name, True, (180, 180, 200))
            self.screen.blit(label, (zone.rect.x + 5, zone.rect.y + 5))
        
        # --- 4. Draw Robot ---
        self.robot.draw(self.screen)
        
        # --- 5. Draw HUD (always last — on top) ---
        telemetry = self.robot.get_telemetry()
        self.hud.draw(
            surface=self.screen,
            telemetry=telemetry,
            chat_history=self.brain.get_recent_history(),
            log_entries=self.robot.hvac.log_entries,
            is_ai_thinking=self.brain.is_thinking
        )
        
        # --- 6. Flip the display buffer ---
        # GAME CONCEPT: Double buffering
        # We draw to a hidden buffer, then flip it to the screen all at once.
        # This prevents flickering and tearing.
        pygame.display.flip()

    def run(self):
        """
        The MAIN GAME LOOP — the heart of the entire program.
        
        SYSTEMS THINKING: CONNECTING EVERYTHING
        This single loop connects:
        - Keyboard input (human interface)
        - Physics simulation (movement)
        - Thermodynamics (HVAC cycle)
        - Artificial intelligence (Gemini API)
        - Data logging (CSV diagnostics)
        - Rendering (visual output)
        
        Just like a real building's BMS scans sensors and actuates 
        equipment in a continuous loop, our game loop reads inputs,
        processes logic, and renders output — forever.
        """
        print("=" * 60)
        print("  🤖 Robot HVAC Simulator — Game Engine Starting")
        print("=" * 60)
        print("  Controls:")
        print("    WASD/Arrows — Move the robot")
        print("    C — Toggle AI chat")
        print("    L — Toggle diagnostic log")
        print("    D — Dump HVAC data to CSV")
        print("    ESC — Quit")
        print("=" * 60)
        
        while self.running:
            # Calculate delta time (seconds since last frame)
            # dt ensures frame-rate-independent simulation
            dt = self.clock.tick(self.FPS) / 1000.0
            
            # Cap dt to prevent physics explosions on lag spikes
            dt = min(dt, 0.05)
            
            # === THE THREE PILLARS OF THE GAME LOOP ===
            self.handle_events()    # 1. Read input
            self.update(dt)         # 2. Process logic
            self.draw()             # 3. Render output
        
        # Cleanup
        pygame.quit()
        print("\n[SHUTDOWN] Robot simulation terminated.")
        print(f"  Final Core Temp: {self.robot.internal_core_temp:.1f}°F")
        print(f"  Total Distance:  {self.robot.distance_walked:.0f} px")
        print(f"  HVAC Cycles:     {self.robot.hvac.total_cycles}")
        sys.exit(0)


# =============================================
#  Entry Point
# =============================================
if __name__ == "__main__":
    game = Game()
    game.run()
