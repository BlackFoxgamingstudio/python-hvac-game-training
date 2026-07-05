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
