#!/usr/bin/env python3
"""
=============================================================================
 EXERCISE 02 — Functions: The Refrigeration Cycle as Code
=============================================================================

 PYTHON CONCEPTS: def, parameters, return values, default arguments,
                  docstrings, dictionaries as structured data, calling
                  functions in sequence, print formatting

 HVAC CONCEPTS:   The 4 components of a vapor-compression refrigeration
                  cycle — evaporator, compressor, condenser, expansion
                  valve — and how refrigerant changes state through each.

 GOAL: Model a complete AC cooling cycle.  Each component is a function
       that takes in refrigerant state and returns the new state.

 WHY FUNCTIONS?
   A function is a reusable block of code — just like a component in an
   HVAC system is a reusable piece of equipment.  You can swap a
   compressor model (change the function internals) without rewiring the
   whole system (rewriting the rest of the program).
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — HELPER UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def f_to_c(f: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return round((f - 32) * 5 / 9, 1)


def print_state(label: str, state: dict) -> None:
    """
    Pretty-print a refrigerant state dictionary.

    PYTHON LESSON:
      - 'dict' is Python's key-value store (like a technician's log sheet).
      - We access values with state["key"].
      - '-> None' means this function doesn't return a value; it just prints.

    HVAC LESSON:
      At every point in the cycle, refrigerant has four measurable properties:
        1. Temperature  — how hot or cold (°F)
        2. Pressure     — how compressed (PSI)
        3. Phase/State  — liquid, vapor, or a mix (two-phase)
        4. Enthalpy     — total heat energy content (BTU/lb)
    """
    print(f"  ┌── {label}")
    print(f"  │  Temp     : {state['temp_f']:>7.1f} °F  ({f_to_c(state['temp_f'])} °C)")
    print(f"  │  Pressure : {state['pressure_psi']:>7.1f} PSI")
    print(f"  │  Phase    : {state['phase']}")
    print(f"  │  Enthalpy : {state['enthalpy_btu_lb']:>7.1f} BTU/lb")
    print(f"  └{'─' * 45}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — THE FOUR COMPONENTS (each is a function)
# ─────────────────────────────────────────────────────────────────────────────

def evaporator(ref_in: dict, room_temp_f: float) -> tuple:
    """
    =========================================================================
    EVAPORATOR — The Indoor Coil (where the magic happens)
    =========================================================================

    HVAC DEEP DIVE:
      The evaporator is a heat exchanger INSIDE the building.  Cold, low-
      pressure liquid refrigerant enters the coil.  Warm room air blows
      across the coil.  The refrigerant ABSORBS heat from the air and
      BOILS (evaporates) — changing from liquid to vapor.

      This is why it's called an "evaporator": the refrigerant evaporates.

      Key physics:
        - Latent heat of vaporization: the refrigerant absorbs a LOT of
          energy when it changes phase, without its temperature rising much.
        - The room air loses that heat and comes out cooler (supply air).
        - By the exit of the evaporator, the refrigerant should be fully
          vaporized, plus a little extra heat (superheat) to protect the
          compressor from liquid slugging.

    PYTHON LESSON:
      - This function takes two parameters: ref_in (a dict) and room_temp_f.
      - It returns a tuple: (new_ref_state_dict, new_room_temp).
      - We build a NEW dict instead of modifying the input (immutability).
    """
    # Refrigerant absorbs heat from the room → it warms up and vaporizes
    # Superheat of ~10°F above the evaporating temperature
    evap_temp = ref_in["temp_f"]  # Boiling point at this pressure
    superheat = 10.0

    ref_out = {
        "temp_f": evap_temp + superheat,        # Slightly above boiling
        "pressure_psi": ref_in["pressure_psi"],  # Pressure stays constant in evaporator
        "phase": "Superheated Vapor",            # Fully boiled + extra heat
        "enthalpy_btu_lb": ref_in["enthalpy_btu_lb"] + 70.0  # Absorbed ~70 BTU/lb
    }

    # Room air is cooled: the supply air comes out ~18-22°F below return air
    delta_t = 19.0  # Typical cooling delta-T
    new_room_temp = room_temp_f - delta_t * 0.15  # Simplified: small step per cycle

    return ref_out, round(new_room_temp, 1)


def compressor(ref_in: dict) -> dict:
    """
    =========================================================================
    COMPRESSOR — The Heart of the System
    =========================================================================

    HVAC DEEP DIVE:
      The compressor is a mechanical pump that squeezes low-pressure vapor
      into high-pressure, high-temperature vapor.  It's the component that
      does the WORK — it's powered by an electric motor.

      Why compress?  We need the refrigerant to be HOTTER than the outdoor
      air so it can REJECT its heat outside.  If the outdoor air is 95°F,
      the refrigerant must be even hotter (say 140-170°F) to push heat
      out through the condenser.

      Types of compressors:
        - Scroll: two interlocking spirals (most common in residential AC)
        - Reciprocating: pistons in cylinders (like a car engine)
        - Screw: rotating helical rotors (large commercial)
        - Centrifugal: impeller spins refrigerant (big chillers)

      The compression ratio (discharge pressure / suction pressure)
      determines efficiency and discharge temperature.

    PYTHON LESSON:
      - This function takes ONE parameter (ref_in) and returns ONE value.
      - Default arguments aren't used here, but we'll see them in ex04.
    """
    # Compression raises both temperature and pressure dramatically
    compression_ratio = 3.4  # Typical for R-410A residential

    ref_out = {
        "temp_f": ref_in["temp_f"] + 120.0,      # Hot gas! ~160-180°F
        "pressure_psi": ref_in["pressure_psi"] * compression_ratio,  # ~230+ PSI
        "phase": "Superheated Vapor (Hot Gas)",   # Still vapor, but very hot
        "enthalpy_btu_lb": ref_in["enthalpy_btu_lb"] + 25.0  # Work added
    }

    return ref_out


def condenser(ref_in: dict, outdoor_temp_f: float) -> dict:
    """
    =========================================================================
    CONDENSER — The Outdoor Coil (heat rejection)
    =========================================================================

    HVAC DEEP DIVE:
      The condenser is a heat exchanger OUTSIDE the building.  Hot, high-
      pressure vapor enters.  The outdoor fan blows ambient air across the
      coil.  The refrigerant REJECTS its heat to the outdoor air and
      CONDENSES — changing from vapor to liquid.

      Three zones in the condenser (in order):
        1. De-superheating: vapor cools from discharge temp to saturation
        2. Condensing: vapor changes to liquid at constant temperature
        3. Subcooling: liquid cools a few degrees below saturation
           (subcooling of 8-12°F protects the expansion valve from flash gas)

      Subcooling is critical: if there's not enough, the expansion valve
      gets flash gas and can't meter properly.  Too much subcooling means
      refrigerant is backing up — possible overcharge.

    PYTHON LESSON:
      - outdoor_temp_f is used to calculate realistic condenser output.
    """
    # Refrigerant condenses and subcools
    subcooling = 10.0  # Degrees below condensing temperature

    # Condensing happens at the saturation temperature for the high-side pressure
    # For R-410A at ~230 PSI, saturation ≈ 105°F
    condensing_sat_temp = 105.0

    ref_out = {
        "temp_f": condensing_sat_temp - subcooling,   # Subcooled liquid ~95°F
        "pressure_psi": ref_in["pressure_psi"],        # Pressure constant through condenser
        "phase": "Subcooled Liquid",                   # Fully liquid + subcooled
        "enthalpy_btu_lb": ref_in["enthalpy_btu_lb"] - 85.0  # Rejected ~85 BTU/lb
    }

    return ref_out


def expansion_valve(ref_in: dict) -> dict:
    """
    =========================================================================
    EXPANSION VALVE (TXV / EEV) — The Metering Device
    =========================================================================

    HVAC DEEP DIVE:
      The expansion valve (also called metering device) is a restriction
      that drops the pressure of the liquid refrigerant.  When pressure
      drops, the boiling point drops too — and some of the liquid instantly
      "flashes" into vapor (flash gas).  This rapid expansion causes a
      dramatic temperature drop.

      Types of metering devices:
        - TXV (Thermostatic Expansion Valve): uses a sensing bulb to
          maintain constant superheat at evaporator outlet
        - EEV (Electronic Expansion Valve): stepper-motor controlled,
          used in variable-speed / inverter systems
        - Fixed orifice (piston/cap tube): simplest, sized for one condition

      The expansion is nearly isenthalpic (constant enthalpy) — no heat
      is added or removed; only pressure and temperature change.

    PYTHON LESSON:
      - Notice the enthalpy barely changes — this models the real physics.
      - The returned dict represents the refrigerant entering the evaporator.
    """
    # Pressure drops dramatically; temperature follows
    ref_out = {
        "temp_f": 34.0,                              # Cold! Near evaporating temp
        "pressure_psi": 68.0,                         # Low-side pressure
        "phase": "Two-Phase (Liquid + Vapor Mix)",    # Partially flashed
        "enthalpy_btu_lb": ref_in["enthalpy_btu_lb"] - 2.0  # Nearly isenthalpic
    }

    return ref_out


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — RUN THE COMPLETE AC CYCLE
# ─────────────────────────────────────────────────────────────────────────────

def run_ac_cycle(room_temp_f: float, outdoor_temp_f: float,
                 target_temp_f: float = 72.0, max_cycles: int = 50) -> float:
    """
    Run a complete air conditioning simulation.

    PYTHON LESSON:
      - 'target_temp_f = 72.0' is a DEFAULT ARGUMENT.  If the caller
        doesn't provide a value, Python uses 72.0 automatically.
      - The function returns the final room temperature (a float).

    HVAC LESSON:
      The system runs in cycles.  Each cycle, the room loses a little heat
      to the evaporator.  When the room hits the target (set-point), the
      thermostat tells the compressor to stop.
    """
    print("╔" + "═" * 58 + "╗")
    print("║   REFRIGERATION CYCLE SIMULATION                         ║")
    print("╚" + "═" * 58 + "╝")
    print(f"  Room Temperature : {room_temp_f} °F")
    print(f"  Outdoor Temp     : {outdoor_temp_f} °F")
    print(f"  Target (Set-point): {target_temp_f} °F")
    print()

    cycle = 0

    while room_temp_f > target_temp_f and cycle < max_cycles:
        cycle += 1
        print(f"  ━━━ CYCLE {cycle} ━━━  Room: {room_temp_f:.1f} °F")

        # STEP 1: Start with refrigerant leaving the expansion valve
        # (entering the evaporator as a cold two-phase mix)
        ref_state = {
            "temp_f": 34.0,
            "pressure_psi": 68.0,
            "phase": "Two-Phase Mix",
            "enthalpy_btu_lb": 45.0
        }
        print_state("① Entering Evaporator", ref_state)

        # STEP 2: Evaporator — absorb heat from room
        ref_state, room_temp_f = evaporator(ref_state, room_temp_f)
        print_state("② Leaving Evaporator (→ Compressor)", ref_state)

        # STEP 3: Compressor — pump it up
        ref_state = compressor(ref_state)
        print_state("③ Leaving Compressor (→ Condenser)", ref_state)

        # STEP 4: Condenser — reject heat outdoors
        ref_state = condenser(ref_state, outdoor_temp_f)
        print_state("④ Leaving Condenser (→ Expansion Valve)", ref_state)

        # STEP 5: Expansion valve — meter & drop pressure
        ref_state = expansion_valve(ref_state)
        print_state("⑤ Leaving Expansion Valve (→ Evaporator)", ref_state)

        print(f"  → Room temp after cycle {cycle}: {room_temp_f:.1f} °F")
        print()

    # Report results
    if room_temp_f <= target_temp_f:
        print(f"  ✅ Target reached! Room at {room_temp_f:.1f} °F after {cycle} cycles.")
    else:
        print(f"  ⚠️  Max cycles reached. Room at {room_temp_f:.1f} °F.")

    return room_temp_f


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Scenario: It's a hot day. Room is 78°F, outdoor is 85°F, target is 72°F.
    final_temp = run_ac_cycle(
        room_temp_f=78.0,
        outdoor_temp_f=85.0,
        target_temp_f=72.0
    )

    print()
    print("=" * 60)
    print(" EXERCISE 02 COMPLETE")
    print("=" * 60)
    print("""
 WHAT YOU LEARNED:
   Python — def, parameters, return, default arguments, tuple unpacking,
            docstrings, dictionaries, calling functions in sequence,
            building data pipelines with functions, __name__ == "__main__"

   HVAC  — The 4-component vapor-compression refrigeration cycle:
            Evaporator (absorb heat), Compressor (do work),
            Condenser (reject heat), Expansion Valve (meter flow).
            Superheat, subcooling, compression ratio, PT relationship,
            flash gas, phases of refrigerant, enthalpy.

 NEXT: Exercise 03 — CSV Logging (recording diagnostic data to files)
""")
