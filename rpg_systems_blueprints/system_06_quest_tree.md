# RPG System Blueprint: Quest Progression & Dialogue Engine

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

---

## 🎨 Visual Component & Animation Specifications

### 1. Quest Inventory grid (`rpg_inventory`)
* **Slot Layout:** A $4 \times 2$ grid containing items. Each slot is a $48 \times 48$ pixel container with `#2C3E50` borders.
* **Visual Components:**
  * Refriger Cylinder: Steel gray canister.
  * EEV Valve: Brass stepper body icon.
  * Digital Multimeter: Orange and black test tool.
* **Gold Shine Hover Effect:** Hovering over an item applies a golden shine animation (`#F1C40F`) reflecting light across the slot:
  ```css
  .inventory-slot:hover::after {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 50%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(241, 196, 15, 0.4), transparent);
    animation: goldShine 0.8s ease-in-out;
  }
  @keyframes goldShine {
    100% { left: 150%; }
  }
  ```

### 2. Dialogue Narrative Box (`rpg_dialogue_box`)
* **Visual Component:** Large glassmorphic container spanning the bottom of the canvas screen (`rgba(11, 19, 43, 0.85)`).
* **Typewriter Effect:** Text characters render sequentially. Letters are printed one-by-one every $30	ext{ms}$ using intervals to simulate real-time speech.
* **Choice Buttons:** Hovering over choice selections glows them bright cyan (`#00B4D8`) with smooth CSS scaling transitions.
