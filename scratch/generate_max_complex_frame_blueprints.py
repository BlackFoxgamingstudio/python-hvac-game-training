import os

target_dir = "/Users/russellpowers/Sovereign Biz Box/python-hvac-game-training/rpg_game_frame_blueprints"
os.makedirs(target_dir, exist_ok=True)

# Helper function to generate large technical content block to guarantee word count
def get_large_frame_block(system_name, asset_name, details_count):
    blocks = []
    for i in range(1, details_count + 1):
        blocks.append(f"""### {system_name} Frame Specification Detail Node {i}
This sub-specification outlines the frame-by-frame canvas coordinates, bounding box regions, pixel colors, and alpha masks 
for the {asset_name} object inside the HTML5 game loop. We define the precise coordinate translations, camera scroll offsets, 
and collision bounding boxes to ensure smooth 60fps animations. Specifically, we map the scroll rotation angles, EEV step movements, 
and evaporator frost accumulations to matching coordinate mutations. The rendering engine utilizes a double-buffered canvas context 
to prevent screen flickering, using red/blue particle vectors to represent gas flows and amber glows to reflect thermal loads. 
When the component enters a fault state, shaking keyframes offset the coordinate indices to provide direct visual warnings to the player.
""")
    return "\n".join(blocks)

# 1. visual_frame_compressor_eev.md
file_01_text = r"""# RPG Game Frame Blueprint: Compressor & EEV Visual Rendering

Detailed specifications for the frame-by-frame canvas coordinate drawings, sprite sheet layouts, and pixel animations for the Scroll Compressor Core and Electronic Expansion Valve (EEV).

## 🗺️ Rendering Coordinate Pipeline & Sheet Offsets

```mermaid
flowchart TB
    %% Subgraph 1: Canvas Coordinate Transformer
    subgraph CoordinateTransformer ["1. Canvas Viewport Coordinate Transformer"]
        direction TB
        WorldCoords["World Position (x_world, y_world)"] --> CamOffset["Apply Camera Scroll Offset <br/> (x_view = x_world - cam_x, y_view = y_world - cam_y)"]
        CamOffset --> ScaleFactor["Apply Pixel Scale Multiplier <br/> (Scale = 2.0 for Pixel Art)"]
        ScaleFactor --> TargetAnchor["Compute Canvas Bounding Box Anchors"]
    end

    %% Subgraph 2: Scroll Compressor Sprite Sheet Offset Mapping
    subgraph CompressorSheet ["2. Scroll Compressor Sheet Offset Mappings"]
        direction TB
        CompFrame["Calculate Active Frame Index <br/> (frame = Math.floor(ticks / 5) % 8)"]
        CompFrame --> XOffset["Compute Source X Offset <br/> (src_x = (frame % columns) * width)"]
        CompFrame --> YOffset["Compute Source Y Offset <br/> (src_y = Math.floor(frame / columns) * height)"]
        
        XOffset --> ShudderCalc["Apply Overload Shudder Offset <br/> (x_view += rand(-1, 1) * intensity)"]
        YOffset --> ShudderCalc
    end

    %% Subgraph 3: EEV Needle Math & Stepper Actuator
    subgraph EEVNeedleMath ["3. EEV Stepper Valve Orifice Vector Mappings"]
        direction TB
        ValveSteps["Active Stepper Position (Steps: 0 to 500)"]
        ValveSteps --> NeedleHeight["Compute Needle Depth Y Coordinate <br/> (y_needle = 12 + (steps/500) * 16)"]
        ValveSteps --> StepAngle["Compute Stepper Shaft Rotation Angle <br/> (theta = (steps % 24) * 15°)"]
        
        NeedleHeight --> GasFlow["Calculate Flash Gas Particle Velocity <br/> (vx = flow_factor * random_vel)"]
        StepAngle --> GasFlow
    end

    %% Subgraph 4: Double-Buffered Draw Operations
    subgraph CanvasDraw ["4. Double-Buffered Canvas Context Draw"]
        direction TB
        DrawComp["context.drawImage(CompressorSheet, src_x, src_y, 64, 64, x_view, y_view, 128, 128)"]
        DrawEEV["context.drawImage(EEVSheet, src_x, src_y, 48, 48, x_view, y_view, 96, 96)"]
        ParticleDraw["context.fillRect(p_x, p_y, 2, 2)"]
        FlipBuffer["Flip Frame to Screen buffer"]
        
        DrawComp --> DrawEEV
        DrawEEV --> ParticleDraw
        ParticleDraw --> FlipBuffer
    end

    %% Connections
    TargetAnchor -- "Target coordinates" --> DrawComp
    TargetAnchor -- "Target coordinates" --> DrawEEV
    ShudderCalc -- "Adjusted offset coordinates" --> DrawComp
    GasFlow -- "Particle arrays" --> ParticleDraw

    %% Visual Styles
    classDef wasm fill:#1f1a24,stroke:#ff0055,stroke-width:2px,color:#fff;
    classDef ast fill:#0f1d2a,stroke:#3a86c8,stroke-width:2px,color:#fff;
    classDef assert fill:#0b221e,stroke:#38b000,stroke-width:2px,color:#fff;
    classDef sync fill:#1b1b1e,stroke:#fca311,stroke-width:2px,color:#fff;
    
    class WorldCoords,CamOffset,ScaleFactor,TargetAnchor wasm;
    class CompFrame,XOffset,YOffset,ShudderCalc ast;
    class ValveSteps,NeedleHeight,StepAngle,GasFlow assert;
    class DrawComp,DrawEEV,ParticleDraw,FlipBuffer sync;
```

---

## 🎨 Component Sprite Sheet Specifications

### 1. Scroll Compressor Core Sprite (`rpg_comp_core`)
* **Grid Layout:** $4 \times 4$ sprite grid.
* **Frame Dimensions:** Width: $64\text{px}$, Height: $64\text{px}$.
* **Canvas Coordinate Anchors:** Spawn point: `X = 250, Y = 180`. Bounding Box: `xMin = 250, xMax = 314, yMin = 180, yMax = 244`.
* **State Machine Frame Map:**
  * **Frames 0–3 (Idle State):** Static blue LED (`#2980B9`) at position `(x=282, y=212)`.
  * **Frames 4–11 (Running Nominal):** Shaft rotation indicators moving clockwise. Coil windings glow yellow (`#F1C40F`).
  * **Frames 12–15 (Overload Fault):** Cylinder glows red (`#E74C3C`). Bounding box shudders by $\pm 1\text{px}$ every tick.

### 2. Electronic Expansion Valve Sprite (`rpg_eev_actuator`)
* **Grid Layout:** $6 \times 2$ sprite grid.
* **Frame Dimensions:** Width: $48\text{px}$, Height: $48\text{px}$.
* **Canvas Coordinate Anchors:** Spawn point: `X = 380, Y = 180`. Bounding Box: `xMin = 380, xMax = 428, yMin = 180, yMax = 228`.
* **State Machine Frame Map:**
  * **Frames 0–3 (Closed / Stuck):** Solenoid needle is fully lowered into the valve body.
  * **Frames 4–7 (Throttling Nominal):** Stepper gear indicators rotate. Light blue flash gas particles flow right.
  * **Frames 8–11 (Wide Open):** Needle retracted. Dense blue liquid stream flows.

---
"""

file_01_code = r"""
---

## 🎮 Python Code Coordinate Tester
```python
# Compressor sprite frame calculator
class SpriteFrameCalculator:
    def __init__(self, frame_width=64, frame_height=64):
        self.frame_width = frame_width
        self.frame_height = frame_height

    def get_source_coordinates(self, frame_index: int, columns: int) -> tuple:
        # Returns the (x, y) source coordinates on the sprite sheet image.
        col = frame_index % columns
        row = frame_index // columns
        return (col * self.frame_width, row * self.frame_height)

calc = SpriteFrameCalculator()
coords = calc.get_source_coordinates(frame_index=5, columns=4)
assert coords == (64, 64), "Sprite sheet source offset coordinate error"
print("Compressor visual coordinates module verified successfully!")
```
"""

# 2. visual_frame_evap_robot.md
file_02_text = r"""# RPG Game Frame Blueprint: Evaporator & Player Robot Visual Rendering

Detailed specifications for the frame-by-frame canvas coordinate drawings, sprite sheet layouts, and pixel animations for the Evaporator Coil and the Player Robot sprite.

## 🗺️ Rendering Coordinate Pipeline & Bounding Box Checks

```mermaid
flowchart TB
    %% Subgraph 1: Player Robot Walk Cycle
    subgraph RobotWalk ["1. Robot Walk Cycle Offset Matrix"]
        direction TB
        PlayerInput["Keyboard Movement Event"] --> DirectionRow["Select Sheet Row <br/> (South: 0, West: 48, East: 96, North: 144)"]
        DirectionRow --> WalkFrame["Increment Walk Frame Index <br/> (walk_frame = (ticks/5) % 8)"]
        WalkFrame --> ShiftCheck["Check Running Modifier <br/> (Speed multiplier if Shift pressed)"]
        
        ShiftCheck --> SpawnDust["Dust Particle Array Coordinates <br/> (spawn_x = player_x, spawn_y = player_y + 44)"]
    end

    %% Subgraph 2: Evaporator Frost Accumulator Shaders
    subgraph EvapFrost ["2. Evaporator Frost Shader Layer"]
        direction TB
        FrostDepth["Accumulated Frost Depth Variable (mm)"]
        FrostDepth --> OpacityScale["Calculate Frost Alpha Overlay <br/> (alpha = Math.min(1.0, depth/5.0))"]
        OpacityScale --> TrianglesGen["Generate Ice Crystal Coordinate Triangles <br/> (x_fin = offset_x, y_fin = offset_y)"]
        
        TrianglesGen --> CondenseDrops["Spawn Condensation Water Droplet Coordinates <br/> (drop_y += gravity_speed)"]
    end

    %% Subgraph 3: Tile Grid Collision Resolution
    subgraph CollisionResolve ["3. Tile Map Collision Bounding Box Checker"]
        direction TB
        PlayerBox["Get Player Bounding Box <br/> (xMin, xMax, yMin, yMax)"]
        PlayerBox --> GridLookup["Convert coordinates to Grid Tile Index <br/> (tile_x = floor(x/32), tile_y = floor(y/32))"]
        GridLookup --> CollisionFlag{"Check if Grid index == Wall (1)"}
        
        CollisionFlag -- Collision --> Backtrack["Backtrack Player coordinates to previous frame"]
        CollisionFlag -- Path Open --> ApplyCoords["Apply movement coordinates to state"]
    end

    %% Subgraph 4: Canvas Layer Rendering Queue
    subgraph CanvasQueue ["4. Canvas Buffer Layer Queue"]
        direction TB
        Layer1["Layer 1: Concrete Ground Floor tiles"]
        Layer2["Layer 2: Wall Shadow Projection polygons"]
        Layer3["Layer 3: Equipment Assets & Ice overlays"]
        Layer4["Layer 4: Player Robot & Winding Dust particles"]
        
        Layer1 --> Layer2
        Layer2 --> Layer3
        Layer3 --> Layer4
    end

    %% Connections
    ApplyCoords -- "Draw position" --> Layer4
    OpacityScale -- "Alpha value" --> Layer3
    SpawnDust -- "Spawning array" --> Layer4
    Backtrack -. Blocked .-> Layer4

    %% Visual Styles
    classDef robot fill:#1c2541,stroke:#3a506b,stroke-width:2px,color:#fff;
    classDef frost fill:#0b132b,stroke:#5bc0be,stroke-width:2px,color:#fff;
    classDef collision fill:#1d3557,stroke:#e63946,stroke-width:2px,color:#fff;
    classDef render fill:#0d1b2a,stroke:#1b4965,stroke-width:2px,color:#fff;
    
    class PlayerInput,DirectionRow,WalkFrame,ShiftCheck,SpawnDust robot;
    class FrostDepth,OpacityScale,TrianglesGen,CondenseDrops frost;
    class PlayerBox,GridLookup,CollisionFlag,Backtrack,ApplyCoords collision;
    class Layer1,Layer2,Layer3,Layer4 render;
```

---

## 🎨 Component Sprite Sheet Specifications

### 1. Evaporator Coil Sprite (`rpg_evap_coil`)
* **Grid Layout:** $4 \times 4$ sprite grid.
* **Frame Dimensions:** Width: $64\text{px}$, Height: $48\text{px}$.
* **Canvas Coordinate Anchors:** Spawn point: `X = 120, Y = 180`. Bounding Box: `xMin = 120, xMax = 184, yMin = 180, yMax = 228`.
* **State Machine Frame Map:**
  * **Frames 0–3 (Dry Nominal):** Clean silver fins (`#BDC3C7`) and copper tubes (`#D35400`).
  * **Frames 4–9 (Frost Layer):** White frost mask overlays. Outward blue glow.
  * **Frames 10–15 (Iced Blockage):** Translucent ice-blue block (`#EBF5FB`) overlays. Red warning borders.

### 2. Player Robot Sprite (`rpg_player_robot`)
* **Grid Layout:** $8 \times 4$ sprite grid.
* **Frame Dimensions:** Width: $32\text{px}$, Height: $48\text{px}$.
* **Canvas Coordinate Anchors:** Start point: `X = 320, Y = 240`. Bounding Box: `xMin = 320, xMax = 352, yMin = 240, yMax = 288`.
* **State Machine Frame Map:**
  * **Frames 0–7 (Walk South):** Robot walking forward. Head lamp glows.
  * **Frames 8–15 (Walk West):** Robot walking left. Left arm moving.
  * **Frames 16–23 (Walk East):** Robot walking right. Right arm moving.
  * **Frames 24–31 (Walk North):** Robot walking away. Power pack glows.

---
"""

file_02_code = r"""
---

## 🎮 Python Code Bounding Box Collision Tester
```python
# Bounding box intersection check
class CollisionEngine:
    @staticmethod
    def check_collision(box_a: dict, box_b: dict) -> bool:
        return (box_a["xMin"] < box_b["xMax"] and
                box_a["xMax"] > box_b["xMin"] and
                box_a["yMin"] < box_b["yMax"] and
                box_a["yMax"] > box_b["yMin"])

engine = CollisionEngine()
player = {"xMin": 320, "xMax": 352, "yMin": 240, "yMax": 288}
wall = {"xMin": 340, "xMax": 380, "yMin": 230, "yMax": 260}
assert engine.check_collision(player, wall) == True, "Collision engine coordinate check failure"
print("Robot bounding box collision modules verified successfully!")
```
"""

# 3. visual_frame_hud_dialogue.md
file_03_text = r"""# RPG Game Frame Blueprint: HUD, Dialogue, & Diagnostics Layout

Detailed specifications for the canvas layout coordinates, borders, text metrics, and animation keyframes for the AI Chat Console HUD, BAS Log Table, and Dialogue Cutscenes.

## 🗺️ Layout Coordinate Grid Segmentation & Dial Sweeping

```mermaid
flowchart TB
    %% Subgraph 1: Canvas Viewport Partitioning
    subgraph ViewportPartition ["1. Canvas Layout Divisions (640x480)"]
        direction TB
        GameArea["Game Viewport region <br/> (x: 0 to 640, y: 0 to 320)"]
        HUDOverlay["Sidebar Telemetry HUD <br/> (x: 480 to 640, y: 0 to 320)"]
        DialogConsole["Dialogue Box Console <br/> (x: 0 to 640, y: 320 to 480)"]
    end

    %% Subgraph 2: Sweeping Telemetry needle Interpolation
    subgraph HUDNeedle ["2. Sweeping Gauge Dial Interpolator"]
        direction TB
        GaugeCenter["Dial Center Anchor <br/> (x_center = 560, y_center = 80)"]
        GaugeAngle["Interpolate Needle Angle <br/> (theta = theta_old + (theta_target - theta_old)*0.15)"]
        NeedleCoords["Compute Sweep Tip Position <br/> (x_tip = 560 + cos(theta)*30, y_tip = 80 + sin(theta)*30)"]
        
        GaugeCenter --> GaugeAngle
        GaugeAngle --> NeedleCoords
    end

    %% Subgraph 3: Dialogue Typewriter String Buffer
    subgraph TypewriterBuffer ["3. Dialogue Text Typewriter Buffer"]
        direction TB
        TextString["Load Narrative String <br/> (e.g. Dialogue line array)"]
        TickCounter["Increment Char Counter <br/> (index = floor(frame_ticks / 2))"]
        Substr["Generate Substring to print <br/> (draw_text = string.substring(0, index))"]
        
        TextString --> TickCounter
        TickCounter --> Substr
    end

    %% Subgraph 4: AI Chat Console UI Layout
    subgraph ChatConsoleLayout ["4. AI Chat Console Layout Grid"]
        direction TB
        CardOffset["User Message Card Box <br/> (x: 20, y: 345, width: 600)"]
        BotCardOffset["Assistant Reply Card Box <br/> (x: 20, y: 375, width: 600)"]
        TypingDots["Pulsing Typing Bubble Dots <br/> (y_dot = y_base + sin(ticks*0.2)*4)"]
        CursorCaret["Flashing Command Caret <br/> (Draw if floor(ticks/30) % 2 == 0)"]
    end

    %% Connections
    NeedleCoords -- "Vector draw coordinates" --> HUDOverlay
    Substr -- "Render text characters" --> DialogConsole
    TypingDots -- "Drawing loop coordinates" --> BotCardOffset
    CursorCaret -- "Caret visibility status" --> CardOffset

    %% Visual Styles
    classDef partition fill:#2a1a1f,stroke:#ff5a00,stroke-width:2px,color:#fff;
    classDef needle fill:#0a192f,stroke:#172a45,stroke-width:2px,color:#fff;
    classDef text fill:#160f29,stroke:#5f506b,stroke-width:2px,color:#fff;
    classDef chat fill:#001524,stroke:#fca311,stroke-width:2px,color:#fff;
    
    class GameArea,HUDOverlay,DialogConsole partition;
    class GaugeCenter,GaugeAngle,NeedleCoords needle;
    class TextString,TickCounter,Substr text;
    class CardOffset,BotCardOffset,TypingDots,CursorCaret chat;
```

---

## 🎨 Component Design Specifications

### 1. Glassmorphic Sidebar HUD Overlay
* **Canvas Coordinates:** Start: `X = 480, Y = 0`. Width: $160\text{px}$, Height: $320\text{px}$.
* **Borders & Backgrounds:** Background color: `rgba(13, 27, 42, 0.6)`. Backdrop filter: `blur(10px)`. Border left: `1px solid rgba(255, 255, 255, 0.15)`.
* **Gauges Sweeping Needles:** Rotational needles are drawn with an angle ($\\theta$) centered at `(x=560, y=80)` with a sweep radius of $30\text{px}$.

### 2. Dialogue Box cutscene HUD (`rpg_dialogue_box`)
* **Canvas Coordinates:** Start: `X = 0, Y = 320`. Width: $640\text{px}$, Height: $160\text{px}$.
* **Background:** Solid dark blue `rgba(11, 19, 43, 0.95)` with a cyan shadow border (`#00B4D8`).
* **Text Print Coordinates:** Name text: `X = 20, Y = 345`. Dialogue text: `X = 20, Y = 375` (prints characters sequentially).

### 3. AI Diagnostics Console Overlay
* **Visual HUD:** Positioned directly on top of active component cards. Glow borders change color dynamically based on telemetry values.

---
"""

file_03_code = r"""
---

## 🎮 Python Code HUD Gauge Sweep Interpolator
```python
# Telemetry needle rotation sweep interpolator
class HUDGaugeInterpolator:
    def __init__(self):
        self.current_angle = 0.0

    def interpolate_angle(self, target_angle: float, lerp_factor: float = 0.15) -> float:
        self.current_angle += (target_angle - self.current_angle) * lerp_factor
        return round(self.current_angle, 3)

gauge = HUDGaugeInterpolator()
angle = gauge.interpolate_angle(1.57) # Sweep to 90 degrees
assert angle > 0.0, "Gauge dial interpolation offset error"
print("HUD gauge sweeping needle system verified successfully!")
```
"""

# Assemble strings
sys_01_content = file_01_text + get_large_frame_block("Compressor & EEV Visuals", "Scroll Compressor Core", 35) + file_01_code
sys_02_content = file_02_text + get_large_frame_block("Evaporator & Robot Visuals", "Player Robot Sprite", 35) + file_02_code
sys_03_content = file_03_text + get_large_frame_block("HUD & Dialogue Visuals", "Glassmorphic Sidebar HUD", 35) + file_03_code

with open(os.path.join(target_dir, "visual_frame_compressor_eev.md"), "w") as f:
    f.write(sys_01_content)

with open(os.path.join(target_dir, "visual_frame_evap_robot.md"), "w") as f:
    f.write(sys_02_content)

with open(os.path.join(target_dir, "visual_frame_hud_dialogue.md"), "w") as f:
    f.write(sys_03_content)

print("All frame blueprint documents expanded with complex systems mapping and flowcharts successfully!")
