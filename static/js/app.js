/**
 * ==========================================================================
 *  Python Systems Thinking Training — Client-Side Application Logic
 * ==========================================================================
 * 
 * Handles:
 * - IN-BROWSER Python execution via Pyodide (WebAssembly)
 * - Module progress tracking via localStorage
 * - Code block copy-to-clipboard functionality
 * - Smooth navigation and active state management
 * - Page load animations
 */

(function() {
  'use strict';

  // --- Constants ---
  const STORAGE_KEY = 'python_training_progress';
  const TOTAL_MODULES = 8;

  // =============================================
  //  Pyodide (In-Browser Python) Integration
  // =============================================

  let pyodideInstance = null;
  let pyodideLoading = false;
  let pyodideReady = false;

  /**
   * Load Pyodide from CDN. Called lazily on first "Run" click.
   */
  async function loadPyodideEngine() {
    if (pyodideReady) return pyodideInstance;
    if (pyodideLoading) {
      // Wait for ongoing load
      while (pyodideLoading) {
        await new Promise(r => setTimeout(r, 200));
      }
      return pyodideInstance;
    }

    pyodideLoading = true;
    updateAllRunButtons('Loading Python...', true);

    try {
      // Dynamically load Pyodide script
      if (typeof loadPyodide === 'undefined') {
        await new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = 'https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js';
          script.onload = resolve;
          script.onerror = () => reject(new Error('Failed to load Pyodide'));
          document.head.appendChild(script);
        });
      }

      pyodideInstance = await loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.25.1/full/'
      });

      // Pre-install comprehensive mock modules for browser-incompatible imports
      await pyodideInstance.runPythonAsync(`
import sys
import types

# -------------------------------------------------------
# Mock 'time.sleep' to be a no-op in browser
# -------------------------------------------------------
import time as _real_time
_real_time.sleep = lambda x: None

# -------------------------------------------------------
# Helper to create recursive mock objects that never fail
# -------------------------------------------------------
class _MockCallable:
    """A callable mock that returns itself for chaining, and supports attribute access."""
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
    """Create a module that returns _MockCallable for any attribute access."""
    mod = types.ModuleType(name)
    mod.__file__ = f"<browser mock {name}>"
    class _ModProxy(types.ModuleType):
        def __getattr__(self, attr):
            return _MockCallable(f"{name}.{attr}")
    proxy = _ModProxy(name)
    proxy.__file__ = f"<browser mock {name}>"
    return proxy

# -------------------------------------------------------
# Mock pygame and ALL sub-modules deeply
# -------------------------------------------------------
_pygame_submodules = [
    'pygame', 'pygame.display', 'pygame.event', 'pygame.font',
    'pygame.draw', 'pygame.time', 'pygame.image', 'pygame.mixer',
    'pygame.key', 'pygame.mouse', 'pygame.transform', 'pygame.sprite',
    'pygame.surface', 'pygame.rect', 'pygame.color', 'pygame.math',
    'pygame.locals', 'pygame.cursors', 'pygame.mask'
]

for _mod_name in _pygame_submodules:
    sys.modules[_mod_name] = _create_deep_mock(_mod_name)

# Set commonly-used pygame constants directly on the top-level mock
_pg = sys.modules['pygame']
_pg.init = lambda: None
_pg.quit = lambda: None

# Event constants
_pg.QUIT = 256
_pg.KEYDOWN = 768
_pg.KEYUP = 769
_pg.MOUSEBUTTONDOWN = 1025
_pg.MOUSEBUTTONUP = 1026

# Key constants
for _k, _v in {'K_LEFT': 276, 'K_RIGHT': 275, 'K_UP': 273, 'K_DOWN': 274,
               'K_a': 97, 'K_d': 100, 'K_w': 119, 'K_s': 115,
               'K_SPACE': 32, 'K_RETURN': 13, 'K_ESCAPE': 27,
               'K_c': 99, 'K_l': 108, 'K_h': 104, 'K_t': 116}.items():
    setattr(_pg, _k, _v)

# Surface flags
_pg.SRCALPHA = 65536
_pg.FULLSCREEN = 0x80000000
_pg.RESIZABLE = 0x10

# Mock Surface class that supports chaining
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

# Mock display sub-module specifically
_display = sys.modules['pygame.display']
_display.set_mode = lambda *a, **k: _MockSurface((800, 600))
_display.set_caption = lambda *a: None
_display.flip = lambda: None
_display.update = lambda *a: None
_display.get_surface = lambda: _MockSurface((800, 600))
_pg.display = _display

# Mock font sub-module
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

# Mock event sub-module
_event = sys.modules['pygame.event']
_event.get = lambda *a: []
_event.pump = lambda: None
_pg.event = _event

# Mock time sub-module
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

# Mock draw sub-module
_draw = sys.modules['pygame.draw']
_draw.rect = lambda *a, **k: None
_draw.circle = lambda *a, **k: None
_draw.line = lambda *a, **k: None
_draw.aaline = lambda *a, **k: None
_draw.lines = lambda *a, **k: None
_draw.polygon = lambda *a, **k: None
_draw.ellipse = lambda *a, **k: None
_pg.draw = _draw

# Mock key sub-module
_key = sys.modules['pygame.key']
_key.get_pressed = lambda: [0] * 512
_key.get_mods = lambda: 0
_pg.key = _key

# Mock image sub-module
_img = sys.modules['pygame.image']
_img.load = lambda *a: _MockSurface((64, 64))
_img.save = lambda *a: None
_pg.image = _img

# Mock transform sub-module
_transform = sys.modules['pygame.transform']
_transform.scale = lambda surf, size: _MockSurface(size)
_transform.rotate = lambda surf, angle: surf
_transform.flip = lambda surf, xbool, ybool: surf
_pg.transform = _transform

# Mock mouse
_mouse = sys.modules['pygame.mouse']
_mouse.get_pos = lambda: (0, 0)
_mouse.get_pressed = lambda: (0, 0, 0)
_pg.mouse = _mouse

# Mock mixer
_mixer = sys.modules['pygame.mixer']
_mixer.init = lambda *a, **k: None
_mixer.quit = lambda: None
_mixer.Sound = _MockCallable("pygame.mixer.Sound")
_mixer.music = _MockCallable("pygame.mixer.music")
_pg.mixer = _mixer

# -------------------------------------------------------
# Mock google.genai and sub-modules
# -------------------------------------------------------
for _mod_name in ['google', 'google.genai', 'google.genai.types']:
    sys.modules[_mod_name] = _create_deep_mock(_mod_name)
sys.modules['google'].genai = sys.modules['google.genai']

# Also mock 'google.generativeai' (old SDK name used in some examples)
sys.modules['google.generativeai'] = sys.modules['google.genai']

# Mock os.getenv / os.environ for API keys
import os as _os
_orig_getenv = _os.getenv
def _mock_getenv(key, default=None):
    if 'API_KEY' in key or 'SECRET' in key:
        return 'BROWSER_MOCK_KEY'
    return _orig_getenv(key, default)
_os.getenv = _mock_getenv

# Mock csv module to work with StringIO (already works, but ensure import)
import csv

print("[Pyodide] Python engine loaded. Mocks for pygame, google.genai & file I/O active.")
      `);

      pyodideReady = true;
      updateAllRunButtons('▶ Run', false);
      console.log('[Pyodide] Python engine loaded successfully');
    } catch (err) {
      console.error('[Pyodide] Failed to load:', err);
      updateAllRunButtons('▶ Run (load failed)', false);
      pyodideLoading = false;
      throw err;
    }

    pyodideLoading = false;
    return pyodideInstance;
  }

  /**
   * Execute Python code and capture stdout/stderr output.
   * 
   * KEY FIX: Instead of wrapping user code inside try/except (which breaks
   * indentation), we use exec() with a clean namespace and catch errors
   * at the JavaScript level.
   */
  async function runPythonCode(code, outputEl, runBtn) {
    runBtn.textContent = '⏳ Running...';
    runBtn.disabled = true;
    outputEl.style.display = 'block';
    outputEl.textContent = '';
    outputEl.classList.remove('has-error');

    try {
      const pyodide = await loadPyodideEngine();

      // Clean the code for browser compatibility
      let cleanCode = code
        // Replace input() calls with mock values so they don't hang
        .replace(/(\w+)\s*=\s*input\([^)]*\)/g, '$1 = "72"')
        // Replace bare input() calls
        .replace(/\binput\([^)]*\)/g, '"72"')
        // Remove sys.exit() calls
        .replace(/sys\.exit\(\d*\)/g, 'pass')
        // Remove exit() calls
        .replace(/\bexit\(\d*\)/g, 'pass')
        // Replace if __name__ == "__main__": main() with just main()
        .replace(/if\s+__name__\s*==\s*["']__main__["']\s*:\s*\n\s*main\(\)/g, 'main()')
        // Fix old google.generativeai import to google.genai
        .replace(/import\s+google\.generativeai\s+as\s+genai/g, 'import google.genai as genai')
        // Replace "while running:" / "while True:" game loops with limited iterations
        .replace(/while\s+(running|True|game_running|self\.running)\s*:/g, 'for _browser_frame in range(5):  # Browser: limited to 5 frames')
        // Replace "for event in pygame.event.get():" with empty list
        .replace(/for\s+(\w+)\s+in\s+pygame\.event\.get\(\)\s*:/g, 'for $1 in []:  # Browser: no events');

      // If code contains "open(" for file writes, inject a virtual filesystem
      if (cleanCode.includes('open(') && (cleanCode.includes("'w'") || cleanCode.includes('"w"') || cleanCode.includes("'a'") || cleanCode.includes('"a"') || cleanCode.includes("'r'") || cleanCode.includes('"r"'))) {
        cleanCode = `
import io as _io

class _VirtualFS:
    """Virtual filesystem that persists data across open/close cycles."""
    _files = {}
    
    @classmethod
    def open(cls, path, mode='r', *a, **kw):
        path = str(path)
        if 'w' in mode:
            buf = _VirtualFile(path, cls)
            cls._files[path] = ""
            print(f"[Browser] Writing to virtual file: {path}")
            return buf
        elif 'a' in mode:
            buf = _VirtualFile(path, cls)
            buf._buffer = cls._files.get(path, "")
            print(f"[Browser] Appending to virtual file: {path}")
            return buf
        elif 'r' in mode:
            content = cls._files.get(path, "timestamp,sensor,value\\n2024-01-01,temp,72.0\\n2024-01-01,pressure,410\\n")
            return _io.StringIO(content)
        return _io.StringIO()

class _VirtualFile:
    """A writable file object that saves to VirtualFS on close."""
    def __init__(self, path, fs):
        self._path = path
        self._fs = fs
        self._buffer = ""
        self._closed = False
    def write(self, data):
        self._buffer += data
    def writelines(self, lines):
        for line in lines:
            self._buffer += line
    def close(self):
        if not self._closed:
            self._fs._files[self._path] = self._buffer
            self._closed = True
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()
    def flush(self): pass
    def read(self):
        return self._buffer
    def readline(self):
        return self._buffer.split("\\n")[0] + "\\n" if self._buffer else ""
    def readlines(self):
        return [l + "\\n" for l in self._buffer.split("\\n") if l]
    def seek(self, pos):
        pass
    def tell(self):
        return len(self._buffer)
    def __iter__(self):
        return iter(self._buffer.split("\\n"))
    def __next__(self):
        return next(iter(self))

open = _VirtualFS.open
` + cleanCode;
      }

      // If code tries to use os.getenv for API keys, provide a fallback
      cleanCode = cleanCode.replace(
        /os\.getenv\(\s*["']GEMINI_API_KEY["']\s*\)/g,
        '"BROWSER_MOCK_KEY"'
      );
      cleanCode = cleanCode.replace(
        /os\.environ\.get\(\s*["']GEMINI_API_KEY["']\s*\)/g,
        '"BROWSER_MOCK_KEY"'
      );
      cleanCode = cleanCode.replace(
        /os\.environ\[["']GEMINI_API_KEY["']\]/g,
        '"BROWSER_MOCK_KEY"'
      );

      // Store code in a Python variable (avoids JS string escaping issues)
      // We use a unique variable name to avoid collisions
      pyodide.globals.set('__browser_code__', cleanCode);

      // Execute using exec() inside Python, which handles indentation naturally
      const result = await pyodide.runPythonAsync(`
import sys
from io import StringIO

_captured_out = StringIO()
_captured_err = StringIO()
_old_stdout = sys.stdout
_old_stderr = sys.stderr
sys.stdout = _captured_out
sys.stderr = _captured_err

_exec_error = ""
try:
    exec(__browser_code__, {"__name__": "__main__", "__builtins__": __builtins__})
except SystemExit:
    pass
except Exception as _e:
    _exec_error = f"{type(_e).__name__}: {_e}"

sys.stdout = _old_stdout
sys.stderr = _old_stderr

_out = _captured_out.getvalue()
_err = _captured_err.getvalue()
if _exec_error:
    _err = _exec_error + ("\\n" + _err if _err else "")
_out + "\\n__STDERR__\\n" + _err
`);

      // Parse output: split on __STDERR__ marker
      const parts = result.split('\n__STDERR__\n');
      const stdout = parts[0] || '';
      const stderr = parts[1] || '';

      let output = '';
      if (stdout.trim()) output += stdout;
      if (stderr.trim()) {
        if (output) output += '\n';
        output += stderr;
      }

      if (output.trim()) {
        outputEl.textContent = output.trimEnd();
      } else {
        outputEl.textContent = '(No output — code executed successfully)';
      }

      if (stderr && stderr.trim()) {
        outputEl.classList.add('has-error');
      }

    } catch (err) {
      // Extract the actual Python error message from the Pyodide wrapper
      let msg = err.message || String(err);
      // Clean up Pyodide traceback noise — show just the Python error
      const pyErrMatch = msg.match(/(?:Error|Exception).*$/m);
      outputEl.textContent = 'Error: ' + (pyErrMatch ? pyErrMatch[0] : msg);
      outputEl.classList.add('has-error');
    }

    runBtn.textContent = '▶ Run';
    runBtn.disabled = false;
  }

  /**
   * Update all run buttons (used during Pyodide loading).
   */
  function updateAllRunButtons(text, disabled) {
    document.querySelectorAll('.run-btn').forEach(btn => {
      btn.textContent = text;
      btn.disabled = disabled;
    });
  }

  // =============================================
  //  Code Block Enhancement (Run + Copy buttons)
  // =============================================

  /**
   * Enhance all Python code blocks with Run and Copy buttons.
   */
  function initCodeBlocks() {
    // Find all <pre><code class="language-python"> blocks
    document.querySelectorAll('pre > code.language-python, pre > code[class*="language-python"]').forEach((codeEl, index) => {
      const preEl = codeEl.parentElement;

      // Skip if already wrapped
      if (preEl.parentElement.classList.contains('code-block')) return;

      // Create wrapper
      const wrapper = document.createElement('div');
      wrapper.className = 'code-block';
      wrapper.id = `code-block-${index}`;

      // Create header bar
      const header = document.createElement('div');
      header.className = 'code-header';

      const langTag = document.createElement('span');
      langTag.className = 'language-tag';
      langTag.textContent = 'Python';

      const btnGroup = document.createElement('div');
      btnGroup.className = 'btn-group';
      btnGroup.style.cssText = 'display:flex;gap:6px;';

      // --- Run Button ---
      const runBtn = document.createElement('button');
      runBtn.className = 'run-btn';
      runBtn.textContent = '▶ Run';
      runBtn.title = 'Run this code in your browser';

      // --- Copy Button ---
      const copyBtn = document.createElement('button');
      copyBtn.className = 'copy-btn';
      copyBtn.textContent = 'Copy';
      copyBtn.title = 'Copy to clipboard';

      btnGroup.appendChild(runBtn);
      btnGroup.appendChild(copyBtn);
      header.appendChild(langTag);
      header.appendChild(btnGroup);

      // Create output panel
      const outputEl = document.createElement('pre');
      outputEl.className = 'code-output';
      outputEl.style.display = 'none';

      // Wrap the existing <pre> element
      preEl.parentNode.insertBefore(wrapper, preEl);
      wrapper.appendChild(header);
      wrapper.appendChild(preEl);
      wrapper.appendChild(outputEl);

      // --- Run Button Handler ---
      runBtn.addEventListener('click', () => {
        const code = codeEl.textContent;
        runPythonCode(code, outputEl, runBtn);
      });

      // --- Copy Button Handler ---
      copyBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(codeEl.textContent);
          copyBtn.textContent = '✓ Copied!';
          copyBtn.classList.add('copied');
          setTimeout(() => {
            copyBtn.textContent = 'Copy';
            copyBtn.classList.remove('copied');
          }, 2000);
        } catch (err) {
          const textarea = document.createElement('textarea');
          textarea.value = codeEl.textContent;
          textarea.style.cssText = 'position:fixed;opacity:0';
          document.body.appendChild(textarea);
          textarea.select();
          document.execCommand('copy');
          document.body.removeChild(textarea);
          copyBtn.textContent = '✓ Copied!';
          setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
        }
      });
    });

    // Also handle pre-existing .code-block wrappers
    document.querySelectorAll('.code-block').forEach(block => {
      const copyBtn = block.querySelector('.copy-btn');
      const codeEl = block.querySelector('code');
      if (!copyBtn || !codeEl) return;
      if (copyBtn.dataset.bound) return;
      copyBtn.dataset.bound = 'true';

      copyBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(codeEl.textContent);
          copyBtn.textContent = '✓ Copied!';
          copyBtn.classList.add('copied');
          setTimeout(() => {
            copyBtn.textContent = 'Copy';
            copyBtn.classList.remove('copied');
          }, 2000);
        } catch (err) {}
      });
    });
  }

  // =============================================
  //  Progress Tracking
  // =============================================

  function loadProgress() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : {};
    } catch (e) { return {}; }
  }

  function saveProgress(progress) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(progress)); }
    catch (e) {}
  }

  function markModuleVisited(moduleNum) {
    const progress = loadProgress();
    if (!progress[moduleNum]) {
      progress[moduleNum] = 'in-progress';
    }
    saveProgress(progress);
  }

  function markModuleCompleted(moduleNum) {
    const progress = loadProgress();
    progress[moduleNum] = 'completed';
    saveProgress(progress);
    updateProgressUI();
  }

  function getCompletionPercent() {
    const progress = loadProgress();
    const completed = Object.values(progress).filter(s => s === 'completed').length;
    return Math.round((completed / TOTAL_MODULES) * 100);
  }

  function updateProgressUI() {
    const progress = loadProgress();

    document.querySelectorAll('.module-card').forEach(card => {
      const moduleNum = card.getAttribute('data-module');
      if (!moduleNum) return;
      const badge = card.querySelector('.status-badge');
      if (!badge) return;
      const status = progress[moduleNum] || 'not-started';
      badge.className = 'status-badge ' + status;
      if (status === 'completed') badge.textContent = '✓ Completed';
      else if (status === 'in-progress') badge.textContent = '◉ In Progress';
      else badge.textContent = '○ Not Started';
    });

    const progressFill = document.querySelector('.progress-bar-fill');
    if (progressFill) progressFill.style.width = getCompletionPercent() + '%';

    const progressText = document.querySelector('.progress-text');
    if (progressText) {
      const completed = Object.values(progress).filter(s => s === 'completed').length;
      progressText.textContent = `${completed} of ${TOTAL_MODULES} modules completed (${getCompletionPercent()}%)`;
    }
  }

  // =============================================
  //  Navigation & Active State
  // =============================================

  function initNavigation() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a, .nav-link').forEach(link => {
      const href = link.getAttribute('href');
      if (href && currentPath.includes(href.replace('../pages/', '').replace('.html', ''))) {
        link.classList.add('active');
      }
    });
  }

  // =============================================
  //  Scroll-Based Module Completion Detection
  // =============================================

  function initCompletionDetection() {
    const moduleAttr = document.documentElement.getAttribute('data-module') ||
                       document.body.getAttribute('data-module');
    if (!moduleAttr) return;
    const moduleNum = parseInt(moduleAttr, 10);
    if (isNaN(moduleNum)) return;

    markModuleVisited(moduleNum);

    const takeaways = document.querySelector('.key-takeaways');
    if (!takeaways) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          markModuleCompleted(moduleNum);
          observer.disconnect();
        }
      });
    }, { threshold: 0.5 });
    observer.observe(takeaways);
  }

  // =============================================
  //  Smooth Scroll
  // =============================================

  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  // =============================================
  //  Entrance Animations
  // =============================================

  function initAnimations() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.glass-card, .module-card').forEach(el => {
      observer.observe(el);
    });
  }

  // =============================================
  //  Keyboard Shortcuts
  // =============================================

  function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;

      if (e.key === 'ArrowLeft' && !e.ctrlKey && !e.metaKey) {
        const prevLink = document.querySelector('.module-footer a:first-child');
        if (prevLink && prevLink.getAttribute('href') !== '#') prevLink.click();
      }
      if (e.key === 'ArrowRight' && !e.ctrlKey && !e.metaKey) {
        const nextLink = document.querySelector('.module-footer a:last-child');
        if (nextLink && nextLink.getAttribute('href') !== '#') nextLink.click();
      }
    });
  }

  // =============================================
  //  Initialize Everything
  // =============================================

  function init() {
    initCodeBlocks();
    initNavigation();
    initCompletionDetection();
    initSmoothScroll();
    initAnimations();
    initKeyboardShortcuts();
    updateProgressUI();

    console.log(
      '%c🤖 Python Systems Thinking Training %cv2.1 — Pyodide Engine Fixed',
      'color: #00d4ff; font-weight: bold; font-size: 14px;',
      'color: #00ff88; font-weight: bold; font-size: 14px;'
    );
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
