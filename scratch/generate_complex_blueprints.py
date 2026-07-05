import os

target_dir = "/Users/russellpowers/Sovereign Biz Box/python-hvac-game-training/rpg_systems_blueprints"
os.makedirs(target_dir, exist_ok=True)

# 1. Detailed system_01_thermodynamics.md
sys_01_content = """# RPG System Blueprint: Thermodynamics & Phase Fluid Simulation

Detailed specifications, math models, and multi-layered data flow networks for the vapor-compression refrigeration cycle and air heat-transfer loops.

## 🗺️ Physical Architecture & Heat Transfer Flow

```mermaid
flowchart TB
    %% Subgraph 1: Refrigerant Loop
    subgraph RefLoop ["1. Refrigerant Circuit Loop (Pressure Boundary)"]
        direction TB
        CompSuct["Compressor Suction Port <br/> (LP Vapor, 70 PSI, 45°F)"] --> CompMotor["Isentropic Scroll Compression"]
        CompMotor --> CompDisch["Compressor Discharge Valve <br/> (HP Gas, 410 PSI, 165°F)"]
        CompDisch --> CondInlet["Condenser Coil Inlet"]
        
        CondInlet --> CondCondense["Sensible Cooling & Latent Condensation <br/> (Gas -> Liquid)"]
        CondCondense --> CondOutlet["Condenser Liquid Line <br/> (HP Liquid, 400 PSI, 95°F)"]
        
        CondOutlet --> EEVInlet["EEV Actuator Orifice <br/> (High Pressure Limit)"]
        EEVInlet --> EEVThrott["Isenthalpic Valve Expansion <br/> (Flash Gas Drop)"]
        
        EEVThrott --> EvapInlet["Evaporator Coil Entry <br/> (LP Liquid-Vapor Mix, 50 PSI, 28°F)"]
        EvapInlet --> EvapBoil["Sensible Boiling & Superheating <br/> (Heat Absorption)"]
        EvapBoil --> Accum["Suction Line Accumulator <br/> (Liquid Slugback Guard)"]
        Accum --> CompSuct
    end

    %% Subgraph 2: Air Circulation Loop
    subgraph AirLoop ["2. Air Distribution & Thermal Zone"]
        direction LR
        RoomZone["Room Space Volume <br/> (Heat Load Gain: 78°F)"] --> ReturnAir["Return Air Plenum <br/> (72°F RAT)"]
        ReturnAir --> EvapFins["Evaporator Fins <br/> (Convective Heat Transfer)"]
        EvapFins --> SupplyAir["Supply Air Duct <br/> (55°F SAT)"]
        SupplyAir --> RoomZone
    end

    %% Subgraph 3: Telemetry Sensor Network
    subgraph SensorNet ["3. Telemetry Transducer Array"]
        direction TB
        EvapTemp["Evap Temp Sensor (RTD)"]
        SuctPres["Suction Pressure Transducer"]
        DischPres["Discharge Pressure Transducer"]
        LiquidTemp["Liquid Line Sensor (Thermistor)"]
        
        SuperheatMath["Superheat Calculation <br/> (SH = Suction Temp - Evap Temp)"]
        SubcoolMath["Subcooling Calculation <br/> (SC = Saturated Cond Temp - Liquid Temp)"]
        
        EvapTemp --> SuperheatMath
        SuctPres --> SuperheatMath
        DischPres --> SubcoolMath
        LiquidTemp --> SubcoolMath
    end

    %% Decoupled Connections
    EvapBoil -- "Latent Cooling Vector" -.-> EvapFins
    CondCondense -- "Outdoor Air Rejection" -.-> OutdoorAir["Ambient Heat Sink (95°F DB)"]

    %% Visual Styles
    classDef loopRef fill:#1c2541,stroke:#3a506b,stroke-width:2px,color:#fff;
    classDef loopAir fill:#0b132b,stroke:#5bc0be,stroke-width:2px,color:#fff;
    classDef loopSensor fill:#1d3557,stroke:#e63946,stroke-width:2px,color:#fff;
    
    class CompSuct,CompMotor,CompDisch,CondInlet,CondCondense,CondOutlet,EEVInlet,EEVThrott,EvapInlet,EvapBoil,Accum loopRef;
    class RoomZone,ReturnAir,EvapFins,SupplyAir,OutdoorAir loopAir;
    class EvapTemp,SuctPres,DischPres,LiquidTemp,SuperheatMath,SubcoolMath loopSensor;
```

---

## ⚙️ Thermodynamic Simulation Models

### 1. Vapor Expansion Across the Expansion Valve (Isenthalpic Throttling)
As refrigerant moves through the expansion valve, enthalpy ($h$) remains constant, but the pressure drops rapidly:
$$h_{evap\\_in} = h_{liquid}$$
The flow coefficient ($C_v$) regulates the refrigerant flow:
$$\\dot{m} = C_v \\cdot \\sqrt{\\rho \\cdot (P_{discharge} - P_{suction})}$$

### 2. Evaporator Air Heat Balance
The heat energy extracted from the air stream ($Q_{sensible}$) must equal the heat energy absorbed by the refrigerant:
$$Q_{sensible} = 1.08 \\cdot CFM \\cdot (RAT - SAT)$$
$$Q_{refrigerant} = \\dot{m} \\cdot (h_{suction\\_gas} - h_{evap\\_in})$$

---

## 🎮 Game Objects and Specifications

### 1. Scroll Compressor Core (`rpg_comp_core`)
* **Amperage Draw Formula:** $I = (CR \\cdot 1.8) + (displacement \\cdot 0.15)$.
* **Visual Quality:** 16-frame rotative animation displaying crankshaft motion and dynamic heat glows.

### 2. Electronic Expansion Valve (`rpg_eev_actuator`)
* **Throttling Range:** 0 to 500 step increments.
* **Control Output:** Decoupled flow coefficient output variable updated at 1.0 Hz by the PID control loop.
"""

# 2. Detailed system_02_electrical_grid.md
sys_02_content = """# RPG System Blueprint: Electrical Grid & DDC Control Loops

Detailed specifications mapping out current paths, high-voltage lines, step-down transformers, DDC controller logic, and digital outputs.

## 🗺️ Power Distribution & Control Loop Schema

```mermaid
flowchart TB
    %% Subgraph 1: High Voltage 208V Line
    subgraph HighVoltage ["1. High-Voltage Power Distribution (208V AC)"]
        direction TB
        L1["Line 1 Source (L1)"] --> Disc["Safety Service Disconnect"]
        L2["Line 2 Source (L2)"] --> Disc
        
        Disc --> TerminalBlock["Distribution Terminal Block"]
        
        TerminalBlock --> CompContactor["Compressor Contactor Contacts"]
        TerminalBlock --> CondFanContactor["Condenser Fan Relay Contacts"]
        TerminalBlock --> EvapFanRelay["Evaporator Fan Relay Contacts"]
        
        CompContactor --> CompMotor["Compressor Motor Windings"]
        CondFanContactor --> CondFanMotor["Condenser Fan Motor windings"]
        EvapFanRelay --> EvapFanMotor["Evaporator Fan Motor windings"]
    end

    %% Subgraph 2: Low Voltage Control Power
    subgraph LowVoltage ["2. Low-Voltage Control System (24V AC)"]
        direction TB
        TerminalBlock --> PrimaryCoil["Transformer Primary (208V)"]
        PrimaryCoil --> SecCoil["Transformer Secondary (24V)"]
        SecCoil --> Fuse["24V System Fuse (4 Amp)"]
        
        Fuse --> CtrlHot["Control Hot Bus (R)"]
        SecCoil --> CtrlCommon["Control Common Bus (C)"]
    end

    %% Subgraph 3: DDC Control Processing
    subgraph DDCProcessor ["3. DDC Microcontroller IO Matrix"]
        direction TB
        DDC_CPU["DDC Controller CPU Core"]
        RoomRTD["Space Temp Thermistor (10K Ohm Type-III)"] --> DDC_CPU
        Setpot["Setpoint Input Variable"] --> DDC_CPU
        
        DDC_CPU --> Y1_Out["Binary Output 1: Compressor Contactor Relay (Y1)"]
        DDC_CPU --> G_Out["Binary Output 2: Evap Fan Relay Control (G)"]
        DDC_CPU --> EEV_Out["Analog Stepper Output (EEV Driver)"]
    end

    %% Control Signals
    Y1_Out -- "24V Coil Pulse" -.-> CompContactor
    G_Out -- "24V Coil Pulse" -.-> EvapFanRelay
    EEV_Out -- "PWM Stepper Steps" -.-> EEVStepper["Stepper Motor Valve Coil"]

    %% Visual Styles
    classDef highPower fill:#2d1a10,stroke:#d4ac0d,stroke-width:2px,color:#fff;
    classDef controlPower fill:#0d1b2a,stroke:#1b4965,stroke-width:2px,color:#fff;
    classDef processor fill:#141b25,stroke:#7b2cbf,stroke-width:2px,color:#fff;
    
    class L1,L2,Disc,TerminalBlock,CompContactor,CondFanContactor,EvapFanRelay,CompMotor,CondFanMotor,EvapFanMotor highPower;
    class PrimaryCoil,SecCoil,Fuse,CtrlHot,CtrlCommon,EEVStepper controlPower;
    class DDC_CPU,RoomRTD,Setpot,Y1_Out,G_Out,EEV_Out processor;
```

---

## 💡 DDC Control Logic System Specifications

### 1. PID Valve Actuation Math
The controller calculates step adjustment ($U_t$) for the EEV using:
$$U_t = K_p \\cdot e(t) + K_i \\cdot \\int_0^t e(\\tau) d\\tau + K_d \\cdot \\frac{de(t)}{dt}$$
* **Error ($e(t)$):** Current Superheat $-$ Target Superheat ($10^\\circ\\text{F}$).

### 2. Auto-Restart Guard (Anti-Short-Cycle Timer)
To prevent compressor damage from rapid restarts, an anti-short-cycle timer asserts safety interlocks:
```python
if compressor_off_time < 300: # 5 minutes cooldown
    prevent_compressor_restart = True
```
"""

# 3. Detailed system_03_game_loop.md
sys_03_content = """# RPG System Blueprint: Game Loop Engine & Canvas Coordinates

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
* **Target Frame Interval:** $16.67\text{ms}$
* **Robot Nominal Movement Speed:** $120\text{ pixels/sec}$
* **Tile Grid Array:** $20 \times 15$ grid map (Tile Size: $32 \times 32$ pixels, total area: $640 \times 480$ pixels).

### 2. Collision Resolution Matrix
* Boundary checks verify the bounding box coordinate edges of the player against the grid indices.
```javascript
let tileX = Math.floor(robot.x / tileSize);
let tileY = Math.floor(robot.y / tileSize);
if (mapGrid[tileY][tileX] === 1) {
  // Prevent movement (revert coordinates to previous step frame)
}
```
"""

# 4. Detailed system_04_data_logging.md
sys_04_content = """# RPG System Blueprint: Data Logging & Persistent VirtualFS

Detailed specifications mapping out sensor streams, Virtual File System (VFS) buffers, CSV data formatting, and cloud synchronization queues.

## 🗺️ Telemetry Buffer & Database Synchronization Pipeline

```mermaid
flowchart TB
    %% Subgraph 1: Sensor Collection
    subgraph Sensors ["1. Real-Time Sensor Array"]
        direction LR
        Therm["Thermistor temperature checks"]
        Pres["Transducer pressure checks"]
        Volt["Amperage current coil check"]
    end

    %% Subgraph 2: VFS File Handling
    subgraph VFSContainer ["2. Persistent Virtual File System (VirtualFS)"]
        direction TB
        VFS_FileOpen["open('hvac_telemetry.csv', mode)"]
        VFS_Write["VFS._files['hvac_telemetry.csv'] buffer write"]
        VFS_Close["flush() & close() cache sync"]
        
        VFS_FileOpen --> VFS_Write
        VFS_Write --> VFS_Close
    end

    %% Subgraph 3: Cloud Database Sync Queue
    subgraph DBQueue ["3. Cloud Synchronization Queue"]
        direction TB
        LocalCache["Local Telemetry Array (5-row Limit)"]
        JSONPayload["Construct JSON Synchronization Document"]
        DBSender["Firebase HTTP POST/SDK Thread"]
        
        LocalCache --> JSONPayload
        JSONPayload --> DBSender
    end

    %% Subgraph 4: Firebase Firestore
    subgraph FirebaseStorage ["4. Firebase Cloud Storage"]
        FStore[("Firestore DB <br/> /telemetry_logs/{logId}")]
    end

    %% Pipelines
    Sensors -- "RAW numbers" --> VFS_FileOpen
    VFS_Close -- "CSV formatted string" --> LocalCache
    DBSender -- "Sync Request" --> FStore

    %% Visual Styles
    classDef loggingSource fill:#2a1a1f,stroke:#ff5a00,stroke-width:2px,color:#fff;
    classDef loggingVFS fill:#0a192f,stroke:#172a45,stroke-width:2px,color:#fff;
    classDef loggingQueue fill:#160f29,stroke:#5f506b,stroke-width:2px,color:#fff;
    classDef loggingDB fill:#001524,stroke:#fca311,stroke-width:2px,color:#fff;
    
    class Therm,Pres,Volt loggingSource;
    class VFS_FileOpen,VFS_Write,VFS_Close loggingVFS;
    class LocalCache,JSONPayload,DBSender loggingQueue;
    class FStore loggingDB;
```

---

## 💾 CSV Log Record Specifications

### 1. Data Schema Columns
Trend logs are written as standard comma-separated ASCII rows:
`timestamp, cycle_index, room_temp_f, evap_temp_f, suction_pressure_psi, discharge_pressure_psi, superheat_f, subcooling_f, status_code`

### 2. VFS Persistence Implementation Rules
To ensure student code executing inside Pyodide can read and write files reliably without relying on native disk drivers, the VirtualFS maintains a class-level dictionary. Files are stored in memory and persist across multiple open/close cycles:
```python
class VirtualFS:
    _files = {} # Keyed by file path, contains raw string buffers
```
"""

# 5. Detailed system_05_ai_diagnostics.md
sys_05_content = """# RPG System Blueprint: Conversational AI Diagnostic Engine

Detailed specifications mapping context assembly, system prompts, token optimization constraints, and secure API gateways.

## 🗺️ Prompt Orchestration & Diagnostics Inference Diagram

```mermaid
flowchart TB
    %% Subgraph 1: Context Aggregator
    subgraph ContextAgg ["1. Context Aggregator Node"]
        direction TB
        StatePayload["Live state variables <br/> (Suction, Amps, Faults)"]
        CSVPayload["Last 5 rows <br/> of BAS CSV History"]
        UserPayload["User Question Text Box input"]
    end

    %% Subgraph 2: API Gateway Handler
    subgraph Gateway ["2. Backend Server Gate (/api/chat)"]
        direction TB
        TokenSec["Verify Client Auth Token"]
        JSONValidate["Validate Input Payload Structure"]
        PromptComp["Compile Context + System prompt instructions"]
        
        TokenSec --> JSONValidate
        JSONValidate --> PromptComp
    end

    %% Subgraph 3: Gemini Inference
    subgraph GeminiEngine ["3. Gemini Model Processor"]
        direction TB
        SDK["google-genai Python Client"]
        SysInst["System Instructions: Certified HVAC Engineer persona"]
        GenModel["Inference Model: gemini-2.5-flash"]
        
        SDK --> SysInst
        SysInst --> GenModel
    end

    %% Subgraph 4: Front-end Render
    subgraph UIRender ["4. Client UI Render Engine"]
        direction TB
        MDParser["Regex Markdown Parser <br/> (Handles Code blocks, tables, lists)"]
        HTMLUpdate["Inject HTML content <br/> into diagnostic chat window"]
        
        MDParser --> HTMLUpdate
    end

    %% Connection routes
    ContextAgg -- "JSON HTTP POST" --> TokenSec
    PromptComp -- "Construct payload" --> SDK
    GenModel -- "JSON response string" --> MDParser

    %% Visual Styles
    classDef context fill:#221530,stroke:#9b5de5,stroke-width:2px,color:#fff;
    classDef gate fill:#0d1b2a,stroke:#415a77,stroke-width:2px,color:#fff;
    classDef ai fill:#38040e,stroke:#d90429,stroke-width:2px,color:#fff;
    classDef ui fill:#03071e,stroke:#e85d04,stroke-width:2px,color:#fff;
    
    class StatePayload,CSVPayload,UserPayload context;
    class TokenSec,JSONValidate,PromptComp gate;
    class SDK,SysInst,GenModel ai;
    class MDParser,HTMLUpdate ui;
```

---

## 📝 Diagnostic Persona Instructions

### 1. Tone and Structural Constraints
* The AI must act as a senior controls engineer. It should explain symptoms logically rather than simply providing answers.
* Explanations must correlate physical anomalies to Python code structures (e.g., how the EEV's stepper count maps to range variables).

### 2. Context Ingestion JSON Template
```json
{
  "system_telemetry": {
    "room_temp": 82.4,
    "suction_psi": 42.0,
    "discharge_psi": 415.0,
    "fault_mode": "STUCK_VALVE"
  },
  "log_history_csv": "timestamp,cycle,room_temp,evap_temp,suction_psi\n12:59:10,3,82.7,29.1,43"
}
```
"""

# 6. Detailed system_06_quest_tree.md
sys_06_content = """# RPG System Blueprint: Quest Progression & Dialogue Engine

Detailed specifications mapping levels, dialogue nodes, user progression states, coding challenges, and unlock paths.

## 🗺️ Progression Tree & Dialogue Schema

```mermaid
flowchart TB
    %% Subgraph 1: Level Spawns & Coding Verification Gates
    subgraph LevelGates ["1. Level Gateways & Code Challenges"]
        direction TB
        L1["Level 1: Thermostat Deadband check <br/> (Verify float/int variables)"] --> L2["Level 2: Mechanical Room Core <br/> (Verify cycle functions)"]
        L2 --> L3["Level 3: Control Operations <br/> (Verify VFS CSV logger)"]
        L3 --> L4["Level 4: Assembly Warehouse <br/> (Verify class constructors)"]
        L4 --> L5["Level 5: Intelligent AI Node <br/> (Verify API key checks)"]
        L5 --> L6["Level 6: Diagnostic Bay <br/> (Verify threshold FDD check)"]
        L6 --> L7["Level 7: Simulation Engine <br/> (Verify key registers)"]
        L7 --> L8["Level 8: Central System Portal <br/> (Verify final project dashboard)"]
    end

    %% Subgraph 2: Dialogue Decision Logic
    subgraph DialogueEngine ["2. Dialogue Decision Tree"]
        direction TB
        NPCSpawn["Trigger NPC Dialogue (e.g. Master Tech)"]
        BranchCheck{"Check User Progress level"}
        UnlockD1["Show Level 1 Tutorial Dialogue"]
        UnlockD8["Show Level 8 System Diagnostic Quest"]
        
        NPCSpawn --> BranchCheck
        BranchCheck -- "level == 1" --> UnlockD1
        BranchCheck -- "level >= 8" --> UnlockD8
    end

    %% Subgraph 3: Inventory and Rewards
    subgraph RewardsEngine ["3. Quest Reward & Inventory Pipeline"]
        direction TB
        ClaimReward["Claim Quest XP & Gold"]
        WriteProgress["Write User Progress level to Firestore"]
        UnlockPart["Unlock Advanced HVAC Part sprite <br/> (Compressor, EEV, Evaporator)"]
        
        ClaimReward --> WriteProgress
        WriteProgress --> UnlockPart
    end

    %% Logic Connections
    L1 -- "Challenge Pass" -.-> ClaimReward
    L8 -- "Challenge Pass" -.-> ClaimReward
    UnlockD8 -- "Complete Objective" --> L8

    %% Visual Styles
    classDef levels fill:#141a29,stroke:#00b4d8,stroke-width:2px,color:#fff;
    classDef dialogue fill:#1a2332,stroke:#ffb703,stroke-width:2px,color:#fff;
    classDef rewards fill:#0f2a1d,stroke:#52b788,stroke-width:2px,color:#fff;
    
    class L1,L2,L3,L4,L5,L6,L7,L8 levels;
    class NPCSpawn,BranchCheck,UnlockD1,UnlockD8 dialogue;
    class ClaimReward,WriteProgress,UnlockPart rewards;
```

---

## 📜 Quest and Dialog Schema Definitions

### 1. Dialogue Node JSON Representation
```json
{
  "dialogue_id": "master_tech_start",
  "npc_name": "Master Tech",
  "dialogue_branches": [
    {
      "text": "Hello apprentice. The rooftop RTU compressor is drawing high amps.",
      "conditions": { "user_level": 8 },
      "options": [
        { "text": "Let me query the BAS trend log.", "next_node": "master_tech_diagnose" },
        { "text": "I'll inspect the EEV.", "next_node": "master_tech_eev" }
      ]
    }
  ]
}
```

### 2. User State Progression Table
* **Level 1:** Requirements: Complete Thermostat variables challenge. Unlocks Level 2.
* **Level 8:** Requirements: Complete final HVAC simulation challenge. Unlocks Certified Smart Building Control Systems Specialist title.
"""

# Write files out
with open(os.path.join(target_dir, "system_01_thermodynamics.md"), "w") as f:
    f.write(sys_01_content)

with open(os.path.join(target_dir, "system_02_electrical_grid.md"), "w") as f:
    f.write(sys_02_content)

with open(os.path.join(target_dir, "system_03_game_loop.md"), "w") as f:
    f.write(sys_03_content)

with open(os.path.join(target_dir, "system_04_data_logging.md"), "w") as f:
    f.write(sys_04_content)

with open(os.path.join(target_dir, "system_05_ai_diagnostics.md"), "w") as f:
    f.write(sys_05_content)

with open(os.path.join(target_dir, "system_06_quest_tree.md"), "w") as f:
    f.write(sys_06_content)

print("All complex blueprint documentation files generated successfully!")
