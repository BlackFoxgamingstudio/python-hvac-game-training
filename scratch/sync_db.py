import sqlite3
import uuid
import datetime

db_path = "/Users/russellpowers/Sovereign Biz Box/databases/sbb_command_center.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Insert into lessons_learned (Advanced dashboard diagnostics)
lesson_id = str(uuid.uuid4())
cursor.execute("""
INSERT INTO lessons_learned (
    id, project_id, pattern_id, category, title, problem, 
    root_cause, fix_applied, generalized_rule, 
    automation_potential, time_cost_minutes, preventable, source_files, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    lesson_id,
    "gcp",
    "fdd_simulation_ui",
    "Interactive UI & FDD simulation",
    "Physical HVAC State Mapping to Interactive UI Dashboards",
    "Static browser canvases fail to convey complex thermodynamic loop behaviors, variables, threshold violations, and AI diagnostics interactively.",
    "Lack of direct hooks between CPython runner models and browser visual components restricts the student's ability to inject faults and verify threshold logic.",
    "Exposed a reference of the robot state machine directly on the canvas element, enabling a local interval polling loop to query telemetry metrics, populate digital gauges, trigger rule-based FDD warning lists, and display real-time logged CSV entries.",
    "When building visual dashboards that tie directly into hardware metrics, expose getter/setter hooks on the model components so that DOM rendering loops can operate asynchronously and independently from core simulation updates.",
    "High. Build standard event interfaces on model classes to automatically bind variables to matching UI gauges.",
    90,
    1,
    "pages/module_08_final_project.html,static/js/game.js,server.py",
    datetime.datetime.now(datetime.UTC).isoformat()
))

# 2. Insert into engineering_patterns (Real-time FDD Dashboard integration)
pattern_uuid = str(uuid.uuid4())
cursor.execute("""
INSERT INTO engineering_patterns (
    id, domain, pattern_name, problem_statement, solution, 
    rationale, anti_patterns, implementation_notes, 
    source_project, source_files, tags, confidence, created_at, updated_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    pattern_uuid,
    "Control Dashboards & Anomaly Detection",
    "Decoupled Telemetry Polling and Rule-Based Anomaly Alerting",
    "How to monitor live thermodynamic loop variables and warn the user of DDC threshold FDD faults in a visual browser UI without blocking game update frame rates.",
    "Store cycle telemetry inside the model. Run a separate 1000ms polling loop to read parameters, execute threshold rules (e.g. Low Suction < 50 PSI = Frozen Coil warning), and push logs to a table and warnings list.",
    "Keeps the 60fps canvas loop lightweight while ensuring telemetry logs and alerts are updated in human-readable intervals (1s) to mimic real-world BAS systems.",
    "Checking rules and updating DOM nodes on every game loop frame (causes massive lag spikes); tightly coupling DOM rendering to game tick calls.",
    "Attach the model reference directly on the canvas element. Query it from the DOM. Parse markdown using simple regex replacements to speed up AI response times.",
    "python-hvac-game-training",
    "pages/module_08_final_project.html,static/js/game.js",
    "fdd,dashboard,bms,bas,telemetry,gemini,polling",
    "verified",
    datetime.datetime.now(datetime.UTC).isoformat(),
    datetime.datetime.now(datetime.UTC).isoformat()
))

# 3. Insert into activities (Dashboard deployment activity)
activity_id = str(uuid.uuid4())
cursor.execute("""
INSERT INTO activities (
    id, session_id, project_id, activity_type, description, outcome, duration_seconds, timestamp
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    activity_id,
    "",
    "gcp",
    "Deployment",
    "Deployed latest revision of python-hvac-game-training to GCP Cloud Run incorporating interactive HVAC dashboard gauges, fault injector, FDD alerts, and Gemini AI diagnose endpoint.",
    "Successful deployment of revision python-hvac-game-training-00004-rml serving 100% of traffic at https://python-hvac-game-training-410866387199.us-central1.run.app",
    600,
    datetime.datetime.now(datetime.UTC).isoformat()
))

conn.commit()
conn.close()
print("Database synchronization completed successfully!")
