import os
import json
import sqlite3
import base64
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from groq import Groq

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "stc_ultra_secret_key_999")
PORT = int(os.environ.get("PORT", 5000))

# Groq API Setup
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Database Setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT DEFAULT 'user',
                        is_activated INTEGER DEFAULT 0)''')
    
    # Default Admin
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, email, password, role, is_activated) VALUES (?, ?, ?, ?, ?)", 
                       ('admin', 'admin@stc.com', 'admin123', 'admin', 1))
    
    conn.commit()
    conn.close()

init_db()

# SHARED FUTURISTIC ANIMATED CSS
COMMON_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: 'Rajdhani', sans-serif;
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
        color: #f8fafc;
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        overflow-x: hidden;
    }
    
    body::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.08) 0%, transparent 60%);
        animation: pulseBg 8s infinite alternate ease-in-out;
        z-index: -1;
    }
    @keyframes pulseBg {
        0% { transform: scale(0.9) rotate(0deg); }
        100% { transform: scale(1.1) rotate(10deg); }
    }

    .glass-card {
        width: 100%;
        max-width: 440px;
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 24px;
        padding: 30px 25px;
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow: 0 0 35px rgba(6, 182, 212, 0.15), inset 0 0 15px rgba(56, 189, 248, 0.05);
        animation: cardFloat 4s infinite ease-in-out alternate;
        position: relative;
    }
    @keyframes cardFloat {
        0% { transform: translateY(0px); box-shadow: 0 10px 30px rgba(6, 182, 212, 0.2); }
        100% { transform: translateY(-6px); box-shadow: 0 20px 45px rgba(56, 189, 248, 0.35); }
    }

    .brand-title {
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        font-size: 22px;
        font-weight: 900;
        background: linear-gradient(135deg, #38bdf8 0%, #a855f7 50%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        margin-bottom: 25px;
        text-transform: uppercase;
    }

    .form-group { margin-bottom: 18px; text-align: left; }
    label { display: block; margin-bottom: 6px; color: #94a3b8; font-size: 13px; font-weight: 600; letter-spacing: 1px; }
    
    input, select {
        width: 100%;
        padding: 14px 16px;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.2);
        color: #f8fafc;
        border-radius: 12px;
        font-size: 14px;
        outline: none;
        transition: all 0.3s ease;
        font-family: 'Rajdhani', sans-serif;
    }
    input:focus, select:focus {
        border-color: #38bdf8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        background: rgba(30, 41, 59, 0.9);
    }

    .btn-neon {
        width: 100%;
        padding: 14px;
        border: none;
        border-radius: 12px;
        font-family: 'Orbitron', sans-serif;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #020617;
        background: linear-gradient(135deg, #38bdf8, #22d3ee);
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
        margin-top: 10px;
    }
    .btn-neon:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(34, 211, 238, 0.8);
    }

    .btn-admin-connect {
        display: block;
        width: 100%;
        padding: 14px;
        margin-top: 15px;
        text-align: center;
        text-decoration: none;
        font-family: 'Orbitron', sans-serif;
        font-size: 13px;
        font-weight: 700;
        color: #38bdf8;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #38bdf8;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }
    .btn-admin-connect:hover {
        background: #38bdf8;
        color: #020617;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.7);
    }

    .switch-link { text-align: center; margin-top: 18px; font-size: 13px; color: #94a3b8; }
    .switch-link a { color: #38bdf8; text-decoration: none; font-weight: bold; }
    .error-msg { color: #f43f5e; font-size: 13px; text-align: center; margin-bottom: 15px; font-weight: 600; }
</style>
"""

# HTML TEMPLATES
REGISTER_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STC ULTRA - Register</title>
    """ + COMMON_CSS + """
</head>
<body>
    <div class="glass-card">
        <div class="brand-title">STC ULTRA ANALYZER</div>
        <h3 style="text-align:center; color:#94a3b8; margin-bottom:20px; font-size:14px; letter-spacing:1px;">CREATE ACCOUNT (STEP 1)</h3>
        
        {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}

        <form method="POST">
            <div class="form-group">
                <label>FULL NAME / USERNAME</label>
                <input type="text" name="username" placeholder="Enter Username" required autocomplete="off">
            </div>
            <div class="form-group">
                <label>GMAIL ADDRESS</label>
                <input type="email" name="email" placeholder="example@gmail.com" required autocomplete="off">
            </div>
            <div class="form-group">
                <label>PASSWORD</label>
                <input type="password" name="password" placeholder="••••••••" required>
            </div>
            <button type="submit" class="btn-neon">REGISTER NOW</button>
        </form>

        <div class="switch-link">
            Already registered? <a href="/login">Login Here</a>
        </div>
    </div>
</body>
</html>"""

LOGIN_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STC ULTRA - Login</title>
    """ + COMMON_CSS + """
</head>
<body>
    <div class="glass-card">
        <div class="brand-title">STC ULTRA ANALYZER</div>
        <h3 style="text-align:center; color:#94a3b8; margin-bottom:20px; font-size:14px; letter-spacing:1px;">USER ACCESS LOGIN</h3>
        
        {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}

        <form method="POST">
            <div class="form-group">
                <label>USERNAME</label>
                <input type="text" name="username" placeholder="Enter Username" required autocomplete="off">
            </div>
            <div class="form-group">
                <label>PASSWORD</label>
                <input type="password" name="password" placeholder="••••••••" required>
            </div>
            <button type="submit" class="btn-neon">LOGIN TO SYSTEM</button>
        </form>

        <div class="switch-link">
            Need an account? <a href="/register">Create One</a>
        </div>
    </div>
</body>
</html>"""

ACTIVATE_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STC ULTRA - Activation</title>
    """ + COMMON_CSS + """
</head>
<body>
    <div class="glass-card">
        <div class="brand-title">STC ULTRA ANALYZER</div>
        <h3 style="text-align:center; color:#e2e8f0; margin-bottom:10px; font-family:'Orbitron'; font-size:15px;">ACTIVATE ANALYZER (STEP 2)</h3>
        <p style="text-align:center; color:#94a3b8; font-size:13px; margin-bottom:20px;">Enter your activation key below to gain full access.</p>

        {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}

        <form method="POST">
            <div class="form-group">
                <label style="text-align:center;">LICENSE ACTIVATION KEY</label>
                <input type="text" name="license_key" placeholder="STC-146625-@@-$$" style="text-align:center; font-family:'Orbitron'; letter-spacing:1px; color:#38bdf8; font-weight:bold;" required autocomplete="off">
            </div>
            <button type="submit" class="btn-neon" style="background: linear-gradient(135deg, #22c55e, #10b981);">ACTIVATE ACCOUNT NOW</button>
        </form>

        <a href="https://t.me/ownerstcsakib" target="_blank" class="btn-admin-connect">CONNECT OFFICIAL ADMIN</a>
        
        <div class="switch-link">
            <a href="/logout" style="color:#f43f5e;">Logout Account</a>
        </div>
    </div>
</body>
</html>"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STC ULTRA ANALYZER</title>
    """ + COMMON_CSS + """
    <style>
        .signal-card {
            margin-top: 20px;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid #38bdf8;
            border-radius: 16px;
            padding: 20px;
            display: none;
            text-align: center;
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.2);
            animation: fadeIn 0.5s ease-in-out;
        }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
        
        .direction-box {
            font-family: 'Orbitron', sans-serif;
            font-size: 32px;
            font-weight: 900;
            margin: 12px 0;
            letter-spacing: 2px;
        }
        .dir-up { color: #22c55e; filter: drop-shadow(0 0 10px rgba(34, 197, 94, 0.8)); }
        .dir-down { color: #f43f5e; filter: drop-shadow(0 0 10px rgba(244, 63, 94, 0.8)); }

        .meta-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
            font-size: 13px;
        }
        .meta-item {
            background: rgba(15, 23, 42, 0.9);
            padding: 10px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        .logic-btn {
            width: 100%;
            padding: 12px;
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid #38bdf8;
            color: #38bdf8;
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            font-weight: 700;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 15px;
            transition: all 0.3s ease;
        }
        .logic-btn:hover { background: #38bdf8; color: #020617; }
        
        .logic-text {
            display: none;
            margin-top: 12px;
            padding: 12px;
            background: rgba(15, 23, 42, 0.95);
            border-left: 3px solid #38bdf8;
            border-radius: 8px;
            font-size: 13px;
            color: #cbd5e1;
            text-align: left;
            white-space: pre-wrap;
        }
        .loading-spinner { display: none; margin-top: 15px; color: #38bdf8; font-family: 'Orbitron'; font-size: 13px; text-align: center; }
    </style>
</head>
<body>
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <div class="brand-title" style="margin:0; font-size:18px;">STC ULTRA</div>
            <a href="/logout" style="color:#f43f5e; text-decoration:none; font-size:13px; font-weight:bold;">Logout</a>
        </div>

        <div class="form-group">
            <label>SELECT OTC ASSET PAIR</label>
            <select id="marketPair">
                <option value="USD/PHP OTC">USD/PHP OTC</option>
                <option value="USD/BDT OTC">USD/BDT OTC</option>
                <option value="EUR/USD OTC">EUR/USD OTC</option>
                <option value="GBP/USD OTC">GBP/USD OTC</option>
            </select>
        </div>

        <div class="form-group">
            <label>UPLOAD CHART SCREENSHOT</label>
            <input type="file" id="screenshotInput" accept="image/*">
        </div>

        <button class="btn-neon" onclick="analyzeScreenshot()">ANALYZE SIGNAL NOW</button>

        <div class="loading-spinner" id="loadingBox">⚡ AI SCANNING CHART PATTERNS...</div>

        <div class="signal-card" id="signalCard">
            <div style="font-size: 11px; color: #94a3b8; font-family:'Orbitron';">NEXT CANDLE PREDICTION</div>
            <div class="direction-box" id="directionText">DOWN</div>
            <div style="font-size: 13px; color: #e2e8f0; font-weight:bold;" id="signalType">PUT / SELL</div>

            <div class="meta-grid">
                <div class="meta-item">TREND: <strong id="trendText" style="color:#38bdf8;">Bearish</strong></div>
                <div class="meta-item">STRENGTH: <strong id="strengthText" style="color:#38bdf8;">High</strong></div>
            </div>

            <button class="logic-btn" onclick="toggleLogic()">VIEW LOGIC & MANIPULATION</button>
            <div class="logic-text" id="logicBox"></div>
        </div>
    </div>

    <script>
        async function analyzeScreenshot() {
            const fileInput = document.getElementById('screenshotInput');
            const marketPair = document.getElementById('marketPair').value;
            const signalCard = document.getElementById('signalCard');
            const loadingBox = document.getElementById('loadingBox');
            const logicBox = document.getElementById('logicBox');

            if (fileInput.files.length === 0) {
                alert('Please upload a chart screenshot first!');
                return;
            }

            signalCard.style.display = 'none';
            logicBox.style.display = 'none';
            loadingBox.style.display = 'block';

            const file = fileInput.files[0];
            const reader = new FileReader();

            reader.onload = async function() {
                const base64Image = reader.result.split(',')[1];
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: base64Image, market: marketPair })
                    });
                    const data = await response.json();
                    loadingBox.style.display = 'none';

                    if (data.status === 'success') {
                        const dir = data.direction.toUpperCase();
                        const dirText = document.getElementById('directionText');
                        dirText.innerText = dir;
                        
                        if(dir.includes('CALL') || dir.includes('UP') || dir.includes('BUY')) {
                            dirText.className = 'direction-box dir-up';
                            document.getElementById('signalType').innerText = 'CALL / BUY';
                        } else {
                            dirText.className = 'direction-box dir-down';
                            document.getElementById('signalType').innerText = 'PUT / SELL';
                        }
                        
                        document.getElementById('trendText').innerText = data.trend || 'Bearish';
                        document.getElementById('strengthText').innerText = data.strength || 'High';
                        logicBox.innerText = data.reasoning;
                        signalCard.style.display = 'block';
                    } else {
                        alert(data.message);
                    }
                } catch (err) {
                    loadingBox.style.display = 'none';
                    alert('Connection Failed: ' + err.message);
                }
            };
            reader.readAsDataURL(file);
        }

        function toggleLogic() {
            const logicBox = document.getElementById('logicBox');
            logicBox.style.display = logicBox.style.display === 'none' ? 'block' : 'none';
        }
    </script>
</body>
</html>"""

ADMIN_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - STC ULTRA</title>
    """ + COMMON_CSS + """
    <style>
        .glass-card { max-width: 680px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }
        th, td { padding: 12px 10px; border: 1px solid rgba(255,255,255,0.08); text-align: center; }
        th { background: rgba(30, 41, 59, 0.9); color: #38bdf8; font-family: 'Orbitron'; }
        .btn-del { background: #f43f5e; color: #fff; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .status-active { color: #22c55e; font-weight: bold; }
        .status-pending { color: #eab308; font-weight: bold; }
    </style>
</head>
<body>
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="brand-title" style="margin:0; font-size:18px;">ADMIN CONTROL</div>
            <a href="/logout" style="color:#f43f5e; text-decoration:none; font-weight:bold;">Logout</a>
        </div>
        
        <table>
            <tr>
                <th>ID</th>
                <th>User</th>
                <th>Gmail</th>
                <th>Status</th>
                <th>Action</th>
            </tr>
            {% for u in users %}
            <tr>
                <td>{{ u[0] }}</td>
                <td>{{ u[1] }}</td>
                <td style="font-size:11px; color:#94a3b8;">{{ u[2] }}</td>
                <td>
                    {% if u[5] == 1 %}
                    <span class="status-active">Active</span>
                    {% else %}
                    <span class="status-pending">Pending</span>
                    {% endif %}
                </td>
                <td>
                    {% if u[1] != 'admin' %}
                    <form action="/admin/delete/{{ u[0] }}" method="POST" style="margin:0;">
                        <button type="submit" class="btn-del">Delete</button>
                    </form>
                    {% else %}
                    <span style="color:#38bdf8;">Admin</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>"""

# ROUTES
@app.route('/')
def index():
    if 'user' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_panel'))
        
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT is_activated FROM users WHERE username = ?", (session['user'],))
            row = cursor.fetchone()
            conn.close()
            
            if row a
