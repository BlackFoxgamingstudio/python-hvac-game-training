"""
=============================================================================
 Robot Brain — Gemini AI Integration for the Game
=============================================================================

 API CONCEPT: INTEGRATING EXTERNAL AI INTO A GAME OBJECT
 
 This module wraps the Google Gemini API into a class that can be embedded
 inside the Robot. It demonstrates:
   - API key management via environment variables
   - System instructions that dynamically include game state
   - Threading for non-blocking API calls (critical for games)
   - Graceful fallback when the API is unavailable
   - Response caching to minimize API calls and costs

 The brain receives the robot's live telemetry (core temp, distance, HVAC
 status) and injects it into the system prompt so the AI "knows" the
 robot's current physical state when answering questions.
=============================================================================
"""

import os
import threading
from typing import Optional


class RobotBrain:
    """
    The AI subsystem of the Robot, powered by the Gemini API.
    
    OOP CONCEPT: OPTIONAL COMPOSITION
    The Robot can function without its brain (if no API key is set).
    This demonstrates graceful degradation — the system works at reduced
    capability rather than crashing entirely.
    """

    def __init__(self, bot_name: str = "RoboMech-V2"):
        """
        Initialize the AI brain, checking for API key availability.
        
        SECURITY CONCEPT: ENVIRONMENT VARIABLES
        API keys should NEVER be hardcoded in source files. Instead,
        we read them from environment variables, which are set outside
        the codebase and not committed to version control.
        """
        self.bot_name = bot_name
        self.api_available = False
        self.client = None
        self.model_name = "gemini-2.5-flash"
        
        # --- Response Cache ---
        # PERFORMANCE CONCEPT: Caching
        # API calls are slow (~1-3 seconds). We cache responses for 
        # identical questions to avoid repeated calls.
        self.response_cache = {}
        self.max_cache_size = 50
        
        # --- Async Response State ---
        self.pending_response = None
        self.is_thinking = False
        self.last_response = ""
        self.last_error = ""
        
        # --- Chat History ---
        self.chat_history = []  # List of {"role": "user"/"ai", "text": "..."}
        
        # --- Prompt Vectors Tracker ---
        self.prompt_vectors = {
            "AI-001": AIPromptVector("AI-001", "AI-001 verifies that sparks particle emitter vectors is calibrated by calibratesing options to animate sweeping dial pointer sweeps."),
            "AI-002": AIPromptVector("AI-002", "AI-002 establishes the process where to avoid liquid slugback hazards occurs by tracking the crankcase heater activation cycle."),
            "AI-003": AIPromptVector("AI-003", "AI-003 configures the engine to evaluates the suction line superheat so that it is possible to open stuck expansion valve steps."),
            "AI-004": AIPromptVector("AI-004", "AI-004 maps where red-blue piping indicator flows is updated during inspectsing cycles to map thermal zone gradients.")
        }
        
        # --- Initialize the API client ---
        self._init_client()

    def _init_client(self):
        """Attempt to initialize the Gemini client."""
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
        if not api_key:
            print("[AI BRAIN] No GEMINI_API_KEY found. AI features disabled.")
            print("[AI BRAIN] Set it with: export GEMINI_API_KEY='your-key-here'")
            self.api_available = False
            return
        
        try:
            from google import genai
            from google.genai import types
            self.genai = genai
            self.types = types
            self.client = genai.Client()
            self.api_available = True
            print(f"[AI BRAIN] Gemini API initialized for {self.bot_name}")
        except ImportError:
            print("[AI BRAIN] google-genai not installed. Run: pip install google-genai")
            self.api_available = False
        except Exception as e:
            print(f"[AI BRAIN] Failed to initialize: {e}")
            self.api_available = False

    def ask(self, user_prompt: str, telemetry: dict) -> None:
        """
        Send a question to Gemini (non-blocking).
        
        GAME PROGRAMMING CONCEPT: NON-BLOCKING OPERATIONS
        API calls take 1-3 seconds. If we waited synchronously, the game
        would freeze. Instead, we use a background thread to make the call,
        allowing the game loop to continue rendering frames.
        
        The response will appear in self.last_response when ready.
        Check self.is_thinking to know if a query is in progress.
        """
        if self.is_thinking:
            return  # Don't stack queries
        
        # Check cache first
        cache_key = user_prompt.strip().lower()
        if cache_key in self.response_cache:
            self.last_response = self.response_cache[cache_key]
            self.chat_history.append({"role": "user", "text": user_prompt})
            self.chat_history.append({"role": "ai", "text": self.last_response})
            return
        
        if not self.api_available:
            self.last_response = self._get_fallback_response(user_prompt, telemetry)
            self.chat_history.append({"role": "user", "text": user_prompt})
            self.chat_history.append({"role": "ai", "text": self.last_response})
            return
        
        # Launch the API call in a background thread
        self.is_thinking = True
        self.chat_history.append({"role": "user", "text": user_prompt})
        
        thread = threading.Thread(
            target=self._query_gemini,
            args=(user_prompt, telemetry, cache_key),
            daemon=True
        )
        thread.start()

    def _query_gemini(self, user_prompt: str, telemetry: dict, cache_key: str):
        """Execute the Gemini API call in a background thread."""
        try:
            # Build dynamic system instruction with live telemetry
            hvac_info = telemetry.get("hvac", {})
            system_instruction = (
                f"You are the internal AI brain of a robot named {self.bot_name}. "
                f"You exist inside this robot and have access to its live sensor data. "
                f"Current Telemetry:\n"
                f"- Core Temperature: {telemetry.get('core_temp', 'N/A')}°F\n"
                f"- HVAC Status: {hvac_info.get('current_stage', 'Unknown')}\n"
                f"- HVAC Target: {hvac_info.get('target_temp', 'N/A')}°F\n"
                f"- Refrigerant: {hvac_info.get('ref_temp', 'N/A')}°F, "
                f"{hvac_info.get('ref_pressure', 'N/A')} pressure, {hvac_info.get('ref_state', 'N/A')}\n"
                f"- Total Distance Walked: {telemetry.get('distance_walked', 0):.0f} pixels\n"
                f"- Position: {telemetry.get('position', (0,0))}\n"
                f"- AC Cycles Completed: {hvac_info.get('total_cycles', 0)}\n\n"
                f"Respond helpfully in 2-3 sentences. If asked about your systems or HVAC, "
                f"explain using real engineering concepts. Be slightly robotic but friendly."
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=self.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    max_output_tokens=200
                )
            )
            
            self.last_response = response.text.strip()
            self.last_error = ""
            
            # Cache the response
            if len(self.response_cache) >= self.max_cache_size:
                # Evict oldest entry
                oldest = next(iter(self.response_cache))
                del self.response_cache[oldest]
            self.response_cache[cache_key] = self.last_response
            
        except Exception as e:
            self.last_error = str(e)
            self.last_response = f"[Communication error: {str(e)[:80]}]"
        
        finally:
            self.chat_history.append({"role": "ai", "text": self.last_response})
            self.is_thinking = False

    def _get_fallback_response(self, prompt: str, telemetry: dict) -> str:
        """
        Provide canned responses when the API is unavailable.
        
        DESIGN PATTERN: GRACEFUL DEGRADATION
        Rather than showing an error, we provide useful preset responses
        based on keyword matching. The user still gets a functional
        experience, just without the dynamic AI capabilities.
        """
        prompt_lower = prompt.lower()
        core_temp = telemetry.get("core_temp", 72.0)
        hvac = telemetry.get("hvac", {})
        
        if "temp" in prompt_lower or "hot" in prompt_lower or "cold" in prompt_lower:
            return (f"My core temperature is currently {core_temp:.1f}°F. "
                    f"{'My HVAC is actively cooling.' if hvac.get('is_running') else 'Systems nominal.'} "
                    f"[AI offline — connect Gemini API for dynamic responses]")
        
        elif "hvac" in prompt_lower or "ac" in prompt_lower or "cool" in prompt_lower:
            stage = hvac.get("current_stage", "Idle")
            return (f"HVAC is in {stage} stage. Refrigerant at {hvac.get('ref_temp', 'N/A')}°F, "
                    f"{hvac.get('ref_pressure', 'N/A')} pressure. "
                    f"Total cycles: {hvac.get('total_cycles', 0)}. "
                    f"[AI offline — set GEMINI_API_KEY for full responses]")
        
        elif "walk" in prompt_lower or "distance" in prompt_lower or "move" in prompt_lower:
            dist = telemetry.get("distance_walked", 0)
            return (f"Total distance walked: {dist:.0f} pixels. "
                    f"Movement generates heat at {Robot.HEAT_PER_PIXEL if hasattr(Robot, 'HEAT_PER_PIXEL') else 0.003}°F/pixel. "
                    f"[AI offline]")
        
        elif "hello" in prompt_lower or "hi" in prompt_lower or "hey" in prompt_lower:
            return (f"Greetings! I am {self.bot_name}. My systems are operational. "
                    f"Core temp: {core_temp:.1f}°F. How can I assist? [AI offline]")
        
        else:
            return (f"I received your query but my AI processor is offline. "
                    f"Set GEMINI_API_KEY environment variable for full AI capabilities. "
                    f"Core status: {core_temp:.1f}°F, HVAC: {hvac.get('current_stage', 'Idle')}.")
    
    def get_recent_history(self, count: int = 10) -> list:
        """Return the last N chat messages."""
        return self.chat_history[-count:]
    
    def clear_history(self):
        """Clear chat history and cache."""
        self.chat_history.clear()
        self.response_cache.clear()


class AIPromptVector:
    """
    Represents a structured prompt vector component for compiling 
    contextual input payloads for the Gemini API.
    """
    def __init__(self, vector_id: str, description: str):
        self.vector_id = vector_id
        self.description = description
        self.calibrated = False

    def compile_payload(self, telemetry: dict) -> str:
        """Compiles prompt payload with physical variables context."""
        return f"AI Prompt Vector {self.vector_id} context: {self.description}\nSystem telemetry: {telemetry}"
