# RPG System Blueprint: Thermodynamics & Phase Fluid Simulation

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
$$h_{evap\_in} = h_{liquid}$$
The flow coefficient ($C_v$) regulates the refrigerant flow:
$$\dot{m} = C_v \cdot \sqrt{\rho \cdot (P_{discharge} - P_{suction})}$$

### 2. Evaporator Air Heat Balance
The heat energy extracted from the air stream ($Q_{sensible}$) must equal the heat energy absorbed by the refrigerant:
$$Q_{sensible} = 1.08 \cdot CFM \cdot (RAT - SAT)$$
$$Q_{refrigerant} = \dot{m} \cdot (h_{suction\_gas} - h_{evap\_in})$$

---

## 🎨 Visual Component & Animation Specifications

### 1. Scroll Compressor Core Sprite (`rpg_comp_core`)
* **Physical Render Frame size:** $64 \times 64$ pixels.
* **Rotational Rendering Calculations:** The crankshaft rendering angle ($\theta$) increments in the draw loop based on the frequency ($f$ in Hz):
  $$\theta_{next} = (\theta_{current} + f \cdot 0.10) \pmod{2\pi}$$
* **Heat-Haze Shader Effect:** When the compressor's thermal state exceeds $140^\circ\text{F}$, a heat-haze canvas filter applies a sine-wave displacement to the rendering rows:
  $$x_{offset} = \sin(y \cdot 0.25 + frameCount \cdot 0.15) \cdot 2.5$$
* **Sprite Sheets Configuration:**
  * Frames 0–3: Low-contrast blue glow, static pistons.
  * Frames 4–11: Shaft rotating, yellow copper coil windings pulse intensity.
  * Frames 12–15: Vibrational offset shuddering, sparks ejecting from terminals.

### 2. Condenser Fan assembly (`rpg_cond_fan`)
* **Physical Render Frame size:** $48 \times 48$ pixels.
* **Rotational Motion Blur:** Drawn using three layered semi-transparent fan blade polygons at offset alphas (0.2, 0.4, 0.7) to represent blade speed.
* **Airflow Indicator Particles:** Warm exhaust air is drawn as red translucent smoke squares ($4 \times 4$ pixels) spawning at the outlet and drifting vertically with an upward velocity ($v_y = -3 \text{ pixels/frame}$).

### 3. Electronic Expansion Valve (EEV) Stepper Actuator (`rpg_eev_actuator`)
* **Physical Render Frame size:** $48 \times 48$ pixels.
* **Needle Throttle Vector:** The needle coordinates ($y_{needle}$) move dynamically between the closed position ($y = 12$) and open position ($y = 28$):
  $$y_{needle} = 12 + \left(\frac{N_{steps}}{500}\right) \cdot 16$$
* **Flash Gas Vaporization Particles:** Sprays ice-blue particles (`#EBF5FB`) into the evaporator inlet. The particle density matches the EEV steps.

### 4. Evaporator Coil Assembly (`rpg_evap_coil`)
* **Physical Render Frame size:** $64 \times 48$ pixels.
* **Frost Overlay Shader:** Ice opacity ($\alpha_{frost}$) increases as frost depth ($t_{frost}$) builds:
  $$\alpha_{frost} = \min\left(1.0, \frac{t_{frost}}{5.0}\right)$$
  Drawn as a white textured mask over the copper tubes.
* **Ice Crystal Generation:** When $\alpha_{frost} > 0.6$, the engine renders small white triangles ($3 \times 3$ pixels) on the boundaries of the aluminum fins.
