# RPG System Blueprint: Electrical Grid & DDC Control Loops

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
$$U_t = K_p \cdot e(t) + K_i \cdot \int_0^t e(\tau) d\tau + K_d \cdot \frac{de(t)}{dt}$$
* **Error ($e(t)$):** Current Superheat $-$ Target Superheat ($10^\circ\text{F}$).

### 2. Auto-Restart Guard (Anti-Short-Cycle Timer)
To prevent compressor damage from rapid restarts, an anti-short-cycle timer asserts safety interlocks:
```python
if compressor_off_time < 300: # 5 minutes cooldown
    prevent_compressor_restart = True
```

---

## 🎨 Visual Component & Animation Specifications

### 1. Power Distribution Board (`rpg_power_board`)
* **Physical Render Frame size:** $96 \times 64$ pixels.
* **Bus Bar Render Specification:** Draws solid copper bus bars using `#D35400` with gold highlights (`#F1C40F`).
* **Active Arcing Particles:** During system overloads or short-circuits, electric spark particles ($1 \times 3$ pixels) are projected outward radially:
  $$x = x_{source} + \cos(\phi) \cdot r, \quad y = y_{source} + \sin(\phi) \cdot r$$
  Where $\phi$ is a random angle $[0, 2\pi]$ and $r$ expands exponentially per frame.

### 2. Magnetic Contactor Relay (`rpg_contactor`)
* **Physical Render Frame size:** $32 \times 32$ pixels.
* **Solenoid Actuation Animation:** The armature block moves vertically downward by $4$ pixels when energized (Y1 active), drawing contact links together.
* **Contact Arcing Arc Spark:** A bright yellow/white flash (`#FFFFFF` background, `#F1C40F` stroke) is drawn at the contact pads for $3$ frames upon engagement to simulate contact closure.
* **Corrosion Overlay:** An overlay of brown/green sulfur corrosion (`#58D68D`) displays over the contact points when contact resistance exceeds $1.5 \, \Omega$.

### 3. Step-down transformer (`rpg_transformer`)
* **Physical Render Frame size:** $48 \times 48$ pixels.
* **Coil Winding Pattern:** Renders copper primary and secondary coil winding wraps.
* **Overheating Thermal Glow:** Transformer housing glows red when primary current exceeds 120% of nominal.
