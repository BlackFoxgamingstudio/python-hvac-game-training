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

By the end of this curriculum, the student will transition from basic variable assignments to building a multi-threaded, real-time game engine in Pygame that simulates a physical robot regulating its internal temperature using a simulated refrigeration cycle while interacting with a Gemini AI brain.

---

## 🎯 Target Audience

This course is designed for:
1. **HVAC Technicians & Facilities Managers:** Professionals with rich domain knowledge in physical systems who want to acquire coding skills to automate their workflows or transition into smart-building software development.
2. **Beginner Programmers:** Students who struggle with dry, abstract programming exercises and learn best when code directly controls a physical or visual system.
3. **Game Developers:** Individuals interested in building robust, modular simulation engines and learning how to structure complex game loop architectures with external API dependencies.

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
* **Programming Concepts:** Variable assignment, data types (float, integer, string, boolean), f-strings, arithmetic operators, conditionals (`if`/`elif`/`else`), and `while` loops.
* **HVAC Concepts:** Delta-T calculations, BTU estimation, suction/discharge pressures, basic deadband thermostat logic.
* **Core Exercise:** `exercises/ex01_variables_and_types.py`
  * Implements a script that simulates a cooling countdown, dropping target temperatures by calculating the thermal load.

### Module 2: HVAC as Functions — Mapping Hardware to Software
* **Pedagogical Goal:** Learn code reuse and input/output mapping by modeling the four key components of a refrigeration cycle.
* **Programming Concepts:** Function definitions, parameter passing, return statements, dictionaries as state representations, docstrings.
* **HVAC Concepts:** Vapor compression cycle thermodynamics. Evaporator (latent heat absorption, phase change to gas), Compressor (mechanical work, pressure/temperature spike), Condenser (heat rejection, phase change to liquid), Expansion Valve (metering device, pressure drop, adiabatic expansion).
* **Core Exercise:** `exercises/ex02_hvac_functions.py`
  * Students pass a refrigerant state dictionary through a chain of functions to calculate temperature differentials.

### Module 3: Data Flow & Diagnostic Logging — CSV Telemetry
* **Pedagogical Goal:** Understand data persistence, file storage, and structural trend logging.
* **Programming Concepts:** `csv` module, file I/O operations (`open()`), context managers (`with` statement), list comprehensions.
* **HVAC Concepts:** BAS (Building Automation System) trend logs, sensor calibration logs, diagnostic data acquisition.
* **Core Exercise:** `exercises/ex03_csv_logging.py`
  * Automates the logging of a 24-cycle refrigeration simulation to a CSV file and reads it back to calculate mean efficiency ratings.

### Module 4: OOP Refactor — Robot + AC Composition
* **Pedagogical Goal:** Master Object-Oriented Programming (OOP) and system composition over inheritance.
* **Programming Concepts:** Class declarations, constructors (`__init__`), instance variables, class methods, encapsulation, composition (the HAS-A relationship).
* **HVAC Concepts:** Modular component design. A robot has an internal air conditioning unit.
* **Core Exercise:** `exercises/ex04_oop_robot_ac.py`
  * Refactors the simulator so that the `Robot` class instantiates an `AirConditioner` instance inside its constructor.

### Module 5: AI Integration — Gemini API & Robot Brain
* **Pedagogical Goal:** Teach modern API interaction, environment variables, and asynchronous design patterns.
* **Programming Concepts:** Environment variables, external packages, error handling, prompt engineering, system instructions.
* **HVAC Concepts:** AI-enabled building management, smart thermostats, natural language interfaces for machinery.
* **Core Exercise:** `exercises/ex05_gemini_robot_brain.py`
  * Connects the robot to the Google Gemini API using the `google-genai` SDK, passing live thermodynamic telemetry inside the system prompt.

### Module 6: Diagnostic Troubleshooting — AI-Powered Analysis
* **Pedagogical Goal:** Implement rule-based anomaly detection alongside generative AI analysis for complex troubleshooting.
* **Programming Concepts:** Exception handling, data classification, structured prompting.
* **HVAC Concepts:** Fault Detection and Diagnostics (FDD), low charge detection, compressor failure signatures, blocked condenser airflow.
* **Core Exercise:** `exercises/ex06_diagnostic_dashboard.py`
  * Simulates sensor faults (e.g. low refrigerant pressure, stuck valves) and calls the AI to diagnose the physical root cause from CSV telemetry.

### Module 7: Game Programming — Pygame & Game Objects
* **Pedagogical Goal:** Transition from sequential CLI scripts to event-driven real-time execution.
* **Programming Concepts:** Game loops, event queues, frame rate control, coordinate systems, keyboard state polling.
* **HVAC Concepts:** Real-time heat dissipation, transient thermal loads.
* **Core Exercise:** `exercises/ex07_pygame_robot.py`
  * Renders a interactive robot using Pygame. The robot's movement generates motor heat, causing it to glow red until the automated HVAC system kicks in.

### Module 8: Final Project — Complete Robot Simulation
* **Pedagogical Goal:** Synthesize all previous lessons into a single large-scale software project.
* **Programming Concepts:** Modular code integration, package management, state machines.
* **HVAC Concepts:** Multi-zone air distribution, variable air volume (VAV) systems, zone heat loads.
* **Core Exercise:** `exercises/ex08_complete_game.py`
  * A full simulation featuring multiple temperature zones, heat sources, visual diagnostic logs, and an in-game AI overlay.

---

## 🎮 Pygame Simulator Architecture

The simulator located in `game/` represents a production-style game engine. Here is how the individual subsystems communicate:

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

### 1. Main Loop & Delta-Time (`main.py`)
In standard programming, execution is sequential. In games, execution is circular. The game loop runs 60 times per second. 
To ensure physics run at the same speed regardless of computer performance, the engine calculates **Delta-Time (dt)**—the fraction of a second since the last frame.
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
API requests are network-bound and take $1$ to $3$ seconds. In a single-threaded game, calling an API synchronously will freeze the screen.
To prevent this, the `RobotBrain` uses Python's `threading` library to call Gemini asynchronously:
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

### 4. Diagnostic Logging System
When diagnostic logging is enabled, the system appends complete state dictionary records every cycle. Pressing `D` writes these entries to `robot_hvac_diagnostic.csv` using Python's `csv.writer`, creating structured logs suitable for analysis in Jupyter, Excel, or by the AI troubleshooters.

---

## ⚡ In-Browser Execution via Pyodide

To allow users to test and run the code directly inside the training website, the platform integrates **Pyodide**—a port of CPython to WebAssembly (WASM).

### How it Works
1. When a user clicks the **"▶ Run"** button on any code block, the frontend lazily downloads the Pyodide runtime from a secure CDN.
2. The browser creates an isolated WebAssembly sandbox.
3. Standard Python input/output (`sys.stdout` and `sys.stderr`) is captured and redirected to a custom output terminal rendered below the code card.
4. Because the browser cannot run graphic loops or access the local filesystem directly, we inject a mock module suite for `pygame` and `google.genai` to prevent import errors and mock their operations.

---

## ☁️ Cloud Deployment Guide (GCP Cloud Run)

This project is fully prepared for serverless deployment on Google Cloud Platform using **Cloud Run**.

### 1. Docker Containerization
The project includes a multi-stage-ready `Dockerfile` based on `python:3.11-slim` to minimize image size and decrease cold-start latency.
The container is configured to bind to `0.0.0.0` and read the `PORT` environment variable injected by Cloud Run.

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

### 3. CI/CD Architecture (Optional)
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
git commit -m "feat: complete interactive systems thinking training platform with Pyodide runner"

# Create a new repository on GitHub using the GitHub CLI
gh repo create python-hvac-game-training --public --source=. --remote=origin --push
```

---

## 💡 Key Educational Takeaways

This program teaches software development not as syntax memorization, but as **component coordination**:

* **State Preservation:** State must live in a central object (like `Robot`) and be mutated via clear, predictable pathways.
* **Composition:** Build complex behaviors by combining simple, isolated subsystems rather than building massive, nested inheritances.
* **Data Pipelines:** Data should flow cleanly. A sensor output becomes a log file input, which becomes an AI prompt context, which returns a system command.
* **Real-time vs. Sequential:** Learn to handle asynchronous networks, physics updates, and user interactions in a single non-blocking flow.

---

*Developed for Sovereign Biz Box — Systems Thinking for Modern AI Engineers & Robotics Technicians.*
