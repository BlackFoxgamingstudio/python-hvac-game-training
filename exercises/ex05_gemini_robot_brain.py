#!/usr/bin/env python3
"""
=============================================================================
 EXERCISE 05 — Robot with a Gemini AI Brain
=============================================================================

 PYTHON CONCEPTS: third-party imports, API clients, error handling
                  (try/except), environment variables (os.environ),
                  CLI input loop, class composition (3 objects),
                  graceful degradation

 HVAC CONCEPTS:   AI-assisted diagnostics, intelligent HVAC controllers,
                  natural language troubleshooting, smart building tech

 GOAL: Give the Robot an AI brain (Google Gemini) so it can answer
       HVAC questions, interpret sensor data, and provide diagnostic
       recommendations — all through a chat interface.

 PREREQUISITES:
   pip install google-genai
   Set environment variable: GEMINI_API_KEY=your_key_here

 NOTE: If no API key is found, the robot runs in "offline mode" with
       pre-programmed responses instead of AI — the script always works.
=============================================================================
"""

import os
import csv
import time

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — SAFE GEMINI IMPORT
# ─────────────────────────────────────────────────────────────────────────────
# We try to import the Gemini SDK. If it's not installed, we handle it
# gracefully so the rest of the exercise still runs.

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("  ⚠️  google-genai not installed. Run: pip install google-genai")
    print("     Robot will use offline mode (pre-programmed responses).")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLASS 1 — RobotBrain (AI Interface)
# ─────────────────────────────────────────────────────────────────────────────

class RobotBrain:
    """
    The robot's AI brain — powered by Google Gemini.

    PYTHON LESSON — TRY/EXCEPT:
      Not everything goes right.  The API key might be missing.  The
      network might be down.  try/except lets you handle errors gracefully
      instead of crashing.

    HVAC LESSON — AI IN HVAC:
      Modern HVAC systems use AI for:
        - Predictive maintenance (detect failing compressors early)
        - Energy optimization (learn occupancy patterns)
        - Fault detection & diagnostics (FDD)
        - Natural language interfaces for operators
    """

    # System prompt that gives Gemini HVAC expertise
    SYSTEM_PROMPT = """You are an HVAC diagnostic AI assistant installed 
in a walking robot. You have deep knowledge of:
- Refrigeration cycles (vapor compression)
- HVAC components (compressors, evaporators, condensers, TXVs)
- Thermodynamics and heat transfer
- Troubleshooting common HVAC faults
- Python programming for HVAC applications

When asked about the robot's status, analyze the provided sensor data 
and give actionable recommendations. Keep answers concise but technical.
Always explain the HVAC science behind your recommendations."""

    def __init__(self):
        """
        Initialize the AI brain.

        PYTHON LESSON — os.environ:
          os.environ is a dictionary of environment variables — system-wide
          settings.  API keys should NEVER be hardcoded in source code.
          Instead, set them as environment variables:
            export GEMINI_API_KEY=your_key_here
        """
        self.online = False
        self.client = None
        self.model_name = "gemini-2.0-flash"  # Fast, capable model

        if not GENAI_AVAILABLE:
            print("  🧠 Brain: Offline mode (SDK not available)")
            return

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

        if not api_key:
            print("  🧠 Brain: Offline mode (no API key found)")
            print("     Set GEMINI_API_KEY environment variable to enable AI.")
            return

        try:
            self.client = genai.Client(api_key=api_key)
            self.online = True
            print(f"  🧠 Brain: ONLINE — Connected to {self.model_name}")
        except Exception as e:
            print(f"  🧠 Brain: Offline mode (connection error: {e})")

    def think(self, prompt: str, context: str = "") -> str:
        """
        Send a prompt to Gemini and get a response.

        PYTHON LESSON — GRACEFUL DEGRADATION:
          If the AI is offline, we return a helpful pre-programmed response
          instead of crashing.  This is a CRITICAL design pattern — your
          software should always have a fallback.

        Parameters:
            prompt: The user's question or command
            context: Additional sensor data / state info
        """
        full_prompt = f"{context}\n\nUser question: {prompt}" if context else prompt

        if not self.online:
            return self._offline_response(prompt)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config={
                    "system_instruction": self.SYSTEM_PROMPT,
                    "temperature": 0.7,       # Balanced creativity
                    "max_output_tokens": 500,  # Keep responses concise
                }
            )
            return response.text
        except Exception as e:
            return f"⚠️ AI Error: {e}\n(Falling back to offline mode)"

    def _offline_response(self, prompt: str) -> str:
        """Pre-programmed responses when AI is unavailable."""
        prompt_lower = prompt.lower()

        if "superheat" in prompt_lower:
            return ("Superheat is measured at the evaporator outlet. "
                    "Target: 8-14°F for TXV systems. "
                    "High superheat → low charge or restricted filter. "
                    "Low superheat → overcharge or TXV stuck open.")
        elif "subcool" in prompt_lower:
            return ("Subcooling is measured at the condenser outlet. "
                    "Target: 8-12°F. "
                    "Low subcooling → undercharge. "
                    "High subcooling → overcharge or restriction.")
        elif "compressor" in prompt_lower:
            return ("The compressor is the heart of the system. "
                    "It raises refrigerant pressure and temperature. "
                    "Check amp draw, discharge temp, and oil level.")
        elif "temp" in prompt_lower or "hot" in prompt_lower:
            return ("High temperatures can indicate: dirty condenser, "
                    "restricted airflow, or overworked system. "
                    "Check filters, clean coils, verify charge.")
        else:
            return ("I'm in offline mode. For full AI diagnostics, "
                    "install google-genai and set GEMINI_API_KEY. "
                    "I can answer basic questions about: "
                    "superheat, subcooling, compressors, temperatures.")


# ─────────────────────────────────────────────────────────────────────────────
# CLASS 2 — AirConditioner (from Exercise 04, compact)
# ─────────────────────────────────────────────────────────────────────────────

class AirConditioner:
    """Self-contained AC unit for the robot."""

    def __init__(self, unit_id: str = "AC-001"):
        self.unit_id = unit_id
        self.compressor_on = False
        self.cycle_count = 0
        self.refrigerant_temp_f = 75.0
        self.refrigerant_phase = "Idle"

    def run_cooling_cycle(self, current_temp_f: float,
                          outdoor_temp_f: float = 85.0) -> float:
        """Run one cooling cycle, return new temperature."""
        self.compressor_on = True
        self.cycle_count += 1
        cooling_delta = 2.85
        new_temp = round(current_temp_f - cooling_delta, 1)
        self.compressor_on = False
        return new_temp

    def __str__(self):
        return f"[{self.unit_id}] Cycles: {self.cycle_count}"


# ─────────────────────────────────────────────────────────────────────────────
# CLASS 3 — Robot (has both AC and Brain)
# ─────────────────────────────────────────────────────────────────────────────

class Robot:
    """
    A walking robot with AC cooling AND an AI brain.

    PYTHON LESSON — MULTIPLE COMPOSITION:
      This robot OWNS two objects:
        self.internal_ac = AirConditioner()   ← cooling hardware
        self.brain = RobotBrain()             ← AI software

      This is like a real building: the HVAC hardware does the work,
      and the BAS (Building Automation System) software makes decisions.
    """

    OVERHEAT_THRESHOLD_F = 150.0
    OPTIMAL_TEMP_F = 98.6

    def __init__(self, name: str):
        self.name = name
        self.core_temp_f = 98.6
        self.position_m = 0.0
        self.total_distance_m = 0.0

        # Composition: Robot HAS an AC and HAS a Brain
        self.internal_ac = AirConditioner(unit_id=f"{name}-AC")
        self.brain = RobotBrain()

    def walk(self, meters: float) -> None:
        """Walk forward, generating heat."""
        heat = meters * 0.4
        self.position_m += meters
        self.total_distance_m += meters
        self.core_temp_f = round(self.core_temp_f + heat, 1)
        print(f"  🤖 Walked {meters}m → Core: {self.core_temp_f}°F "
              f"| Pos: {self.position_m}m")

    def cool_down(self, outdoor_temp_f: float = 85.0) -> None:
        """Run AC until optimal temperature."""
        cycles = 0
        while self.core_temp_f > self.OPTIMAL_TEMP_F:
            cycles += 1
            self.core_temp_f = self.internal_ac.run_cooling_cycle(
                self.core_temp_f, outdoor_temp_f
            )
        print(f"  ❄️  Cooled to {self.core_temp_f}°F in {cycles} cycles")

    def ask_brain(self, question: str) -> str:
        """Ask the AI brain a question with current sensor context."""
        context = (
            f"Robot Status:\n"
            f"  Core Temperature: {self.core_temp_f}°F\n"
            f"  Position: {self.position_m}m\n"
            f"  Total Distance: {self.total_distance_m}m\n"
            f"  AC Cycles: {self.internal_ac.cycle_count}\n"
            f"  Overheat Threshold: {self.OVERHEAT_THRESHOLD_F}°F"
        )
        return self.brain.think(question, context)

    def get_status_str(self) -> str:
        """Return formatted status string."""
        return (
            f"\n  ╔══════════════════════════════════════╗\n"
            f"  ║  🤖 {self.name:<33s}║\n"
            f"  ╠══════════════════════════════════════╣\n"
            f"  ║  Core Temp  : {self.core_temp_f:>6.1f} °F{' ' * 14}║\n"
            f"  ║  Position   : {self.position_m:>6.1f} m{' ' * 15}║\n"
            f"  ║  Distance   : {self.total_distance_m:>6.1f} m{' ' * 15}║\n"
            f"  ║  AC Cycles  : {self.internal_ac.cycle_count:>6d}{' ' * 16}║\n"
            f"  ║  Brain      : {'ONLINE' if self.brain.online else 'OFFLINE':<22s}║\n"
            f"  ╚══════════════════════════════════════╝"
        )


# ─────────────────────────────────────────────────────────────────────────────
# CLI LOOP — Interactive Robot Control
# ─────────────────────────────────────────────────────────────────────────────

def run_cli(robot: Robot) -> None:
    """
    Interactive command-line interface for controlling the robot.

    PYTHON LESSON — INPUT LOOP:
      input() reads text from the user.
      We use a while True loop with break to create an interactive session.
      .strip().lower() normalizes the input for reliable comparison.
    """
    print("\n" + "═" * 55)
    print("  ROBOT CONTROL TERMINAL")
    print("═" * 55)
    print("  Commands:")
    print("    walk <meters>  — Walk forward (generates heat)")
    print("    cool           — Run climate control")
    print("    status         — Show robot status")
    print("    ask <question> — Ask the AI brain an HVAC question")
    print("    exit           — Shut down")
    print("═" * 55)

    while True:
        try:
            raw = input("\n  🤖 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Shutting down...")
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == "exit" or cmd == "quit":
            print("  👋 Robot shutting down. Goodbye!")
            break

        elif cmd == "walk":
            try:
                meters = float(parts[1]) if len(parts) > 1 else 10.0
                robot.walk(meters)
            except ValueError:
                print("  ❌ Usage: walk <meters>  (e.g., walk 25)")

        elif cmd == "cool":
            robot.cool_down()

        elif cmd == "status":
            print(robot.get_status_str())

        elif cmd == "ask":
            if len(parts) < 2:
                print("  ❌ Usage: ask <question>  (e.g., ask What is superheat?)")
                continue
            print(f"\n  🧠 Thinking...")
            answer = robot.ask_brain(parts[1])
            print(f"\n  🧠 AI Response:")
            # Word-wrap the response at 60 chars
            words = answer.split()
            line = "     "
            for word in words:
                if len(line) + len(word) + 1 > 65:
                    print(line)
                    line = "     " + word
                else:
                    line += " " + word if line.strip() else word
            if line.strip():
                print(line)

        else:
            print(f"  ❓ Unknown command: '{cmd}'")
            print("     Try: walk, cool, status, ask, exit")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print(" EXERCISE 05 — Robot with Gemini AI Brain")
    print("=" * 60)
    print()

    # Create the robot (this also initializes Brain + AC)
    bot = Robot(name="Atlas-AI")

    # Show initial status
    print(bot.get_status_str())

    # Launch the interactive CLI
    run_cli(bot)

    print()
    print("=" * 60)
    print(" EXERCISE 05 COMPLETE")
    print("=" * 60)
    print("""
 WHAT YOU LEARNED:
   Python — try/except error handling, os.environ for API keys,
            third-party imports (google.genai), graceful degradation,
            interactive input() loops, string manipulation,
            multiple composition (Robot has AC + Brain)

   HVAC  — AI-assisted diagnostics, smart building controllers,
           fault detection & diagnostics (FDD), natural language
           interfaces for HVAC systems, predictive maintenance

 NEXT: Exercise 06 — Diagnostic Dashboard (AI-powered analysis)
""")
