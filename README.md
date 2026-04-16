# OAC SOC — Vulnerable Demo Application

> ⚠️ **FOR EDUCATIONAL / DEMONSTRATION USE ONLY**  
> This application contains **intentional security vulnerabilities**.  
> **DO NOT deploy in any production environment.**

---

## Overview

A Flask-based Security Operations Center (SOC) dashboard demo with:
- Cinematic dark-themed login page
- Live-animated SOC dashboard (fake real-time data)
- MySQL backend
- **Two intentional vulnerabilities** for security demonstrations

---

## Quick Setup

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Start MySQL and initialize the database
```bash
mysql -u root -p < setup_db.sql
```

### 3. Update DB credentials in `app.py`
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD",   # ← change this
    "database": "soc_demo"
}
```

### 4. Run the app
```bash
python app.py
```

Open `http://localhost:5000` in your browser.

---

## Demo Credentials

| Username   | Password    | Role    |
|------------|-------------|---------|
| admin      | admin123    | admin   |
| analyst    | analyst456  | analyst |
| jsmith     | password1   | analyst |
| mwilliams  | sec0ps!     | senior  |

---

## 🔴 Vulnerability 1 — SQL Injection (Login Form)

**Location:** `app.py` → `/login` route  
**Code:**
```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(query)
```

**Demo payloads:**

| Field      | Value                  | Effect                        |
|------------|------------------------|-------------------------------|
| Username   | `' OR '1'='1' --`      | Bypass login as first user    |
| Username   | `admin' --`            | Login as admin, any password  |
| Username   | `' OR 1=1 LIMIT 1 --`  | Bypass with LIMIT             |
| Username   | `' UNION SELECT 1,'hacked','admin','x',now() --` | Login with injected user |

**What to show:** Enter the bypass payload in the username field. Notice:
- Login succeeds without valid credentials
- The debug console logs the raw SQL query
- The error message exposes DB structure on failure

---

## 🔴 Vulnerability 2 — XSS (Cross-Site Scripting)

**Location 1 — Stored-like via session (server-side):**  
`app.py` → `/dashboard` renders `username` with `render_template_string` without `|e` escaping.

**Location 2 — Reflected DOM XSS (client-side):**  
`dashboard.html` (inline JS) → `innerHTML` used with unsanitized input:
```javascript
// In doSearch():
document.getElementById('searchResults').innerHTML =
  '// Search results for: <strong>' + val + '</strong>...'

// In URL param reflection:
document.getElementById('searchNote').innerHTML = 'last query: ' + q;
```

**Demo payloads:**

| Location           | Payload                                          | Effect                  |
|--------------------|--------------------------------------------------|-------------------------|
| Search box         | `<img src=x onerror=alert('XSS')>`               | Alert dialog pops       |
| Search box         | `<script>document.body.style.background='red'</script>` | Page turns red   |
| URL `?q=` param    | `http://localhost:5000/dashboard?q=<img src=x onerror=alert(1)>` | Reflected XSS |
| Search box         | `<svg onload=alert(document.cookie)>`            | Cookie theft demo       |

---

## Dashboard Features

- **KPI Strip** — Live updating incident counts, EPS, endpoint count, IOC matches, threat score
- **EPS Sparkline** — Canvas-drawn live traffic graph with peak highlights
- **Attack Map** — Animated origin dots on world map
- **Recent Alerts Table** — Auto-refreshing with severity badges
- **Alert Donut Chart** — Category breakdown, canvas-rendered
- **Endpoint Status** — Health badges including COMPROMISED state
- **IOC Feed** — Live indicator of compromise stream
- **Event Log** — Streaming SIEM-like log entries
- **Threat Intel Search** — The XSS demo point
- **Health Bars** — System coverage metrics

---

## Architecture

```
browser
  └── Flask (app.py)
        ├── GET  /           → redirect
        ├── GET  /login      → login page (Jinja2 inline template)
        ├── POST /login      → SQLi-vulnerable auth → session
        ├── GET  /dashboard  → SOC dashboard (XSS-vulnerable)
        └── GET  /logout     → clear session
              │
              └── MySQL (soc_demo.users)
```

