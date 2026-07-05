# RPG System Blueprint: Thermodynamics & Phase Fluid Simulation

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
$$W_{comp} = \dot{m} \cdot (h_{discharge} - h_{suction})$$

### 2. Evaporator Heat Absorption
The cooling load ($Q_{evap}$) absorbed by the coil is calculated using:
$$Q_{evap} = \dot{m} \cdot (h_{suction} - h_{evap\_in})$$

---

## 🎮 Game Objects and Specifications

### 1. Scroll Compressor Core (`rpg_comp_core`)
* **Features:** Variable frequency motor simulation, dynamic noise vibration, thermal decay thresholds.
* **Sprite Sheets:** 16 frames of animation mapping current voltage loops.

### 2. Condenser Coil Assembly (`rpg_cond_coil`)
* **Features:** Subcooling state variables, ambient fan efficiency offsets.
* **Sprite Sheets:** 8 frames representing condensation air particle vectors.
