#!/usr/bin/env python3
"""
=============================================================================
 EXERCISE 06 — Diagnostic Dashboard: AI-Powered HVAC Analysis
=============================================================================

 PYTHON CONCEPTS: data analysis, anomaly detection, conditional logic,
                  formatted terminal output, optional AI integration,
                  random module for simulation, list comprehensions

 HVAC CONCEPTS:   Fault detection & diagnostics (FDD), stuck compressor,
                  high discharge temperature, low superheat, equipment
                  trending, AI-powered maintenance recommendations

 GOAL: Build a terminal-based diagnostic dashboard that:
       1. Generates (or reads) CSV diagnostic data
       2. Analyzes for anomalies (fault injection!)
       3. Feeds findings to Gemini AI for recommendations
       4. Displays a rich terminal dashboard

 NOTE: Runs fully without Gemini API key (uses pre-built analysis).
=============================================================================
"""

import csv
import os
import random
import time

# Safe Gemini import
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — DATA GENERATION (with Fault Injection)
# ─────────────────────────────────────────────────────────────────────────────

# Normal operating ranges for R-410A residential AC
NORMAL_RANGES = {
    "suction_pressure_psi": (65, 75),
    "discharge_pressure_psi": (220, 250),
    "evap_temp_f": (38, 48),
    "discharge_temp_f": (140, 180),
    "superheat_f": (8, 14),
    "subcooling_f": (8, 12),
    "supply_air_f": (52, 58),
    "return_air_f": (72, 78),
    "outdoor_temp_f": (80, 100),
    "compressor_amps": (12, 18),
}

# Fault profiles — what bad readings look like
FAULT_PROFILES = {
    "stuck_compressor": {
        "description": "Compressor stuck / not pumping — mechanical failure",
        "suction_pressure_psi": (90, 110),  # Pressures equalize
        "discharge_pressure_psi": (100, 130),  # Can't build pressure
        "discharge_temp_f": (85, 100),  # No compression = no heat
        "superheat_f": (2, 5),  # Low — refrigerant not absorbing heat
        "compressor_amps": (25, 35),  # Locked rotor amps
    },
    "dirty_condenser": {
        "description": "Condenser coil blocked — heat can't reject",
        "discharge_pressure_psi": (280, 340),  # Head pressure sky-high
        "discharge_temp_f": (200, 240),  # Way too hot
        "subcooling_f": (2, 5),  # Not enough liquid forming
    },
    "low_charge": {
        "description": "Low refrigerant charge — possible leak",
        "suction_pressure_psi": (40, 55),  # Low suction
        "discharge_pressure_psi": (170, 200),  # Low head
        "superheat_f": (20, 35),  # Way too high
        "subcooling_f": (1, 4),  # Almost no subcooling
        "supply_air_f": (60, 68),  # Not cooling well
    },
}


def generate_reading(cycle: int, fault: str = None) -> dict:
    """
    Generate one cycle's worth of sensor readings.

    PYTHON LESSON — RANDOM MODULE:
      random.uniform(a, b) returns a random float between a and b.
      This simulates the natural variation in real sensor readings.
      No two readings are ever exactly the same — just like real equipment.

    HVAC LESSON — FAULT INJECTION:
      To test diagnostic systems, we deliberately inject faults.
      This is exactly how HVAC training simulators work — they let
      students practice on "broken" systems without risking real equipment.
    """
    reading = {"cycle": cycle, "fault_injected": fault or "none"}

    for param, (lo, hi) in NORMAL_RANGES.items():
        value = round(random.uniform(lo, hi), 1)

        # Apply fault overrides if this parameter is affected
        if fault and fault in FAULT_PROFILES:
            fault_data = FAULT_PROFILES[fault]
            if param in fault_data:
                flo, fhi = fault_data[param]
                value = round(random.uniform(flo, fhi), 1)

        reading[param] = value

    # Compute delta-T (derived value)
    reading["delta_t_f"] = round(
        reading["return_air_f"] - reading["supply_air_f"], 1
    )

    return reading


def generate_diagnostic_csv(filepath: str, num_cycles: int = 20,
                            fault_start: int = 12,
                            fault_type: str = "stuck_compressor") -> str:
    """
    Generate a CSV with normal readings + injected fault.

    Cycles 1 through fault_start-1 are normal.
    Cycles fault_start through num_cycles have the fault.
    """
    readings = []

    for cycle in range(1, num_cycles + 1):
        if cycle >= fault_start:
            reading = generate_reading(cycle, fault=fault_type)
        else:
            reading = generate_reading(cycle, fault=None)
        readings.append(reading)

    # Write to CSV
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=readings[0].keys())
        writer.writeheader()
        writer.writerows(readings)

    return filepath


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — ANOMALY DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def analyze_readings(readings: list) -> dict:
    """
    Analyze a list of readings for anomalies.

    PYTHON LESSON — LIST COMPREHENSIONS:
      [r["discharge_temp_f"] for r in readings]
      This creates a new list by extracting one field from each reading.
      It's equivalent to a for loop but more Pythonic and faster.

    HVAC LESSON — FAULT DETECTION:
      We compare each reading against known normal ranges.
      Readings outside the range are flagged as anomalies.
      Multiple related anomalies point to a specific fault.
    """
    anomalies = []
    summary = {
        "total_cycles": len(readings),
        "normal_cycles": 0,
        "anomaly_cycles": 0,
        "anomalies": [],
        "avg_values": {},
        "max_values": {},
        "min_values": {},
    }

    # Compute averages, min, max for each parameter
    params = [k for k in NORMAL_RANGES.keys()]
    for param in params:
        values = [float(r[param]) for r in readings]
        summary["avg_values"][param] = round(sum(values) / len(values), 1)
        summary["max_values"][param] = round(max(values), 1)
        summary["min_values"][param] = round(min(values), 1)

    # Check each reading for out-of-range values
    for r in readings:
        cycle_anomalies = []
        for param, (lo, hi) in NORMAL_RANGES.items():
            val = float(r[param])
            if val < lo * 0.85 or val > hi * 1.15:  # 15% tolerance
                severity = "CRITICAL" if val < lo * 0.7 or val > hi * 1.3 else "WARNING"
                cycle_anomalies.append({
                    "cycle": r["cycle"],
                    "param": param,
                    "value": val,
                    "normal_range": f"{lo}-{hi}",
                    "severity": severity,
                })

        if cycle_anomalies:
            summary["anomaly_cycles"] += 1
            summary["anomalies"].extend(cycle_anomalies)
        else:
            summary["normal_cycles"] += 1

    return summary


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — AI ANALYSIS (optional)
# ─────────────────────────────────────────────────────────────────────────────

def get_ai_diagnosis(summary: dict) -> str:
    """
    Feed anomaly data to Gemini for intelligent diagnosis.
    Falls back to rule-based diagnosis if AI unavailable.
    """
    # Build the anomaly report for AI
    anomaly_text = "HVAC Diagnostic Anomaly Report:\n"
    anomaly_text += f"Total cycles: {summary['total_cycles']}\n"
    anomaly_text += f"Anomaly cycles: {summary['anomaly_cycles']}\n\n"

    # Group anomalies by parameter
    param_counts = {}
    for a in summary["anomalies"]:
        p = a["param"]
        param_counts[p] = param_counts.get(p, 0) + 1

    anomaly_text += "Anomalies by parameter:\n"
    for param, count in sorted(param_counts.items(), key=lambda x: -x[1]):
        anomaly_text += (
            f"  {param}: {count} anomalies "
            f"(avg={summary['avg_values'].get(param, 'N/A')}, "
            f"normal={NORMAL_RANGES.get(param, 'N/A')})\n"
        )

    # Try AI analysis
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if GENAI_AVAILABLE and api_key:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=(
                    "You are an expert HVAC diagnostician. Analyze these "
                    "readings and provide:\n"
                    "1. Most likely fault\n"
                    "2. Root cause explanation\n"
                    "3. Recommended actions\n"
                    "4. Safety concerns\n\n" + anomaly_text
                ),
                config={"temperature": 0.3, "max_output_tokens": 600}
            )
            return "🤖 AI DIAGNOSIS:\n" + response.text
        except Exception as e:
            pass  # Fall through to rule-based

    # Rule-based fallback diagnosis
    return _rule_based_diagnosis(summary, param_counts)


def _rule_based_diagnosis(summary: dict, param_counts: dict) -> str:
    """Rule-based diagnosis when AI is unavailable."""
    diagnosis = "📋 RULE-BASED DIAGNOSIS (AI offline):\n\n"

    # Check for stuck compressor signature
    high_suction = summary["avg_values"].get("suction_pressure_psi", 0) > 85
    low_discharge = summary["avg_values"].get("discharge_pressure_psi", 0) < 150
    high_amps = summary["avg_values"].get("compressor_amps", 0) > 22

    if high_suction and low_discharge:
        diagnosis += (
            "  🔴 FAULT: Stuck/Failed Compressor\n"
            "  Root Cause: Compressor cannot build differential pressure.\n"
            "     Suction and discharge pressures are equalizing.\n"
            "  Actions:\n"
            "    1. Check compressor windings (ohm test)\n"
            "    2. Check start capacitor and relay\n"
            "    3. Feel discharge line — should be HOT\n"
            "    4. If cool, compressor valves may be broken\n"
        )
        if high_amps:
            diagnosis += "  ⚠️  HIGH AMPS detected — possible locked rotor!\n"
            diagnosis += "     SAFETY: Disconnect power immediately.\n"
    elif "discharge_pressure_psi" in param_counts:
        avg_dp = summary["avg_values"].get("discharge_pressure_psi", 0)
        if avg_dp > 280:
            diagnosis += (
                "  🟡 FAULT: Dirty/Blocked Condenser\n"
                "  Root Cause: Heat rejection impaired, head pressure rising.\n"
                "  Actions: Clean condenser coil, check fan motor.\n"
            )
        elif avg_dp < 180:
            diagnosis += (
                "  🟡 FAULT: Low Refrigerant Charge\n"
                "  Root Cause: Possible refrigerant leak.\n"
                "  Actions: Leak test, weigh-in proper charge.\n"
            )
    else:
        diagnosis += "  🟢 No critical faults detected in available data.\n"

    return diagnosis


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — TERMINAL DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def render_dashboard(summary: dict, diagnosis: str, fault_type: str) -> None:
    """
    Render a rich terminal dashboard.

    PYTHON LESSON — STRING FORMATTING:
      f-strings with format specs: {value:>8.1f} means
        > = right-align, 8 = total width, .1f = 1 decimal float
      This creates clean, aligned terminal output.
    """
    w = 62  # Dashboard width

    print()
    print("╔" + "═" * w + "╗")
    print("║" + " HVAC DIAGNOSTIC DASHBOARD".center(w) + "║")
    print("╠" + "═" * w + "╣")

    # System overview
    print("║" + " SYSTEM OVERVIEW".ljust(w) + "║")
    print("║" + f"   Total Cycles    : {summary['total_cycles']}".ljust(w) + "║")
    print("║" + f"   Normal Cycles   : {summary['normal_cycles']}".ljust(w) + "║")
    print("║" + f"   Anomaly Cycles  : {summary['anomaly_cycles']}".ljust(w) + "║")
    print("║" + f"   Injected Fault  : {fault_type}".ljust(w) + "║")

    # Overall status
    if summary["anomaly_cycles"] > summary["total_cycles"] * 0.3:
        status = "🔴 CRITICAL — Service Required"
    elif summary["anomaly_cycles"] > 0:
        status = "🟡 WARNING — Monitor Closely"
    else:
        status = "🟢 NORMAL — All Systems OK"
    print("║" + f"   Status          : {status}".ljust(w) + "║")

    print("╠" + "═" * w + "╣")

    # Key metrics table
    print("║" + " KEY METRICS".ljust(w) + "║")
    print("║" + f"   {'Parameter':<28s} {'Avg':>7s} {'Min':>7s} "
          f"{'Max':>7s}  {'Range':>8s}".ljust(w) + "║")
    print("║" + "   " + "─" * (w - 4) + " ║")

    display_params = [
        "suction_pressure_psi", "discharge_pressure_psi",
        "discharge_temp_f", "superheat_f", "subcooling_f",
        "supply_air_f", "compressor_amps",
    ]

    for param in display_params:
        avg = summary["avg_values"].get(param, 0)
        mn = summary["min_values"].get(param, 0)
        mx = summary["max_values"].get(param, 0)
        lo, hi = NORMAL_RANGES.get(param, (0, 0))
        flag = " ⚠️" if avg < lo * 0.85 or avg > hi * 1.15 else ""
        line = (f"   {param:<28s} {avg:>7.1f} {mn:>7.1f} "
                f"{mx:>7.1f}  {lo}-{hi}{flag}")
        print("║" + line.ljust(w) + "║")

    print("╠" + "═" * w + "╣")

    # Anomaly summary
    print("║" + " ANOMALIES DETECTED".ljust(w) + "║")
    if summary["anomalies"]:
        # Show top 5 most critical
        critical = [a for a in summary["anomalies"] if a["severity"] == "CRITICAL"]
        warnings = [a for a in summary["anomalies"] if a["severity"] == "WARNING"]
        print("║" + f"   🔴 Critical: {len(critical)}".ljust(w) + "║")
        print("║" + f"   🟡 Warning : {len(warnings)}".ljust(w) + "║")

        for a in critical[:3]:
            line = (f"   C{a['cycle']:>2d} | {a['param']:<25s} "
                    f"= {a['value']:>7.1f}  (normal: {a['normal_range']})")
            print("║" + line.ljust(w) + "║")
    else:
        print("║" + "   None — all readings within normal range.".ljust(w) + "║")

    print("╠" + "═" * w + "╣")

    # AI / Rule-based diagnosis
    print("║" + " DIAGNOSIS".ljust(w) + "║")
    for line in diagnosis.split("\n"):
        # Truncate long lines
        display_line = line[:w - 2] if len(line) > w - 2 else line
        print("║" + f"  {display_line}".ljust(w) + "║")

    print("╚" + "═" * w + "╝")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 64)
    print(" EXERCISE 06 — HVAC Diagnostic Dashboard")
    print("=" * 64)
    print()

    # Configuration
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "diagnostic_data.csv")
    fault_type = "stuck_compressor"  # Try: "dirty_condenser", "low_charge"

    # STEP 1: Generate diagnostic data with fault injection
    print(f"  📊 Generating diagnostic data with fault: {fault_type}")
    generate_diagnostic_csv(
        filepath=csv_path,
        num_cycles=20,
        fault_start=12,
        fault_type=fault_type
    )
    print(f"  📝 Data written to: {csv_path}")

    # STEP 2: Read the data back
    print("  📖 Reading diagnostic data...")
    readings = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            readings.append(row)
    print(f"  ✅ Loaded {len(readings)} cycle records")

    # STEP 3: Analyze for anomalies
    print("  🔍 Analyzing for anomalies...")
    summary = analyze_readings(readings)
    print(f"  ⚠️  Found {len(summary['anomalies'])} anomalies "
          f"across {summary['anomaly_cycles']} cycles")

    # STEP 4: Get AI diagnosis
    print("  🧠 Running diagnostic analysis...")
    diagnosis = get_ai_diagnosis(summary)

    # STEP 5: Render the dashboard
    render_dashboard(summary, diagnosis, fault_type)

    print()
    print("=" * 64)
    print(" EXERCISE 06 COMPLETE")
    print("=" * 64)
    print(f"""
 OUTPUT FILE: {csv_path}

 TRY DIFFERENT FAULTS:
   Change 'fault_type' variable to:
     "stuck_compressor"  — Compressor can't build pressure
     "dirty_condenser"   — Blocked condenser, high head pressure
     "low_charge"        — Refrigerant leak, high superheat

 WHAT YOU LEARNED:
   Python — data analysis, anomaly detection, random module,
            list comprehensions, dict operations, formatted output,
            optional AI integration, graceful degradation

   HVAC  — Fault Detection & Diagnostics (FDD), stuck compressor
           signature, dirty condenser signature, low charge signature,
           normal operating ranges, sensor trending, field diagnostics

 NEXT: Exercise 07 — Pygame Robot (visual simulation!)
""")
