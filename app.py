"""
SOC DEMO APPLICATION - INTENTIONALLY VULNERABLE
================================================
WARNING: This application contains INTENTIONAL security vulnerabilities
for educational/demonstration purposes ONLY.

Vulnerabilities included:
1. SQL INJECTION - Login form uses raw string concatenation in SQL queries
2. XSS (Cross-Site Scripting) - User input rendered unescaped in dashboard
3. No CSRF protection
4. Plaintext passwords in database
5. Verbose error messages exposing DB structure

DO NOT deploy this in any production environment.
"""

from flask import Flask, request, session, redirect, url_for, render_template_string, jsonify
import mysql.connector
import json
import random
import time
import jwt
import datetime
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Weak secret key - vulnerability

# ─── DB CONFIG ───────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "jackjack",
    "database": "soc_demo"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ─── LOGIN PAGE ───────────────────────────────────────────────────────────────
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OAC CYBER FORENSICS Portal — Login</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #050a0f;
    --surface: #0a1520;
    --border: #0d2235;
    --accent: #00d4ff;
    --accent2: #ff3c00;
    --text: #c8e6f5;
    --muted: #4a7a99;
    --danger: #ff3c00;
    --success: #00ff88;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: var(--bg);
    font-family: 'Rajdhani', sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
  }

  /* Animated grid background */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    animation: gridMove 20s linear infinite;
  }
  @keyframes gridMove {
    0% { transform: translateY(0); }
    100% { transform: translateY(40px); }
  }

  /* Scan line effect */
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.08) 2px,
      rgba(0,0,0,0.08) 4px
    );
    pointer-events: none;
    z-index: 999;
  }

  .corner-deco {
    position: fixed;
    width: 200px;
    height: 200px;
    pointer-events: none;
  }
  .corner-deco.tl { top: 0; left: 0; border-top: 2px solid var(--accent); border-left: 2px solid var(--accent); opacity: 0.3; }
  .corner-deco.tr { top: 0; right: 0; border-top: 2px solid var(--accent); border-right: 2px solid var(--accent); opacity: 0.3; }
  .corner-deco.bl { bottom: 0; left: 0; border-bottom: 2px solid var(--accent); border-left: 2px solid var(--accent); opacity: 0.3; }
  .corner-deco.br { bottom: 0; right: 0; border-bottom: 2px solid var(--accent); border-right: 2px solid var(--accent); opacity: 0.3; }

  .login-wrapper {
    position: relative;
    z-index: 10;
    width: 420px;
  }

  .org-header {
    text-align: center;
    margin-bottom: 32px;
  }
  .org-logo {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }
  .logo-icon {
    width: 48px;
    height: 48px;
    border: 2px solid var(--accent);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0,212,255,0.05);
    box-shadow: 0 0 20px rgba(0,212,255,0.2);
  }
  .logo-icon svg { width: 28px; height: 28px; fill: none; stroke: var(--accent); stroke-width: 1.5; }
  .org-name {
    font-family: 'Share Tech Mono', monospace;
    font-size: 22px;
    color: var(--accent);
    letter-spacing: 4px;
    text-shadow: 0 0 20px rgba(0,212,255,0.5);
  }
  .org-sub {
    font-size: 11px;
    letter-spacing: 6px;
    color: var(--muted);
    text-transform: uppercase;
    margin-top: 4px;
  }

  .login-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent);
    padding: 36px;
    position: relative;
    clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 0 100%);
  }
  .login-card::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 20px; height: 20px;
    background: var(--accent);
    clip-path: polygon(0 0, 100% 100%, 100% 0);
    opacity: 0.6;
  }

  .status-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 28px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }
  .status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 8px var(--success);
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }
  .status-text {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 2px;
  }
  .status-time {
    margin-left: auto;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: var(--muted);
  }

  h2 {
    font-size: 14px;
    font-weight: 600;
    color: var(--muted);
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 24px;
  }

  .field {
    margin-bottom: 20px;
  }
  label {
    display: block;
    font-size: 11px;
    letter-spacing: 3px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 8px;
    font-family: 'Share Tech Mono', monospace;
  }
  input[type=text], input[type=password] {
    width: 100%;
    background: rgba(0,212,255,0.03);
    border: 1px solid var(--border);
    border-bottom: 1px solid rgba(0,212,255,0.3);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    font-size: 14px;
    padding: 12px 14px;
    outline: none;
    transition: all 0.2s;
    letter-spacing: 1px;
  }
  input:focus {
    border-color: rgba(0,212,255,0.6);
    background: rgba(0,212,255,0.06);
    box-shadow: 0 0 15px rgba(0,212,255,0.1);
  }

  .btn-login {
    width: 100%;
    padding: 14px;
    background: transparent;
    border: 1px solid var(--accent);
    color: var(--accent);
    font-family: 'Rajdhani', sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 5px;
    text-transform: uppercase;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
    margin-top: 8px;
  }
  .btn-login::before {
    content: '';
    position: absolute;
    left: -100%;
    top: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.15), transparent);
    transition: left 0.4s;
  }
  .btn-login:hover::before { left: 100%; }
  .btn-login:hover {
    background: rgba(0,212,255,0.1);
    box-shadow: 0 0 20px rgba(0,212,255,0.3);
  }

  .error-box {
    background: rgba(255,60,0,0.08);
    border: 1px solid rgba(255,60,0,0.4);
    padding: 10px 14px;
    margin-bottom: 20px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: var(--danger);
    letter-spacing: 1px;
  }

  .hint-box {
    margin-top: 20px;
    padding: 12px;
    background: rgba(0,255,136,0.03);
    border: 1px solid rgba(0,255,136,0.1);
    border-left: 2px solid rgba(0,255,136,0.3);
  }
  .hint-box p {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: rgba(0,255,136,0.5);
    letter-spacing: 1px;
    margin-bottom: 4px;
  }
  .hint-box p:last-child { margin-bottom: 0; }

  .footer-info {
    margin-top: 20px;
    text-align: center;
  }
  .footer-info span {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: rgba(74,122,153,0.4);
    letter-spacing: 2px;
  }
</style>
</head>
<body>
<div class="corner-deco tl"></div>
<div class="corner-deco tr"></div>
<div class="corner-deco bl"></div>
<div class="corner-deco br"></div>

<div class="login-wrapper">
  <div class="org-header">
    <div class="org-logo">
      <div class="logo-icon">
        <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
      </div>
      <div class="org-name">OAC CYBER FORENSICS-SOC</div>
    </div>
    <div class="org-sub">Security Operations Center</div>
  </div>

  <div class="login-card">
    <div class="status-bar">
      <div class="status-dot"></div>
      <span class="status-text">SYSTEMS NOMINAL</span>
      <span class="status-time" id="clock">--:--:--</span>
    </div>

    <h2>Operator Authentication</h2>

    {% if error %}
    <div class="error-box">
      ⚠ {{ error }}
    </div>
    {% endif %}

    <form method="POST" action="/login">
      <div class="field">
        <label>Operator ID</label>
        <input type="text" name="username" placeholder="Enter username" autocomplete="off">
      </div>
      <div class="field">
        <label>Access Code</label>
        <input type="password" name="password" placeholder="••••••••••">
      </div>
      <button type="submit" class="btn-login">Authenticate</button>
    </form>

    <div class="hint-box">
      <p>// DEMO CREDENTIALS:</p>
      <p>// admin / admin123</p>
      <p>// analyst / analyst456</p>
      <p>// SQLi: ' OR '1'='1' --</p>
    </div>
  </div>

  <div class="footer-info">
    <span>NEXUS-SOC v3.1.4 &nbsp;|&nbsp; CLASSIFIED SYSTEM &nbsp;|&nbsp; AUTHORIZED ACCESS ONLY</span>
  </div>
</div>

<script>
function tick() {
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toTimeString().slice(0,8);
}
tick(); setInterval(tick, 1000);
</script>
</body>
</html>
"""

# ─── DASHBOARD PAGE ───────────────────────────────────────────────────────────
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OAC CYBER FORENSICS-SOC — Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #050a0f;
    --bg2: #070d15;
    --surface: #0a1520;
    --surface2: #0d1a28;
    --border: #0d2235;
    --border2: #112840;
    --accent: #00d4ff;
    --accent2: #ff3c00;
    --yellow: #ffd700;
    --green: #00ff88;
    --purple: #a855f7;
    --text: #c8e6f5;
    --muted: #4a7a99;
    --danger: #ff3c00;
    --warn: #ffaa00;
    --info: #00d4ff;
    --critical: #ff0055;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: var(--bg);
    font-family: 'Rajdhani', sans-serif;
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* scanlines */
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.05) 2px, rgba(0,0,0,0.05) 4px);
    pointer-events: none;
    z-index: 9999;
  }

  /* ── TOP NAV ── */
  .topnav {
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    padding: 0 24px;
    height: 56px;
    display: flex;
    align-items: center;
    gap: 20px;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-right: 8px;
  }
  .nav-logo svg { width: 22px; height: 22px; stroke: var(--accent); fill: none; stroke-width: 1.5; }
  .nav-logo-text {
    font-family: 'Share Tech Mono', monospace;
    font-size: 16px;
    color: var(--accent);
    letter-spacing: 3px;
    text-shadow: 0 0 15px rgba(0,212,255,0.4);
  }
  .nav-divider { width: 1px; height: 28px; background: var(--border); }
  .nav-tabs { display: flex; gap: 2px; }
  .nav-tab {
    padding: 6px 16px;
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.2s;
    font-weight: 600;
  }
  .nav-tab.active {
    color: var(--accent);
    border-color: rgba(0,212,255,0.3);
    background: rgba(0,212,255,0.05);
  }
  .nav-tab:hover:not(.active) { color: var(--text); }

  .nav-right { margin-left: auto; display: flex; align-items: center; gap: 16px; }
  .threat-level {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 12px;
    border: 1px solid rgba(255,170,0,0.4);
    background: rgba(255,170,0,0.06);
  }
  .threat-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--warn); box-shadow: 0 0 8px var(--warn); animation: pulse 1.5s infinite; }
  @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.3; } }
  .threat-label { font-family: 'Share Tech Mono', monospace; font-size: 11px; color: var(--warn); letter-spacing: 2px; }

  .nav-user {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .user-avatar {
    width: 30px; height: 30px;
    border: 1px solid var(--accent);
    background: rgba(0,212,255,0.1);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: var(--accent);
  }
  .user-name { font-size: 13px; color: var(--text); font-weight: 600; letter-spacing: 1px; }
  .nav-clock { font-family: 'Share Tech Mono', monospace; font-size: 12px; color: var(--muted); letter-spacing: 2px; }

  .logout-btn {
    padding: 5px 14px;
    border: 1px solid rgba(255,60,0,0.4);
    background: transparent;
    color: rgba(255,60,0,0.7);
    font-family: 'Rajdhani', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s;
  }
  .logout-btn:hover { background: rgba(255,60,0,0.1); color: var(--danger); }

  /* ── LAYOUT ── */
  .main { padding: 20px 24px; }

  /* ── KPI STRIP ── */
  .kpi-strip {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin-bottom: 20px;
  }
  .kpi {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 2px solid var(--border2);
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
  }
  .kpi::before {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, currentColor, transparent);
    opacity: 0.15;
  }
  .kpi.red { border-top-color: var(--critical); }
  .kpi.red .kpi-val { color: var(--critical); text-shadow: 0 0 15px rgba(255,0,85,0.5); }
  .kpi.orange { border-top-color: var(--warn); }
  .kpi.orange .kpi-val { color: var(--warn); text-shadow: 0 0 15px rgba(255,170,0,0.5); }
  .kpi.green { border-top-color: var(--green); }
  .kpi.green .kpi-val { color: var(--green); text-shadow: 0 0 15px rgba(0,255,136,0.5); }
  .kpi.blue { border-top-color: var(--accent); }
  .kpi.blue .kpi-val { color: var(--accent); text-shadow: 0 0 15px rgba(0,212,255,0.5); }
  .kpi.purple { border-top-color: var(--purple); }
  .kpi.purple .kpi-val { color: var(--purple); text-shadow: 0 0 15px rgba(168,85,247,0.5); }
  .kpi-label { font-size: 10px; letter-spacing: 3px; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; font-family: 'Share Tech Mono', monospace; }
  .kpi-val { font-family: 'Share Tech Mono', monospace; font-size: 26px; font-weight: 700; line-height: 1; }
  .kpi-delta { font-family: 'Share Tech Mono', monospace; font-size: 10px; color: var(--muted); margin-top: 4px; }
  .kpi-delta.up { color: var(--danger); }
  .kpi-delta.dn { color: var(--green); }

  /* ── GRID ── */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 16px; }
  .grid-13 { display: grid; grid-template-columns: 1fr 2fr; gap: 16px; margin-bottom: 16px; }

  /* ── PANEL ── */
  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    overflow: hidden;
  }
  .panel-hdr {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    background: var(--bg2);
  }
  .panel-hdr-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 6px var(--accent); }
  .panel-hdr-dot.red { background: var(--critical); box-shadow: 0 0 6px var(--critical); }
  .panel-hdr-dot.yellow { background: var(--warn); box-shadow: 0 0 6px var(--warn); }
  .panel-hdr-dot.green { background: var(--green); box-shadow: 0 0 6px var(--green); }
  .panel-title { font-size: 11px; letter-spacing: 3px; color: var(--muted); text-transform: uppercase; font-family: 'Share Tech Mono', monospace; font-weight: 400; }
  .panel-badge { margin-left: auto; font-family: 'Share Tech Mono', monospace; font-size: 10px; padding: 2px 8px; border: 1px solid; }
  .panel-badge.live { color: var(--green); border-color: rgba(0,255,136,0.3); background: rgba(0,255,136,0.05); animation: pulse 2s infinite; }
  .panel-body { padding: 16px; }

  /* ── ALERTS TABLE ── */
  .alerts-table { width: 100%; border-collapse: collapse; }
  .alerts-table th {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
    padding: 6px 10px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }
  .alerts-table td {
    padding: 8px 10px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: var(--text);
    border-bottom: 1px solid rgba(13,34,53,0.5);
    vertical-align: middle;
  }
  .alerts-table tr:hover td { background: rgba(0,212,255,0.03); }
  .sev {
    display: inline-block;
    padding: 2px 8px;
    font-size: 9px;
    letter-spacing: 1px;
    font-weight: 700;
    text-transform: uppercase;
  }
  .sev.critical { background: rgba(255,0,85,0.15); color: var(--critical); border: 1px solid rgba(255,0,85,0.3); }
  .sev.high { background: rgba(255,60,0,0.12); color: var(--danger); border: 1px solid rgba(255,60,0,0.3); }
  .sev.medium { background: rgba(255,170,0,0.1); color: var(--warn); border: 1px solid rgba(255,170,0,0.3); }
  .sev.low { background: rgba(0,212,255,0.08); color: var(--info); border: 1px solid rgba(0,212,255,0.2); }
  .sev.info { background: rgba(168,85,247,0.08); color: var(--purple); border: 1px solid rgba(168,85,247,0.2); }

  /* ── SPARKLINE CANVAS ── */
  canvas { display: block; }

  /* ── MINI BAR CHART ── */
  .bar-chart { display: flex; align-items: flex-end; gap: 4px; height: 60px; padding: 0 4px; }
  .bar { flex: 1; background: rgba(0,212,255,0.2); border-top: 1px solid rgba(0,212,255,0.5); position: relative; min-height: 4px; transition: height 0.4s ease; }
  .bar.hot { background: rgba(255,0,85,0.25); border-top-color: rgba(255,0,85,0.6); }

  /* ── GEO ATTACK MAP ── */
  .geo-map {
    background: var(--bg);
    position: relative;
    height: 220px;
    overflow: hidden;
    border: 1px solid var(--border);
  }
  .geo-map svg { width: 100%; height: 100%; }
  .attack-dot {
    position: absolute;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--critical);
    box-shadow: 0 0 8px var(--critical);
    transform: translate(-50%, -50%);
    animation: attackPulse 2s infinite;
  }
  @keyframes attackPulse {
    0% { transform: translate(-50%,-50%) scale(1); opacity: 1; }
    100% { transform: translate(-50%,-50%) scale(3); opacity: 0; }
  }
  .attack-ring {
    position: absolute;
    border-radius: 50%;
    border: 1px solid var(--critical);
    transform: translate(-50%,-50%);
    animation: ringExpand 2s infinite;
  }
  @keyframes ringExpand {
    0% { width: 6px; height: 6px; opacity: 0.8; }
    100% { width: 40px; height: 40px; opacity: 0; }
  }

  /* ── ENDPOINT TABLE ── */
  .ep-row { display: flex; align-items: center; gap: 12px; padding: 9px 0; border-bottom: 1px solid rgba(13,34,53,0.5); }
  .ep-row:last-child { border-bottom: none; }
  .ep-icon { width: 28px; height: 28px; background: rgba(0,212,255,0.06); border: 1px solid rgba(0,212,255,0.15); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .ep-icon svg { width: 14px; height: 14px; stroke: var(--muted); fill: none; stroke-width: 1.5; }
  .ep-name { font-family: 'Share Tech Mono', monospace; font-size: 12px; color: var(--text); }
  .ep-ip { font-family: 'Share Tech Mono', monospace; font-size: 10px; color: var(--muted); margin-top: 2px; }
  .ep-status { margin-left: auto; }
  .ep-badge { font-family: 'Share Tech Mono', monospace; font-size: 10px; padding: 2px 8px; }
  .ep-badge.ok { color: var(--green); border: 1px solid rgba(0,255,136,0.3); background: rgba(0,255,136,0.05); }
  .ep-badge.warn { color: var(--warn); border: 1px solid rgba(255,170,0,0.3); background: rgba(255,170,0,0.05); }
  .ep-badge.comp { color: var(--critical); border: 1px solid rgba(255,0,85,0.3); background: rgba(255,0,85,0.05); animation: pulse 1s infinite; }

  /* ── IOC FEED ── */
  .ioc-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 0;
    border-bottom: 1px solid rgba(13,34,53,0.4);
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
  }
  .ioc-type { color: var(--purple); min-width: 40px; font-size: 9px; letter-spacing: 1px; }
  .ioc-val { color: var(--text); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .ioc-source { color: var(--muted); font-size: 9px; min-width: 70px; text-align: right; }

  /* ── MINI DONUT ── */
  .donut-wrap { display: flex; align-items: center; gap: 20px; }
  .donut-legend { display: flex; flex-direction: column; gap: 8px; }
  .leg-item { display: flex; align-items: center; gap: 8px; font-family: 'Share Tech Mono', monospace; font-size: 11px; }
  .leg-dot { width: 8px; height: 8px; border-radius: 50%; }

  /* ── XSS DEMO SECTION ── */
  .xss-section { margin-top: 16px; }
  .xss-input-row { display: flex; gap: 8px; margin-bottom: 12px; }
  .xss-input {
    flex: 1;
    background: rgba(0,212,255,0.03);
    border: 1px solid var(--border2);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    padding: 8px 12px;
    outline: none;
    transition: border 0.2s;
  }
  .xss-input:focus { border-color: rgba(0,212,255,0.4); }
  .xss-btn {
    padding: 8px 16px;
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.3);
    color: var(--accent);
    font-family: 'Rajdhani', sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    cursor: pointer;
    text-transform: uppercase;
    white-space: nowrap;
  }
  .xss-btn:hover { background: rgba(0,212,255,0.15); }
  .search-results {
    padding: 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    min-height: 36px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: var(--muted);
  }
  .vuln-label {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: var(--danger);
    border: 1px solid rgba(255,60,0,0.3);
    padding: 2px 8px;
    margin-bottom: 8px;
    background: rgba(255,60,0,0.04);
  }

  /* ── LOG STREAM ── */
  .log-stream {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    max-height: 160px;
    overflow-y: auto;
    scrollbar-width: none;
  }
  .log-stream::-webkit-scrollbar { display: none; }
  .log-entry { padding: 3px 0; border-bottom: 1px solid rgba(13,34,53,0.3); display: flex; gap: 12px; }
  .log-ts { color: var(--muted); min-width: 80px; }
  .log-lvl { min-width: 50px; }
  .log-lvl.CRIT { color: var(--critical); }
  .log-lvl.WARN { color: var(--warn); }
  .log-lvl.INFO { color: var(--accent); }
  .log-msg { color: var(--text); opacity: 0.8; }

  .progress-bar { height: 4px; background: var(--border); margin-top: 6px; position: relative; overflow: hidden; }
  .progress-fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--purple)); transition: width 0.5s ease; }

  .welcome-banner {
    background: rgba(0,212,255,0.04);
    border: 1px solid rgba(0,212,255,0.15);
    border-left: 3px solid var(--accent);
    padding: 10px 16px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: var(--muted);
  }
  .welcome-banner strong { color: var(--accent); }

  @media (max-width: 1400px) {
    .kpi-strip { grid-template-columns: repeat(3, 1fr); }
    .grid-3 { grid-template-columns: 1fr 1fr; }
  }
</style>
</head>
<body>

<!-- TOP NAV -->
<nav class="topnav">
  <div class="nav-logo">
    <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
    <span class="nav-logo-text">OAC CYBER FORENSICS-SOC</span>
  </div>
  <div class="nav-divider"></div>
  <div class="nav-tabs">
    <div class="nav-tab active">Overview</div>
    <div class="nav-tab">Incidents</div>
    <div class="nav-tab">Threat Intel</div>
    <div class="nav-tab">Assets</div>
    <div class="nav-tab">Reports</div>
  </div>
  <div class="nav-right">
    <div class="threat-level">
      <div class="threat-dot"></div>
      <span class="threat-label">ELEVATED</span>
    </div>
    <div class="nav-user">
      <div class="user-avatar" id="avatarInitials">?</div>
      <span class="user-name">{{ username }}</span>
    </div>
    <span class="nav-clock" id="navclock">--:--:--</span>
    <a href="/logout" class="logout-btn">Logout</a>
  </div>
</nav>

<div class="main">

  <!-- WELCOME BANNER -->
  <div class="welcome-banner">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
    Welcome back, <strong>{{ username }}</strong> &nbsp;|&nbsp; Last login: 2025-03-14 08:22:41 UTC &nbsp;|&nbsp;
    <!-- ⚠ XSS VULNERABILITY: user-controlled data rendered unescaped below -->
    Search note: <span id="searchNote"></span>
  </div>

  <!-- KPI STRIP -->
  <div class="kpi-strip">
    <div class="kpi red">
      <div class="kpi-label">Active Incidents</div>
      <div class="kpi-val" id="k1">14</div>
      <div class="kpi-delta up" id="k1d">▲ +3 last hour</div>
    </div>
    <div class="kpi orange">
      <div class="kpi-label">Open Alerts</div>
      <div class="kpi-val" id="k2">287</div>
      <div class="kpi-delta up" id="k2d">▲ +42 last 15m</div>
    </div>
    <div class="kpi blue">
      <div class="kpi-label">Events / Sec</div>
      <div class="kpi-val" id="k3">1,842</div>
      <div class="kpi-delta">EPS (live)</div>
    </div>
    <div class="kpi green">
      <div class="kpi-label">Endpoints Online</div>
      <div class="kpi-val" id="k4">3,241</div>
      <div class="kpi-delta dn">▼ 18 offline</div>
    </div>
    <div class="kpi purple">
      <div class="kpi-label">IOC Matches</div>
      <div class="kpi-val" id="k5">63</div>
      <div class="kpi-delta up">▲ +9 today</div>
    </div>
    <div class="kpi orange">
      <div class="kpi-label">Threat Score</div>
      <div class="kpi-val" id="k6">7.4</div>
      <div class="kpi-delta up">▲ HIGH</div>
    </div>
  </div>

  <!-- ROW 1: Traffic Sparkline + Attack Map -->
  <div class="grid-2">
    <div class="panel">
      <div class="panel-hdr">
        <div class="panel-hdr-dot"></div>
        <span class="panel-title">Network Traffic (EPS — 60s window)</span>
        <span class="panel-badge live">● LIVE</span>
      </div>
      <div class="panel-body" style="padding:12px 16px;">
        <canvas id="sparkCanvas" width="520" height="90"></canvas>
      </div>
    </div>
    <div class="panel">
      <div class="panel-hdr">
        <div class="panel-hdr-dot red"></div>
        <span class="panel-title">Attack Origin Map (Last 5 min)</span>
        <span class="panel-badge live">● LIVE</span>
      </div>
      <div class="geo-map" id="geoMap">
        <!-- SVG world outline approximation -->
        <svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" style="opacity:0.15">
          <rect width="800" height="400" fill="#050a0f"/>
          <!-- Very simplified continent blobs -->
          <ellipse cx="150" cy="180" rx="80" ry="60" fill="#0d2235"/>
          <ellipse cx="300" cy="160" rx="110" ry="70" fill="#0d2235"/>
          <ellipse cx="450" cy="150" rx="80" ry="50" fill="#0d2235"/>
          <ellipse cx="580" cy="160" rx="70" ry="55" fill="#0d2235"/>
          <ellipse cx="680" cy="200" rx="50" ry="70" fill="#0d2235"/>
          <ellipse cx="420" cy="250" rx="40" ry="30" fill="#0d2235"/>
          <ellipse cx="250" cy="270" rx="50" ry="35" fill="#0d2235"/>
          <ellipse cx="480" cy="310" rx="25" ry="45" fill="#0d2235"/>
        </svg>
      </div>
    </div>
  </div>

  <!-- ROW 2: Recent Alerts (big table) + Alert breakdown -->
  <div class="grid-13">
    <div class="panel" style="grid-column: span 1;">
      <div class="panel-hdr">
        <div class="panel-hdr-dot yellow"></div>
        <span class="panel-title">Alert Breakdown by Category</span>
      </div>
      <div class="panel-body">
        <canvas id="donutCanvas" width="200" height="200"></canvas>
        <div class="donut-legend" id="donutLegend" style="margin-top:12px;"></div>
      </div>
    </div>
    <div class="panel">
      <div class="panel-hdr">
        <div class="panel-hdr-dot red"></div>
        <span class="panel-title">Recent Alerts</span>
        <span class="panel-badge live">● LIVE</span>
      </div>
      <div class="panel-body" style="padding:0;">
        <table class="alerts-table">
          <thead>
            <tr>
              <th>TIME</th>
              <th>SEV</th>
              <th>TYPE</th>
              <th>SRC IP</th>
              <th>DST IP</th>
              <th>DESCRIPTION</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody id="alertsBody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ROW 3: Endpoints + IOC Feed + Event Log -->
  <div class="grid-3">
    <div class="panel">
      <div class="panel-hdr">
        <div class="panel-hdr-dot green"></div>
        <span class="panel-title">Monitored Endpoints</span>
      </div>
      <div class="panel-body" style="padding: 8px 16px;" id="endpointList"></div>
    </div>
    <div class="panel">
      <div class="panel-hdr">
        <div class="panel-hdr-dot red"></div>
        <span class="panel-title">IOC Feed (Live Threat Intel)</span>
        <span class="panel-badge live">● LIVE</span>
      </div>
      <div class="panel-body" style="padding:8px 16px;" id="iocFeed"></div>
    </div>
    <div class="panel">
      <div class="panel-hdr">
        <div class="panel-hdr-dot"></div>
        <span class="panel-title">System Event Log</span>
      </div>
      <div class="panel-body" style="padding:8px 16px;">
        <div class="log-stream" id="logStream"></div>
      </div>
    </div>
  </div>

  <!-- ROW 4: XSS Demo + Vulnerability Status -->
  <div class="grid-2">
    <div class="panel xss-section">
      <div class="panel-hdr">
        <div class="panel-hdr-dot red"></div>
        <span class="panel-title">Threat Intelligence Search</span>
        <span class="vuln-label" style="margin-left:auto;">⚡ XSS DEMO POINT</span>
      </div>
      <div class="panel-body">
        <p style="font-family:'Share Tech Mono',monospace; font-size:10px; color:var(--muted); margin-bottom:10px;">
          Search for IOC, IP, domain, or hash. Input is reflected unsanitized — try: &lt;img src=x onerror=alert('XSS')&gt;
        </p>
        <div class="xss-input-row">
          <input class="xss-input" id="searchInput" type="text" placeholder="Enter IOC, IP, domain or hash...">
          <button class="xss-btn" onclick="doSearch()">Search</button>
        </div>
        <div class="search-results" id="searchResults">
          // Results appear here — input is NOT sanitized
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-hdr">
        <div class="panel-hdr-dot yellow"></div>
        <span class="panel-title">System Health & Coverage</span>
      </div>
      <div class="panel-body">
        <div id="healthBars"></div>
      </div>
    </div>
  </div>

</div><!-- /main -->

<script>
// ─────────────────────────────────────────────
// CLOCK
// ─────────────────────────────────────────────
function tick() {
  const now = new Date();
  document.getElementById('navclock').textContent = now.toUTCString().slice(17,25) + ' UTC';
}
tick(); setInterval(tick, 1000);

// Set avatar initials
const uname = "{{ username }}";
document.getElementById('avatarInitials').textContent = uname.slice(0,2).toUpperCase();

// ─────────────────────────────────────────────
// KPI LIVE UPDATES
// ─────────────────────────────────────────────
function rnd(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function flt(min, max) { return (Math.random() * (max - min) + min).toFixed(1); }

setInterval(() => {
  document.getElementById('k1').textContent = rnd(10, 22);
  document.getElementById('k2').textContent = rnd(240, 340).toLocaleString();
  document.getElementById('k3').textContent = rnd(1100, 2800).toLocaleString();
  document.getElementById('k4').textContent = (3000 + rnd(-50, 50)).toLocaleString();
  document.getElementById('k5').textContent = rnd(50, 90);
  document.getElementById('k6').textContent = flt(5.0, 9.9);
}, 2000);

// ─────────────────────────────────────────────
// SPARKLINE (EPS)
// ─────────────────────────────────────────────
const sparkData = Array.from({length: 60}, () => rnd(800, 2800));
function drawSparkline() {
  const c = document.getElementById('sparkCanvas');
  if (!c) return;
  c.width = c.offsetWidth || 520;
  const ctx = c.getContext('2d');
  const w = c.width, h = c.height, pad = 10;
  ctx.clearRect(0, 0, w, h);
  const max = Math.max(...sparkData), min = Math.min(...sparkData);
  const pts = sparkData.map((v, i) => ({
    x: pad + (i / (sparkData.length - 1)) * (w - pad*2),
    y: h - pad - ((v - min) / (max - min + 1)) * (h - pad*2)
  }));
  // fill
  const grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, 'rgba(0,212,255,0.18)');
  grad.addColorStop(1, 'rgba(0,212,255,0)');
  ctx.beginPath();
  ctx.moveTo(pts[0].x, h - pad);
  pts.forEach(p => ctx.lineTo(p.x, p.y));
  ctx.lineTo(pts[pts.length-1].x, h - pad);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();
  // line
  ctx.beginPath();
  ctx.moveTo(pts[0].x, pts[0].y);
  pts.forEach(p => ctx.lineTo(p.x, p.y));
  ctx.strokeStyle = '#00d4ff';
  ctx.lineWidth = 1.5;
  ctx.stroke();
  // spike highlight
  const peakIdx = sparkData.indexOf(max);
  ctx.beginPath();
  ctx.arc(pts[peakIdx].x, pts[peakIdx].y, 3, 0, Math.PI*2);
  ctx.fillStyle = '#ff0055';
  ctx.fill();
}
drawSparkline();
setInterval(() => {
  sparkData.shift();
  sparkData.push(rnd(800, 2800));
  drawSparkline();
}, 1000);

// ─────────────────────────────────────────────
// ALERTS TABLE
// ─────────────────────────────────────────────
const alertTypes = [
  ['Brute Force Login','CRIT','critical'],
  ['SQL Injection Attempt','CRIT','critical'],
  ['Port Scan Detected','MED','medium'],
  ['Malware Callback','HIGH','high'],
  ['Lateral Movement','HIGH','high'],
  ['Data Exfiltration','CRIT','critical'],
  ['Privilege Escalation','HIGH','high'],
  ['Suspicious DNS','MED','medium'],
  ['Ransomware Signature','CRIT','critical'],
  ['Phishing Email','MED','medium'],
  ['CVE Exploit Attempt','HIGH','high'],
  ['Anomalous Traffic','LOW','low'],
  ['C2 Beacon','CRIT','critical'],
  ['Credential Stuffing','HIGH','high'],
];
const statuses = ['NEW','TRIAGING','ASSIGNED','SUPPRESSED'];
const statusColors = {NEW:'color:var(--critical)',TRIAGING:'color:var(--warn)',ASSIGNED:'color:var(--accent)',SUPPRESSED:'color:var(--muted)'};

function rndIP() { return `${rnd(10,220)}.${rnd(0,255)}.${rnd(0,255)}.${rnd(1,254)}`; }
function rndTime() {
  const d = new Date();
  d.setSeconds(d.getSeconds() - rnd(5, 300));
  return d.toTimeString().slice(0,8);
}

function refreshAlerts() {
  const tbody = document.getElementById('alertsBody');
  if (!tbody) return;
  let rows = '';
  const count = 12;
  for (let i = 0; i < count; i++) {
    const [type,, sev] = alertTypes[rnd(0, alertTypes.length-1)];
    const status = statuses[rnd(0, statuses.length-1)];
    rows += `<tr>
      <td>${rndTime()}</td>
      <td><span class="sev ${sev}">${sev.toUpperCase()}</span></td>
      <td>${alertTypes[rnd(0,alertTypes.length-1)][0]}</td>
      <td>${rndIP()}</td>
      <td>${rndIP()}</td>
      <td>${type}</td>
      <td style="${statusColors[status]};font-size:10px;">${status}</td>
    </tr>`;
  }
  tbody.innerHTML = rows;
}
refreshAlerts();
setInterval(refreshAlerts, 3000);

// ─────────────────────────────────────────────
// DONUT CHART
// ─────────────────────────────────────────────
const donutCategories = [
  {label:'Malware', color:'#ff0055'},
  {label:'Network', color:'#00d4ff'},
  {label:'Identity', color:'#ffd700'},
  {label:'Endpoint', color:'#a855f7'},
  {label:'Data Loss', color:'#ff3c00'},
  {label:'Other', color:'#4a7a99'},
];
function drawDonut() {
  const c = document.getElementById('donutCanvas');
  if (!c) return;
  const ctx = c.getContext('2d');
  const cx = 100, cy = 100, r = 75, inner = 45;
  const vals = donutCategories.map(() => rnd(5, 40));
  const total = vals.reduce((a,b)=>a+b,0);
  ctx.clearRect(0,0,200,200);
  let angle = -Math.PI/2;
  vals.forEach((v,i) => {
    const slice = (v/total)*Math.PI*2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, r, angle, angle+slice);
    ctx.closePath();
    ctx.fillStyle = donutCategories[i].color;
    ctx.globalAlpha = 0.75;
    ctx.fill();
    angle += slice;
  });
  // inner hole
  ctx.globalAlpha = 1;
  ctx.beginPath();
  ctx.arc(cx, cy, inner, 0, Math.PI*2);
  ctx.fillStyle = '#0a1520';
  ctx.fill();
  // center text
  ctx.fillStyle = '#c8e6f5';
  ctx.font = 'bold 18px Share Tech Mono';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(total, cx, cy);

  // legend
  const leg = document.getElementById('donutLegend');
  if (leg) {
    leg.innerHTML = donutCategories.map((cat,i) =>
      `<div class="leg-item"><div class="leg-dot" style="background:${cat.color}"></div>${cat.label}: <span style="color:${cat.color};margin-left:4px;">${vals[i]}</span></div>`
    ).join('');
  }
}
drawDonut();
setInterval(drawDonut, 4000);

// ─────────────────────────────────────────────
// ATTACK MAP — animated dots
// ─────────────────────────────────────────────
const attackSites = [
  {x:'18%',y:'45%'},{x:'22%',y:'55%'},{x:'38%',y:'38%'},
  {x:'42%',y:'50%'},{x:'55%',y:'35%'},{x:'60%',y:'45%'},
  {x:'72%',y:'38%'},{x:'78%',y:'55%'},{x:'48%',y:'65%'},
];
function spawnAttack() {
  const map = document.getElementById('geoMap');
  if (!map) return;
  const site = attackSites[rnd(0, attackSites.length-1)];
  const dot = document.createElement('div');
  dot.className = 'attack-dot';
  dot.style.left = site.x;
  dot.style.top = site.y;
  map.appendChild(dot);
  const ring = document.createElement('div');
  ring.className = 'attack-ring';
  ring.style.left = site.x;
  ring.style.top = site.y;
  map.appendChild(ring);
  setTimeout(() => { dot.remove(); ring.remove(); }, 2100);
}
setInterval(spawnAttack, 600);

// ─────────────────────────────────────────────
// ENDPOINT LIST
// ─────────────────────────────────────────────
const endpoints = [
  {name:'WS-EXEC-001', ip:'10.0.1.12', status:'ok'},
  {name:'SRV-DB-PROD', ip:'10.0.1.50', status:'warn'},
  {name:'WS-FINANCE-03',ip:'10.0.2.7',  status:'ok'},
  {name:'SRV-MAIL-01', ip:'10.0.1.45', status:'comp'},
  {name:'WS-HR-009',   ip:'10.0.3.22', status:'ok'},
  {name:'SRV-DC-MAIN', ip:'10.0.1.2',  status:'warn'},
];
const statusLabel = {ok:'HEALTHY', warn:'WARNING', comp:'COMPROMISED'};
function renderEndpoints() {
  const el = document.getElementById('endpointList');
  if (!el) return;
  el.innerHTML = endpoints.map(ep => `
    <div class="ep-row">
      <div class="ep-icon">
        <svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8m-4-4v4"/></svg>
      </div>
      <div>
        <div class="ep-name">${ep.name}</div>
        <div class="ep-ip">${ep.ip}</div>
      </div>
      <div class="ep-status">
        <span class="ep-badge ${ep.status}">${statusLabel[ep.status]}</span>
      </div>
    </div>
  `).join('');
}
renderEndpoints();

// ─────────────────────────────────────────────
// IOC FEED
// ─────────────────────────────────────────────
const iocTypes = ['IP','HASH','URL','DOM','EMAIL'];
const iocSamples = [
  '185.220.101.47','45.83.64.1','198.51.100.24','203.0.113.55',
  'e99a18c428cb38d5f260853678922e03','d41d8cd98f00b204e9800998ecf8427e',
  'malware-cdn.ru/drop.exe','update-flash.xyz/payload',
  'c2-beacon.onion','exfil-bucket.s3-fake.com',
  'phishing@secure-bank.fake','invoice@delivery-notice.xyz',
];
function renderIOC() {
  const el = document.getElementById('iocFeed');
  if (!el) return;
  let html = '';
  for (let i = 0; i < 8; i++) {
    const type = iocTypes[rnd(0, iocTypes.length-1)];
    const val = iocSamples[rnd(0, iocSamples.length-1)];
    const sources = ['VirusTotal','AlienVault','MISP','AbuseIPDB','ThreatFox'];
    html += `<div class="ioc-row">
      <span class="ioc-type">${type}</span>
      <span class="ioc-val">${val}</span>
      <span class="ioc-source">${sources[rnd(0,sources.length-1)]}</span>
    </div>`;
  }
  el.innerHTML = html;
}
renderIOC();
setInterval(renderIOC, 4000);

// ─────────────────────────────────────────────
// EVENT LOG STREAM
// ─────────────────────────────────────────────
const logMessages = [
  ['CRIT','Ransomware process tree detected on SRV-MAIL-01'],
  ['WARN','Failed SSH login from 185.220.101.47 (attempt 47)'],
  ['INFO','YARA rule WannaCry_v2 matched on endpoint WS-EXEC-001'],
  ['WARN','Outbound DNS to known C2 domain blocked'],
  ['CRIT','Admin credentials dumped (LSASS access) on SRV-DC-MAIN'],
  ['INFO','Firewall rule updated: BLOCK 203.0.113.55/32'],
  ['WARN','Unusual volume of SMB traffic detected (lateral?)'],
  ['INFO','Playbook RANSOMWARE-001 triggered automatically'],
  ['CRIT','Data exfiltration alert: 4.2 GB to external IP'],
  ['WARN','Phishing email quarantined for 14 recipients'],
  ['INFO','EDR agent updated on WS-FINANCE-03'],
  ['INFO','Threat hunt completed: 3 IOCs confirmed'],
];
function addLog() {
  const el = document.getElementById('logStream');
  if (!el) return;
  const [lvl, msg] = logMessages[rnd(0, logMessages.length-1)];
  const now = new Date().toTimeString().slice(0,8);
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  entry.innerHTML = `<span class="log-ts">${now}</span><span class="log-lvl ${lvl}">${lvl}</span><span class="log-msg">${msg}</span>`;
  el.insertBefore(entry, el.firstChild);
  if (el.children.length > 20) el.removeChild(el.lastChild);
}
setInterval(addLog, 1200);
addLog();

// ─────────────────────────────────────────────
// HEALTH BARS
// ─────────────────────────────────────────────
const healthItems = [
  {label:'SIEM Coverage', pct: 94, color:'#00d4ff'},
  {label:'EDR Enrollment', pct: 87, color:'#a855f7'},
  {label:'Patch Compliance',pct: 71, color:'#ffd700'},
  {label:'Vuln Scan Coverage',pct: 89, color:'#00ff88'},
  {label:'Log Ingestion Health',pct: 98, color:'#00d4ff'},
  {label:'Backup Integrity', pct: 62, color:'#ff3c00'},
];
function renderHealth() {
  const el = document.getElementById('healthBars');
  if (!el) return;
  el.innerHTML = healthItems.map(h => {
    const pct = Math.max(20, Math.min(100, h.pct + rnd(-3, 3)));
    return `<div style="margin-bottom:12px;">
      <div style="display:flex;justify-content:space-between;font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--muted);margin-bottom:4px;">
        <span>${h.label}</span><span style="color:${pct < 70 ? 'var(--warn)' : h.color}">${pct}%</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width:${pct}%;background:linear-gradient(90deg,${h.color},${h.color}88)"></div>
      </div>
    </div>`;
  }).join('');
}
renderHealth();
setInterval(renderHealth, 3000);

// ─────────────────────────────────────────────
// XSS DEMO — intentionally unsafe innerHTML
// ─────────────────────────────────────────────
function doSearch() {
  const val = document.getElementById('searchInput').value;
  // ⚠ VULNERABILITY: Direct innerHTML injection — no sanitization!
  document.getElementById('searchResults').innerHTML =
    '// Search results for: <strong style="color:var(--accent)">' + val + '</strong><br><br>' +
    '<span style="color:var(--muted)">No exact matches found in threat database.<br>Try enrichment via external feeds.</span>';
}

// Also reflect search query in welcome banner unsafely
const urlParams = new URLSearchParams(window.location.search);
const q = urlParams.get('q');
if (q) {
  // ⚠ VULNERABILITY: URL param reflected directly in DOM
  document.getElementById('searchNote').innerHTML = 'last query: ' + q;
  document.getElementById('searchInput').value = q;
}
</script>
</body>
</html>
"""
# base login and bypass
# Simulated database
users = {
    "doron": {
        "username": "doron",
        "role": "user",
        "isAdmin": False
    }
}

# Simple HTML UI (with readonly fields)
HTML_FORM = """
<h2>User Profile</h2>
<form method="POST" action="/update">
    Username: <input name="username" value="doron"><br><br>
    Role: <input name="role" value="user" readonly><br><br>
    Is Admin: <input name="isAdmin" value="False" readonly><br><br>
    <button type="submit">Update</button>
</form>
"""
# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        print("Auth on")
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)

            # ══════════════════════════════════════════════════════
            # ⚠  SQL INJECTION VULNERABILITY — INTENTIONAL
            # Raw string interpolation directly into SQL query.
            # Bypass example: username = ' OR '1'='1' --
            # ══════════════════════════════════════════════════════
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            print(f"[DEBUG] Executing query: {query}")  # Verbose logging — bad practice
            cursor.execute(query)
            user = cursor.fetchone()
            cursor.close()
            db.close()

            if user:
                session['username'] = user['username']
                session['role'] = user.get('role', 'analyst')
                return redirect(url_for('dashboard'))
            else:
                error = f"Authentication failed for user '{username}'. Invalid credentials."

        except Exception as e:
            # ⚠ VULNERABILITY: Exposing full DB error to user
            error = f"Database error: {str(e)}"

    return render_template_string(LOGIN_HTML, error=error)


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']

    # ══════════════════════════════════════════════════════
    # ⚠  XSS VULNERABILITY — INTENTIONAL
    # The 'username' from session is passed directly into
    # render_template_string without escaping. If an attacker
    # sets a crafted username (e.g. via SQLi), the JS in the
    # template will execute their payload.
    # Additionally, the ?q= URL parameter is reflected via
    # innerHTML in client-side JS with no sanitization.
    # ══════════════════════════════════════════════════════
    return render_template_string(DASHBOARD_HTML, username=username)

SECRET_KEY = "secret123"  # ❌ Weak / guessable

# Generate token
def generate_token(username):
    payload = {
        "username": username,
        "isAdmin": users[username]["isAdmin"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


# ❌ Vulnerable decorator (does not enforce algorithm properly)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"message": "Token missing"}), 401

        try:
            # ❌ Vulnerability: no algorithm restriction
            decoded = jwt.decode(token, SECRET_KEY, options={"verify_signature": False})
        except Exception as e:
            return jsonify({"message": "Invalid token"}), 401

        return f(decoded, *args, **kwargs)

    return decorated

@app.route("/secure-update", methods=["POST"])
@token_required
def secure_update(decoded_token):
    data = request.json
    username = decoded_token["username"]

    # ❌ Still vulnerable to mass assignment
    users[username].update(data)

    return jsonify({
        "message": "Secure update",
        "user": users[username]
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

    
@app.route("/updatesecure", methods=["POST"])
def updatesecure():
    data = request.form.to_dict()
    username = data.get("username")

    if username not in users:
        return "User not found", 404

    # ✅ Only allow safe fields
    users[username]["username"] = data.get("username")

    return jsonify({
        "message": "Secure update",
        "user": users[username]
    })

@app.route("/api/update", methods=["POST"])
def api_update():
    data = request.json
    users[data["username"]].update(data)  # still vulnerable
    return jsonify(users[data["username"]])
   
@app.route("/update", methods=["POST"])
def update():
    data = request.form.to_dict()

    username = data.get("username")

    if username not in users:
        return "User not found", 404

    # ❌ VULNERABILITY: mass assignment (trusting user input)
    users[username].update(data)

    return jsonify({
        "message": "User updated",
        "user": users[username]
    })


if __name__ == '__main__':
    # ⚠ Debug mode on in production — exposes stack traces
    app.run(debug=True, host='0.0.0.0', port=5000)
