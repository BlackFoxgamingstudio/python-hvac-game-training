# RPG System Blueprint: Conversational AI Diagnostic Engine

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
  "log_history_csv": "timestamp,cycle,room_temp,evap_temp,suction_psi
12:59:10,3,82.7,29.1,43"
}
```
