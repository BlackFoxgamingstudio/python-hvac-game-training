import os
import re

target_file = "/Users/russellpowers/Sovereign Biz Box/python-hvac-game-training/requirements.md"

requirements = [
    # Category 1: Python & HVAC Curriculum (Reqs 1-16)
    ("CURR-001", "Thermostat variables definition", "The system must verify float/int definitions for setpoint, deadband, and room temperature."),
    ("CURR-002", "F-strings formatting readouts", "Student code must format temperature and pressure variables inside printable sensor labels."),
    ("CURR-003", "Compressor stage conditionals", "Must run if/elif/else blocks to stage cooling cycles based on deadband deviations."),
    ("CURR-004", "Continuous cycle loops", "Must implement while/for loops to repeat the thermodynamic vapor compression steps."),
    ("CURR-005", "Modular component functions", "Isolated functions must calculate evaporator, compressor, condenser, and expansion mutations."),
    ("CURR-006", "Function parameters & returns", "Refrigerant dictionaries must pass through functions as parameters and return updated states."),
    ("CURR-007", "Stateful dictionary structures", "Refrigerant states must store temperature, pressure, enthalpy, and vapor-fraction variables."),
    ("CURR-008", "BAS telemetry CSV logger", "Must write sensor readings as row streams using Python's csv module formatting."),
    ("CURR-009", "VirtualFS mock open/close", "VFS must mimic file descriptors and persist buffers across close() closures."),
    ("CURR-010", "Equipment unit class syntax", "Must declare classes containing attributes and methods for RTU, AHU, and split systems."),
    ("CURR-011", "Self object identity tracker", "Must use self references in constructor initializers to isolate component properties."),
    ("CURR-012", "Composite system has-a mapping", "The parent unit (RTU) constructor must encapsulate child components (compressor, fan, EEV)."),
    ("CURR-013", "Gemini API gateway integration", "Must instantiate generative AI models and connect to local backend API routes."),
    ("CURR-014", "Troubleshooting system instructions", "Must prompt Gemini with system instruct roles acting as a certified controls technician."),
    ("CURR-015", "DDC threshold check alerts", "Must assert safety limits on pressures, coil temperatures, superheat, and subcooling."),
    ("CURR-016", "HUD Overlay hud console", "Renders text log grids, sweeping pointers, and fault alarms inside the game canvas HUD."),

    # Category 2: Simulation Engine & Canvas UI (Reqs 17-28)
    ("SIM-017", "60 FPS Ticker loop", "Main loop must run using window.requestAnimationFrame targeting 16.67ms ticks."),
    ("SIM-018", "Keyboard event capture registers", "Captures ArrowKeys/WASD movement inputs and Shift key speed multipliers."),
    ("SIM-019", "Tile map coordinate layout", "Maps a 20x15 grid (Tile size: 32x32px) for player navigation bounds."),
    ("SIM-020", "Wall boundary collision matcher", "Lookup indices check wall tiles and backtrack coordinates on overlaps."),
    ("SIM-021", "Off-screen double buffer", "Draws backgrounds, sprites, and HUD to an off-screen canvas context before flipping."),
    ("SIM-022", "Camera scrolling offset tracker", "Subtracts scroll camera positions from world bounds to compute view anchors."),
    ("SIM-023", "Piston rotation frame calculation", "Compressor pistons angle index increments based on motor active frequency."),
    ("SIM-024", "Rotational fan blur rendering", "Draws layered fan blade geometry with offset alphas to represent speed blur."),
    ("SIM-025", "Friction dust particle emitters", "Spawns particle arrays at player feet drifting away from movement vectors."),
    ("SIM-026", "Shadow drop polygon drawing", "Draws semi-transparent black polygons at wall base coordinates."),
    ("SIM-027", "Thermal warning icon overlay", "Flashing thermometer icon pulses above the robot under extreme zone temps."),
    ("SIM-028", "Sweeping gauge LERP interpolation", "HUD needles rotate smoothly using linear interpolations toward target angles."),

    # Category 3: Physical System Models (Reqs 29-40)
    ("PHYS-029", "Compression ratio calculation", "Maintains CR = P_discharge / P_suction equations dynamically."),
    ("PHYS-030", "Isentropic work enthalpy shifts", "Compressor motor work updates discharge gas enthalpy based on efficiency."),
    ("PHYS-031", "Electrical amperage load draw", "Amps scale as a function of the compression ratio and cylinder volume."),
    ("PHYS-032", "EEV flow coefficient throttle", "Stepper steps open map the needle orifice coefficient Cv (0 to 1.0)."),
    ("PHYS-033", "Orifice flow mass equation", "Liquid flow rate scales as Cv * sqrt(density * pressure_drop)."),
    ("PHYS-034", "PID feedback superheat tune", "Valve steps update based on proportional, integral, and derivative errors."),
    ("PHYS-035", "Frost thickness scaling", "Fins moisture freezes when suction pressure drops below 50 PSI ($32^\\circ\\text{F}$)."),
    ("PHYS-036", "Heat transfer decay coefficient", "UA coefficient decays exponentially based on frost depth in mm."),
    ("PHYS-037", "Airflow restriction CFM drop", "Clog ratio limits CFM flow rate toward total coil blockage at 5.0mm."),
    ("PHYS-038", "Liquid slugback hazard triggers", "Asserts warnings when evaporator airflow drops below 400 CFM."),
    ("PHYS-039", "Voltage drop calculations", "Winding electrical drops scale as current load exceeds wire thresholds."),
    ("PHYS-040", "Magnetic contactor pull-down", "Armature moves down by 4px and flashes contact sparks upon coil energization."),

    # Category 4: Data Logging & VFS (Reqs 41-52)
    ("LOG-041", "CSV record layout column mapping", "Saves time, cycle, temps, pressures, superheat, subcooling, and status."),
    ("LOG-042", "Time-series logging interval", "Appends a new CSV row when temperature changes by >= 0.3°F or cycle increments."),
    ("LOG-043", "Persistent VirtualFS files cache", "Maintains path-content dictionaries across Pyodide open/close cycles."),
    ("LOG-044", "BAS table alternating rows styling", "Renders grid borders with dark theme slate colors."),
    ("LOG-045", "Row insert green flash animation", "Appends animate rows glowing green and fading to transparent over 2s."),
    ("LOG-046", "Pulsing red alarm row outline", "Pulsing outline surrounds table rows flagged with FAULT status."),
    ("LOG-047", "VirtualFS read/write indicators", "LEDs flash green on file writes and blue on file reads."),
    ("LOG-048", "Local sync array buffer limit", "Floating log history cache limits database synchronization arrays to 5 rows."),
    ("LOG-049", "JSON sync payload construction", "Compiles live telemetry variables and CSV rows into JSON documents."),
    ("LOG-050", "Firestore collection write queues", "Post payloads securely to user and log collections in Firestore."),
    ("LOG-051", "Firestore security authentication checks", "Restricts read/write commands to matching user uids."),
    ("LOG-052", "Append-only database sync rules", "Locks telemetry log edits as write-only/append-only to preserve history."),

    # Category 5: Conversational AI Engine (Reqs 53-64)
    ("AI-053", "HTTP POST /api/chat gateway", "Exposes API gateway route for chat queries and diagnoses."),
    ("AI-054", "User token verification interlock", "Validates client session Auth tokens before forwarding requests to Gemini."),
    ("AI-055", "Context prompt aggregator compiler", "Combines current telemetry variables, CSV rows, and user query strings."),
    ("AI-056", "HVAC diagnostics system instructions", "Configures Gemini system prompt acting as a certified controls technician."),
    ("AI-057", "Inference model configurations", "Sets target parameters: gemini-2.5-flash model, temperature 0.2, max 1000 tokens."),
    ("AI-058", "Markdown regex parser wrapper", "Formats response strings containing code blocks, tables, and headers on-screen."),
    ("AI-059", "AI chat console overlay panels", "Glassmorphic window layout with dark overlays and custom scrollbars."),
    ("AI-060", "Typing dots bounce CSS animation", "Bounces three dots sequentially while processing queries."),
    ("AI-061", "Command caret blinking caret", "Draws flashing cursor caret at user input box terminal prompt."),
    ("AI-062", "Diagnostic heatmap canvas overlay", "Renders temperature zone gradients (red-blue) on-canvas based on data."),
    ("AI-063", "Few-shot prompt templates", "Aggregates few-shot diagnostics examples for charge, condenser, and valve faults."),
    ("AI-064", "Token budget tracking log", "Monitors API token counts to prevent billing and thinking limit overruns."),

    # Category 6: RPG Story & Quests (Reqs 65-76)
    ("RPG-065", "Quest progression sequence", "Chain-gates levels 1-8 challenges matching Python/HVAC modules."),
    ("RPG-066", "NPC dialogue typewriter printing", "Sequential letters print one-by-one with 30ms timers."),
    ("RPG-067", "Interactive selection choices outlines", "Option buttons glow cyan and scale up smoothly on hover."),
    ("RPG-068", "Behemoth frozen coil boss math", "Level 3 boss HP decays as evaporator temperature increases above 32°F."),
    ("RPG-069", "Surge Daemon voltage drop boss math", "Level 6 boss HP decays when student code asserts safety limits."),
    ("RPG-070", "Golem stuck EEV steps boss math", "Level 10 boss HP decays when EEV steps open towards nominal ranges."),
    ("RPG-071", "Active NPC dialogue highlight glow", "Displays active speaker portrait with glowing cyan border filters."),
    ("RPG-072", "100 NPC directory directory lookup", "Spawns 100 structured NPCs across BAS, Scholars, and Union factions."),
    ("RPG-073", "NPC dialogue JSON branches", "Dialogue structures parse node IDs, NPC names, and level conditions."),
    ("RPG-074", "User progress state document sync", "Writes current level, gold, and completed modules to Firestore doc."),
    ("RPG-075", "Inventory slot layout boundaries", "A 4x2 grid containing item slots sized at 48x48px with slate borders."),
    ("RPG-076", "Golden item shine hover keyframes", "Hovering items reflects light across the slot using linear gradients."),

    # Category 7: Apple Glass AR HUD (Reqs 77-88)
    ("AR-077", "Spatial coordinate projection matrix", "Maps equipment coordinates on-canvas offset by camera scroll positions."),
    ("AR-078", "Translucent visor frame border", "Renders border overlay using rgba(0, 180, 216, 0.4) borders."),
    ("AR-079", "Vertical scanline visual shader", "A cyan line sweeps vertically across the viewport using CSS keyframes."),
    ("AR-080", "Hot vapor pipe glowing trace", "Pipes flow translucent red dots (`rgba(231, 76, 60, 0.4)`) towards condenser."),
    ("AR-081", "Liquid line cooling flow trace", "Pipes flow blue dots (`rgba(52, 152, 219, 0.5)`) towards expansion valve."),
    ("AR-082", "Superheat bounding box outline", "Evaporator outline glows green under nominal and pulses red under faults."),
    ("AR-083", "Scanning radar indicator overlay", "Renders radar sweep arcs at visual anchor centers."),
    ("AR-084", "Equipment health index visual", "Draws vertical bar gauges representing structural integrity of parts."),
    ("AR-085", "VisorHUDParser string formatting challenge", "Level 10-20 check requires formatting floating variables inside string readouts."),
    ("AR-086", "FrostMapGenerator visual density check", "Level 20-30 check requires mapping opacity ranges based on frost depth."),
    ("AR-087", "PID regulator step modulator check", "Level 30-40 check requires tuning steps to balance superheat variables."),
    ("AR-088", "RUL predictive failure decay checks", "Level 50-60 check requires estimating remaining life using exponential wear."),

    # Category 8: Hotel Starship Decks (Reqs 89-100)
    ("HOTEL-089", "Floor 1 Atrium sensible heat model", "Lobby space balances window wall transmission gains and occupant loads."),
    ("HOTEL-090", "Floor 2 Guest Suites VAV balancing", "Life support deck balances damper position air volumes across suites."),
    ("HOTEL-091", "Floor 3 Warp Core Kitchen load model", "High thermal kitchen hood exhaust fans stabilize zone static pressures."),
    ("HOTEL-092", "Floor 4 Deflector Laundry moisture math", "Laundry loops calculate moisture removal rates using CFM and grains."),
    ("HOTEL-093", "Floor 5 Bridge Rooftop chiller sequencing", "RTUs sequence lead/lag staging based on total cooling tons demand."),
    ("HOTEL-094", "Engineering crew ranking structure", "Progresses titles from Apprentice through Specialist, Officer, and Chief."),
    ("HOTEL-095", "Holo-deck Freon leak hazard gas visuals", "Translucent green gas clouds drift across lobby projection nodes."),
    ("HOTEL-096", "Warp core kitchen thermal cascade visuals", "Cooking columns glow red with yellow sparks floating upward."),
    ("HOTEL-097", "Life support CO2 visor alarm warning", "VIP Suite HUD gauges tick red as CO2 rises during damper failures."),
    ("HOTEL-098", "Lag chiller start relay logic", "Bridge sequencer starts secondary compressor as load exceeds 120 tons."),
    ("HOTEL-099", "Crew bridge coordination console", "Syncs status panels across 100 crew NPCs on the main bridge HUD."),
    ("HOTEL-100", "Digital twin prognostics warning check", "Main controller triggers alarms when parts remaining life falls below 60%."),

    # Category 9: LMS Sandbox & AST Parser (Reqs 101-110)
    ("LMS-101", "Pyodide WASM runtime sandboxing", "Student code executes in isolated global dictionaries scope namespaces."),
    ("LMS-102", "AST tree generation validation", "Compiles code string to AST structure to check syntactical patterns."),
    ("LMS-103", "NodeVisitor constructor checks", "Inspects functions to ensure initialization constructors exist in classes."),
    ("LMS-104", "Security disallowed imports blockers", "Blocks code containing imports for os, sys, subprocess, or request."),
    ("LMS-105", "Dynamic unit tests assertions engine", "Executes unit test validation cases against student namespaces."),
    ("LMS-106", "VFS mock file persisting cache", "Saves VirtualFile writes globally, surviving open/close cycles."),
    ("LMS-107", "Grade scoring and rewards incrementer", "Calculates XP and gold gains on passing all unit test checks."),
    ("LMS-108", "Error console formatting and trace", "Captures stdout/stderr streams to format error trace layouts."),
    ("LMS-109", "Success glow console keyframes", "Editor container border glows green and shadows pulse on pass."),
    ("LMS-110", "Level up HUD shield and confetti", "Animates gold shield and confettis when user progress level increments.")
]

# Write out requirements.md
with open(target_file, "w") as f:
    f.write("# Sovereign HVAC RPG: Comprehensive System Requirements Directory\n\n")
    f.write("This document compiles every single unique requirement established across the 10 System Blueprints, Visual Frame specifications, and core HTML5 Canvas models.\n\n")
    f.write(f"## 📊 Total Unique Requirements: **{len(requirements)}**\n\n")
    
    f.write("## 📋 Requirements Directory Table\n\n")
    f.write("| Req ID | Title | Description | Category |\n")
    f.write("| :--- | :--- | :--- | :--- |\n")
    for req in requirements:
        cat = "Curriculum"
        if req[0].startswith("SIM"): cat = "Simulation"
        elif req[0].startswith("PHYS"): cat = "Physics Model"
        elif req[0].startswith("LOG"): cat = "Data Logging"
        elif req[0].startswith("AI"): cat = "AI Engine"
        elif req[0].startswith("RPG"): cat = "RPG Systems"
        elif req[0].startswith("AR"): cat = "Apple Glass AR"
        elif req[0].startswith("HOTEL"): cat = "Hotel Starship"
        elif req[0].startswith("LMS"): cat = "LMS & AST Sandbox"
        f.write(f"| `{req[0]}` | **{req[1]}** | {req[2]} | {cat} |\n")
        
    f.write("\n\n")
    f.write("## 🔍 Category Summaries\n\n")
    f.write("### 1. Python & HVAC Curriculum (1-16)\n")
    f.write("Covers variables, f-strings, conditional staging loops, parameter mapping, composition classes, and AI system instructions.\n\n")
    f.write("### 2. Simulation Engine & Canvas UI (17-28)\n")
    f.write("Covers 60fps game ticker, key listener arrays, tile mapping coordinates, wall collision looks, and LERP dial gauges.\n\n")
    f.write("### 3. Physical System Models (29-40)\n")
    f.write("Covers scroll compressor current work calculations, EEV stepper PID feedback loops, evaporator frost decay curves, and contactor solenoid pull-downs.\n\n")
    f.write("### 4. Data Logging & VFS (41-52)\n")
    f.write("Covers CSV formatting, float log parameters, memory VFS cache, spreadsheet highlight flashes, and Firestore writes.\n\n")
    f.write("### 5. Conversational AI Engine (53-64)\n")
    f.write("Covers Flask api gate endpoints, context compilers, system instructions, Markdown response maps, typing dot bounces, and heatmap overlays.\n\n")
    f.write("### 6. RPG Story & Quests (65-76)\n")
    f.write("Covers level quest lists, dialogue typewriters, option selection sweeps, boss health points decay equations, and inventory grids.\n\n")
    f.write("### 7. Apple Glass AR HUD (77-88)\n")
    f.write("Covers camera offset viewport projections, scanline filters, pipe vapor flow trails, superheat outlines, and prognostic checks.\n\n")
    f.write("### 8. Hotel Starship Decks (89-100)\n")
    f.write("Covers sensible lobby loads, VAV dampering loops, warp kitchens static pressure exhaust, laundry grains, RTU chillers sequencing, and crew ranks.\n\n")
    f.write("### 9. LMS Sandbox & AST Parser (101-110)\n")
    f.write("Covers Pyodide globals namespaces, AST compilations, constructors validation, disallowed import blocks, unit tests asserts, success editor animations, and level-up indicators.\n")

print("requirements.md file created successfully!")
print(f"Total requirements logged: {len(requirements)}")
