# 🤖 Python Systems Thinking: From HVAC to Game Engine

A complete, self-contained educational curriculum and interactive simulation ecosystem designed to teach professional software engineering, systems thinking, and artificial intelligence integration through the physical principles of heating, ventilation, and air conditioning (HVAC) engineering.

---

## 📖 Introduction & Pedagogical Philosophy

Software is not written in a vacuum. The greatest challenge for novice programmers is not learning syntax—it is learning **how to reason about complex, stateful, and dynamic systems**. Modern web development often abstracts away the core loops and state machines that govern software. To teach systems thinking, we must anchor programming concepts in tangible, physical systems.

This course bridges the gap between hardware engineering and software engineering. We use the **Vapor Compression Refrigeration Cycle** as our central metaphor. An air conditioning system is a perfect physical analogue to a software system:
* **Sensors** maps directly to **Variables**.
* **Thermostat thresholding** maps directly to **Conditionals (if/else)**.
* **Continuous cycles** map directly to **Loops**.
* **Individual mechanical components** map to **Functions**.
* **Complete physical units** map to **Objects (OOP)**.
* **Building Management Systems (BMS)** map to **Software Architectures**.

By mapping dynamic, physical systems to software constructs, students build an intuitive mental model for concepts like state, inputs, outputs, and encapsulation. By the end of this curriculum, the student will transition from basic variable assignments to building a playable, real-time game engine in HTML5 Canvas and Pygame that simulates a physical robot regulating its internal temperature using a simulated refrigeration cycle while interacting with a Gemini AI brain.

---

## 🎯 Target Audience

This course is designed for:
1. **HVAC Technicians & Facilities Managers:** Professionals with rich domain knowledge in physical systems who want to acquire coding skills to automate their workflows or transition into smart-building software development.
2. **Beginner Programmers:** Students who struggle with dry, abstract programming exercises and learn best when code directly controls a physical or visual system.
3. **Game Developers & Simulators:** Individuals interested in building robust, modular simulation engines and learning how to structure complex game loop architectures with external API dependencies.

---

## 📋 Course Prerequisites

Before starting, ensure your local workspace has the following:
* **Python 3.10 or higher** (compiled with standard development libraries).
* **Terminal Access** (bash, zsh, or command prompt).
* **A Text Editor** (Visual Studio Code, PyCharm, or Vim).
* **A Web Browser** (Chrome, Firefox, or Safari with WebAssembly enabled for the in-browser interactive runner).
* **(Optional) A Gemini API Key:** Required for Module 5 and the AI features of the Pygame simulator. Get a key at [Google AI Studio](https://aistudio.google.com/apikey).

---

## 🚀 Quick Start (Local Setup)

Clone this repository and run the local development server:

```bash
# 1. Navigate to the project directory
cd python-hvac-game-training

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install core dependencies
pip install -r requirements.txt

# 4. Start the interactive training web server
python3 server.py
```

Open your browser and navigate to **`http://localhost:8080`** to access the glassmorphic training site, where you can read the theory, run exercises in-browser via Pyodide, and track your progress.

To start the graphical simulator directly:
```bash
python3 -m game.main
```

---

## 📚 Curriculum Blueprint & Module Breakdown

```
 ┌─────────────────────────────────────────────────────────────┐
 │                     MODULE ROADMAP                          │
 ├──────────┬──────────────────────────────┬───────────────────┤
 │ Module 1 │ Python Fundamentals          │ Variables & Loops │
 ├──────────┼──────────────────────────────┼───────────────────┤
 │ Module 2 │ HVAC as Functions            │ State & Functions │
 ├──────────┼──────────────────────────────┼───────────────────┤
 │ Module 3 │ Data Flow & Logging          │ CSV Log Writing   │
 ├──────────┼──────────────────────────────┼───────────────────┤
 │ Module 4 │ OOP Refactor                 │ composition (HAS) │
 ├──────────┼──────────────────────────────┼───────────────────┤
 │ Module 5 │ AI Integration               │ Gemini SDK        │
 ├──────────┼──────────────────────────────┼───────────────────┤
 │ Module 6 │ Diagnostic Troubleshooting   │ FDD Classifier    │
 ├──────────┼──────────────────────────────┼───────────────────┤
 │ Module 7 │ Game Programming             │ Pygame Loop       │
 ├──────────┼──────────────────────────────┼───────────────────┤
 │ Module 8 │ Final Integrated Project     │ Robot Simulation  │
 └──────────┴──────────────────────────────┴───────────────────┘
```

### Module 1: Python Fundamentals — The Language of Systems
* **Pedagogical Goal:** Introduce the building blocks of Python using temperature, pressure, and flow rates as the data.
* **Programming Concepts:** Variable assignment, data types (float, integer, string, boolean), f-strings, arithmetic operators, conditionals (`if`/`elif`/`else`), and loops.
* **HVAC Concepts:** Delta-T calculations, BTU estimation, suction/discharge pressures, basic deadband thermostat logic.
* **Core Exercises:** Inside `exercises/ex01_variables_and_types.py`, students implement a script that simulates a cooling countdown, dropping target temperatures by calculating the sensible heat transfer equation:
  $$\text{Sensible Load (BTU/hr)} = 1.08 \times \text{CFM} \times \Delta T$$

### Module 2: HVAC as Functions — Mapping Hardware to Software
* **Pedagogical Goal:** Learn code reuse and input/output mapping by modeling the four key components of a refrigeration cycle.
* **Programming Concepts:** Function definitions, parameter passing, return statements, dictionaries as state representations, docstrings.
* **HVAC Concepts:** Vapor compression cycle thermodynamics.
  * **Evaporator:** Low-pressure liquid refrigerant absorbs heat from indoor air, boiling into low-pressure gas.
  * **Compressor:** Squeezes low-pressure gas to high-pressure gas, raising temperature.
  * **Condenser:** Rejects heat to outdoor air, condensing hot gas back to liquid.
  * **Expansion Valve:** Throttles high-pressure liquid to low-pressure mixture.
* **Core Exercises:** Found in `exercises/ex02_hvac_functions.py`, students pipeline state dictionaries sequentially through each function, feeding the output of one component as the input to the next.

### Module 3: Data Flow & Diagnostic Logging — CSV Telemetry
* **Pedagogical Goal:** Understand data persistence, file storage, and structural trend logging.
* **Programming Concepts:** `csv` module, file I/O operations (`open()`), context managers (`with` statement), list comprehensions.
* **HVAC Concepts:** BAS (Building Automation System) trend logs, sensor calibration logs, diagnostic data acquisition.
* **Core Exercises:** In `exercises/ex03_csv_logging.py`, students automate logging of a 24-cycle refrigeration simulation to a CSV file and read it back to analyze mean efficiency ratings using list comprehensions.

### Module 4: OOP Refactor — Robot + AC Composition
* **Pedagogical Goal:** Master Object-Oriented Programming (OOP), encapsulation, and composition over inheritance.
* **Programming Concepts:** Class declarations, constructors (`__init__`), instance variables, class methods, encapsulation, composition (the HAS-A relationship).
* **HVAC Concepts:** Modular equipment design. A robot has an internal air conditioning unit.
* **Core Exercises:** In `exercises/ex04_oop_robot_ac.py`, students refactor the procedural refrigeration cycle into an `AirConditioner` object that acts as a child component inside a `Robot` object.

### Module 5: AI Integration — Gemini API & Robot Brain
* **Pedagogical Goal:** Teach modern API integration, environment variables, and asynchronous communication design patterns.
* **Programming Concepts:** Environment variables, external packages (`google-genai` SDK), error handling, prompt engineering, system instructions.
* **HVAC Concepts:** AI-enabled building management, smart thermostats, natural language interfaces for machinery.
* **Core Exercises:** In `exercises/ex05_gemini_robot_brain.py`, students connect the robot to the Google Gemini API, passing live thermodynamic telemetry inside the system prompt to receive natural language operational status reviews.

### Module 6: Diagnostic Troubleshooting — AI-Powered Analysis
* **Pedagogical Goal:** Implement rule-based anomaly detection alongside generative AI analysis for complex troubleshooting.
* **Programming Concepts:** Exception handling, data classification, structured prompting.
* **HVAC Concepts:** Fault Detection and Diagnostics (FDD), low charge detection, compressor failure signatures, blocked condenser airflow.
* **Core Exercises:** In `exercises/ex06_diagnostic_dashboard.py`, the code simulates sensor faults (e.g. low refrigerant pressure, stuck valves) and calls the AI to diagnose the physical root cause from CSV telemetry logs.

### Module 7: Game Programming — Pygame & Game Objects
* **Pedagogical Goal:** Transition from sequential CLI scripts to event-driven real-time execution.
* **Programming Concepts:** Game loops, event queues, frame rate control, coordinate systems, keyboard state polling.
* **HVAC Concepts:** Real-time heat dissipation, transient thermal loads.
* **Core Exercises:** In `exercises/ex07_pygame_robot.py`, students render an interactive robot using Pygame. The robot's movement generates motor heat, causing it to glow red until the automated HVAC system kicks in.

### Module 8: Final Project — Complete Robot Simulation
* **Pedagogical Goal:** Synthesize all previous lessons into a single large-scale software project.
* **Programming Concepts:** Modular code integration, package management, state machines.
* **HVAC Concepts:** Multi-zone air distribution, variable air volume (VAV) systems, zone heat loads.
* **Core Exercises:** In `exercises/ex08_complete_game.py`, students build a full simulation featuring multiple temperature zones, heat sources, visual diagnostic logs, and an in-game AI overlay.

---

## 🎮 Game Engine Architecture

The game simulation (both the Python Pygame app and the in-browser HTML5 Canvas widget) represents a production-style game engine. Here is how the individual subsystems communicate:

```
                  ┌───────────────────────┐
                  │       Game Loop       │
                  │       (main.py)       │
                  └───────────┬───────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
     ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
     │ Handle Keys │   │ Physics/AC  │   │   Render    │
     │  (main.py)  │   │ (robot.py)  │   │  (hud.py)   │
     └─────────────┘   └──────┬──────┘   └─────────────┘
                              │
                    ┌──────────┴──────────┐
                    ▼                     ▼
           ┌────────────────┐    ┌────────────────┐
           │  HVAC System   │    │  Gemini Brain  │
           │ (hvac_system.py)│   │  (ai_brain.py) │
           └────────────────┘    └────────────────┘
```

### 1. Main Loop & Delta-Time
In standard programming, execution is sequential. In games, execution is circular. The game loop runs 60 times per second. To ensure physics run at the same speed regardless of computer performance, the engine calculates **Delta-Time (dt)**—the fraction of a second since the last frame.
```python
# Cap physics delta to prevent collisions breaking during lag spikes
dt = min(self.clock.tick(self.FPS) / 1000.0, 0.05)
self.update(dt)
self.draw()
```

### 2. Thermodynamic Simulation (`game/hvac_system.py`)
The HVAC system models real thermodynamic properties:
* **Evaporator:** 
  $$\Delta T_{core} = (T_{core} - T_{ref}) \times \text{Heat Transfer Coeff} \times dt$$
* **Compressor:** Increases refrigerant temperature by $50^\circ\text{F}$ and changes the state indicator to `High` pressure.
* **Condenser:** Rejects heat based on the outdoor ambient temperature. If the zone is $110^\circ\text{F}$, heat transfer is less efficient, modeled by dropping the `efficiency_rating` factor.
* **Expansion Valve:** Decreases refrigerant temperature by $65^\circ\text{F}$ via pressure drop.

### 3. Threaded Non-Blocking AI Brain (`game/ai_brain.py`)
API requests are network-bound and take $1$ to $3$ seconds. In a single-threaded game, calling an API synchronously will freeze the screen. To prevent this, the `RobotBrain` uses Python's `threading` library to call Gemini asynchronously:
```python
def ask(self, user_prompt: str, telemetry: dict):
    if self.is_thinking:
        return
    self.is_thinking = True
    thread = threading.Thread(
        target=self._query_gemini,
        args=(user_prompt, telemetry),
        daemon=True
    )
    thread.start()
```

---

## ⚡ In-Browser Execution via Pyodide

To allow users to test and run the code directly inside the training website, the platform integrates **Pyodide**—a port of CPython to WebAssembly (WASM).

### How it Works
1. When a user clicks the **"▶ Run"** button on any code block, the frontend lazily downloads the Pyodide runtime from a secure CDN.
2. The browser creates an isolated WebAssembly sandbox.
3. Standard Python input/output (`sys.stdout` and `sys.stderr`) is captured and redirected to a custom output terminal rendered below the code card.
4. Because the browser cannot run graphic loops or access the local filesystem directly, we inject a mock module suite for `pygame` and `google.genai` to prevent import errors and mock their operations.

### The Virtual File System (VirtualFS)
Since Pyodide runs in a WebAssembly sandbox inside the browser, it has no direct access to your computer's hard drive. To allow code blocks in Module 3 and Module 6 to read and write CSV files, we built a **Virtual File System** in JavaScript that intercepts Python's built-in `open()` function.

```javascript
class _VirtualFS {
  static _files = {};
  
  static open(path, mode='r') {
    path = String(path);
    if (mode.includes('w')) {
      // Create a writable virtual file buffer
      let file = new _VirtualFile(path, _VirtualFS);
      _VirtualFS._files[path] = "";
      return file;
    } else if (mode.includes('a')) {
      // Append to an existing virtual file buffer
      let file = new _VirtualFile(path, _VirtualFS);
      file._buffer = _VirtualFS._files[path] || "";
      return file;
    } else if (mode.includes('r')) {
      // Read from virtual file buffer
      let content = _VirtualFS._files[path] || "timestamp,sensor,value\n2024-01-01,temp,72.0\n";
      return new io.StringIO(content);
    }
  }
}
```

This ensures that files written in one part of a code block can be seamlessly opened, appended to, and read back in another part of the block without causing an `I/O Error`.

---

## 🎨 Interactive HTML5 Canvas Game Engine

To provide the absolute best visual implementation of the training program directly in the browser, we built a native **HTML5 Canvas game engine** inside [game.js](file:///Users/russellpowers/Sovereign%20Biz%20Box/python-hvac-game-training/static/js/game.js). This engine recreates the exact Python OOP systems model using high-performance vanilla JavaScript.

### Key Architecture Components
1. **Core Loop & Tick Rate:** Runs via `requestAnimationFrame` for buttery-smooth 60fps rendering, matching monitor refresh rates.
2. **State Syncing:** Every frame, the javascript engine updates the robot coordinates, calculates thermodynamic heat accumulation, checks if the AC should cycle, and spawns corresponding particles.
3. **Bobbing Phase & Physics:** The robot includes a sinus-based bobbing animation:
   $$\text{Bobbing Offset} = \sin(\text{phase}) \times 2$$
   This makes the robot feel alive and floating. A smooth trail system follows behind the robot coordinates using linear interpolation (lerp).
4. **Visual States & Color Accents:**
   * **Nominal:** The robot glows with a soft cyan/green light when operating under 80°F.
   * **Warning:** The robot turns orange if internal temperature reaches 80°F.
   * **Alarm:** The robot turns red and shoots off orange heat particles if internal temperature exceeds 92°F.
   * **AC Cooling:** Activating the AC displays a glowing blue indicator and spawns cool blue breeze particles.

### Particle System Mechanics
The particle system handles three particle types:
* `heat` (orange, rises upward, decays quickly)
* `cool` (blue, falls downward, slows down over time)
* `exhaust` (gray, floats away, fades)

Each particle maintains individual velocity vectors, alpha decay rates, and size scales to create rich, dynamic feedback for thermodynamic processes.

---

## ☁️ Cloud Deployment Guide (GCP Cloud Run)

This project is fully prepared for serverless deployment on Google Cloud Platform using **Cloud Run**.

### 1. Docker Containerization
The project includes a multi-stage-ready `Dockerfile` based on `python:3.11-slim` to minimize image size and decrease cold-start latency. The container is configured to bind to `0.0.0.0` and read the `PORT` environment variable injected by Cloud Run.

### 2. Manual Deploy Commands
To deploy the application to GCP manually:

```bash
# 1. Authenticate with Google Cloud
gcloud auth login

# 2. Set your active project
gcloud config set project vibeup-platform

# 3. Enable required services
gcloud services enable run.googleapis.com \
                       containerregistry.googleapis.com \
                       cloudbuild.googleapis.com

# 4. Deploy using Cloud Build (builds image remotely and deploys)
gcloud run deploy python-hvac-game-training \
    --source . \
    --region us-central1 \
    --allow-unauthenticated
```

### 3. CI/CD Architecture
For production setups, you can configure GitHub Actions to deploy automatically on push:
1. Create a service account with `Cloud Run Developer` and `Storage Admin` permissions.
2. Export the service account key and add it to your GitHub Repository Secrets as `GCP_SA_KEY`.
3. Create a workflow at `.github/workflows/deploy.yml` to trigger `gcloud run deploy`.

---

## 📂 Git & Repository Management

This directory is structured as a clean, stand-alone Git repository. Follow these steps to commit and push changes:

```bash
# Initialize git if not already initialized
git init

# Add all files (respecting the rules in .dockerignore and .gitignore)
git add .

# Create the initial commit
git commit -m "feat: complete interactive systems thinking training platform with Pyodide runner and Canvas sandbox"

# Push to your remote repository
git branch -M main
git remote add origin https://github.com/BlackFoxgamingstudio/python-hvac-game-training.git
git push -u origin main --force
```

---

## 📂 Repository File Structure & Exercise Breakdown

To facilitate ease of development and structured learning, the repository is organized into distinct directories and modular components. Below is a detailed map of the codebase and the educational exercise templates provided to the students.

### 1. Codebase Directory Map

* **`pages/` — Curriculum Content:** Contains the HTML pages for the 8 learning modules and the main landing page (`index.html`). Each module page is fully documented with engineering theory, systems thinking concepts, and interactive code blocks.
* **`static/` — Frontend Assets:**
  * **`static/css/style.css`:** The styling sheet containing all CSS rules. Implements the glassmorphic card layouts, responsive flex/grid wrappers, glow states, custom selection overlays, and scrollbar modifications.
  * **`static/js/app.js`:** The core JS logic driving Pyodide compilation. Manages WebAssembly initialization, intercepts `sys.stdout`/`sys.stderr` to feed output DOM elements, and defines mock classes for pygame and Google AI SDKs.
  * **`static/js/game.js`:** The browser-native HTML5 Canvas engine. Manages floating robot physics, key polling state arrays, particle pool updates, and telemetry HUD overlays.
* **`exercises/` — Student Programming Assignments:** Practical coding exercises corresponding to each module. These files contain code scaffolds with descriptive docstrings and `TODO` comments guiding the student to implement the physical models.
* **`game/` — Native Pygame Codebase:**
  * **`game/main.py`:** The entry point for the desktop graphical simulator. Spawns the screen surface, configures key loops, and controls frame rates.
  * **`game/robot.py`:** Manages the desktop visual representation of the robot, incorporating physics bounds and visual indicator updates.
  * **`game/hvac_system.py`:** Models the thermodynamic compression/expansion cycle equations.
  * **`game/hud.py`:** Draws the local desktop HUD showing pressure and temperature metrics.
  * **`game/ai_brain.py`:** Manages non-blocking threads to make HTTP calls to the Google Generative AI API.
* **Root Utility Files:**
  * **`server.py`:** A built-in HTTP server to serve the training portal locally. It implements custom routing maps and is used for GCP Cloud Run deployments.
  * **`Dockerfile`:** Contains build configurations for Docker containerization.
  * **`requirements.txt`:** Lists standard library and external package dependencies for desktop execution.
  * **`audit_code_blocks.py`:** A validation tool that parses all HTML modules, extracts raw code blocks, applies browser mocks, and runs an automated verification pipeline to check for syntax errors or runtime exceptions.

---

### 2. Comprehensive Exercise Scaffolds

Each exercise inside the `exercises/` folder is designed to reinforce the matching module's theory with practical software engineering patterns.

#### Exercise 1: Variables, Types & Thermostat Deadbands
* **File:** `exercises/ex01_variables_and_types.py`
* **Assignment:** Students write a script to monitor room temperatures. They must calculate the Sensible Heat Load using variables, convert Fahrenheit values to Celsius, and implement a deadband conditional structure:
  * If temperature is above $75^\circ\text{F}$, turn cooling ON.
  * If temperature drops below $70^\circ\text{F}$, turn cooling OFF.
  * Implement a loop simulating a cooling cycle over 10 minutes.
* **Student Focus:** Master variables, arithmetic operators, data type conversion, and boundary comparisons.

#### Exercise 2: Procedural Refrigeration Cycle Simulation
* **File:** `exercises/ex02_hvac_functions.py`
* **Assignment:** Transition the procedural code of Module 1 into modular, reusable functions. Students implement 4 functions representing the physical stages of the refrigeration cycle:
  1. `evaporator(refrigerant, room_temp)`: Absorbs room heat, return modified refrigerant dict (state changes to gas) and cools room temperature.
  2. `compressor(refrigerant)`: Squeezes low-pressure gas, raising temperature and pressure (multiplies pressure by 6, adds 80 to temperature).
  3. `condenser(refrigerant, outdoor_temp)`: Cools high-pressure gas close to outdoor temperature and condenses it to liquid state.
  4. `expansion_valve(refrigerant)`: Drops pressure (divides by 6) and resets refrigerant temperature to $40^\circ\text{F}$ liquid.
* **Student Focus:** Understand dictionaries as mutable state containers, parameter scopes, return values, and functional pipelines.

#### Exercise 3: Automated Logging of Telemetry Trend Logs
* **File:** `exercises/ex03_csv_logging.py`
* **Assignment:** Write the simulated thermodynamic state metrics into a persistent file. Students must write headers and rows of cycle data to `hvac_trend_log.csv` using Python's `csv` module. After writing, they must use a context manager to read the CSV back, extract room temperatures using a list comprehension, and compute standard system performance indicators.
* **Student Focus:** Master context managers (`with` statements), file writing permissions, list comprehensions, and basic data extraction filters.

#### Exercise 4: Refactoring to Object-Oriented Composition
* **File:** `exercises/ex04_oop_robot_ac.py`
* **Assignment:** Refactor the modular procedural logic of Module 2 and Module 3 into class-based models. Students construct an `AirConditioner` class to encapsulate thermodynamic calculations and a `Robot` class to manage coordinates. The `Robot` constructor must instantiate the `AirConditioner` inside itself, representing composition:
  ```python
  class Robot:
      def __init__(self, name):
          self.name = name
          self.ac = AirConditioner(f"{name}-AC", capacity=1.0)
  ```
* **Student Focus:** Grasp object instantiation, the `self` parameter, encapsulation, helper methods, and structural composition hierarchies.

#### Exercise 5: Building the Asynchronous Generative AI Brain
* **File:** `exercises/ex05_gemini_robot_brain.py`
* **Assignment:** Connect the class-based robot model to the Google Gemini AI using the `google-genai` SDK. Students write API calls requesting analysis of operational conditions. They must configure system instructions that guide the model to act as a certified building engineer, parse incoming JSON telemetry payloads, and generate professional recommendations.
* **Student Focus:** Understand environment variables (`os.getenv`), SDK client initialization, token structures, system instructions, and response string parsing.

#### Exercise 6: Automated Rule-Based Fault Detection & Diagnostics
* **File:** `exercises/ex06_diagnostic_dashboard.py`
* **Assignment:** Build an automated Fault Detection and Diagnostics (FDD) engine. The script reads diagnostic data logs containing injected hardware faults (e.g. low suction pressure, dirty coils, high approach temperatures). Students write rule-based threshold algorithms to identify anomaly cycles and send those specific entries to Gemini to compile root-cause remediation steps.
* **Student Focus:** Implement exception handling structures (`try`/`except` blocks), data validation logic, diagnostic reports, and hybrid rule-based/AI systems.

#### Exercise 7: Event-Driven Game Loops and Sprite Rendering
* **File:** `exercises/ex07_pygame_robot.py`
* **Assignment:** Transition the robot class into an event-driven framework. Students implement the classic Game Loop template:
  1. **Process Input:** Poll keyboard keys (`pygame.key.get_pressed()`) and handle events (`pygame.event.get()`).
  2. **Update State:** Move coordinates, calculate motor heat accumulation (running generates double heat), and cycle the AC to cool.
  3. **Render:** Clear canvas, draw grids, and render the robot sprite.
* **Student Focus:** Manage game tick rates, coordinate grids, continuous keyboard polling, and rendering states.

#### Exercise 8: Complete Integrated Systems Simulation
* **File:** `exercises/ex08_complete_game.py`
* **Assignment:** Combine all previous assignments. Build a graphical simulation where a robot navigates multiple temperature zones. Telemetry is written to a CSV file every 60 frames. The robot can run diagnostic checks, which trigger a separate thread to consult the Gemini API, rendering the AI diagnostics directly onto an overlay HUD on screen without blocking the game play.
* **Student Focus:** Thread scheduling, file sharing, VAV zone thermodynamic heat balance formulas, and final system integration.

---


## 💡 Key Educational Takeaways

This program teaches software development not as syntax memorization, but as **component coordination**:

* **State Preservation:** State must live in a central object (like `Robot`) and be mutated via clear, predictable pathways.
* **Composition:** Build complex behaviors by combining simple, isolated subsystems rather than building massive, nested inheritances.
* **Data Pipelines:** Data should flow cleanly. A sensor output becomes a log file input, which becomes an AI prompt context, which returns a system command.
* **Real-time vs. Sequential:** Learn to handle asynchronous networks, physics updates, and user interactions in a single non-blocking flow.

---

*Developed for Sovereign Biz Box — Systems Thinking for Modern AI Engineers & Robotics Technicians.*
