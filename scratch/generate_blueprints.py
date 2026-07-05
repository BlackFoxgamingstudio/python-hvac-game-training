import os

# Create the directory for RPG blueprints
target_dir = "/Users/russellpowers/Sovereign Biz Box/python-hvac-game-training/rpg_systems_blueprints"
os.makedirs(target_dir, exist_ok=True)

# 1. Thermodynamics System Blueprint
sys_01_content = """# RPG System Blueprint: Thermodynamics & Phase Fluid Simulation

This document defines the variables, components, visual specs, and data flows for the physical refrigerant and air systems modeled across the RPG.

## 🗺️ System Interaction Topology

```mermaid
flowchart TB
    subgraph EvaporatorCoil ["Evaporator Phase Change Node"]
        EvapIn["Low-Temp Liquid-Vapor Mixture"] --> EvapBoil["Sensible & Latent Heat Absorption"]
        EvapBoil --> EvapOut["Low-Pressure Superheated Vapor"]
    end

    subgraph CompressorMotor ["Compressor Pressure Boost Node"]
        EvapOut --> CompIn["Suction Gas Inlet"]
        CompIn --> CompWork["Isentropic Compression Work"]
        CompWork --> CompOut["High-Pressure Hot Discharge Vapor"]
    end

    subgraph CondenserCoil ["Condenser Heat Rejection Node"]
        CompOut --> CondCool["Sensible & Latent Condensation"]
        CondCool --> CondOut["High-Pressure Subcooled Liquid"]
    end

    subgraph ExpansionValve ["Throttling & Pressure Drop Node"]
        CondOut --> EEVThrottle["Isenthalpic Pressure Drop"]
        EEVThrottle --> EvapIn
    end

    classDef cycle fill:#1a263b,stroke:#415a77,stroke-width:2px,color:#fff;
    class EvaporatorCoil,CompressorMotor,CondenserCoil,ExpansionValve cycle;
```

## ⚙️ Thermodynamic System Equations

### 1. Compressor Work and Enthalpy Mutation
The energy added to the system ($W_{comp}$) matches the enthalpy shift:
$$W_{comp} = \\dot{m} \\cdot (h_{discharge} - h_{suction})$$

### 2. Evaporator Heat Absorption
The cooling load ($Q_{evap}$) absorbed by the coil is calculated using:
$$Q_{evap} = \\dot{m} \\cdot (h_{suction} - h_{evap\\_in})$$

---

## 🎮 Game Objects and Specifications

### 1. Scroll Compressor Core (`rpg_comp_core`)
* **Features:** Variable frequency motor simulation, dynamic noise vibration, thermal decay thresholds.
* **Sprite Sheets:** 16 frames of animation mapping current voltage loops.

### 2. Condenser Coil Assembly (`rpg_cond_coil`)
* **Features:** Subcooling state variables, ambient fan efficiency offsets.
* **Sprite Sheets:** 8 frames representing condensation air particle vectors.
"""

# 2. Electrical Grid & Control Loops Blueprint
sys_02_content = """# RPG System Blueprint: Electrical Grid & DDC Control Loops

Defines the voltage nodes, wiring loops, current meters, and automated DDC logic rules.

## 🗺️ System Topology

```mermaid
flowchart TD
    PowerSource["208V AC Line Source"] --> MainBreaker["Main Overcurrent Breaker"]
    MainBreaker --> Contactor["Compressor Magnetic Contactor"]
    MainBreaker --> FanRelay["Evaporator Fan Speed Relay"]
    
    Contactor --> CompMotor["Compressor Motor Stator"]
    FanRelay --> FanMotor["Evaporator Fan Motor windings"]
    
    MicroController["DDC Controller Node"] -- "24V Control Signal" --> Contactor
    MicroController -- "24V Control Signal" --> FanRelay
    
    classDef power fill:#2a1f10,stroke:#d4ac0d,stroke-width:2px,color:#fff;
    classDef control fill:#0d1b2a,stroke:#1b4965,stroke-width:2px,color:#fff;
    class PowerSource,MainBreaker,Contactor,FanRelay,CompMotor,FanMotor power;
    class MicroController control;
```

## 💡 DDC Logic Specifications

### Thermostat Deadband Checks
```python
if current_temp > setpoint + deadband:
    stage_cooling_on()
elif current_temp < setpoint - deadband:
    stage_cooling_off()
```
"""

# 3. Game Loop Engine & Canvas Coordinates
sys_03_content = """# RPG System Blueprint: Game Loop Engine & Collision Coordinates

Defines the core rendering cycles, frame tickers, collision boundaries, and keyboard listeners.

## 🗺️ Loop Pipeline Topology

```mermaid
flowchart LR
    Start["Loop Initializer"] --> GetInput["Keyboard Listener Buffer"]
    GetInput --> UpdatePhysics["Delta Time Frame Update"]
    UpdatePhysics --> ResolveCollisions["Map Boundary Collision Engine"]
    ResolveCollisions --> RenderFrame["Canvas Draw Sprite Buffers"]
    RenderFrame --> FrameTicker["RequestAnimationFrame Loop"]
    FrameTicker --> GetInput
```

## 🎮 Game Engine Constants
* **Target FPS:** 60 FPS ($16.67\\text{ms}$ ticks)
* **Tile Size:** $32 \\times 32$ pixels
* **Map Size:** $20 \\times 15$ tiles ($640 \\times 480$ Canvas width/height)
"""

# 4. Data Logging & Persistent VFS
sys_04_content = """# RPG System Blueprint: Data Logging & Persistent VirtualFS

Maps the write buffers, CSV trend table streams, and Firestore logging synchronizers.

## 🗺️ Telemetry Pipe Topology

```mermaid
flowchart TD
    Sensor["Thermistor & Transducer Array"] -- Readings --> Logger["CSV File Writer Instance"]
    Logger -- Flush --> VFS["VirtualFS Memory Cache"]
    VFS -- Sync Queue --> FirebaseSender["Firestore Appending Thread"]
    FirebaseSender --> Firestore[("Firestore Telemetry Collection")]
```
"""

# 5. AI Ingestion & Prompt Assembly
sys_05_content = """# RPG System Blueprint: Conversational AI Diagnostic Engine

Defines prompt generation pipelines, token buffers, and diagnostic response markdown parsing.

## 🗺️ Prompt Pipeline Topology

```mermaid
flowchart LR
    CSVHistory["5-row Telemetry CSV"] --> PromptCompiler["System Prompt Aggregator"]
    StateVars["Active System Variables"] --> PromptCompiler
    UserQuestion["User Question String"] --> PromptCompiler
    PromptCompiler --> GemSDK["google-genai Client Connection"]
    GemSDK --> Gemini["Gemini-2.5-Flash Inference Engine"]
```
"""

# 6. Quest & Story Progression Tree
sys_06_content = """# RPG System Blueprint: Quest Progression & Dialogue Engine

Defines the story chapters, quest trigger items, dialog schemas, and experience point rewards.

## 🗺️ Quest Tree Flowchart

```mermaid
flowchart TD
    StartQuest["Level 1 Spawn: The Cold Start"] --> Q1["Fix Thermostat deadband logic"]
    Q1 -- XP Reward --> Q2["Repair broken compressor relay"]
    Q2 -- XP Reward --> Q3["Unclog frosted evaporator fins"]
    Q3 -- Gold Reward --> EndQuest["Level 8: Master Controller certification"]
```
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

print("All blueprint documentation files created successfully!")
