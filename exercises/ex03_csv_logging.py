#!/usr/bin/env python3
"""
=============================================================================
 EXERCISE 03 — CSV Logging: Recording Diagnostic Data Like a Pro
=============================================================================

 PYTHON CONCEPTS: import csv, context managers (with statement), file I/O,
                  csv.writer, csv.DictWriter, csv.reader, csv.DictReader,
                  lists of dicts, string formatting, os.path

 HVAC CONCEPTS:   Diagnostic logging, cycle-by-cycle component tracking,
                  data-driven troubleshooting, field service reports

 GOAL: Run the AC cycle from Exercise 02, but this time LOG every
       component's input/output to a CSV file — like a modern diagnostic
       tool that records data for later analysis.

 WHY CSV?
   CSV (Comma-Separated Values) is the universal data format.  Every
   diagnostic tool, building management system (BMS), and data logger
   can export CSV.  Learning to read/write CSV is essential for both
   programming AND HVAC field work.
=============================================================================
"""

import csv          # Python's built-in CSV module — no pip install needed
import os           # For file path operations


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — HVAC CYCLE FUNCTIONS (from Exercise 02, condensed)
# ─────────────────────────────────────────────────────────────────────────────

def evaporator(ref_in: dict, room_temp_f: float) -> tuple:
    """Evaporator: absorb heat from room air, boil refrigerant."""
    superheat = 10.0
    ref_out = {
        "temp_f": ref_in["temp_f"] + superheat,
        "pressure_psi": ref_in["pressure_psi"],
        "phase": "Superheated Vapor",
        "enthalpy_btu_lb": ref_in["enthalpy_btu_lb"] + 70.0
    }
    new_room = round(room_temp_f - 19.0 * 0.15, 1)
    return ref_out, new_room


def compressor(ref_in: dict) -> dict:
    """Compressor: raise pressure and temperature of vapor."""
    return {
        "temp_f": ref_in["temp_f"] + 120.0,
        "pressure_psi": ref_in["pressure_psi"] * 3.4,
        "phase": "Superheated Vapor (Hot Gas)",
        "enthalpy_btu_lb": ref_in["enthalpy_btu_lb"] + 25.0
    }


def condenser(ref_in: dict, outdoor_temp_f: float) -> dict:
    """Condenser: reject heat to outdoor air, liquefy refrigerant."""
    return {
        "temp_f": 95.0,   # Condensing sat temp minus subcooling
        "pressure_psi": ref_in["pressure_psi"],
        "phase": "Subcooled Liquid",
        "enthalpy_btu_lb": ref_in["enthalpy_btu_lb"] - 85.0
    }


def expansion_valve(ref_in: dict) -> dict:
    """Expansion valve: drop pressure, flash some liquid to vapor."""
    return {
        "temp_f": 34.0,
        "pressure_psi": 68.0,
        "phase": "Two-Phase Mix",
        "enthalpy_btu_lb": ref_in["enthalpy_btu_lb"] - 2.0
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — CSV WRITING: Logging the Cycle
# ─────────────────────────────────────────────────────────────────────────────

# Define CSV column headers
# Each row captures: which cycle, which component, room/outdoor conditions,
# refrigerant state going IN and coming OUT.
CSV_HEADERS = [
    "Cycle",
    "Component",
    "Room_Temp_In_F",
    "Outdoor_Temp_F",
    "Ref_Temp_In_F",
    "Ref_Pressure_In",
    "Ref_State_In",
    "Ref_Temp_Out_F",
    "Ref_Pressure_Out",
    "Ref_State_Out",
    "Room_Temp_Out_F",
]


def make_log_row(cycle: int, component: str, room_in: float,
                 outdoor: float, ref_in: dict, ref_out: dict,
                 room_out: float) -> dict:
    """
    Build one row of CSV data as a dictionary.

    PYTHON LESSON:
      Returning a dict whose keys match CSV_HEADERS lets us use
      csv.DictWriter, which maps dict keys → CSV columns automatically.
      This is MUCH safer than relying on list order.
    """
    return {
        "Cycle": cycle,
        "Component": component,
        "Room_Temp_In_F": round(room_in, 1),
        "Outdoor_Temp_F": round(outdoor, 1),
        "Ref_Temp_In_F": round(ref_in["temp_f"], 1),
        "Ref_Pressure_In": round(ref_in["pressure_psi"], 1),
        "Ref_State_In": ref_in["phase"],
        "Ref_Temp_Out_F": round(ref_out["temp_f"], 1),
        "Ref_Pressure_Out": round(ref_out["pressure_psi"], 1),
        "Ref_State_Out": ref_out["phase"],
        "Room_Temp_Out_F": round(room_out, 1),
    }


def run_and_log_cycle(room_temp_f: float, outdoor_temp_f: float,
                      target_temp_f: float, csv_path: str,
                      max_cycles: int = 20) -> float:
    """
    Run the full AC cycle and log every component transition to CSV.

    PYTHON LESSON — CONTEXT MANAGERS (the 'with' statement):
      'with open(path, "w") as f:'  does THREE things:
        1. Opens the file
        2. Gives you 'f' to work with
        3. AUTOMATICALLY closes the file when the block ends — even if
           an error occurs!

      This is critical because unclosed files can:
        - Lose data (buffered writes never flushed)
        - Lock files on Windows
        - Leak file descriptors (crash on long-running programs)

      HVAC ANALOGY: A context manager is like a service disconnect.
      You open the disconnect (open the file), do your work, and the
      disconnect automatically closes when you walk away — safety first.
    """
    print(f"  📝 Writing diagnostic log to: {csv_path}")
    print()

    # ── OPEN CSV FOR WRITING ──
    # 'w' = write mode (creates new file, overwrites if exists)
    # newline='' is required on Windows to prevent double line breaks
    with open(csv_path, "w", newline="") as csv_file:
        # DictWriter maps dict keys to column headers
        writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)

        # Write the header row first
        writer.writeheader()

        cycle = 0

        while room_temp_f > target_temp_f and cycle < max_cycles:
            cycle += 1
            room_before_cycle = room_temp_f

            # ── Component 1: Expansion Valve → Evaporator inlet ──
            ref_start = {
                "temp_f": 34.0, "pressure_psi": 68.0,
                "phase": "Two-Phase Mix", "enthalpy_btu_lb": 45.0
            }

            # ── Component 2: Evaporator ──
            ref_in_evap = ref_start.copy()
            ref_out_evap, room_temp_f = evaporator(ref_in_evap, room_temp_f)
            writer.writerow(make_log_row(
                cycle, "Evaporator", room_before_cycle, outdoor_temp_f,
                ref_in_evap, ref_out_evap, room_temp_f
            ))

            # ── Component 3: Compressor ──
            ref_in_comp = ref_out_evap.copy()
            ref_out_comp = compressor(ref_in_comp)
            writer.writerow(make_log_row(
                cycle, "Compressor", room_temp_f, outdoor_temp_f,
                ref_in_comp, ref_out_comp, room_temp_f
            ))

            # ── Component 4: Condenser ──
            ref_in_cond = ref_out_comp.copy()
            ref_out_cond = condenser(ref_in_cond, outdoor_temp_f)
            writer.writerow(make_log_row(
                cycle, "Condenser", room_temp_f, outdoor_temp_f,
                ref_in_cond, ref_out_cond, room_temp_f
            ))

            # ── Component 5: Expansion Valve ──
            ref_in_exp = ref_out_cond.copy()
            ref_out_exp = expansion_valve(ref_in_exp)
            writer.writerow(make_log_row(
                cycle, "Expansion Valve", room_temp_f, outdoor_temp_f,
                ref_in_exp, ref_out_exp, room_temp_f
            ))

            status = "✓" if room_temp_f <= target_temp_f else "→"
            print(f"    Cycle {cycle:>2}: Room {room_before_cycle:.1f} → "
                  f"{room_temp_f:.1f} °F  {status}")

    # File is automatically closed here (context manager magic)
    print()
    print(f"  ✅ Logged {cycle * 4} component records across {cycle} cycles.")
    return room_temp_f


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — CSV READING: Analyzing the Log
# ─────────────────────────────────────────────────────────────────────────────

def read_and_summarize(csv_path: str) -> None:
    """
    Read the CSV log back and print a diagnostic summary.

    PYTHON LESSON:
      csv.DictReader automatically uses the first row as column headers
      and returns each subsequent row as an OrderedDict.

    HVAC LESSON:
      Field technicians review logged data to spot trends:
        - Is discharge pressure climbing? (dirty condenser coil)
        - Is suction pressure dropping? (low charge or restricted filter)
        - Is superheat too high? (undercharge or TXV issue)
    """
    print("╔" + "═" * 58 + "╗")
    print("║   DIAGNOSTIC LOG SUMMARY                                 ║")
    print("╚" + "═" * 58 + "╝")

    if not os.path.exists(csv_path):
        print(f"  ❌ File not found: {csv_path}")
        return

    # Accumulators for analysis
    total_rows = 0
    components_seen = {}  # Count how many times each component appears
    max_discharge_temp = -999.0
    min_evap_temp = 999.0

    with open(csv_path, "r", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            total_rows += 1
            comp = row["Component"]
            components_seen[comp] = components_seen.get(comp, 0) + 1

            # Track extreme values (useful for diagnostics)
            ref_out_temp = float(row["Ref_Temp_Out_F"])

            if comp == "Compressor" and ref_out_temp > max_discharge_temp:
                max_discharge_temp = ref_out_temp

            if comp == "Evaporator":
                ref_in_temp = float(row["Ref_Temp_In_F"])
                if ref_in_temp < min_evap_temp:
                    min_evap_temp = ref_in_temp

    # Print the summary
    print(f"\n  📊 Total Records     : {total_rows}")
    print(f"  📊 Total Cycles      : {total_rows // 4}")
    print()
    print("  Component Breakdown:")
    for comp, count in components_seen.items():
        print(f"    {comp:<25s} : {count} records")

    print()
    print(f"  🔥 Max Discharge Temp : {max_discharge_temp:.1f} °F"
          f"  {'⚠️  HIGH!' if max_discharge_temp > 200 else '✅ Normal'}")
    print(f"  ❄️  Min Evaporator In  : {min_evap_temp:.1f} °F"
          f"  {'⚠️  Freezing risk!' if min_evap_temp < 32 else '✅ Normal'}")
    print()


def print_raw_csv(csv_path: str, max_rows: int = 12) -> None:
    """
    Print the first N rows of the CSV in a formatted table.

    PYTHON LESSON:
      csv.reader returns each row as a list of strings (no dict keys).
      This is simpler but you have to track column positions yourself.
    """
    print("┌" + "─" * 58 + "┐")
    print("│  RAW CSV PREVIEW (first rows)                            │")
    print("└" + "─" * 58 + "┘")

    with open(csv_path, "r", newline="") as csv_file:
        reader = csv.reader(csv_file)

        for i, row in enumerate(reader):
            if i == 0:
                # Header row — print in caps
                print(f"  {'  |  '.join(row[:5])}  ...")
                print(f"  {'─' * 55}")
            elif i <= max_rows:
                print(f"  {'  |  '.join(str(v)[:12] for v in row[:5])}  ...")
            else:
                remaining = total_rows_count(csv_path) - max_rows
                print(f"  ... and {remaining} more rows")
                break
    print()


def total_rows_count(csv_path: str) -> int:
    """Count total data rows (excluding header) in a CSV file."""
    with open(csv_path, "r") as f:
        return sum(1 for _ in f) - 1  # -1 for header


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Output file path — same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_output = os.path.join(script_dir, "hvac_diagnostic_log.csv")

    print("=" * 60)
    print(" EXERCISE 03 — CSV Diagnostic Logging")
    print("=" * 60)
    print()

    # PHASE 1: Run the cycle and log to CSV
    print("  PHASE 1: Running AC cycle with logging...")
    print("  " + "─" * 50)
    final_temp = run_and_log_cycle(
        room_temp_f=78.0,
        outdoor_temp_f=85.0,
        target_temp_f=72.0,
        csv_path=csv_output
    )

    # PHASE 2: Read the CSV back and analyze
    print("  PHASE 2: Reading and analyzing the log...")
    print("  " + "─" * 50)
    read_and_summarize(csv_output)

    # PHASE 3: Show raw CSV preview
    print("  PHASE 3: Raw CSV preview...")
    print("  " + "─" * 50)
    print_raw_csv(csv_output)

    print("=" * 60)
    print(" EXERCISE 03 COMPLETE")
    print("=" * 60)
    print(f"""
 OUTPUT FILE: {csv_output}

 WHAT YOU LEARNED:
   Python — import csv, context managers (with open), csv.DictWriter,
            csv.DictReader, csv.reader, file modes ('w', 'r'),
            newline='' for CSV, os.path, dict.get(), enumerate()

   HVAC  — Diagnostic data logging, component-by-component tracking,
           discharge temperature analysis, evaporator temp monitoring,
           data-driven troubleshooting workflow

 NEXT: Exercise 04 — OOP (Robot + AirConditioner classes)
""")
