#!/usr/bin/env python3
"""
=============================================================================
 EXERCISE 04 — OOP: Robot with Air Conditioning
=============================================================================

 PYTHON CONCEPTS: classes, __init__, self, instance variables, methods,
                  composition (object owns another object), __str__,
                  encapsulation, class vs instance, property access

 HVAC CONCEPTS:   Portable/self-contained AC systems, heat generation
                  from mechanical work, thermal management, diagnostic
                  logging from equipment controllers

 GOAL: Build a Robot class that HAS an AirConditioner (composition).
       The robot walks, generates heat, and uses its internal AC to
       cool itself.  All operations are logged to CSV.

 WHY OOP?
   Object-Oriented Programming models the real world.  An HVAC system
   IS a collection of objects: a thermostat object, a compressor object,
   a sensor object.  Each has its own state (data) and behavior (methods).
   OOP lets us write code that mirrors this physical reality.
=============================================================================
"""

import csv
import os


# ─────────────────────────────────────────────────────────────────────────────
# CLASS 1 — AirConditioner
# ─────────────────────────────────────────────────────────────────────────────

class AirConditioner:
    """
    A self-contained air conditioning unit.

    PYTHON LESSON — CLASSES & __init__:
      A class is a BLUEPRINT.  When you call AirConditioner(), Python:
        1. Creates a new, empty object in memory
        2. Calls __init__(self) to set up that object's initial state
        3. Returns the fully initialized object

      'self' is a reference to THE SPECIFIC object being created.
      Think of 'self' as "this particular unit" — when you have 10 AC
      units on a building, 'self' is how each unit knows its OWN data.

    HVAC LESSON:
      This models a packaged AC unit.  It has its own compressor,
      evaporator, condenser — all self-contained.  Each unit tracks
      its own cycle count, runtime, and refrigerant state.
    """

    def __init__(self, unit_id: str = "AC-001", capacity_btu: int = 12000):
        """
        Initialize the AC unit.

        PYTHON LESSON — self.variable:
          Variables prefixed with 'self.' belong to THIS specific instance.
          If you create two ACs, each has its OWN set of these variables.

          self.compressor_on   → THIS unit's compressor state
          self.cycle_count     → THIS unit's cycle count

        HVAC LESSON:
          capacity_btu = 12000 means this is a "1 ton" unit.
          (1 ton of cooling = 12,000 BTU/hr)
        """
        # Identity
        self.unit_id = unit_id
        self.capacity_btu = capacity_btu

        # Operating state
        self.compressor_on = False
        self.cycle_count = 0
        self.total_runtime_cycles = 0

        # Refrigerant state (simplified)
        self.refrigerant_temp_f = 75.0      # Ambient when off
        self.refrigerant_pressure_psi = 0.0 # No pressure when off
        self.refrigerant_phase = "Idle"

        # Performance
        self.last_cooling_amount = 0.0

    def run_cooling_cycle(self, current_temp_f: float,
                          outdoor_temp_f: float = 85.0) -> float:
        """
        Run one complete cooling cycle and return the new temperature.

        PYTHON LESSON — METHODS:
          A method is a function that belongs to a class.  It always
          takes 'self' as its first parameter — Python passes this
          automatically when you call robot.ac.run_cooling_cycle(temp).

          The caller writes:  ac.run_cooling_cycle(80.0)
          Python executes:    AirConditioner.run_cooling_cycle(ac, 80.0)

        HVAC LESSON:
          Each cycle cools the air by a certain amount (delta-T).
          The actual cooling depends on capacity, airflow, and conditions.
        """
        self.compressor_on = True
        self.cycle_count += 1
        self.total_runtime_cycles += 1

        # ── Simulate the 4-component cycle ──

        # 1. Expansion valve: drop pressure, cool the refrigerant
        self.refrigerant_temp_f = 34.0
        self.refrigerant_pressure_psi = 68.0
        self.refrigerant_phase = "Two-Phase Mix"

        # 2. Evaporator: absorb heat from the space
        cooling_delta = 2.85  # Degrees cooled per cycle
        new_temp = current_temp_f - cooling_delta
        self.refrigerant_temp_f = 44.0
        self.refrigerant_pressure_psi = 68.0
        self.refrigerant_phase = "Superheated Vapor"

        # 3. Compressor: pump it up
        self.refrigerant_temp_f = 164.0
        self.refrigerant_pressure_psi = 231.2
        self.refrigerant_phase = "Hot Gas"

        # 4. Condenser: reject heat outside
        self.refrigerant_temp_f = 95.0
        self.refrigerant_pressure_psi = 231.2
        self.refrigerant_phase = "Subcooled Liquid"

        # Shut down compressor
        self.compressor_on = False
        self.last_cooling_amount = cooling_delta

        return round(new_temp, 1)

    def get_status(self) -> dict:
        """Return current AC status as a dictionary."""
        return {
            "unit_id": self.unit_id,
            "compressor_on": self.compressor_on,
            "cycles": self.cycle_count,
            "ref_temp_f": self.refrigerant_temp_f,
            "ref_pressure_psi": self.refrigerant_pressure_psi,
            "ref_phase": self.refrigerant_phase,
            "last_cooling": self.last_cooling_amount,
        }

    def __str__(self) -> str:
        """
        String representation of the AC unit.

        PYTHON LESSON — __str__:
          When you print(ac) or str(ac), Python calls this method.
          It's like a name badge for the object.
        """
        status = "ON" if self.compressor_on else "OFF"
        return (f"[{self.unit_id}] {self.capacity_btu} BTU/hr | "
                f"Compressor: {status} | Cycles: {self.cycle_count}")


# ─────────────────────────────────────────────────────────────────────────────
# CLASS 2 — Robot
# ─────────────────────────────────────────────────────────────────────────────

class Robot:
    """
    A walking robot with an internal air conditioning system.

    PYTHON LESSON — COMPOSITION:
      Composition means "has-a" relationship.  The Robot HAS an
      AirConditioner.  This is different from inheritance ("is-a").

      In __init__, we create: self.internal_ac = AirConditioner(...)
      The AC object LIVES INSIDE the Robot object.  The robot can
      call self.internal_ac.run_cooling_cycle() anytime.

    HVAC LESSON:
      Think of this like a data center server rack.  The server (robot)
      generates heat from computation and mechanical work.  It has a
      dedicated cooling unit (the AC) to manage its temperature.
      If the cooling fails, the server overheats and shuts down.
    """

    # Class variable — shared by ALL robots (like a spec sheet)
    OVERHEAT_THRESHOLD_F = 150.0  # Emergency shutdown temperature
    OPTIMAL_TEMP_F = 98.6         # Ideal operating temperature

    def __init__(self, name: str, model: str = "HVAC-BOT v1"):
        """
        Initialize the robot.

        PYTHON LESSON — COMPOSITION IN ACTION:
          self.internal_ac = AirConditioner(unit_id=f"{name}-AC")
          This creates an AirConditioner object and stores it as part
          of this robot.  The robot OWNS the AC.
        """
        # Identity
        self.name = name
        self.model = model

        # Physical state
        self.core_temp_f = 98.6    # Starting temperature (like body temp)
        self.position_m = 0.0      # Current position in meters
        self.total_distance_m = 0.0
        self.battery_pct = 100.0

        # Movement log
        self.movement_log = []     # List of (distance, temp_after) tuples

        # ── COMPOSITION: Robot HAS an AirConditioner ──
        self.internal_ac = AirConditioner(
            unit_id=f"{name}-AC",
            capacity_btu=6000  # Small unit for a robot
        )

    def walk(self, meters: float) -> None:
        """
        Move the robot forward.  Walking generates heat!

        PYTHON LESSON:
          This method modifies self.position_m, self.total_distance_m,
          and self.core_temp_f — all instance variables.

        HVAC LESSON:
          Mechanical work always generates waste heat (2nd Law of
          Thermodynamics).  Motors, compressors, pumps — they all
          produce heat as a byproduct.  The harder a system works,
          the more cooling it needs.
        """
        # Heat generated: roughly 0.4°F per meter walked
        heat_per_meter = 0.4
        heat_generated = meters * heat_per_meter

        self.position_m += meters
        self.total_distance_m += meters
        self.core_temp_f += heat_generated
        self.core_temp_f = round(self.core_temp_f, 1)
        self.battery_pct = max(0, self.battery_pct - meters * 0.3)

        # Log this movement
        self.movement_log.append((meters, self.core_temp_f))

        # Status emoji based on temperature
        if self.core_temp_f > self.OVERHEAT_THRESHOLD_F:
            status = "🔥 OVERHEAT WARNING"
        elif self.core_temp_f > 120:
            status = "🌡️  Running warm"
        else:
            status = "✅ Normal"

        print(f"  🤖 {self.name} walked {meters}m | "
              f"Position: {self.position_m}m | "
              f"Core: {self.core_temp_f}°F | {status}")

    def run_climate_control(self, outdoor_temp_f: float = 85.0,
                            csv_filename: str = None) -> None:
        """
        Activate the internal AC to cool the robot back to optimal temp.

        PYTHON LESSON — METHOD CALLING ANOTHER OBJECT'S METHOD:
          self.internal_ac.run_cooling_cycle(self.core_temp_f)
          The robot calls ITS AC's cooling method, passing ITS temp.

        HVAC LESSON:
          This is exactly how a building automation system (BAS) works.
          The controller (robot brain) reads a sensor (core_temp_f),
          compares it to a set-point (OPTIMAL_TEMP_F), and tells the
          HVAC equipment (internal_ac) to run until satisfied.
        """
        print()
        print(f"  ❄️  {self.name} activating climate control...")
        print(f"     Core temp: {self.core_temp_f}°F → Target: {self.OPTIMAL_TEMP_F}°F")

        cycles = 0
        log_rows = []  # Collect rows for CSV

        while self.core_temp_f > self.OPTIMAL_TEMP_F:
            cycles += 1
            temp_before = self.core_temp_f
            self.core_temp_f = self.internal_ac.run_cooling_cycle(
                self.core_temp_f, outdoor_temp_f
            )

            log_rows.append({
                "Cycle": cycles,
                "Temp_Before_F": temp_before,
                "Temp_After_F": self.core_temp_f,
                "Outdoor_F": outdoor_temp_f,
                "AC_Cycles_Total": self.internal_ac.cycle_count,
            })

            print(f"     Cycle {cycles}: {temp_before:.1f}°F → "
                  f"{self.core_temp_f:.1f}°F")

        print(f"  ✅ Cooling complete! Core: {self.core_temp_f}°F "
              f"({cycles} cycles)")

        # Write CSV log if filename provided
        if csv_filename and log_rows:
            self._write_csv_log(csv_filename, log_rows)

    def _write_csv_log(self, filename: str, rows: list) -> None:
        """
        Write cooling log to CSV.

        PYTHON LESSON — PRIVATE METHODS:
          The underscore prefix (_write_csv_log) is a Python convention
          meaning "this method is internal — don't call it from outside."
          It's not enforced by Python, but it signals intent to other devs.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)

        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        print(f"  📝 Log saved: {filepath}")

    def status_report(self) -> None:
        """Print a full status report for the robot."""
        print()
        print("╔" + "═" * 50 + "╗")
        print(f"║  STATUS REPORT: {self.name:<33s}║")
        print("╠" + "═" * 50 + "╣")
        print(f"║  Model          : {self.model:<31s}║")
        print(f"║  Core Temp      : {self.core_temp_f:<6.1f}°F{' ' * 22}║")
        print(f"║  Position       : {self.position_m:<6.1f} m{' ' * 21}║")
        print(f"║  Total Distance : {self.total_distance_m:<6.1f} m{' ' * 21}║")
        print(f"║  Battery        : {self.battery_pct:<6.1f}%{' ' * 21}║")
        print(f"║  AC Unit        : {str(self.internal_ac):<31s}║")
        print("╚" + "═" * 50 + "╝")

    def __str__(self) -> str:
        return (f"Robot({self.name}, {self.core_temp_f}°F, "
                f"pos={self.position_m}m)")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION — The Robot's Mission
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print(" EXERCISE 04 — OOP: Robot + AirConditioner")
    print("=" * 60)
    print()

    # ── Create the robot ──
    # This ONE line creates a Robot AND its internal AirConditioner
    bot = Robot(name="Atlas", model="HVAC-BOT MK-II")

    print(f"  Created: {bot}")
    print(f"  Internal AC: {bot.internal_ac}")
    print()

    # ── Mission Sequence ──
    print("  ── MISSION: Navigate the facility ──")
    print()

    # Walk 30 meters (generates 12°F of heat)
    bot.walk(30)

    # Walk another 25 meters (more heat!)
    bot.walk(25)

    # Status check — robot is getting warm
    bot.status_report()

    # Cool down! Run climate control with CSV logging
    bot.run_climate_control(
        outdoor_temp_f=85.0,
        csv_filename="robot_cooling_log.csv"
    )

    # Walk 10 more meters
    print()
    bot.walk(10)

    # Final status
    bot.status_report()

    # ── Show the movement log ──
    print("\n  📋 Movement Log:")
    for i, (dist, temp) in enumerate(bot.movement_log, 1):
        print(f"     {i}. Walked {dist}m → Core: {temp}°F")

    print()
    print("=" * 60)
    print(" EXERCISE 04 COMPLETE")
    print("=" * 60)
    print("""
 WHAT YOU LEARNED:
   Python — class, __init__, self, instance variables, methods,
            composition ("has-a"), __str__, private methods (_prefix),
            class variables vs instance variables, objects owning objects

   HVAC  — Self-contained AC units, heat generation from work,
           thermal management controllers, BAS logic (read sensor →
           compare to set-point → run equipment), cooling cycles

 NEXT: Exercise 05 — Gemini AI Brain (adding intelligence to the robot)
""")
