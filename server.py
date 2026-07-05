#!/usr/bin/env python3
"""
=============================================================================
 Python HVAC Game Training — Local Web Server
=============================================================================

 TEACHING CONCEPT: Python's Standard Library HTTP Server
 
 Python comes with a built-in HTTP server module (`http.server`) that can 
 serve static files without any external frameworks like Flask or Django.
 This demonstrates that Python is a "batteries-included" language — many 
 common tasks already have solutions in the standard library.

 HOW IT WORKS:
 1. We create a custom request handler that maps URL paths to our HTML files
 2. The handler serves static assets (CSS, JS, images) from the static/ dir
 3. Module pages are served from the pages/ directory
 4. The server listens on port 8080 and handles requests in a loop

 RUN:
    python server.py
    Then open http://localhost:8080 in your browser.
=============================================================================
"""

import os
import sys
import json
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

# --- Configuration ---
PORT = int(os.environ.get("PORT", 8080))
HOST = os.environ.get("HOST", "0.0.0.0")

# Get the directory where this script lives
BASE_DIR = Path(__file__).parent.resolve()
PAGES_DIR = BASE_DIR / "pages"
STATIC_DIR = BASE_DIR / "static"


class TrainingServerHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler for the training website.
    
    PROGRAMMING CONCEPT: Inheritance
    We inherit from SimpleHTTPRequestHandler (a built-in Python class) and 
    override its `do_GET` method to add our own routing logic. This is 
    exactly like how our Robot class might inherit from a base GameObject.
    """

    def do_GET(self):
        """Handle GET requests by routing to the correct file."""
        
        # Strip query parameters and normalize the path
        path = self.path.split("?")[0]
        
        # --- Route: Landing Page ---
        if path == "/" or path == "/index.html":
            self._serve_file(PAGES_DIR / "index.html", "text/html")
        
        # --- Route: Module Pages ---
        elif path.startswith("/module"):
            # Convert URL like /module/01 to pages/module_01_python_basics.html
            # or /module/module_01_python_basics.html to the file directly
            filename = path.lstrip("/")
            if not filename.endswith(".html"):
                # Try /module/01 → module_01_*.html pattern
                parts = filename.split("/")
                if len(parts) == 2 and parts[1].isdigit():
                    module_num = parts[1].zfill(2)
                    matches = list(PAGES_DIR.glob(f"module_{module_num}_*.html"))
                    if matches:
                        self._serve_file(matches[0], "text/html")
                        return
                filename += ".html"
            filepath = PAGES_DIR / filename.replace("module/", "")
            if filepath.exists():
                self._serve_file(filepath, "text/html")
            else:
                self._serve_404()
        
        # --- Route: Static Assets (CSS, JS, Images) ---
        elif path.startswith("/static/"):
            relative_path = path[len("/static/"):]
            filepath = STATIC_DIR / relative_path
            if filepath.exists() and filepath.is_file():
                content_type, _ = mimetypes.guess_type(str(filepath))
                self._serve_file(filepath, content_type or "application/octet-stream")
            else:
                self._serve_404()
        
        # --- Route: Direct page file access ---
        elif path.startswith("/pages/"):
            relative_path = path[len("/pages/"):]
            filepath = PAGES_DIR / relative_path
            if filepath.exists():
                self._serve_file(filepath, "text/html")
            else:
                self._serve_404()
        
        # --- Route: API endpoint for progress tracking ---
        elif path == "/api/modules":
            self._serve_module_list()
        
        # --- Fallback: Try to serve from base directory ---
        else:
            filepath = BASE_DIR / path.lstrip("/")
            if filepath.exists() and filepath.is_file():
                content_type, _ = mimetypes.guess_type(str(filepath))
                self._serve_file(filepath, content_type or "application/octet-stream")
            else:
                self._serve_404()

    def do_POST(self):
        """Handle POST requests, specifically for AI diagnostics."""
        path = self.path.split("?")[0]
        
        if path == "/api/diagnose":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                telemetry = json.loads(post_data.decode('utf-8'))
                
                # Fetch Gemini API Key
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    response_data = {
                        "status": "error",
                        "message": "GEMINI_API_KEY environment variable is not configured on the server. Please set it to enable live AI analysis.",
                        "diagnosis": "### ⚠️ AI Configuration Missing\n\nThe `GEMINI_API_KEY` environment variable is not configured on the host server.\n\n**Simulated Diagnostic Report (Nominal Data):**\n* **Head Pressure:** " + str(telemetry.get('discharge_psi', 410)) + " PSI\n* **Suction Pressure:** " + str(telemetry.get('suction_psi', 68)) + " PSI\n* **Fault Code:** " + str(telemetry.get('fault', 'None')) + "\n* **Analysis:** Please configure your Google Gemini API key to enable live smart-building analytics."
                    }
                else:
                    try:
                        from google import genai
                        from google.genai import types
                        
                        client = genai.Client(api_key=api_key)
                        
                        system_instruction = (
                            "You are a master HVAC technician and certified smart-building control automation engineer. "
                            "Analyze the provided thermodynamic telemetry data, identify any faults (frozen coil, dirty condenser, low charge, stuck expansion valve), "
                            "explain the physics of the fault, and provide a clear step-by-step remediation guide for the service technician."
                        )
                        
                        prompt = f"""
                        Analyze this system telemetry payload:
                        - Zone Temperature: {telemetry.get('temp', 72.0):.1f}°F
                        - Suction Pressure: {telemetry.get('suction_psi', 68):d} PSI
                        - Discharge (Head) Pressure: {telemetry.get('discharge_psi', 410):d} PSI
                        - Superheat: {telemetry.get('superheat', 10.0):.1f}°F
                        - Subcooling: {telemetry.get('subcooling', 12.0):.1f}°F
                        - Delta-T (Return vs Supply Air Temp): {telemetry.get('delta_t', 18.0):.1f}°F
                        - Active Fault Code: {telemetry.get('fault', 'NONE')}
                        
                        Generate a comprehensive, markdown-formatted diagnostic report.
                        """
                        
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction
                            )
                        )
                        
                        response_data = {
                            "status": "success",
                            "diagnosis": response.text
                        }
                    except Exception as e:
                        response_data = {
                            "status": "error",
                            "message": f"Gemini API Call Failed: {str(e)}",
                            "diagnosis": f"### ❌ API Call Failed\n\nFailed to invoke Gemini API model: `{str(e)}`."
                        }
                
                data = json.dumps(response_data).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                
            except Exception as e:
                print(f"[ERROR] Failed to handle API request: {e}")
                self._serve_500()
        else:
            self._serve_404()

    
    def _serve_file(self, filepath: Path, content_type: str):
        """Read and serve a file with the given content type."""
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")  # Dev mode: no caching
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            print(f"[ERROR] Failed to serve {filepath}: {e}")
            self._serve_500()
    
    def _serve_module_list(self):
        """Serve a JSON list of available modules for the frontend."""
        modules = [
            {"id": 1, "slug": "module_01_python_basics", "title": "Python Fundamentals", "subtitle": "The Language of Systems"},
            {"id": 2, "slug": "module_02_hvac_functions", "title": "HVAC as Functions", "subtitle": "Mapping Hardware to Software"},
            {"id": 3, "slug": "module_03_data_flow_logging", "title": "Data Flow & Logging", "subtitle": "CSV Telemetry"},
            {"id": 4, "slug": "module_04_oop_refactor", "title": "OOP Refactor", "subtitle": "Robot + AC Composition"},
            {"id": 5, "slug": "module_05_api_ai_integration", "title": "AI Integration", "subtitle": "Gemini API & Robot Brain"},
            {"id": 6, "slug": "module_06_diagnostic_troubleshooting", "title": "Diagnostic Troubleshooting", "subtitle": "AI-Powered Analysis"},
            {"id": 7, "slug": "module_07_game_programming", "title": "Game Programming", "subtitle": "Pygame & Game Objects"},
            {"id": 8, "slug": "module_08_final_project", "title": "Final Project", "subtitle": "Complete Robot Simulation"},
        ]
        data = json.dumps(modules).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    
    def _serve_404(self):
        """Serve a styled 404 error page."""
        html = """<!DOCTYPE html><html><head>
        <title>404 — Not Found</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>body{background:#0a0a1a;color:#e0e0e0;font-family:'Inter',sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}
        .box{text-align:center;padding:3rem;border-radius:1rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1)}
        h1{font-size:5rem;margin:0;background:linear-gradient(135deg,#00d4ff,#7b2ff7);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        a{color:#00d4ff;text-decoration:none}</style>
        </head><body><div class="box"><h1>404</h1><p>Module not found.</p><a href="/">← Back to Course</a></div></body></html>"""
        content = html.encode("utf-8")
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
    
    def _serve_500(self):
        """Serve a 500 internal server error."""
        self.send_response(500)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"500 Internal Server Error")
    
    def log_message(self, format, *args):
        """Override default logging to use a cleaner format."""
        print(f"[{self.log_date_time_string()}] {args[0]}")


def main():
    """Start the training server."""
    # Verify directories exist
    if not PAGES_DIR.exists():
        print(f"[WARNING] Pages directory not found: {PAGES_DIR}")
        print("          Creating it now...")
        PAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    if not STATIC_DIR.exists():
        print(f"[WARNING] Static directory not found: {STATIC_DIR}")
        print("          Creating it now...")
        STATIC_DIR.mkdir(parents=True, exist_ok=True)
    
    # Start the server
    server = HTTPServer((HOST, PORT), TrainingServerHandler)
    
    print("=" * 60)
    print("  🤖 Python Systems Thinking Training Server")
    print("=" * 60)
    print(f"  📡 Server running at: http://{HOST}:{PORT}")
    print(f"  📁 Serving pages from: {PAGES_DIR}")
    print(f"  🎨 Static assets from: {STATIC_DIR}")
    print(f"  ⏹  Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Training server stopped.")
        server.server_close()
        sys.exit(0)


if __name__ == "__main__":
    main()
