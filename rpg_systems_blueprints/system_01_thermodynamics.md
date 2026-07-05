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

## 🎮 Game Objects and Specifications

### 1. Scroll Compressor Core (`rpg_comp_core`)
* **Amperage Draw Formula:** $I = (CR \cdot 1.8) + (displacement \cdot 0.15)$.
* **Visual Quality:** 16-frame rotative animation displaying crankshaft motion and dynamic heat glows.

### 2. Electronic Expansion Valve (`rpg_eev_actuator`)
* **Throttling Range:** 0 to 500 step increments.
* **Control Output:** Decoupled flow coefficient output variable updated at 1.0 Hz by the PID control loop.
