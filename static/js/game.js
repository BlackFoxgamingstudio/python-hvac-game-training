/**
 * ═══════════════════════════════════════════════════════════════
 *  ROBOT HVAC GAME ENGINE — HTML5 Canvas
 *  Python Systems Thinking: From HVAC to Game Engine
 * ═══════════════════════════════════════════════════════════════
 *
 *  This is the real, playable game that runs in the browser.
 *  Same logic as the Python OOP lessons — Robot, AirConditioner,
 *  evaporator/compressor/condenser/expansion valve cycle.
 *
 *  Controls:
 *    WASD / Arrow Keys  — Move robot
 *    Shift + Move       — Run (more heat)
 *    Space              — Toggle AC
 *    T                  — Toggle telemetry HUD
 *    R                  — Reset
 * ═══════════════════════════════════════════════════════════════
 */

(function () {
  'use strict';

  // ─── COLORS ──────────────────────────────────────────────
  const C = {
    bg:       '#0e1017',
    grid:     '#1a1d2a',
    gridHi:   '#242838',
    white:    '#e8eaf0',
    green:    '#3cd868',
    greenDk:  '#28a04a',
    orange:   '#ff9f33',
    red:      '#ef4444',
    cyan:     '#22d3ee',
    cyanGlow: 'rgba(34,211,238,0.25)',
    blue:     '#3b82f6',
    yellow:   '#facc15',
    panel:    'rgba(10,12,22,0.88)',
    panelBd:  'rgba(34,211,238,0.2)',
    coolPart: '#60a5fa',
    heatPart: '#fb923c',
  };

  // ─── PARTICLE SYSTEM ─────────────────────────────────────
  class Particle {
    constructor(x, y, type) {
      this.x = x;
      this.y = y;
      this.type = type; // 'heat' | 'cool' | 'exhaust'
      this.life = 1.0;
      const angle = Math.random() * Math.PI * 2;
      const speed = 0.4 + Math.random() * 1.2;
      this.vx = Math.cos(angle) * speed;
      this.vy = Math.sin(angle) * speed - (type === 'heat' ? 1.2 : 0.4);
      this.size = 2 + Math.random() * 3;
      this.decay = 0.012 + Math.random() * 0.018;
    }
    update() {
      this.x += this.vx;
      this.y += this.vy;
      this.life -= this.decay;
      if (this.type === 'heat') this.vy -= 0.03;
      if (this.type === 'cool') { this.vy += 0.01; this.vx *= 0.98; }
    }
    draw(ctx) {
      const a = Math.max(0, this.life);
      if (this.type === 'heat') {
        ctx.fillStyle = `rgba(251,146,60,${a * 0.7})`;
      } else if (this.type === 'cool') {
        ctx.fillStyle = `rgba(96,165,250,${a * 0.8})`;
      } else {
        ctx.fillStyle = `rgba(100,100,120,${a * 0.4})`;
      }
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size * a, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // ─── AIR CONDITIONER (same logic as Python) ──────────────
  class AirConditioner {
    constructor(unitId) {
      this.unitId = unitId;
      this.cycleCount = 0;
      this.isRunning = false;
      this.coolingPower = 0.35;
      this.faultMode = 'NONE'; // 'NONE' | 'LOW_CHARGE' | 'DIRTY_CONDENSER' | 'STUCK_VALVE'
      
      // Live pressures and temperatures (Equalized at startup)
      this.suctionPressure = 150;
      this.dischargePressure = 150;
      this.superheat = 0;
      this.subcooling = 0;
      this.evaporatorTemp = 72;
      this.condenserTemp = 95;
      this.deltaT = 0;
      this.tickCount = 0;
    }

    update(isActive, currentTemp, outdoorTemp = 95) {
      this.isRunning = isActive;
      this.tickCount++;

      if (!isActive) {
        // Equalize pressures back to ambient when system is OFF
        this.suctionPressure += (150 - this.suctionPressure) * 0.05;
        this.dischargePressure += (150 - this.dischargePressure) * 0.05;
        this.superheat += (0 - this.superheat) * 0.05;
        this.subcooling += (0 - this.subcooling) * 0.05;
        this.evaporatorTemp += (currentTemp - this.evaporatorTemp) * 0.05;
        this.condenserTemp += (outdoorTemp - this.condenserTemp) * 0.05;
        this.deltaT += (0 - this.deltaT) * 0.05;
        return currentTemp;
      }

      // Dynamic oscillation to look like real live telemetry
      const noise = Math.sin(this.tickCount * 0.05);

      if (this.faultMode === 'NONE') {
        this.coolingPower = 0.35;
        this.suctionPressure += (70 + noise * 1 - this.suctionPressure) * 0.08;
        this.dischargePressure += (410 + noise * 3 - this.dischargePressure) * 0.08;
        this.superheat += (10.0 + noise * 0.3 - this.superheat) * 0.08;
        this.subcooling += (12.0 + noise * 0.4 - this.subcooling) * 0.08;
        this.evaporatorTemp += (42.0 - this.evaporatorTemp) * 0.08;
        this.condenserTemp += (95.0 - this.condenserTemp) * 0.08;
        this.deltaT += (18.0 + noise * 0.2 - this.deltaT) * 0.08;
      } else if (this.faultMode === 'LOW_CHARGE') {
        this.coolingPower = 0.12;
        this.suctionPressure += (45 + noise * 0.8 - this.suctionPressure) * 0.08;
        this.dischargePressure += (310 + noise * 2 - this.dischargePressure) * 0.08;
        this.superheat += (28.0 + noise * 0.8 - this.superheat) * 0.08; // High superheat
        this.subcooling += (3.0 + noise * 0.2 - this.subcooling) * 0.08;  // Low subcooling
        this.evaporatorTemp += (30.0 - this.evaporatorTemp) * 0.08; // Low evap temp (frozen)
        this.condenserTemp += (85.0 - this.condenserTemp) * 0.08;
        this.deltaT += (8.0 + noise * 0.2 - this.deltaT) * 0.08;
      } else if (this.faultMode === 'DIRTY_CONDENSER') {
        this.coolingPower = 0.08;
        this.suctionPressure += (85 + noise * 1.5 - this.suctionPressure) * 0.08;
        this.dischargePressure += (485 + noise * 5 - this.dischargePressure) * 0.08; // High head
        this.superheat += (6.0 + noise * 0.2 - this.superheat) * 0.08;
        this.subcooling += (4.0 + noise * 0.3 - this.subcooling) * 0.08;
        this.evaporatorTemp += (50.0 - this.evaporatorTemp) * 0.08;
        this.condenserTemp += (125.0 - this.condenserTemp) * 0.08; // Hot condenser
        this.deltaT += (9.0 + noise * 0.2 - this.deltaT) * 0.08;
      } else if (this.faultMode === 'STUCK_VALVE') {
        this.coolingPower = 0.04;
        this.suctionPressure += (35 + noise * 0.5 - this.suctionPressure) * 0.08;
        this.dischargePressure += (290 + noise * 2 - this.dischargePressure) * 0.08;
        this.superheat += (35.0 + noise * 1.0 - this.superheat) * 0.08;
        this.subcooling += (15.0 + noise * 0.5 - this.subcooling) * 0.08;
        this.evaporatorTemp += (24.0 - this.evaporatorTemp) * 0.08; // Coil freezes
        this.condenserTemp += (80.0 - this.condenserTemp) * 0.08;
        this.deltaT += (4.0 + noise * 0.1 - this.deltaT) * 0.08;
      }

      return Math.max(65.0, currentTemp - this.coolingPower);
    }
    stop() { this.isRunning = false; }
  }

  // ─── ROBOT ───────────────────────────────────────────────
  class Robot {
    constructor(x, y, name) {
      this.name = name;
      this.x = x;
      this.y = y;
      this.w = 44;
      this.h = 54;
      this.speed = 3;
      this.internalTemp = 72;
      this.maxTemp = 105;
      this.steps = 0;
      this.direction = 'right';
      this.ac = new AirConditioner(`${name}-AC`);
      this.acActive = false;
      this.bobPhase = 0;
      this.eyeBlink = 0;
      this.trailX = x;
      this.trailY = y;
    }

    update(keys, bounds, particles) {
      const shift = keys['ShiftLeft'] || keys['ShiftRight'];
      const spd = shift ? this.speed * 2.2 : this.speed;
      const heat = shift ? 0.22 : 0.08;
      let moved = false;

      if (keys['ArrowLeft'] || keys['KeyA'])  { this.x -= spd; this.direction = 'left';  moved = true; }
      if (keys['ArrowRight'] || keys['KeyD']) { this.x += spd; this.direction = 'right'; moved = true; }
      if (keys['ArrowUp'] || keys['KeyW'])    { this.y -= spd; this.direction = 'up';    moved = true; }
      if (keys['ArrowDown'] || keys['KeyS'])  { this.y += spd; this.direction = 'down';  moved = true; }

      // Clamp to bounds
      this.x = Math.max(5, Math.min(bounds.w - this.w - 5, this.x));
      this.y = Math.max(60, Math.min(bounds.h - this.h - 50, this.y));

      if (moved) {
        this.steps++;
        this.internalTemp += heat;
        // Heat particles when running
        if (shift && Math.random() < 0.4) {
          particles.push(new Particle(this.x + this.w / 2, this.y + this.h, 'heat'));
        }
      }

      // Passive cooling
      if (this.internalTemp > 68) this.internalTemp -= 0.012;

      // AC cooling
      if (this.acActive) {
        if (!this.ac.isRunning) {
          this.ac.cycleCount++;
        }
        this.internalTemp = this.ac.update(true, this.internalTemp);
        // Cool particles
        if (Math.random() < 0.5) {
          particles.push(new Particle(
            this.x + this.w / 2 + (Math.random() - 0.5) * 20,
            this.y + 10,
            'cool'
          ));
        }
        if (this.internalTemp <= 70) {
          this.acActive = false;
          this.ac.stop();
        }
      } else {
        this.ac.update(false, this.internalTemp);
      }

      this.internalTemp = Math.max(40, Math.min(this.maxTemp, this.internalTemp));
      this.bobPhase += 0.06;
      this.eyeBlink = (this.eyeBlink + 1) % 180;

      // Smooth trail
      this.trailX += (this.x - this.trailX) * 0.15;
      this.trailY += (this.y - this.trailY) * 0.15;
    }

    toggleAC() {
      this.acActive = !this.acActive;
      if (!this.acActive) this.ac.stop();
    }

    injectFault(faultMode) {
      this.ac.faultMode = faultMode;
      // If we inject a fault, activate AC to demonstrate the thermodynamic feedback
      if (faultMode !== 'NONE') {
        this.acActive = true;
      }
    }

    getColor() {
      if (this.internalTemp >= 92) return C.red;
      if (this.internalTemp >= 80) return C.orange;
      return C.green;
    }

    draw(ctx) {
      const bob = Math.sin(this.bobPhase) * 2;
      const cx = this.x;
      const cy = this.y + bob;
      const color = this.getColor();

      // Shadow
      ctx.fillStyle = 'rgba(0,0,0,0.3)';
      ctx.beginPath();
      ctx.ellipse(cx + this.w / 2, this.y + this.h + 4, this.w / 2 - 2, 6, 0, 0, Math.PI * 2);
      ctx.fill();

      // Body glow
      ctx.shadowColor = color;
      ctx.shadowBlur = 18;

      // Body
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.roundRect(cx, cy, this.w, this.h, 8);
      ctx.fill();

      // Body outline
      ctx.strokeStyle = C.white;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(cx, cy, this.w, this.h, 8);
      ctx.stroke();

      ctx.shadowBlur = 0;

      // Visor (dark strip for eyes)
      ctx.fillStyle = 'rgba(0,0,0,0.45)';
      ctx.beginPath();
      ctx.roundRect(cx + 4, cy + 10, this.w - 8, 16, 4);
      ctx.fill();

      // Eyes
      const eyeY = cy + 18;
      const blinking = this.eyeBlink > 175;
      const eyeH = blinking ? 1 : 6;
      const eyeW = 7;

      // Left eye
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.roundRect(cx + 9, eyeY - eyeH / 2, eyeW, eyeH, 2);
      ctx.fill();

      // Right eye
      ctx.beginPath();
      ctx.roundRect(cx + this.w - 9 - eyeW, eyeY - eyeH / 2, eyeW, eyeH, 2);
      ctx.fill();

      if (!blinking) {
        // Pupils
        const pupilOff = this.direction === 'left' ? -1.5 : this.direction === 'right' ? 1.5 : 0;
        const pupilOffY = this.direction === 'up' ? -1.5 : this.direction === 'down' ? 1.5 : 0;
        ctx.fillStyle = '#111';
        ctx.beginPath();
        ctx.arc(cx + 12.5 + pupilOff, eyeY + pupilOffY, 2, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(cx + this.w - 12.5 + pupilOff, eyeY + pupilOffY, 2, 0, Math.PI * 2);
        ctx.fill();
      }

      // Chest panel (HVAC indicator)
      ctx.fillStyle = this.acActive ? 'rgba(34,211,238,0.35)' : 'rgba(255,255,255,0.08)';
      ctx.beginPath();
      ctx.roundRect(cx + 10, cy + 30, this.w - 20, 14, 3);
      ctx.fill();
      ctx.strokeStyle = this.acActive ? C.cyan : 'rgba(255,255,255,0.15)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // AC snowflake icon
      if (this.acActive) {
        ctx.fillStyle = C.cyan;
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('❄', cx + this.w / 2, cy + 41);
      }

      // Name plate
      ctx.fillStyle = C.white;
      ctx.font = 'bold 11px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(this.name, cx + this.w / 2, cy - 6);
    }

    getTelemetry() {
      return {
        name: this.name,
        x: Math.round(this.x),
        y: Math.round(this.y),
        temp: this.internalTemp,
        acRunning: this.acActive,
        acCycles: this.ac.cycleCount,
        steps: this.steps,
        direction: this.direction,
        fault: this.ac.faultMode,
        suction_psi: Math.round(this.ac.suctionPressure),
        discharge_psi: Math.round(this.ac.dischargePressure),
        superheat: Number(this.ac.superheat.toFixed(1)),
        subcooling: Number(this.ac.subcooling.toFixed(1)),
        evap_temp: Number(this.ac.evaporatorTemp.toFixed(1)),
        cond_temp: Number(this.ac.condenserTemp.toFixed(1)),
        delta_t: Number(this.ac.deltaT.toFixed(1))
      };
    }
  }

  // ─── NPC CLASS ───────────────────────────────────────────
  class NPC {
    constructor(id, name, x, y, faction, description) {
      this.id = id;
      this.name = name;
      this.x = x;
      this.y = y;
      this.w = 32;
      this.h = 44;
      this.faction = faction;
      this.description = description;
      this.bobPhase = Math.random() * Math.PI;
      this.dialogueActive = false;
      this.calibrated = false;
    }
    update(player, particles) {
      this.bobPhase += 0.04;
      const dx = (this.x + this.w / 2) - (player.x + player.w / 2);
      const dy = (this.y + this.h / 2) - (player.y + player.h / 2);
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 55) {
        this.dialogueActive = true;
        if (!this.calibrated && Math.random() < 0.15) {
          // Emit sparks particles
          for (let k = 0; k < 3; k++) {
            particles.push(new Particle(this.x + this.w / 2, this.y + this.h / 2, 'cool'));
          }
        }
      } else {
        this.dialogueActive = false;
      }
    }
    draw(ctx) {
      const bob = Math.sin(this.bobPhase) * 1.5;
      const cx = this.x;
      const cy = this.y + bob;

      // Shadow
      ctx.fillStyle = 'rgba(0,0,0,0.2)';
      ctx.beginPath();
      ctx.ellipse(cx + this.w / 2, this.y + this.h + 2, this.w / 2 - 2, 4, 0, 0, Math.PI * 2);
      ctx.fill();

      // Faction coloring
      ctx.fillStyle = this.faction === 'BAS Guild' ? '#8b5cf6' : this.faction === 'Refrigeration Scholars' ? '#3b82f6' : '#f97316';
      ctx.beginPath();
      ctx.roundRect(cx, cy, this.w, this.h, 6);
      ctx.fill();

      ctx.strokeStyle = C.white;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Name Label
      ctx.fillStyle = C.white;
      ctx.font = 'bold 9px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(this.name, cx + this.w / 2, cy - 4);

      // Dialogue bubble
      if (this.dialogueActive) {
        ctx.fillStyle = 'rgba(10,12,22,0.92)';
        ctx.strokeStyle = C.cyan;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(cx - 100, cy - 50, 232, 40, 6);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = C.white;
        ctx.font = '7.5px Inter, sans-serif';
        ctx.textAlign = 'center';
        
        // Wrap description to fit dialogue bubble width
        const descWords = this.description.split(' ');
        let line1 = '', line2 = '', line3 = '';
        descWords.forEach((word, idx) => {
          if (idx < 6) line1 += word + ' ';
          else if (idx < 13) line2 += word + ' ';
          else line3 += word + ' ';
        });

        ctx.fillText(line1.trim(), cx + this.w / 2, cy - 38);
        if (line2) ctx.fillText(line2.trim(), cx + this.w / 2, cy - 28);
        if (line3) ctx.fillText(line3.trim(), cx + this.w / 2, cy - 18);
      }
    }
  }

  // ─── HUD ─────────────────────────────────────────────────
  function drawHUD(ctx, telemetry, W, H, showTelemetry) {
    // Top bar
    ctx.fillStyle = 'rgba(10,12,22,0.92)';
    ctx.fillRect(0, 0, W, 52);
    ctx.strokeStyle = C.panelBd;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, 52);
    ctx.lineTo(W, 52);
    ctx.stroke();

    // Title
    ctx.fillStyle = C.cyan;
    ctx.font = 'bold 16px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('🤖 Robot HVAC Simulation', 14, 22);

    // Controls hint
    ctx.fillStyle = 'rgba(255,255,255,0.35)';
    ctx.font = '11px Inter, sans-serif';
    ctx.fillText('WASD: Move | Shift: Run | Space: AC | T: HUD | R: Reset', 14, 40);

    // Temperature bar (bottom)
    const barY = H - 32;
    const barW = W - 20;
    const barH = 12;
    const tempPct = Math.min(1, telemetry.temp / 105);

    // Bar background
    ctx.fillStyle = 'rgba(255,255,255,0.06)';
    ctx.beginPath();
    ctx.roundRect(10, barY, barW, barH, 4);
    ctx.fill();

    // Bar fill with gradient
    const grad = ctx.createLinearGradient(10, 0, 10 + barW, 0);
    grad.addColorStop(0, C.blue);
    grad.addColorStop(0.4, C.green);
    grad.addColorStop(0.7, C.orange);
    grad.addColorStop(1, C.red);
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.roundRect(10, barY, barW * tempPct, barH, 4);
    ctx.fill();

    // Temp label
    const tempColor = telemetry.temp >= 92 ? C.red : telemetry.temp >= 80 ? C.orange : C.green;
    ctx.fillStyle = tempColor;
    ctx.font = 'bold 12px Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(`${telemetry.temp.toFixed(1)}°F`, W - 14, barY - 4);

    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Internal Temperature', 14, barY - 4);

    // AC status badge
    if (telemetry.acRunning) {
      ctx.fillStyle = 'rgba(34,211,238,0.15)';
      ctx.beginPath();
      ctx.roundRect(W - 100, 8, 86, 20, 10);
      ctx.fill();
      ctx.strokeStyle = C.cyan;
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.fillStyle = C.cyan;
      ctx.font = 'bold 11px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('❄ AC ACTIVE', W - 57, 22);
    }

    // Telemetry panel
    if (showTelemetry) {
      const pw = 200, ph = 210;
      const px = W - pw - 12, py = 60;

      // Panel background
      ctx.fillStyle = C.panel;
      ctx.beginPath();
      ctx.roundRect(px, py, pw, ph, 10);
      ctx.fill();
      ctx.strokeStyle = C.panelBd;
      ctx.lineWidth = 1;
      ctx.stroke();

      // Panel title
      ctx.fillStyle = C.cyan;
      ctx.font = 'bold 13px Inter, sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText('📡 TELEMETRY', px + 12, py + 22);

      // Divider
      ctx.strokeStyle = 'rgba(255,255,255,0.08)';
      ctx.beginPath();
      ctx.moveTo(px + 12, py + 30);
      ctx.lineTo(px + pw - 12, py + 30);
      ctx.stroke();

      const lines = [
        [`Temperature`, `${telemetry.temp.toFixed(1)}°F`, tempColor],
        [`Suction Press.`, `${telemetry.suction_psi} PSI`, C.white],
        [`Discharge Press.`, `${telemetry.discharge_psi} PSI`, telemetry.discharge_psi > 450 ? C.red : C.white],
        [`Superheat`, `${telemetry.superheat}°F`, telemetry.superheat > 20 ? C.orange : C.white],
        [`Subcooling`, `${telemetry.subcooling}°F`, telemetry.subcooling < 5 ? C.orange : C.white],
        [`Delta-T`, `${telemetry.delta_t}°F`, C.white],
        [`AC System`, telemetry.acRunning ? 'ON' : 'OFF', telemetry.acRunning ? C.cyan : 'rgba(255,255,255,0.4)'],
        [`Active Fault`, telemetry.fault === 'NONE' ? '🟢 NONE' : `🚨 ${telemetry.fault.replace('_', ' ')}`, telemetry.fault === 'NONE' ? C.green : C.red],
      ];

      lines.forEach((line, i) => {
        const ly = py + 48 + i * 20;
        ctx.fillStyle = 'rgba(255,255,255,0.45)';
        ctx.font = '11px Inter, sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(line[0], px + 12, ly);
        ctx.fillStyle = line[2];
        ctx.font = 'bold 11px Inter, sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(line[1], px + pw - 12, ly);
      });
    }
  }

  // ─── GRID ────────────────────────────────────────────────
  function drawGrid(ctx, W, H, frame) {
    ctx.fillStyle = C.bg;
    ctx.fillRect(0, 0, W, H);

    const spacing = 40;
    for (let x = 0; x <= W; x += spacing) {
      ctx.strokeStyle = (x % (spacing * 4) === 0) ? C.gridHi : C.grid;
      ctx.lineWidth = (x % (spacing * 4) === 0) ? 0.8 : 0.4;
      ctx.beginPath();
      ctx.moveTo(x, 52);
      ctx.lineTo(x, H - 40);
      ctx.stroke();
    }
    for (let y = 52; y <= H - 40; y += spacing) {
      ctx.strokeStyle = (y % (spacing * 4) < spacing) ? C.gridHi : C.grid;
      ctx.lineWidth = ((y - 52) % (spacing * 4) === 0) ? 0.8 : 0.4;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }
  }

  // ─── MAIN GAME INIT ─────────────────────────────────────
  function initGame(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;

    let robot = new Robot(W / 2 - 22, H / 2 - 27, 'Atlas');
    canvas.robotRef = robot;
    let particles = [];
    let keys = {};
    let showTelemetry = true;
    let frame = 0;

    let npcs = [
      new NPC('NPC-001', 'Agent Clog-001', 103, 152, 'BAS Guild', 'NPC-001 verifies that sparks particle emitter vectors is calibrated by calibratesing options to animate sweeping dial pointer sweeps.')
    ];

    // Key handlers
    const handleKeyDown = (e) => {
      keys[e.code] = true;
      if (e.code === 'Space') { e.preventDefault(); robot.toggleAC(); }
      if (e.code === 'KeyT') showTelemetry = !showTelemetry;
      if (e.code === 'KeyR') {
        robot = new Robot(W / 2 - 22, H / 2 - 27, 'Atlas');
        canvas.robotRef = robot;
        particles = [];
      }
    };
    const handleKeyUp = (e) => { keys[e.code] = false; };

    // Focus handling
    canvas.tabIndex = 1;
    canvas.addEventListener('keydown', handleKeyDown);
    canvas.addEventListener('keyup', handleKeyUp);
    canvas.addEventListener('click', () => canvas.focus());

    // Also listen globally when canvas is focused
    canvas.addEventListener('focus', () => {
      canvas.style.outline = `2px solid ${C.cyan}`;
      canvas.style.outlineOffset = '2px';
    });
    canvas.addEventListener('blur', () => {
      canvas.style.outline = 'none';
      keys = {};
    });

    // Game loop
    function gameLoop() {
      frame++;

      // Update
      robot.update(keys, { w: W, h: H }, particles);
      npcs.forEach(n => n.update(robot, particles));

      // Update particles
      particles = particles.filter(p => p.life > 0);
      particles.forEach(p => p.update());

      // Overheat particles
      if (robot.internalTemp >= 90 && Math.random() < 0.3) {
        particles.push(new Particle(
          robot.x + Math.random() * robot.w,
          robot.y + robot.h - 5,
          'heat'
        ));
      }

      // Draw
      drawGrid(ctx, W, H, frame);

      // Particles behind robot
      particles.forEach(p => p.draw(ctx));

      // NPCs
      npcs.forEach(n => n.draw(ctx));

      // Robot
      robot.draw(ctx);

      // HUD
      drawHUD(ctx, robot.getTelemetry(), W, H, showTelemetry);

      requestAnimationFrame(gameLoop);
    }

    // Start
    canvas.focus();
    gameLoop();
  }

  // Expose
  window.RobotHVACGame = { init: initGame };
})();
