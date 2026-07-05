"""
=============================================================================
 Robot — The Central Game Object
=============================================================================

 OOP CONCEPT: THE GAME OBJECT PATTERN
 
 In game development, a "game object" is any entity that exists in the game
 world. It typically has:
   - Position (x, y) — where it is
   - Velocity (vx, vy) — how fast it's moving  
   - An update() method — called every frame to apply physics
   - A draw() method — called every frame to render it on screen
   - State attributes — health, temperature, inventory, etc.
 
 Our Robot is the PRIMARY game object. It demonstrates:
   - COMPOSITION: The Robot HAS-AN HVACSystem and optionally HAS-A RobotBrain
   - ENCAPSULATION: Internal state (core_temp, distance) is managed by methods
   - DELEGATION: The Robot delegates cooling to its HVAC subsystem
   - POLYMORPHISM: The Robot could be subclassed into different robot types

 HVAC CONCEPT: HEAT GENERATION
 When the robot moves, its motors and actuators generate kinetic heat.
 This is the "heat load" that the internal HVAC system must counteract.
 In real buildings, heat loads come from people, lights, equipment, and
 solar gain through windows.
=============================================================================
"""

import math
import pygame
from .hvac_system import HVACSystem


class Robot:
    """
    The player-controlled robot — the central game object.
    
    Contains an internal HVAC system for temperature regulation and
    tracks physics, movement, and rendering state.
    """

    # --- Class Constants ---
    # PROGRAMMING CONCEPT: Class-level constants define shared config
    SPEED = 200.0           # Pixels per second
    BODY_WIDTH = 40
    BODY_HEIGHT = 50
    HEAD_RADIUS = 14
    HEAT_PER_PIXEL = 0.003  # Temperature rise per pixel moved
    
    # Temperature color thresholds (°F)
    TEMP_COOL = 68.0
    TEMP_NORMAL = 72.0
    TEMP_WARM = 78.0
    TEMP_HOT = 85.0
    TEMP_CRITICAL = 95.0

    def __init__(self, x: float, y: float, name: str = "RoboMech-V2"):
        """
        Initialize the Robot at the given position.
        
        OOP CONCEPT: __init__ is the CONSTRUCTOR
        It runs once when the object is created, setting up all the
        initial state values that define this specific robot instance.
        """
        # --- Identity ---
        self.name = name
        
        # --- Position & Movement (Physics State) ---
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0          # Velocity X (pixels/sec)
        self.vy = 0.0          # Velocity Y (pixels/sec)
        self.is_moving = False
        self.facing = "right"  # Direction for rendering
        
        # --- Thermodynamic State ---
        self.internal_core_temp = 71.5   # Starting temp (°F)
        self.distance_walked = 0.0       # Total pixels moved
        
        # --- Animation State ---
        self.walk_cycle = 0.0     # Animation timer for leg movement
        self.glow_pulse = 0.0     # Pulsing glow when overheating
        self.eye_blink_timer = 0.0
        self.is_blinking = False
        
        # --- COMPOSITION: Internal Systems ---
        # OOP: The Robot CONTAINS an HVAC system. It doesn't inherit from one.
        self.hvac = HVACSystem(target_temp=72.0)

    def handle_input(self, keys):
        """
        Process keyboard input to control the robot.
        
        GAME PROGRAMMING CONCEPT: INPUT HANDLING
        In the game loop, we check which keys are currently pressed
        (not just key-down events) to allow smooth, continuous movement.
        The `keys` parameter is from `pygame.key.get_pressed()`.
        """
        self.vx = 0.0
        self.vy = 0.0
        
        # WASD + Arrow key support
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.SPEED
            self.facing = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.SPEED
            self.facing = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -self.SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = self.SPEED
        
        # Normalize diagonal movement so it's not faster
        if self.vx != 0 and self.vy != 0:
            factor = 1.0 / math.sqrt(2)
            self.vx *= factor
            self.vy *= factor
        
        self.is_moving = (self.vx != 0 or self.vy != 0)

    def update(self, dt: float, outdoor_temp: float, bounds: pygame.Rect):
        """
        Update the robot's state for this frame.
        
        GAME PROGRAMMING CONCEPT: THE UPDATE STEP
        Every frame, we:
        1. Apply velocity to position (movement physics)
        2. Generate heat from movement (thermodynamics)
        3. Run the HVAC system (subsystem delegation)
        4. Update animation timers
        5. Enforce boundary constraints
        
        Parameters:
            dt: Delta time (seconds since last frame)
            outdoor_temp: Current zone's outdoor temperature
            bounds: Screen boundaries as a pygame.Rect
        """
        # --- 1. MOVEMENT PHYSICS ---
        # Position = Position + Velocity × Time
        # This is basic Euler integration — the simplest physics model
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # --- 2. BOUNDARY ENFORCEMENT ---
        # Keep the robot inside the play area
        half_w = self.BODY_WIDTH / 2
        half_h = (self.BODY_HEIGHT + self.HEAD_RADIUS * 2) / 2
        self.x = max(bounds.left + half_w, min(bounds.right - half_w, self.x))
        self.y = max(bounds.top + half_h, min(bounds.bottom - half_h, self.y))
        
        # --- 3. HEAT GENERATION FROM MOVEMENT ---
        # HVAC CONCEPT: HEAT LOAD
        # Moving motors generate waste heat. The faster and further
        # the robot moves, the more heat its core accumulates.
        if self.is_moving:
            distance_this_frame = math.sqrt((self.vx * dt) ** 2 + (self.vy * dt) ** 2)
            self.distance_walked += distance_this_frame
            heat_generated = distance_this_frame * self.HEAT_PER_PIXEL
            self.internal_core_temp += heat_generated
        
        # --- 4. HVAC SUBSYSTEM TICK ---
        # DELEGATION: The robot doesn't know HOW cooling works.
        # It just tells its HVAC system the current temp and lets
        # the subsystem handle the thermodynamics.
        self.internal_core_temp = self.hvac.tick(
            core_temp=self.internal_core_temp,
            outdoor_temp=outdoor_temp,
            dt=dt
        )
        
        # --- 5. ANIMATION TIMERS ---
        if self.is_moving:
            self.walk_cycle += dt * 8.0  # Leg animation speed
        
        # Overheating glow pulse
        if self.internal_core_temp > self.TEMP_WARM:
            self.glow_pulse += dt * 3.0
        else:
            self.glow_pulse = 0.0
        
        # Eye blink timer
        self.eye_blink_timer += dt
        if self.eye_blink_timer > 3.0:  # Blink every 3 seconds
            self.is_blinking = True
            if self.eye_blink_timer > 3.15:
                self.is_blinking = False
                self.eye_blink_timer = 0.0

    def draw(self, surface: pygame.Surface):
        """
        Render the robot on the screen.
        
        GAME PROGRAMMING CONCEPT: THE DRAW STEP
        Drawing happens AFTER update. We use the robot's current state
        (position, temperature, animation timers) to decide exactly
        what to render and where.
        
        Instead of loading sprite images, we draw the robot procedurally
        using pygame.draw shapes. This teaches the fundamentals of
        rendering without requiring external asset files.
        """
        cx = int(self.x)
        cy = int(self.y)
        
        # --- Determine body color based on temperature ---
        body_color = self._get_temp_color()
        
        # --- Draw overheating glow effect ---
        if self.internal_core_temp > self.TEMP_WARM:
            glow_alpha = int(40 + 30 * math.sin(self.glow_pulse))
            glow_radius = self.BODY_WIDTH + 15
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_color = (*body_color[:3], glow_alpha)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (cx - glow_radius, cy - glow_radius))
        
        # --- Draw legs (animated when walking) ---
        leg_offset = math.sin(self.walk_cycle) * 6 if self.is_moving else 0
        leg_y = cy + self.BODY_HEIGHT // 2
        leg_color = (120, 120, 140)
        # Left leg
        pygame.draw.line(surface, leg_color,
                         (cx - 10, leg_y),
                         (cx - 10 - leg_offset, leg_y + 15), 3)
        # Right leg
        pygame.draw.line(surface, leg_color,
                         (cx + 10, leg_y),
                         (cx + 10 + leg_offset, leg_y + 15), 3)
        
        # --- Draw body (rectangle) ---
        body_rect = pygame.Rect(
            cx - self.BODY_WIDTH // 2,
            cy - self.BODY_HEIGHT // 2 + 5,
            self.BODY_WIDTH,
            self.BODY_HEIGHT
        )
        pygame.draw.rect(surface, body_color, body_rect, border_radius=6)
        
        # Body outline
        outline_color = tuple(min(255, c + 40) for c in body_color[:3])
        pygame.draw.rect(surface, outline_color, body_rect, width=2, border_radius=6)
        
        # --- Draw chest indicator (AC status) ---
        indicator_color = (0, 255, 136) if self.hvac.is_running else (100, 100, 120)
        indicator_rect = pygame.Rect(cx - 6, cy + 2, 12, 4)
        pygame.draw.rect(surface, indicator_color, indicator_rect, border_radius=2)
        
        # --- Draw head (circle) ---
        head_y = cy - self.BODY_HEIGHT // 2 - self.HEAD_RADIUS + 8
        pygame.draw.circle(surface, body_color, (cx, head_y), self.HEAD_RADIUS)
        pygame.draw.circle(surface, outline_color, (cx, head_y), self.HEAD_RADIUS, 2)
        
        # --- Draw eyes ---
        if not self.is_blinking:
            eye_color = (0, 212, 255)  # Cyan eyes
            eye_y = head_y - 2
            eye_offset = 5 if self.facing == "right" else -5
            pygame.draw.circle(surface, eye_color, (cx - 5 + (eye_offset // 3), eye_y), 3)
            pygame.draw.circle(surface, eye_color, (cx + 5 + (eye_offset // 3), eye_y), 3)
            # Pupil dots
            pygame.draw.circle(surface, (255, 255, 255), (cx - 5 + (eye_offset // 3), eye_y), 1)
            pygame.draw.circle(surface, (255, 255, 255), (cx + 5 + (eye_offset // 3), eye_y), 1)
        else:
            # Blink: draw horizontal lines
            eye_y = head_y - 2
            pygame.draw.line(surface, (0, 212, 255), (cx - 8, eye_y), (cx - 2, eye_y), 2)
            pygame.draw.line(surface, (0, 212, 255), (cx + 2, eye_y), (cx + 8, eye_y), 2)
        
        # --- Draw antenna ---
        antenna_base = (cx, head_y - self.HEAD_RADIUS)
        antenna_tip = (cx, head_y - self.HEAD_RADIUS - 10)
        pygame.draw.line(surface, (180, 180, 200), antenna_base, antenna_tip, 2)
        # Antenna light (blinks with AC activity)
        ant_color = (0, 255, 136) if self.hvac.is_running else (255, 140, 0)
        pygame.draw.circle(surface, ant_color, antenna_tip, 3)

    def _get_temp_color(self) -> tuple:
        """
        Map core temperature to a color for visual feedback.
        
        GAME DESIGN CONCEPT: VISUAL FEEDBACK
        Players need immediate visual cues about game state. By changing
        the robot's color based on temperature, players instantly know
        when the robot is overheating without reading numbers.
        """
        t = self.internal_core_temp
        
        if t <= self.TEMP_COOL:
            return (60, 120, 200)    # Cool blue
        elif t <= self.TEMP_NORMAL:
            return (60, 180, 100)    # Normal green
        elif t <= self.TEMP_WARM:
            return (200, 180, 60)    # Warm yellow
        elif t <= self.TEMP_HOT:
            return (220, 120, 40)    # Hot orange
        else:
            return (220, 50, 50)     # Critical red

    def get_telemetry(self) -> dict:
        """
        Return all robot state as a dictionary for the HUD and AI brain.
        
        PROGRAMMING CONCEPT: DATA SERIALIZATION
        Converting internal state into a standard dict format allows
        different subsystems (HUD, AI, logging) to consume the same
        data without knowing the Robot's internal implementation.
        """
        hvac_status = self.hvac.get_status()
        return {
            "name": self.name,
            "position": (round(self.x, 1), round(self.y, 1)),
            "velocity": (round(self.vx, 1), round(self.vy, 1)),
            "is_moving": self.is_moving,
            "core_temp": round(self.internal_core_temp, 1),
            "distance_walked": round(self.distance_walked, 1),
            "facing": self.facing,
            "hvac": hvac_status,
        }

    def get_rect(self) -> pygame.Rect:
        """Return the robot's bounding box for collision detection."""
        return pygame.Rect(
            self.x - self.BODY_WIDTH // 2,
            self.y - self.BODY_HEIGHT // 2,
            self.BODY_WIDTH,
            self.BODY_HEIGHT + 20
        )
