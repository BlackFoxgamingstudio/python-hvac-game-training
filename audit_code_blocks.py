#!/usr/bin/env python3
"""
Audit script v2: Extract every Python code block from every module HTML,
attempt to exec() it with the same mock setup + code transforms that
the browser Pyodide engine uses, and report pass/fail for each.
Includes timeout protection for infinite loops.
"""
import sys
import re
import types
import os
import html
import signal
import traceback
from pathlib import Path
from io import StringIO

# ───────────────────────────────────────────
# Timeout handler
# ───────────────────────────────────────────
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out (>5s) — likely infinite loop")

# ───────────────────────────────────────────
# Replicate the EXACT mock setup from app.js
# ───────────────────────────────────────────

import time as _real_time
_real_time.sleep = lambda x: None

class _MockCallable:
    def __init__(self, name="mock"):
        self._name = name
    def __call__(self, *args, **kwargs):
        return self
    def __getattr__(self, name):
        return _MockCallable(f"{self._name}.{name}")
    def __repr__(self):
        return f"<Mock {self._name}>"
    def __bool__(self):
        return True
    def __iter__(self):
        return iter([])
    def __len__(self):
        return 0
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def __getitem__(self, key):
        return _MockCallable(f"{self._name}[{key}]")

def _create_deep_mock(name):
    class _ModProxy(types.ModuleType):
        def __getattr__(self, attr):
            return _MockCallable(f"{name}.{attr}")
    proxy = _ModProxy(name)
    proxy.__file__ = f"<browser mock {name}>"
    return proxy

# Mock pygame sub-modules
_pygame_submodules = [
    'pygame', 'pygame.display', 'pygame.event', 'pygame.font',
    'pygame.draw', 'pygame.time', 'pygame.image', 'pygame.mixer',
    'pygame.key', 'pygame.mouse', 'pygame.transform', 'pygame.sprite',
    'pygame.surface', 'pygame.rect', 'pygame.color', 'pygame.math',
    'pygame.locals', 'pygame.cursors', 'pygame.mask'
]
for _mod_name in _pygame_submodules:
    sys.modules[_mod_name] = _create_deep_mock(_mod_name)

_pg = sys.modules['pygame']
_pg.init = lambda: None
_pg.quit = lambda: None
_pg.QUIT = 256; _pg.KEYDOWN = 768; _pg.KEYUP = 769
_pg.MOUSEBUTTONDOWN = 1025; _pg.MOUSEBUTTONUP = 1026
for _k, _v in {'K_LEFT': 276, 'K_RIGHT': 275, 'K_UP': 273, 'K_DOWN': 274,
               'K_a': 97, 'K_d': 100, 'K_w': 119, 'K_s': 115,
               'K_SPACE': 32, 'K_RETURN': 13, 'K_ESCAPE': 27,
               'K_c': 99, 'K_l': 108}.items():
    setattr(_pg, _k, _v)
_pg.SRCALPHA = 65536; _pg.FULLSCREEN = 0x80000000; _pg.RESIZABLE = 0x10

class _MockSurface:
    def __init__(self, *args, **kwargs):
        self._w = args[0][0] if args and isinstance(args[0], (tuple, list)) else 800
        self._h = args[0][1] if args and isinstance(args[0], (tuple, list)) else 600
    def fill(self, *a, **k): pass
    def blit(self, *a, **k): pass
    def get_rect(self, **k): return _MockRect(0, 0, self._w, self._h)
    def get_size(self): return (self._w, self._h)
    def get_width(self): return self._w
    def get_height(self): return self._h
    def set_alpha(self, *a): pass
    def convert(self, *a): return self
    def convert_alpha(self, *a): return self
    def set_colorkey(self, *a): pass
    def copy(self): return self
    def subsurface(self, *a): return self

class _MockRect:
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.top, self.left = y, x
        self.bottom, self.right = y + h, x + w
        self.centerx, self.centery = x + w // 2, y + h // 2
        self.center = (self.centerx, self.centery)
        self.topleft = (x, y)
        self.size = (w, h)
    def colliderect(self, other): return False
    def clamp_ip(self, other): pass
    def move(self, dx, dy): return _MockRect(self.x + dx, self.y + dy, self.width, self.height)

_pg.Surface = _MockSurface
_pg.Rect = _MockRect

_display = sys.modules['pygame.display']
_display.set_mode = lambda *a, **k: _MockSurface((800, 600))
_display.set_caption = lambda *a: None
_display.flip = lambda: None
_display.update = lambda *a: None
_display.get_surface = lambda: _MockSurface((800, 600))
_pg.display = _display

class _MockFont:
    def __init__(self, *a, **k): pass
    def render(self, text, aa, color, *a): return _MockSurface((100, 20))
    def size(self, text): return (100, 20)
    def get_height(self): return 20

_font = sys.modules['pygame.font']
_font.init = lambda: None
_font.Font = _MockFont
_font.SysFont = lambda *a, **k: _MockFont()
_pg.font = _font

_event = sys.modules['pygame.event']
_event.get = lambda *a: []
_event.pump = lambda: None
_pg.event = _event

class _MockClock:
    def __init__(self): pass
    def tick(self, fps=60): return 16
    def get_time(self): return 16
    def get_fps(self): return 60.0

_ptime = sys.modules['pygame.time']
_ptime.Clock = _MockClock
_ptime.get_ticks = lambda: 0
_ptime.wait = lambda ms: None
_ptime.delay = lambda ms: None
_pg.time = _ptime

_draw = sys.modules['pygame.draw']
for fn in ['rect','circle','line','aaline','lines','polygon','ellipse']:
    setattr(_draw, fn, lambda *a, **k: None)
_pg.draw = _draw

_key = sys.modules['pygame.key']
_key.get_pressed = lambda: [0] * 512
_key.get_mods = lambda: 0
_pg.key = _key

_img = sys.modules['pygame.image']
_img.load = lambda *a: _MockSurface((64, 64))
_img.save = lambda *a: None
_pg.image = _img

_transform = sys.modules['pygame.transform']
_transform.scale = lambda surf, size: _MockSurface(size)
_transform.rotate = lambda surf, angle: surf
_transform.flip = lambda surf, xbool, ybool: surf
_pg.transform = _transform

_mouse = sys.modules['pygame.mouse']
_mouse.get_pos = lambda: (0, 0)
_mouse.get_pressed = lambda: (0, 0, 0)
_pg.mouse = _mouse

_mixer = sys.modules['pygame.mixer']
_mixer.init = lambda *a, **k: None
_mixer.quit = lambda: None
_mixer.Sound = _MockCallable("pygame.mixer.Sound")
_mixer.music = _MockCallable("pygame.mixer.music")
_pg.mixer = _mixer

# Mock google.genai AND google.generativeai
for _mod_name in ['google', 'google.genai', 'google.genai.types', 'google.generativeai']:
    sys.modules[_mod_name] = _create_deep_mock(_mod_name)
sys.modules['google'].genai = sys.modules['google.genai']

# Mock os.getenv for API keys
_orig_getenv = os.getenv
def _mock_getenv(key, default=None):
    if 'API_KEY' in str(key) or 'SECRET' in str(key):
        return 'BROWSER_MOCK_KEY'
    return _orig_getenv(key, default)
os.getenv = _mock_getenv

# ───────────────────────────────────────────
# Code cleaning (mirrors app.js transforms)
# ───────────────────────────────────────────

def clean_code_for_browser(code):
    code = re.sub(r'(\w+)\s*=\s*input\([^)]*\)', r'\1 = "72"', code)
    code = re.sub(r'\binput\([^)]*\)', '"72"', code)
    code = re.sub(r'sys\.exit\(\d*\)', 'pass', code)
    code = re.sub(r'\bexit\(\d*\)', 'pass', code)
    code = re.sub(r'if\s+__name__\s*==\s*["\']__main__["\']\s*:\s*\n\s*main\(\)', 'main()', code)
    code = re.sub(r'import\s+google\.generativeai\s+as\s+genai', 'import google.genai as genai', code)
    # Replace infinite loops with limited iterations
    code = re.sub(r'while\s+(running|True|game_running|self\.running)\s*:',
                  'for _browser_frame in range(5):  # Browser: limited to 5 frames', code)
    # Replace pygame event loop
    code = re.sub(r'for\s+(\w+)\s+in\s+pygame\.event\.get\(\)\s*:',
                  r'for \1 in []:  # Browser: no events', code)
    # Mock os.getenv for API keys
    code = re.sub(r'os\.getenv\(\s*["\']GEMINI_API_KEY["\']\s*\)', '"BROWSER_MOCK_KEY"', code)
    code = re.sub(r'os\.environ\.get\(\s*["\']GEMINI_API_KEY["\']\s*\)', '"BROWSER_MOCK_KEY"', code)
    code = re.sub(r'os\.environ\[["\']GEMINI_API_KEY["\']\]', '"BROWSER_MOCK_KEY"', code)
    
    # Mock file I/O with VirtualFS (matches app.js)
    if 'open(' in code and ("'w'" in code or '"w"' in code or "'a'" in code or '"a"' in code or "'r'" in code or '"r"' in code):
        mock_prefix = '''
import io as _io

class _VFS:
    _f = {}
    @classmethod
    def open(cls, path, mode='r', *a, **kw):
        path = str(path)
        if 'w' in mode:
            cls._f[path] = ""
            print(f"[Browser] Writing to virtual file: {path}")
            return _VF(path, cls)
        elif 'a' in mode:
            buf = _VF(path, cls)
            buf._b = cls._f.get(path, "")
            print(f"[Browser] Appending to virtual file: {path}")
            return buf
        elif 'r' in mode:
            content = cls._f.get(path, "timestamp,sensor,value\\n2024-01-01,temp,72.0\\n2024-01-01,pressure,410\\n")
            return _io.StringIO(content)
        return _io.StringIO()

class _VF:
    def __init__(self, p, fs):
        self._p = p; self._fs = fs; self._b = ""; self._c = False
    def write(self, d):
        self._b += d
    def writelines(self, lines):
        for line in lines:
            self._b += line
    def close(self):
        if not self._c:
            self._fs._f[self._p] = self._b; self._c = True
    def __enter__(self):
        return self
    def __exit__(self, *a):
        self.close()
    def flush(self): pass
    def read(self):
        return self._b
    def readline(self):
        return self._b.split("\\n")[0] + "\\n" if self._b else ""
    def readlines(self):
        return [l + "\\n" for l in self._b.split("\\n") if l]
    def seek(self, pos): pass
    def tell(self):
        return len(self._b)
    def __iter__(self):
        return iter(self._b.split("\\n"))

open = _VFS.open
'''
        code = mock_prefix + code
    
    return code

# ───────────────────────────────────────────
# Extract and test
# ───────────────────────────────────────────

def extract_code_blocks(html_content):
    pattern = r'<pre>\s*<code\s+class="language-python">(.*?)</code>\s*</pre>'
    matches = re.findall(pattern, html_content, re.DOTALL)
    return [html.unescape(m) for m in matches]

def test_code_block(code, module_name, block_index):
    cleaned = clean_code_for_browser(code)
    
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    captured_out = StringIO()
    captured_err = StringIO()
    sys.stdout = captured_out
    sys.stderr = captured_err
    
    error = None
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)  # 5 second timeout
    
    try:
        exec(cleaned, {"__name__": "__main__", "__builtins__": __builtins__})
    except SystemExit:
        pass
    except TimeoutError as e:
        error = str(e)
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    finally:
        signal.alarm(0)  # Cancel alarm
    
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    stdout = captured_out.getvalue()
    stderr = captured_err.getvalue()
    
    passed = error is None
    return passed, stdout, stderr, error

def main():
    pages_dir = Path(__file__).parent / "pages"
    module_files = sorted(pages_dir.glob("module_*.html"))
    
    total_blocks = 0
    total_passed = 0
    total_failed = 0
    failures = []
    
    for html_file in module_files:
        module_name = html_file.stem
        content = html_file.read_text(encoding='utf-8')
        blocks = extract_code_blocks(content)
        
        print(f"\n{'='*70}")
        print(f"  {module_name} — {len(blocks)} code blocks")
        print(f"{'='*70}", flush=True)
        
        for i, code in enumerate(blocks):
            total_blocks += 1
            first_line = code.strip().split('\n')[0][:60]
            
            passed, stdout, stderr, error = test_code_block(code, module_name, i)
            
            if passed:
                total_passed += 1
                has_output = bool(stdout.strip())
                status = "✅ PASS" + (" (has output)" if has_output else " (no output)")
                print(f"  Block {i+1}: {status}", flush=True)
                if has_output:
                    lines = stdout.strip().split('\n')[:2]
                    for l in lines:
                        print(f"           → {l[:80]}")
            else:
                total_failed += 1
                print(f"  Block {i+1}: ❌ FAIL — {error}", flush=True)
                print(f"           Code starts: {first_line}")
                failures.append({
                    'module': module_name,
                    'block': i + 1,
                    'error': error,
                    'first_line': first_line,
                    'code': code[:500]
                })
    
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total code blocks: {total_blocks}")
    print(f"  Passed:            {total_passed}")
    print(f"  Failed:            {total_failed}")
    print(f"{'='*70}")
    
    if failures:
        print(f"\n  FAILURES DETAIL:")
        for f in failures:
            print(f"\n  ┌─ {f['module']} Block {f['block']}")
            print(f"  │  Error: {f['error']}")
            print(f"  │  First line: {f['first_line']}")
            code_lines = f['code'].strip().split('\n')[:15]
            for cl in code_lines:
                print(f"  │  {cl[:100]}")
            print(f"  └─")
    
    return total_failed

if __name__ == "__main__":
    failures = main()
    sys.exit(1 if failures else 0)
