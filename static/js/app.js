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

      // Pre-install mock modules for imports that won't work in browser
      await pyodideInstance.runPythonAsync(`
import sys
import types

# Mock 'time' module sleep to be a no-op in browser
import time as _real_time
_real_time.sleep = lambda x: None

# Create mock modules for browser-incompatible imports
def _create_mock(name, attrs=None):
    mod = types.ModuleType(name)
    mod.__file__ = f"<mock {name}>"
    if attrs:
        for k, v in attrs.items():
            setattr(mod, k, v)
    return mod

# Mock pygame
pygame_mock = _create_mock('pygame')
pygame_mock.init = lambda: None
pygame_mock.quit = lambda: None
pygame_mock.K_LEFT = 276
pygame_mock.K_RIGHT = 275
pygame_mock.K_UP = 273
pygame_mock.K_DOWN = 274
pygame_mock.K_a = 97
pygame_mock.K_d = 100
pygame_mock.K_w = 119
pygame_mock.K_s = 115
pygame_mock.SRCALPHA = 65536
pygame_mock.QUIT = 256
pygame_mock.KEYDOWN = 768
pygame_mock.K_ESCAPE = 27
pygame_mock.K_c = 99
pygame_mock.K_l = 108
sys.modules['pygame'] = pygame_mock

# Mock google.genai
google_mock = _create_mock('google')
genai_mock = _create_mock('google.genai')
types_mock = _create_mock('google.genai.types')
google_mock.genai = genai_mock
sys.modules['google'] = google_mock
sys.modules['google.genai'] = genai_mock
sys.modules['google.genai.types'] = types_mock
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
   */
  async function runPythonCode(code, outputEl, runBtn) {
    runBtn.textContent = '⏳ Running...';
    runBtn.disabled = true;
    outputEl.style.display = 'block';
    outputEl.textContent = '';

    try {
      const pyodide = await loadPyodideEngine();

      // Redirect stdout/stderr to capture output
      await pyodide.runPythonAsync(`
import sys
from io import StringIO
_captured_out = StringIO()
_captured_err = StringIO()
sys.stdout = _captured_out
sys.stderr = _captured_err
      `);

      // Clean the code: remove interactive elements that break in browser
      let cleanCode = code
        // Replace input() calls with mock values
        .replace(/(\w+)\s*=\s*input\([^)]*\)/g, '$1 = "72"')
        // Remove sys.exit() calls
        .replace(/sys\.exit\(\d*\)/g, 'pass')
        // Remove exit() calls
        .replace(/\bexit\(\d*\)/g, 'pass');

      // Wrap in try/except to catch runtime errors gracefully
      const wrappedCode = `
try:
${cleanCode.split('\n').map(line => '    ' + line).join('\n')}
except SystemExit:
    pass
except Exception as _e:
    print(f"Error: {type(_e).__name__}: {_e}")
`;

      await pyodide.runPythonAsync(wrappedCode);

      // Get captured output
      const stdout = await pyodide.runPythonAsync(`_captured_out.getvalue()`);
      const stderr = await pyodide.runPythonAsync(`_captured_err.getvalue()`);

      // Reset stdout/stderr
      await pyodide.runPythonAsync(`
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
      `);

      let output = '';
      if (stdout) output += stdout;
      if (stderr) output += '\n' + stderr;

      if (output.trim()) {
        outputEl.textContent = output.trimEnd();
      } else {
        outputEl.textContent = '(No output — code executed successfully)';
      }

      // Color output based on errors
      if (stderr && stderr.trim()) {
        outputEl.classList.add('has-error');
      } else {
        outputEl.classList.remove('has-error');
      }

    } catch (err) {
      outputEl.textContent = `Execution Error: ${err.message}`;
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
      '%c🤖 Python Systems Thinking Training %cv2.0 — Pyodide Enabled',
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
