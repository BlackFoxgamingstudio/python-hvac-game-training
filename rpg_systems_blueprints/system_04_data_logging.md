# RPG System Blueprint: Data Logging & Persistent VirtualFS

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

---

## 🎨 Visual Component & Animation Specifications

### 1. BAS Log Spreadsheet Table (`rpg_bas_table`)
* **Styling Theme:** Sleek dark slate grid layout with `#1C2541` borders and `#0B132B` alternating row backgrounds.
* **Alarm Flash Effect:** If any telemetry log contains a `status` of `FAULT` (e.g. frozen coil), the table row displays a pulsing red outline (`rgba(231, 76, 60, 0.4)`) using keyframe transitions.
* **Row Append Highlight:** When a new row is appended, the row background glows green (`#27AE60`) and slowly fades to the default background color over $2.0$ seconds:
  ```css
  @keyframes rowInsertFlash {
    from { background-color: rgba(39, 174, 96, 0.5); }
    to { background-color: transparent; }
  }
  ```

### 2. VirtualFS Storage Space Monitor Gauge
* **Visual Component:** A progress bar showing virtual space usage.
* **Activity Indicator LEDs:** Two round status indicator circles:
  * **Read Indicator (Blue):** Blinks green-blue (`#3498DB`) when a script calls `read()` or `readlines()`.
  * **Write Indicator (Green):** Blinks neon-green (`#2ECC71`) when a script calls `write()` or `writelines()`.
