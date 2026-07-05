"""
=============================================================================
 HVAC System — Game-Integrated Vapor Compression Refrigeration Simulation
=============================================================================

 HVAC CONCEPT: THE REFRIGERATION CYCLE
 
 An air conditioner does NOT create cold. It is a heat pump that moves
 thermal energy from one place (the robot's core) to another (the outdoor
 ambient air). It does this by cycling a chemical refrigerant through
 four stages that change its pressure, temperature, and physical state.

 THE FOUR STAGES:
 ┌──────────────────────────────────────────────────────────────────────┐
 │                                                                      │
 │   [EVAPORATOR] ──→ [COMPRESSOR] ──→ [CONDENSER] ──→ [EXP VALVE]    │
 │        ↑            Cold gas           Hot gas         Hot liquid    │
 │        │            becomes            dumps heat      pressure     │
 │        │            hot gas            becomes         drops,       │
 │        │                               liquid          temp drops   │
 │        └────────────────────────────────────────────────────┘       │
 │                       (Cycle repeats)                                │
 └──────────────────────────────────────────────────────────────────────┘

 PROGRAMMING CONCEPT: REAL-TIME GAME SUBSYSTEM
 
 Unlike the exercise scripts that run the full cycle instantly, this
 version is designed for frame-by-frame updates. The `tick()` method
 is called every game frame with a delta-time (dt) value, allowing
 the HVAC system to simulate gradually over real time.
=============================================================================
"""

import csv
import time


class HVACSystem:
    """
    A vapor compression refrigeration system adapted for real-time game simulation.
    
    OOP CONCEPT: ENCAPSULATION
    All refrigerant state (temperature, pressure, phase) is managed internally.
    The game only needs to call tick() and read the status — it never directly
    manipulates the refrigerant properties.
    """

    def __init__(self, target_temp: float = 72.0):
        """
        Initialize the HVAC system with default parameters.
        
        HVAC CONCEPT: SETPOINT
        The target_temp is the thermostat setpoint — the temperature the system
        tries to maintain. In a real BAS (Building Automation System), this is
        configurable by the operator.
        """
        # --- Thermostat Configuration ---
        self.target_temp = target_temp
        self.deadband = 2.0  # Don't cycle on/off for tiny fluctuations

        # --- Refrigerant State ---
        self.ref_temp = 45.0        # Starting cold temperature (°F)
        self.ref_pressure = "Low"   # "Low" or "High"
        self.ref_state = "Liquid"   # "Liquid", "Gas", or "Saturated"

        # --- Operational State ---
        self.is_running = False
        self.current_stage = "Idle"  # Which component is currently active
        self.total_cycles = 0
        self.stage_index = 0         # 0-3 for the 4 stages
        self.stage_timer = 0.0       # Time spent in current stage
        self.stage_duration = 0.3    # Seconds per stage for visual effect

        # --- Diagnostic Logging ---
        self.log_enabled = False
        self.log_entries = []        # In-memory log buffer
        self.csv_filename = None

        # --- Performance Metrics ---
        self.last_cool_amount = 0.0
        self.efficiency_rating = 1.0  # Degrades with extreme outdoor temps

    # -----------------------------------------------------------------
    #  STAGE 1: EVAPORATOR — Indoor Heat Absorption
    # -----------------------------------------------------------------
    def _evaporator(self, core_temp: float) -> float:
        """
        HVAC CONCEPT: THE EVAPORATOR
        
        Located inside the space being cooled (the robot's core). Cold,
        low-pressure liquid refrigerant enters the evaporator coil. Because
        the robot's core is warmer than the refrigerant, heat naturally
        flows from the core INTO the refrigerant.
        
        As the refrigerant absorbs heat, it reaches its boiling point and
        EVAPORATES — changing from a liquid to a low-pressure gas. This
        phase change is what actually removes the heat.
        
        THERMODYNAMIC FORMULA (simplified):
        Q_absorbed = (T_core - T_refrigerant) × heat_transfer_coefficient
        """
        heat_transfer_coeff = 0.4 * self.efficiency_rating
        heat_absorbed = (core_temp - self.ref_temp) * heat_transfer_coeff
        
        # Refrigerant warms up as it absorbs heat
        self.ref_temp += heat_absorbed
        
        # Core cools down as heat is removed
        new_core_temp = core_temp - (heat_absorbed * 0.5)
        
        # Phase change: liquid → gas (latent heat absorption)
        self.ref_state = "Gas"
        self.current_stage = "Evaporator"
        self.last_cool_amount = heat_absorbed * 0.5
        
        return new_core_temp

    # -----------------------------------------------------------------
    #  STAGE 2: COMPRESSOR — The Heart of the System
    # -----------------------------------------------------------------
    def _compressor(self):
        """
        HVAC CONCEPT: THE COMPRESSOR
        
        The compressor is the MOST CRITICAL component. It takes the low-
        pressure gas from the evaporator and mechanically compresses it.
        
        WHY COMPRESS?
        Compressing a gas packs molecules tighter, which INCREASES both
        pressure and temperature. The refrigerant must be heated ABOVE
        the outdoor temperature, or it won't be able to dump heat outside.
        
        Think of it like squeezing a balloon — the air inside gets warmer.
        
        ENERGY COST: The compressor is the #1 energy consumer in any
        AC system. This is why higher SEER ratings matter — they indicate
        more efficient compression.
        """
        # Mechanical work spikes the temperature
        self.ref_temp += 50.0 * self.efficiency_rating
        
        # Pressure transitions from Low to High
        self.ref_pressure = "High"
        
        # State stays as Gas, but now it's a "superheated" gas
        self.current_stage = "Compressor"

    # -----------------------------------------------------------------
    #  STAGE 3: CONDENSER — Outdoor Heat Rejection
    # -----------------------------------------------------------------
    def _condenser(self, outdoor_temp: float):
        """
        HVAC CONCEPT: THE CONDENSER
        
        Located OUTSIDE. The hot, high-pressure gas enters the condenser
        coil. Because the refrigerant (130°F+) is now MUCH hotter than
        the outdoor air (85-100°F), heat flows OUT of the refrigerant
        into the outdoor air. A condenser fan assists this process.
        
        As the refrigerant loses heat, it cools down and CONDENSES —
        changing from a gas back into a high-pressure liquid.
        
        IMPORTANT: If the outdoor temp is extremely high (like 115°F),
        the temperature differential shrinks, making heat rejection harder.
        This is why AC systems lose efficiency on the hottest days.
        """
        # Heat rejection: energy flows from hot refrigerant to cooler outdoor air
        heat_rejection_coeff = 0.6
        heat_rejected = (self.ref_temp - outdoor_temp) * heat_rejection_coeff
        self.ref_temp -= heat_rejected
        
        # Phase change: gas → liquid (latent heat release)
        self.ref_state = "Liquid"
        self.current_stage = "Condenser"
        
        # Efficiency degrades when outdoor temp is very high
        if outdoor_temp > 100:
            self.efficiency_rating = max(0.5, 1.0 - (outdoor_temp - 100) * 0.01)
        else:
            self.efficiency_rating = 1.0

    # -----------------------------------------------------------------
    #  STAGE 4: EXPANSION VALVE — Pressure Drop & Temp Reset
    # -----------------------------------------------------------------
    def _expansion_valve(self):
        """
        HVAC CONCEPT: THE EXPANSION VALVE (Metering Device)
        
        The refrigerant is now a high-pressure liquid, but it's still too
        warm to absorb heat from the core. The expansion valve is a small
        restriction (like crimping a garden hose) that RAPIDLY drops the
        pressure.
        
        ADIABATIC EXPANSION: When fluid pressure drops suddenly, its
        temperature drops proportionally. This is the same principle that
        makes aerosol cans feel cold when you spray them.
        
        After passing through the valve, the refrigerant is once again a
        cold, low-pressure liquid — ready to enter the evaporator and
        start the cycle over.
        """
        # Sudden restriction drops pressure → temperature plummets
        self.ref_temp -= 65.0
        self.ref_pressure = "Low"
        
        # State remains liquid, but now cold and low-pressure
        self.current_stage = "Expansion Valve"

    # -----------------------------------------------------------------
    #  GAME INTEGRATION: Frame-by-Frame Tick
    # -----------------------------------------------------------------
    def tick(self, core_temp: float, outdoor_temp: float, dt: float) -> float:
        """
        Called every game frame to simulate the HVAC system in real-time.
        
        GAME PROGRAMMING CONCEPT: DELTA TIME (dt)
        In game development, we multiply all time-dependent operations by
        'dt' (delta time) — the time elapsed since the last frame. This
        ensures the simulation runs at the same speed regardless of the
        frame rate (60fps vs 30fps).
        
        Parameters:
            core_temp: Current robot core temperature (°F)
            outdoor_temp: Current zone's outdoor temperature (°F)  
            dt: Delta time in seconds since last frame
            
        Returns:
            Updated core temperature after HVAC processing
        """
        # --- Thermostat Logic: Should the AC run? ---
        if not self.is_running:
            # Start cooling if temp exceeds setpoint + deadband
            if core_temp > self.target_temp + self.deadband:
                self.is_running = True
                self.stage_index = 0
                self.stage_timer = 0.0
        else:
            # Stop cooling if temp drops below setpoint
            if core_temp <= self.target_temp:
                self.is_running = False
                self.current_stage = "Idle"
                self.total_cycles += 1
                return core_temp

        if not self.is_running:
            self.current_stage = "Idle"
            return core_temp

        # --- Run the current stage based on timer ---
        self.stage_timer += dt
        
        if self.stage_timer >= self.stage_duration:
            self.stage_timer = 0.0
            
            # Execute the current stage
            stages = [
                lambda: self._evaporator(core_temp),
                lambda: self._compressor(),
                lambda: self._condenser(outdoor_temp),
                lambda: self._expansion_valve(),
            ]
            
            if self.stage_index == 0:
                core_temp = stages[0]()
                self._log_stage(core_temp, outdoor_temp)
            else:
                stages[self.stage_index]()
                self._log_stage(core_temp, outdoor_temp)
            
            # Advance to next stage (loop back to 0 after stage 3)
            self.stage_index = (self.stage_index + 1) % 4
            
            if self.stage_index == 0:
                self.total_cycles += 1

        return core_temp

    # -----------------------------------------------------------------
    #  DIAGNOSTIC LOGGING
    # -----------------------------------------------------------------
    def _log_stage(self, core_temp: float, outdoor_temp: float):
        """Record the current state to the in-memory log buffer."""
        if not self.log_enabled:
            return
            
        entry = {
            "cycle": self.total_cycles + 1,
            "stage": self.current_stage,
            "core_temp": round(core_temp, 1),
            "outdoor_temp": round(outdoor_temp, 1),
            "ref_temp": round(self.ref_temp, 1),
            "ref_pressure": self.ref_pressure,
            "ref_state": self.ref_state,
            "efficiency": round(self.efficiency_rating, 2),
            "timestamp": time.time()
        }
        self.log_entries.append(entry)

    def dump_csv(self, filename: str = "robot_hvac_diagnostic.csv"):
        """Write all logged entries to a CSV file for post-analysis."""
        if not self.log_entries:
            print("[HVAC] No diagnostic entries to dump.")
            return
            
        headers = ["Cycle", "Stage", "Core_Temp_F", "Outdoor_Temp_F",
                    "Ref_Temp_F", "Ref_Pressure", "Ref_State", "Efficiency"]
        
        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for entry in self.log_entries:
                writer.writerow([
                    entry["cycle"], entry["stage"], entry["core_temp"],
                    entry["outdoor_temp"], entry["ref_temp"],
                    entry["ref_pressure"], entry["ref_state"],
                    entry["efficiency"]
                ])
        
        print(f"[HVAC] Dumped {len(self.log_entries)} diagnostic entries to {filename}")

    def toggle_logging(self):
        """Toggle diagnostic logging on/off."""
        self.log_enabled = not self.log_enabled
        status = "ENABLED" if self.log_enabled else "DISABLED"
        print(f"[HVAC] Diagnostic logging {status}")

    # -----------------------------------------------------------------
    #  STATUS REPORTING
    # -----------------------------------------------------------------
    def get_status(self) -> dict:
        """Return a dictionary of all current HVAC system values for the HUD."""
        return {
            "is_running": self.is_running,
            "current_stage": self.current_stage,
            "target_temp": self.target_temp,
            "ref_temp": round(self.ref_temp, 1),
            "ref_pressure": self.ref_pressure,
            "ref_state": self.ref_state,
            "total_cycles": self.total_cycles,
            "efficiency": round(self.efficiency_rating, 2),
            "last_cool_amount": round(self.last_cool_amount, 1),
            "log_entries_count": len(self.log_entries),
        }
