import os
import json
import sqlite3
import base64
from flask import Flask, request, jsonify, session, redirect, Response
from groq import Groq

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "stc_ultra_secret_key_99")
PORT = int(os.environ.get("PORT", 5000))

# Groq API Setup
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Database Setup with safe migration
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        cursor.execute('''CREATE TABLE users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL,
                            role TEXT DEFAULT 'user',
                            is_activated INTEGER DEFAULT 0)''')
    else:
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'is_activated' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_activated INTEGER DEFAULT 0")
            
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, email, password, role, is_activated) VALUES (?, ?, ?, ?, ?)", 
                       ('admin', 'admin@stc.com', 'admin123', 'admin', 1))
    else:
        cursor.execute("UPDATE users SET role = 'admin', is_activated = 1 WHERE username = 'admin'")
    
    conn.commit()
    conn.close()

init_db()

BASE_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Plus Jakarta Sans', sans-serif; background: #020617; color: #f8fafc; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 10px; }
.mobile-frame { width: 100%; max-width: 420px; background: #060b19; border-radius: 28px; padding: 20px 16px; border: 1px solid rgba(56, 189, 248, 0.2); box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8); position: relative; min-height: 840px; display: flex; flex-direction: column; }
.top-nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.brand-name { font-family: 'Orbitron', sans-serif; font-size: 18px; font-weight: 800; color: #f8fafc; }
.user-icon { width: 36px; height: 36px; border-radius: 50%; background: radial-gradient(circle, #38bdf8 0%, #030712 100%); border: 1px solid #38bdf8; display: flex; justify-content: center; align-items: center; }
.market-tabs { display: flex; background: rgba(15, 23, 42, 0.9); border-radius: 12px; padding: 4px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 18px; }
.tab-item { flex: 1; padding: 10px; text-align: center; font-family: 'Orbitron', sans-serif; font-size: 11px; font-weight: 700; border-radius: 8px; color: #94a3b8; }
.tab-item.active { background: #06b6d4; color: #020617; box-shadow: 0 0 15px rgba(6, 182, 212, 0.5); }
.upload-area { border: 2px dashed rgba(56, 189, 248, 0.3); background: rgba(15, 23, 42, 0.6); border-radius: 16px; padding: 22px 15px; text-align: center; cursor: pointer; margin-bottom: 15px; }
.live-card { background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 18px; padding: 14px 16px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.direction-card { background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 18px; padding: 16px; display: flex; align-items: center; gap: 15px; margin-bottom: 14px; }
.direction-card.up-bg { background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(34, 197, 94, 0.4); }
.dir-circle { width: 48px; height: 48px; border-radius: 14px; border: 1px dashed #ef4444; display: flex; justify-content: center; align-items: center; font-size: 22px; }
.up-bg .dir-circle { border-color: #22c55e; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
.info-box { background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 14px; padding: 12px; }
.btn-cyan { width: 100%; padding: 13px; border: none; border-radius: 12px; background: #06b6d4; color: #020617; font-family: 'Orbitron', sans-serif; font-size: 12px; font-weight: 800; cursor: pointer; box-shadow: 0 0 20px rgba(6, 182, 212, 0.4); margin-top: 8px; }
.bottom-nav { margin-top: auto; display: flex; justify-content: space-around; align-items: center; background: rgba(15, 23, 42, 0.95); border-radius: 16px; padding: 10px 5px; border: 1px solid rgba(56, 189, 248, 0.15); }
.nav-btn { text-align: center; color: #64748b; font-size: 10px; font-weight: 600; }
.nav-btn.active { color: #38bdf8; }
.modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 100; justify-content: center; align-items: center; padding: 20px; }
.modal-content { background: #0f172a; border: 1px solid #38bdf8; border-radius: 20px; padding: 20px; max-width: 380px; width: 100%; position: relative; }
"""

DASHBOARD_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>STC ULTRA ANALYZER</title><style>""" + BASE_STYLE + """</style></head><body>
    <div class="mobile-frame">
        <div class="top-nav">
            <div class="brand-name">Live Signal</div>
            <div class="user-icon"><a href="/logout" style="color:#38bdf8; text-decoration:none; font-size:14px;">👤</a></div>
        </div>
        <div class="market-tabs">
            <div class="tab-item active">OTC Market</div>
            <div class="tab-item">Real Market</div>
        </div>
        <div class="upload-area" onclick="document.getElementById('screenshotInput').click()">
            <div style="font-size:24px; color:#38bdf8; margin-bottom:4px;">📷</div>
            <div style="font-family:'Orbitron'; font-size:11px; font-weight:700; color:#e2e8f0;">UPLOAD CHART SCREENSHOT</div>
            <div style="font-size:10px; color:#64748b; margin-top:2px;">AI Auto-Detects Pair & Signals</div>
            <input type="file" id="screenshotInput" accept="image/*" style="display:none;" onchange="autoAnalyze(this)">
        </div>
        <div id="loadingBox" style="display:none; text-align:center; padding:15px; color:#38bdf8; font-family:'Orbitron'; font-size:11px;">⚡ SCANNING CHART PATTERNS...</div>
        <div id="analysisResult" style="display:none;">
            <div class="live-card">
                <div>
                    <div style="font-size:9px; color:#94a3b8; font-family:'Orbitron';">LIVE ASSET PAIR</div>
                    <div style="font-family:'Orbitron'; font-size:18px; font-weight:900; color:#fff;" id="detectedPair">USD/PHP <span style="font-size:10px; background:#0f172a; padding:2px 6px; border-radius:4px; color:#38bdf8;">OTC</span></div>
                </div>
                <div style="font-size:20px;">🇺🇸🇵🇭</div>
            </div>
            <div class="direction-card" id="dirCard">
                <div class="dir-circle" id="dirArrow">↓</div>
                <div>
                    <div style="font-size:9px; color:#94a3b8; font-family:'Orbitron';">NEXT CANDLE DIRECTION</div>
                    <div style="font-family:'Orbitron'; font-size:24px; font-weight:900;" id="dirText">DOWN</div>
                    <div style="font-size:10px; font-weight:700; color:#e2e8f0;" id="dirSub">PUT / SELL</div>
                </div>
            </div>
            <div style="background:rgba(15,23,42,0.8); border:1px solid rgba(56,189,248,0.2); border-radius:14px; padding:12px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; font-size:10px; font-family:'Orbitron'; margin-bottom:6px;">
                    <span style="color:#94a3b8;">SIGNAL STRENGTH</span>
                    <span style="color:#fbbf24;" id="strengthLabel">Medium</span>
                </div>
                <div style="height:6px; background:#1e293b; border-radius:3px; overflow:hidden;">
                    <div id="strengthBar" style="width:70%; height:100%; background:linear-gradient(90deg, #38bdf8, #fbbf24);"></div>
                </div>
            </div>
            <div class="grid-2">
                <div class="info-box">
                    <div style="font-size:9px; color:#94a3b8; font-family:'Orbitron';">MARKET TREND</div>
                    <div style="font-size:13px; font-weight:800; color:#f43f5e; margin-top:4px;" id="trendVal">Bearish</div>
                </div>
                <div class="info-box">
                    <div style="font-size:9px; color:#94a3b8; font-family:'Orbitron';">TRAP LEVEL</div>
                    <div style="font-size:13px; font-weight:800; color:#fbbf24; margin-top:4px;" id="trapVal">Medium</div>
                </div>
            </div>
            <div class="grid-2">
                <div class="info-box">
                    <div style="font-size:9px; color:#94a3b8; font-family:'Orbitron';">SUPPORT</div>
                    <div style="font-size:13px; font-weight:800; color:#e2e8f0; margin-top:4px;" id="supVal">62.702</div>
                </div>
                <div class="info-box">
                    <div style="font-size:9px; color:#94a3b8; font-family:'Orbitron';">RESISTANCE</div>
                    <div style="font-size:13px; font-weight:800; color:#e2e8f0; margin-top:4px;" id="resVal">62.746</div>
                </div>
            </div>
            <button class="btn-cyan" onclick="openLogicModal()">👁 View Logic & Manipulation</button>
            <button class="btn-cyan" style="background:transparent; border:1px solid #06b6d4; color:#06b6d4;" onclick="document.getElementById('screenshotInput').click()">🔄 Analyze Another Signal</button>
        </div>
        <div class="bottom-nav">
            <div class="nav-btn">📊<br>Dashboard</div>
            <div class="nav-btn active">📡<br>Live Signal</div>
            <div class="nav-btn">📈<br>Analyzer</div>
            <div class="nav-btn">⏰<br>Future</div>
            <div class="nav-btn">💳<br>Money</div>
        </div>
    </div>
    <div class="modal" id="logicModal">
        <div class="modal-content">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="font-family:'Orbitron'; font-size:13px; font-weight:800; color:#38bdf8;">TRAP & MAIN LOGIC</div>
                <span style="color:#f43f5e; cursor:pointer; font-weight:bold;" onclick="closeLogicModal()">&times;</span>
            </div>
            <div id="logicTextContent" style="font-size:12px; color:#cbd5e1; line-height:1.6; white-space:pre-wrap;"></div>
        </div>
    </div>
    <script>
        async function autoAnalyze(input) {
            if(input.files.length === 0) return;
            const loadingBox = document.getElementById('loadingBox');
            const resultBox = document.getElementById('analysisResult');
            resultBox.style.display = 'none';
            loadingBox.style.display = 'block';
            const reader = new FileReader();
            reader.onload = async function() {
                const base64Image = reader.result.split(',')[1];
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: base64Image })
                    });
                    const data = await response.json();
                    loadingBox.style.display = 'none';
                    if (data.status === 'success') {
                        document.getElementById('detectedPair').innerText = data.pair + " OTC";
                        const dir = data.direction.toUpperCase();
                        const dirText = document.getElementById('dirText');
                        const dirCard = document.getElementById('dirCard');
                        const dirArrow = document.getElementById('dirArrow');
                        dirText.innerText = dir;
                        if(dir.includes('CALL') || dir.includes('UP') || dir.includes('BUY')) {
                            dirCard.className = 'direction-card up-bg';
                            dirArrow.innerText = '↑';
                            document.getElementById('dirSub').innerText = 'CALL / BUY';
                        } else {
                            dirCard.className = 'direction-card';
                            dirArrow.innerText = '↓';
                            document.getElementById('dirSub').innerText = 'PUT / SELL';
                        }
                        document.getElementById('trendVal').innerText = data.trend || 'Bearish';
                        document.getElementById('trapVal').innerText = data.trap_level || 'Medium';
                        document.getElementById('supVal').innerText = data.support || 'Auto';
                        document.getElementById('resVal').innerText = data.resistance || 'Auto';
                        document.getElementById('strengthLabel').innerText = data.strength || 'Medium';
                        document.getElementById('logicTextContent').innerText = data.reasoning;
                        resultBox.style.display = 'block';
                    } else { alert(data.message); }
                } catch (err) { loadingBox.style.display = 'none'; alert('Analysis Failed!'); }
            };
            reader.readAsDataURL(input.files[0]);
        }
        function openLogicModal() { document.getElementById('logicModal').style.display = 'flex'; }
        function closeLogicModal() { document.getElementById('logicModal').style.display = 'none'; }
    </script></body></html>"""

LOGIN_TEMPLATE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>STC ULTRA - Login</title><style>""" + BASE_STYLE + """</style></head><body>
<div class="mobile-frame" style="justify-content:center;">
    <div style="text-align:center; margin-bottom:30px;">
        <div style="font-family:'Orbitron'; font-size:22px; font-weight:900; color:#38bdf8;">STC ULTRA</div>
        <div style="font-size:12px; color:#94a3b8; margin-top:5px;">AI CHART ANALYZER LOGIN</div>
    </div>
    __ERROR_MSG__
    <form method="POST">
        <div style="margin-bottom:15px;"><label style="font-size:11px; color:#94a3b8; font-family:'Orbitron';">USERNAME</label>
        <input type="text" name="username" required style="width:100%; padding:12px; background:#0f172a; border:1px solid rgba(56,189,248,0.3); color:#fff; border-radius:10px; margin-top:5px;"></div>
        <div style="margin-bottom:20px;"><label style="font-size:11px; color:#94a3b8; font-family:'Orbitron';">PASSWORD</label>
        <input type="password" name="password" required style="width:100%; padding:12px; background:#0f172a; border:1px solid rgba(56,189,248,0.3); color:#fff; border-radius:10px; margin-top:5px;"></div>
        <button type="submit" class="btn-cyan">LOGIN SYSTEM</button>
    </form>
    <div style="text-align:center; margin-top:20px; font-size:12px; color:#94a3b8;">No account? <a href="/register" style="color:#38bdf8; text-decoration:none;">Register</a></div>
</div></body></html>"""

REGISTER_TEMPLATE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>STC ULTRA - Register</title><style>""" + BASE_STYLE + """</style></head><body>
<div class="mobile-frame" style="justify-content:center;">
    <div style="text-align:center; margin-bottom:30px;">
        <div style="font-family:'Orbitron'; font-size:22px; font-weight:900; color:#38bdf8;">STC ULTRA</div>
        <div style="font-size:12px; color:#94a3b8; margin-top:5px;">CREATE NEW ACCOUNT</div>
    </div>
    __ERROR_MSG__
    <form method="POST">
        <div style="margin-bottom:12px;"><label style="font-size:11px; color:#94a3b8; font-family:'Orbitron';">USERNAME</label>
        <input type="text" name="username" required style="width:100%; padding:12px; background:#0f172a; border:1px solid rgba(56,189,248,0.3); color:#fff; border-radius:10px; margin-top:4px;"></div>
        <div style="margin-bottom:12px;"><label style="font-size:11px; color:#94a3b8; font-family:'Orbitron';">GMAIL</label>
        <input type="email" name="email" required style="width:100%; padding:12px; background:#0f172a; border:1px solid rgba(56,189,248,0.3); color:#fff; border-radius:10px; margin-top:4px;"></div>
        <div style="margin-bottom:20px;"><label style="font-size:11px; color:#94a3b8; font-family:'Orbitron';">PASSWORD</label>
        <input type="password" name="password" required style="width:100%; padding:12px; background:#0f172a; border:1px solid rgba(56,189,248,0.3); color:#fff; border-radius:10px; margin-top:4px;"></div>
        <button type="submit" class="btn-cyan">CREATE ACCOUNT</button>
    </form>
    <div style="text-align:center; margin-top:20px; font-size:12px; color:#94a3b8;">Already registered? <a href="/login" style="color:#38bdf8; text-decoration:none;">Login</a></div>
</div></body></html>"""

ACTIVATE_TEMPLATE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>STC ULTRA - Activate</title><style>""" + BASE_STYLE + """</style></head><body>
<div class="mobile-frame" style="justify-content:center;">
    <div style="text-align:center; margin-bottom:25px;">
        <div style="font-family:'Orbitron'; font-size:20px; font-weight:900; color:#38bdf8;">LICENSE ACTIVATION</div>
        <div style="font-size:11px; color:#94a3b8; margin-top:5px;">ENTER KEY TO UNLOCK DASHBOARD</div>
    </div>
    __ERROR_MSG__
    <form method="POST">
        <input type="text" name="license_key" autocomplete="off" required style="width:100%; padding:14px; background:#0f172a; border:1px solid #38bdf8; color:#38bdf8; font-family:'Orbitron'; text-align:center; font-weight:bold; border-radius:10px; margin-bottom:15px;">
        <button type="submit" class="btn-cyan">VERIFY KEY</button>
    </form>
    <a href="https://t.me/ownerstcsakib" target="_blank" style="display:block; text-align:center; margin-top:15px; color:#38bdf8; text-decoration:none; font-family:'Orbitron'; font-size:11px;">CONTACT ADMIN FOR KEY</a>
    <div style="text-align:center; margin-top:15px;"><a href="/logout" style="color:#f43f5e; text-decoration:none; font-size:11px;">Logout Account</a></div>
</div></body></html>"""

ADMIN_TEMPLATE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Admin Panel</title><style>""" + BASE_STYLE + """</style></head><body>
<div class="mobile-frame" style="justify-content:flex-start;">
    <div style="font-family:'Orbitron'; font-size:16px; color:#38bdf8; margin-bottom:15px;">ADMIN PANEL</div>
    <table style="width:100%; font-size:11px; border-collapse:collapse;">
        <tr style="color:#38bdf8; border-bottom:1px solid #38bdf8;"><th>ID</th><th>User</th><th>Status</th><th>Action</th></tr>
        __USER_ROWS__
    </table>
    <a href="/logout" style="display:block; margin-top:20px; color:#f43f5e; font-size:12px; text-decoration:none;">Logout</a>
</div></body></html>"""


@app.route('/')
def index():
    if 'user' in session:
        if session.get('role') == 'admin':
            return redirect('/admin')
        conn = sqlite3.connect('da
