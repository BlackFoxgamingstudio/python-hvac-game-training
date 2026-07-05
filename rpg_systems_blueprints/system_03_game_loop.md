# RPG System Blueprint: Game Loop Engine & Canvas Coordinates

Detailed specifications mapping out frame intervals, keyboard input capture arrays, collision matrices, coordinates update pipelines, and UI layer buffers.

## 🗺️ Ticker Loop & Draw Engine Topology

```mermaid
flowchart TB
    %% Subgraph 1: Core Ticker Loop
    subgraph TickerLoop ["1. RequestAnimationFrame Core Ticker"]
        direction TB
        Tick["Frame Request Ticker"] --> CalcDelta["Calculate Delta Time (dt)"]
        CalcDelta --> KeyBuffer["Read Keyboard Input Registers"]
        KeyBuffer --> PhysicsUpdate["Run Update Cycle (60 FPS)"]
    end

    %% Subgraph 2: Game State Updates
    subgraph StateUpdate ["2. Simulation State & Physics Updates"]
        direction TB
        PhysicsUpdate --> MovePlayer["Calculate Player Position (X, Y)"]
        MovePlayer --> BoundaryCheck["Resolve Tile Map Collisions"]
        BoundaryCheck --> HVACLoad["Calculate Friction Heat & Power Load"]
        HVACLoad --> RunFDD["Execute DDC Threshold Alarm checks"]
    end

    %% Subgraph 3: Graphic Rendering Pipeline
    subgraph RenderPipe ["3. Canvas Dual-Buffer Rendering"]
        direction TB
        DrawBackground["Draw Map Tiles (Ground, Walls)"] --> DrawSprites["Draw Sprite Sheet frames (Robot, AC Nodes)"]
        DrawSprites --> DrawHUD["Draw Text & Status Hud Overlay"]
        DrawHUD --> FlipBuffer["Flip Frame to Screen View"]
    end

    %% Control Loops
    RunFDD -- "Telemetry updates" --> DrawHUD
    FlipBuffer -- "Next Frame Request" --> Tick
    
    %% Visual Styles
    classDef loopCore fill:#1a1c23,stroke:#ff0055,stroke-width:2px,color:#fff;
    classDef loopState fill:#0d1b2a,stroke:#3a86c8,stroke-width:2px,color:#fff;
    classDef loopRender fill:#0b221e,stroke:#38b000,stroke-width:2px,color:#fff;
    
    class Tick,CalcDelta,KeyBuffer loopCore;
    class PhysicsUpdate,MovePlayer,BoundaryCheck,HVACLoad,RunFDD loopState;
    class DrawBackground,DrawSprites,DrawHUD,FlipBuffer loopRender;
```

---

## 🎮 Simulation Physics & Rendering Constants

### 1. Velocity and Grid Matrices
* **Target Frame Interval:** $16.67	ext{ms}$
* **Robot Nominal Movement Speed:** $120	ext{ pixels/sec}$
* **Tile Grid Array:** $20 	imes 15$ grid map (Tile Size: $32 	imes 32$ pixels, total area: $640 	imes 480$ pixels).

### 2. Collision Resolution Matrix
* Boundary checks verify the bounding box coordinate edges of the player against the grid indices.
```javascript
let tileX = Math.floor(robot.x / tileSize);
let tileY = Math.floor(robot.y / tileSize);
if (mapGrid[tileY][tileX] === 1) {
  // Prevent movement (revert coordinates to previous step frame)
}
```
