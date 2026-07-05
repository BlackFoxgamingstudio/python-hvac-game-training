#!/usr/bin/env python3
"""
=============================================================================
 EXERCISE 01 — Variables & Types: Reading the World Like a Sensor
=============================================================================

 PYTHON CONCEPTS: variables, int, float, str, bool, f-strings, type
                  conversion, math operators, if/elif/else, while loops

 HVAC CONCEPTS:   temperature scales (°F / °C), pressure readings (PSI),
                  thermostat set-point logic, cooling cycles

 GOAL: You are a technician's digital clipboard.  Every value you store
       is a reading from a real piece of equipment on a rooftop unit.
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — VARIABLES: Storing Sensor Readings
# ─────────────────────────────────────────────────────────────────────────────
# In Python, a variable is just a label stuck on a value.
# In HVAC, a sensor does exactly the same thing — it reads a physical
# quantity and labels it so the controller can use it.

# int  — whole numbers, perfect for counting compressor cycles
compressor_cycles = 47          # How many times the compressor kicked on today

# float — decimal numbers, how most sensors actually report
supply_air_temp_f = 55.4        # Temperature of air leaving the evaporator (°F)
return_air_temp_f = 74.8        # Temperature of air coming back from the room (°F)
outdoor_temp_f = 95.2           # Outside ambient temperature (°F)
suction_pressure_psi = 68.5     # Low-side pressure at compressor inlet (PSI)
discharge_pressure_psi = 235.0  # High-side pressure at compressor outlet (PSI)

# str  — text strings, for labeling and logging
unit_id = "RTU-07"              # Rooftop unit identification tag
refrigerant_type = "R-410A"     # The refrigerant charged in this system

# bool — True/False, like a relay: it's either energized or it's not
compressor_running = True       # Is the compressor contactor pulled in?
fan_running = True              # Is the supply fan on?
defrost_mode = False            # Is the unit running a defrost cycle?

print("=" * 60)
print(" SECTION 1 — Current Sensor Readings")
print("=" * 60)

# f-strings let us embed variables directly inside text.
# Think of them as a technician's field report template.
print(f"  Unit ID           : {unit_id}")
print(f"  Refrigerant       : {refrigerant_type}")
print(f"  Outdoor Temp      : {outdoor_temp_f} °F")
print(f"  Return Air Temp   : {return_air_temp_f} °F")
print(f"  Supply Air Temp   : {supply_air_temp_f} °F")
print(f"  Suction Pressure  : {suction_pressure_psi} PSI")
print(f"  Discharge Pressure: {discharge_pressure_psi} PSI")
print(f"  Compressor ON?    : {compressor_running}")
print(f"  Fan ON?           : {fan_running}")
print(f"  Defrost Mode?     : {defrost_mode}")
print(f"  Compressor Cycles : {compressor_cycles}")
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — TYPE CONVERSION: Fahrenheit ↔ Celsius
# ─────────────────────────────────────────────────────────────────────────────
# HVAC in the US uses Fahrenheit; most engineering references use Celsius.
# A technician needs both.  Python makes the conversion trivial.
#
# Formula:  °C = (°F − 32) × 5/9
#           °F = (°C × 9/5) + 32

def fahrenheit_to_celsius(f: float) -> float:
    """Convert Fahrenheit to Celsius — the universal HVAC math."""
    return (f - 32) * 5 / 9

def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (c * 9 / 5) + 32

print("=" * 60)
print(" SECTION 2 — Temperature Conversions")
print("=" * 60)

outdoor_temp_c = fahrenheit_to_celsius(outdoor_temp_f)
supply_air_temp_c = fahrenheit_to_celsius(supply_air_temp_f)

# round() controls decimal places — sensors typically report 1 decimal
print(f"  Outdoor : {outdoor_temp_f} °F  →  {round(outdoor_temp_c, 1)} °C")
print(f"  Supply  : {supply_air_temp_f} °F  →  {round(supply_air_temp_c, 1)} °C")

# type() tells you what kind of data you're holding
print(f"\n  type(outdoor_temp_f)   = {type(outdoor_temp_f)}")   # <class 'float'>
print(f"  type(compressor_cycles) = {type(compressor_cycles)}") # <class 'int'>
print(f"  type(unit_id)           = {type(unit_id)}")           # <class 'str'>
print(f"  type(compressor_running)= {type(compressor_running)}")# <class 'bool'>
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — MATH OPERATORS: HVAC Calculations
# ─────────────────────────────────────────────────────────────────────────────
# Every HVAC tech calculates Delta-T (temperature difference across the coil).
# If Delta-T is too low, airflow may be restricted (dirty filter).
# If Delta-T is too high, refrigerant charge may be low.

delta_t = return_air_temp_f - supply_air_temp_f  # Expected: 15-22 °F for cooling
print("=" * 60)
print(" SECTION 3 — HVAC Math")
print("=" * 60)
print(f"  Delta-T (Return − Supply) = {return_air_temp_f} − {supply_air_temp_f}"
      f" = {round(delta_t, 1)} °F")

# Superheat: how much the refrigerant is heated above its boiling point
# at suction pressure.  For R-410A at ~68 PSI suction, saturation ≈ 34°F.
saturation_temp_f = 34.0  # Looked up from a PT chart for R-410A @ 68 PSI
suction_line_temp_f = 44.0  # Measured with a clamp thermometer
superheat = suction_line_temp_f - saturation_temp_f
print(f"  Superheat = {suction_line_temp_f} − {saturation_temp_f}"
      f" = {round(superheat, 1)} °F  (target: 8-14 °F)")

# Integer division (//) and modulus (%) — how many full hours of runtime?
runtime_minutes = 487
full_hours = runtime_minutes // 60   # integer division → 8
leftover_mins = runtime_minutes % 60 # modulus → 7
print(f"  Runtime: {runtime_minutes} min = {full_hours}h {leftover_mins}m")

# Exponent (**) — BTU estimation (simplified)
# BTU/hr ≈ 1.08 × CFM × Delta_T  (sensible heat formula)
cfm = 1200  # Cubic feet per minute of airflow
btu_hr = 1.08 * cfm * delta_t
print(f"  Estimated Sensible Load = 1.08 × {cfm} × {round(delta_t,1)}"
      f" = {round(btu_hr, 0)} BTU/hr")
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — IF / ELIF / ELSE: Thermostat Logic
# ─────────────────────────────────────────────────────────────────────────────
# A thermostat is just a chain of if/elif/else decisions.
# The set-point is the target.  The deadband prevents short-cycling.

set_point_f = 72.0   # Desired room temperature
deadband = 1.0        # Don't turn on/off within ±1°F of set-point
room_temp_f = 74.8    # Current room temperature (same as return air)

print("=" * 60)
print(" SECTION 4 — Thermostat Decision Logic")
print("=" * 60)
print(f"  Set-point  : {set_point_f} °F")
print(f"  Deadband   : ±{deadband} °F")
print(f"  Room Temp  : {room_temp_f} °F")

if room_temp_f > set_point_f + deadband:
    # Room is too warm — call for cooling
    action = "COOLING ON — room is above set-point + deadband"
elif room_temp_f < set_point_f - deadband:
    # Room is too cold — in cooling mode, just shut off (no heat call here)
    action = "SYSTEM OFF — room is below set-point − deadband"
else:
    # Room is within the deadband — maintain current state
    action = "DEADBAND — no change, system holds current state"

print(f"  Decision   : {action}")
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — WHILE LOOP: Cooling Countdown Simulation
# ─────────────────────────────────────────────────────────────────────────────
# A while loop keeps running as long as its condition is True.
# Here we simulate cooling the room from 78°F down to the 72°F set-point.
# Each "cycle" drops the temp by a small amount (like a real AC running).

print("=" * 60)
print(" SECTION 5 — Cooling Cycle Simulation (while loop)")
print("=" * 60)

sim_room_temp = 78.0          # Starting room temperature
cooling_rate = 0.5            # Degrees dropped per cycle
cycle_count = 0               # Cycle counter
max_cycles = 100              # Safety limit — prevents infinite loop

print(f"  Target: {set_point_f} °F | Starting at {sim_room_temp} °F")
print(f"  Cooling rate: {cooling_rate} °F per cycle")
print()

while sim_room_temp > set_point_f and cycle_count < max_cycles:
    # Each pass through the loop = one cooling cycle
    cycle_count += 1
    sim_room_temp -= cooling_rate
    sim_room_temp = round(sim_room_temp, 1)  # Avoid floating-point drift

    # Status update every 3 cycles (or the final cycle)
    if cycle_count % 3 == 0 or sim_room_temp <= set_point_f:
        status = "✓ TARGET REACHED" if sim_room_temp <= set_point_f else "cooling..."
        print(f"    Cycle {cycle_count:>3}: Room = {sim_room_temp:>5.1f} °F  [{status}]")

print()
print(f"  Cooling complete in {cycle_count} cycles.")
print(f"  Final room temperature: {sim_room_temp} °F")
print()


# ─────────────────────────────────────────────────────────────────────────────
# WRAP-UP
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print(" EXERCISE 01 COMPLETE")
print("=" * 60)
print("""
 WHAT YOU LEARNED:
   Python — variables, int/float/str/bool, f-strings, type(),
            math operators (+, -, *, /, //, %, **), if/elif/else,
            while loops, round(), comparison operators

   HVAC  — sensor readings, Delta-T, superheat, BTU estimation,
           thermostat set-point logic, deadband, cooling cycles,
           Fahrenheit ↔ Celsius conversion, pressure-temperature
           relationship (PT chart), compressor runtime tracking

 NEXT: Exercise 02 — Functions (the refrigeration cycle as code)
""")
