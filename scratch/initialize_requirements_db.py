import os
import sqlite3

db_path = "/Users/russellpowers/Sovereign Biz Box/python-hvac-game-training/rpg_game_requirements.db"

# Connect and create schema
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS requirements_tracker (
    req_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    implemented_at TEXT,
    verified_at TEXT
)
""")

# Setup bulk insert collections
reqs_to_insert = []

# 1. 100 Faction NPCs
for i in range(1, 101):
    reqs_to_insert.append((
        f"NPC-{i:03d}",
        f"NPC Character {i:03d}",
        f"NPC Dialogue state, coordinate bounds, level check, faction rule, and UI display status. Coordinates: X={50+i}, Y={100+i*2}.",
        "RPG Systems"
    ))

# 2. 60 Levels Quests
for i in range(1, 61):
    reqs_to_insert.append((
        f"LVL-{i:03d}-Q",
        f"Level {i:03d} Quest",
        f"Objective descriptions, NPC triggers, completion checks, and XP reward values.",
        "RPG Systems"
    ))

# 3. 60 Levels Coding Inputs
for i in range(1, 61):
    reqs_to_insert.append((
        f"LVL-{i:03d}-I",
        f"Level {i:03d} Code Inputs",
        f"Variables names, data formats, expected float values, and default strings.",
        "LMS & AST Sandbox"
    ))

# 4. 60 Levels Grading Unit Tests
for i in range(1, 61):
    reqs_to_insert.append((
        f"LVL-{i:03d}-T",
        f"Level {i:03d} Unit Test Assertions",
        f"Python assert checks, scope maps, stderr capturing, and console layouts.",
        "LMS & AST Sandbox"
    ))

# 5. 60 Levels UI Canvas Coordinates
for i in range(1, 61):
    reqs_to_insert.append((
        f"LVL-{i:03d}-C",
        f"Level {i:03d} Canvas Layout Anchors",
        f"Camera offsets, relative viewport borders, assets scale multipliers.",
        "Simulation"
    ))

# 6. 60 Levels AR HUD Visor Mappings
for i in range(1, 61):
    reqs_to_insert.append((
        f"LVL-{i:03d}-A",
        f"Level {i:03d} AR HUD Overlays",
        f"Visor scanlines, pipe glows, equipment health bars, superheat glows.",
        "Apple Glass AR"
    ))

# 7. 60 Levels Dialog Typewriter Branches
for i in range(1, 61):
    reqs_to_insert.append((
        f"LVL-{i:03d}-D",
        f"Level {i:03d} Dialogue Branching",
        f"Dialogue text arrays, choice glow, hover scaling parameters.",
        "RPG Systems"
    ))

# 8. 60 Levels Database State Sync
for i in range(1, 61):
    reqs_to_insert.append((
        f"LVL-{i:03d}-V",
        f"Level {i:03d} Firestore Variables",
        f"User progression columns, auth token session locks, upload queues.",
        "Data Logging"
    ))

# 9. 200 Animation Frames
for i in range(1, 201):
    reqs_to_insert.append((
        f"FRM-{i:03d}",
        f"Frame Asset {i:03d}",
        f"Sprite sheet row-column coordinates offsets, pixel dimensions, color codes, rotation angles.",
        "Simulation"
    ))

# 10. 400 Physics Parameters
for i in range(1, 401):
    reqs_to_insert.append((
        f"PHYS-{i:03d}",
        f"Thermodynamic Variable {i:03d}",
        f"Enthalpy change, compression ratio, suction pressure, subcooling, amperage draw bounds.",
        "Physics Model"
    ))

# 11. 300 AST Nodes
for i in range(1, 301):
    reqs_to_insert.append((
        f"AST-{i:03d}",
        f"AST Validation Node {i:03d}",
        f"Abstract Syntax Tree node visitor check, import filter logic, loop structure checker.",
        "LMS & AST Sandbox"
    ))

# 12. 300 AI Vectors
for i in range(1, 301):
    reqs_to_insert.append((
        f"AI-{i:03d}",
        f"AI Prompt Aggregator {i:03d}",
        f"System instruct parameters, diagnostic response regex maps, few-shot patterns.",
        "AI Engine"
    ))

# 13. 300 Facility registers
for i in range(1, 301):
    reqs_to_insert.append((
        f"FAC-{i:03d}",
        f"Facility Register {i:03d}",
        f"VAV suite damper output, exhaust fan RPM static pressure, lead/lag chillers staging load.",
        "Hotel Starship"
    ))

# 14. 100 Network Control
for i in range(1, 101):
    reqs_to_insert.append((
        f"NET-{i:03d}",
        f"BACnet Controller {i:03d}",
        f"Distributed segment scanner IP registers, binding ports, timeout check loops.",
        "Hotel Starship"
    ))

# Bulk insert with ignore key collisions
cursor.executemany("""
INSERT OR IGNORE INTO requirements_tracker (req_id, title, description, category)
VALUES (?, ?, ?, ?)
""", reqs_to_insert)

conn.commit()

# Verify count
cursor.execute("SELECT COUNT(*) FROM requirements_tracker")
count = cursor.fetchone()[0]
conn.close()

print("Requirements tracking database initialized successfully!")
print(f"Total inserted records: {count}")
