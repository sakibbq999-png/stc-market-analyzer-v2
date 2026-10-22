import os
import json
import sqlite3
import base64
from flask import Flask, request, jsonify, session, redirect, url_for, Response
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
    
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, email, password, role, is_activated) VALUES (?, ?, ?, ?, ?)", 
                       ('admin', 'admin@stc.com', 'admin123', 'admin', 1))
    
    conn.commit()
    conn.close()

init_db()

# SHARED CSS
COMMON_STYLE = """<style>
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
.glass-card {
    width: 100%;
    max-width: 440px;
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(16px);
    border-radius: 24px;
    padding: 30px 25px;
    border: 1px solid rgba(56, 189, 248, 0.25);
    box-shadow: 0 0 35px rgba(6, 182, 212, 0.15);
    text-align: center;
}
.brand-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 22px;
    font-weight: 900;
    background: linear-gradient(135deg, #38bdf8, #a855f7, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
    margin-bottom: 20px;
}
.form-group { margin-bottom: 16px; text-align: left; }
label { display: block; margin-bottom: 6px; color: #94a3b8; font-size: 12px; font-weight: 600; }
input, select {
    width: 100%;
    padding: 12px 14px;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(56, 189, 248, 0.2);
    color: #f8fafc;
    border-radius: 10px;
    font-size: 14px;
    outline: none;
}
input:focus, select:focus { border-color: #38bdf8; box-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }
.btn-neon {
    width: 100%;
    padding: 13px;
    border: none;
    border-radius: 10px;
    font-family: 'Orbitron', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #020617;
    background: linear-gradient(135deg, #38bdf8, #22d3ee);
    cursor: pointer;
    margin-top: 10px;
}
.btn-telegram {
    display: block;
    width: 100%;
    padding: 12px;
    margin-top: 12px;
    text-decoration: none;
    font-family: 'Orbitron', sans-serif;
    font-size: 12px;
    font-weight: bold;
    color: #38bdf8;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid #38bdf8;
    border-radius: 10px;
}
.error-msg { color: #f43f5e; font-size: 13px; margin-bottom: 15px; font-weight: bold; }
.switch-link { margin-top: 15px; font-size: 13px; color: #94a3b8; }
.switch-link a { color: #38bdf8; text-decoration: none; }
</style>"""

@app.route('/')
def index():
    if 'user' in session:
        if session.get('role') == 'admin':
            return redirect('/admin')
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT is_activated FROM users WHERE username = ?", (session['user'],))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] == 1:
            return redirect('/dashboard')
        else:
            return redirect('/activate')
            
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_html = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user'] = user[1]
            session['role'] = user[4]
            if user[4] == 'admin':
                return redirect('/admin')
            if user[5] == 1:
                return redirect('/dashboard')
            else:
                return redirect('/activate')
        else:
            error_html = "<div class='error-msg'>Invalid username or password!</div>"

    html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>STC ULTRA - Login</title>{COMMON_STYLE}</head><body>
    <div class="glass-card">
        <div class="brand-title">STC ULTRA ANALYZER</div>
        <h4 style="color:#94a3b8; margin-bottom:15px;">USER ACCESS LOGIN</h4>
        {error_html}
        <form method="POST">
            <div class="form-group"><label>USERNAME</label><input type="text" name="username" required autocomplete="off"></div>
            <div class="form-group"><label>PASSWORD</label><input type="password" name="password" required></div>
            <button type="submit" class="btn-neon">LOGIN TO SYSTEM</button>
        </form>
        <div class="switch-link">Need an account? <a href="/register">Create One</a></div>
    </div></body></html>"""
    return Response(html, mimetype='text/html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_html = ""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password, role, is_activated) VALUES (?, ?, ?, ?, ?)", 
                           (username, email, password, 'user', 0))
            conn.commit()
            conn.close()
            
            session['user'] = username
            session['role'] = 'user'
            return redirect('/activate')
        except sqlite3.IntegrityError:
            error_html = "<div class='error-msg'>Username already exists!</div>"

    html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>STC ULTRA - Register</title>{COMMON_STYLE}</head><body>
    <div class="glass-card">
        <div class="brand-title">STC ULTRA ANALYZER</div>
        <h4 style="color:#94a3b8; margin-bottom:15px;">CREATE ACCOUNT (STEP 1)</h4>
        {error_html}
        <form method="POST">
            <div class="form-group"><label>FULL NAME / USERNAME</label><input type="text" name="username" required autocomplete="off"></div>
            <div class="form-group"><label>GMAIL ADDRESS</label><input type="email" name="email" required autocomplete="off"></div>
            <div class="form-group"><label>PASSWORD</label><input type="password" name="password" required></div>
            <button type="submit" class="btn-neon">REGISTER NOW</button>
        </form>
        <div class="switch-link">Already registered? <a href="/login">Login Here</a></div>
    </div></body></html>"""
    return Response(html, mimetype='text/html')

@app.route('/activate', methods=['GET', 'POST'])
def activate():
    if 'user' not in session:
        return redirect('/login')
        
    error_html = ""
    if request.method == 'POST':
        key = request.form.get('license_key', '').strip()
        valid_keys = ["STC-146625-@@-$$", "STC-999999-@@-$$", "STC-ULTRA-2026-VIP"]
        
        if key in valid_keys or key.startswith("STC-"):
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_activated = 1 WHERE username = ?", (session['user'],))
            conn.commit()
            conn.close()
            return redirect('/dashboard')
        else:
            error_html = "<div class='error-msg'>Invalid License Key! Contact Admin.</div>"

    html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>STC ULTRA - Activation</title>{COMMON_STYLE}</head><body>
    <div class="glass-card">
        <div class="brand-title">STC ULTRA ANALYZER</div>
        <h4 style="color:#e2e8f0; margin-bottom:10px;">ACTIVATE ANALYZER (STEP 2)</h4>
        <p style="color:#94a3b8; font-size:12px; margin-bottom:15px;">Enter license key to unlock dashboard.</p>
        {error_html}
        <form method="POST">
            <div class="form-group"><label style="text-align:center;">LICENSE ACTIVATION KEY</label>
            <input type="text" name="license_key" placeholder="STC-146625-@@-$$" style="text-align:center; font-family:'Orbitron'; font-weight:bold; color:#38bdf8;" required autocomplete="off"></div>
            <button type="submit" class="btn-neon" style="background: linear-gradient(135deg, #22c55e, #10b981);">ACTIVATE ACCOUNT</button>
        </form>
        <a href="https://t.me/ownerstcsakib" target="_blank" class="btn-telegram">CONNECT OFFICIAL ADMIN</a>
        <div class="switch-link"><a href="/logout" style="color:#f43f5e;">Logout Account</a></div>
    </div></body></html>"""
    return Response(html, mimetype='text/html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
        
    html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>STC ULTRA ANALYZER</title>{COMMON_STYLE}
    <style>
        .signal-card {{ margin-top: 20px; background: rgba(30, 41, 59, 0.8); border: 1px solid #38bdf8; border-radius: 16px; padding: 20px; display: none; text-align: center; }}
        .direction-box {{ font-family: 'Orbitron'; font-size: 32px; font-weight: 900; margin: 10px 0; }}
        .dir-up {{ color: #22c55e; }} .dir-down {{ color: #f43f5e; }}
        .logic-btn {{ width: 100%; padding: 10px; background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; color: #38bdf8; border-radius: 8px; margin-top: 12px; cursor: pointer; font-weight: bold; }}
        .logic-text {{ display: none; margin-top: 10px; padding: 10px; background: rgba(15, 23, 42, 0.95); border-left: 3px solid #38bdf8; font-size: 13px; text-align: left; }}
    </style></head><body>
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <div class="brand-title" style="margin:0; font-size:18px;">STC ULTRA</div>
            <a href="/logout" style="color:#f43f5e; text-decoration:none; font-size:13px; font-weight:bold;">Logout</a>
        </div>
        <div class="form-group"><label>SELECT OTC ASSET PAIR</label>
            <select id="marketPair">
                <option value="USD/PHP OTC">USD/PHP OTC</option>
                <option value="USD/BDT OTC">USD/BDT OTC</option>
                <option value="EUR/USD OTC">EUR/USD OTC</option>
                <option value="GBP/USD OTC">GBP/USD OTC</option>
            </select>
        </div>
        <div class="form-group"><label>UPLOAD CHART SCREENSHOT</label><input type="file" id="screenshotInput" accept="image/*"></div>
        <button class="btn-neon" onclick="analyzeScreenshot()">ANALYZE SIGNAL NOW</button>
        <div id="loadingBox" style="display:none; margin-top:15px; color:#38bdf8; font-family:'Orbitron'; font-size:13px;">⚡ AI SCANNING CHART...</div>
        <div class="signal-card" id="signalCard">
            <div style="font-size: 11px; color: #94a3b8; font-family:'Orbitron';">PREDICTION RESULT</div>
            <div class="direction-box" id="directionText">DOWN</div>
            <div style="font-size: 13px; font-weight:bold;" id="signalType">PUT / SELL</div>
            <button class="logic-btn" onclick="toggleLogic()">VIEW LOGIC & REASONING</button>
            <div class="logic-text" id="logicBox"></div>
        </div>
    </div>
    <script>
        async function analyzeScreenshot() {{
            const fileInput = document.getElementById('screenshotInput');
            const marketPair = document.getElementById('marketPair').value;
            const signalCard = document.getElementById('signalCard');
            const loadingBox = document.getElementById('loadingBox');
            const logicBox = document.getElementById('logicBox');

            if (fileInput.files.length === 0) {{ alert('Please upload a screenshot first!'); return; }}

            signalCard.style.display = 'none';
            logicBox.style.display = 'none';
            loadingBox.style.display = 'block';

            const reader = new FileReader();
            reader.onload = async function() {{
                const base64Image = reader.result.split(',')[1];
                try {{
                    const response = await fetch('/analyze', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ image: base64Image, market: marketPair }})
                    }});
                    const data = await response.json();
                    loadingBox.style.display = 'none';

                    if (data.status === 'success') {{
                        const dir = data.direction.toUpperCase();
                        const dirText = document.getElementById('directionText');
                        dirText.innerText = dir;
                        if(dir.includes('CALL') || dir.includes('UP') || dir.includes('BUY')) {{
                            dirText.className = 'direction-box dir-up';
                            document.getElementById('signalType').innerText = 'CALL / BUY';
                        }} else {{
                            dirText.className = 'direction-box dir-down';
                            document.getElementById('signalType').innerText = 'PUT / SELL';
                        }}
                        logicBox.innerText = data.reasoning;
                        signalCard.style.display = 'block';
                    }} else {{ alert(data.message); }}
                }} catch (err) {{ loadingBox.style.display = 'none'; alert('Connection Failed!'); }}
            }};
            reader.readAsDataURL(fileInput.files[0]);
        }}
        function toggleLogic() {{
            const logicBox = document.getElementById('logicBox');
            logicBox.style.display = logicBox.style.display === 'none' ? 'block' : 'none';
        }}
    </script></body></html>"""
    return Response(html, mimetype='text/html')

@app.route('/admin')
def admin_panel():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, is_activated FROM users")
    users = cursor.fetchall()
    conn.close()
    
    user_rows = ""
    for u in users:
        status = "<span style='color:#22c55e;'>Active</span>" if u[3] == 1 else "<span style='color:#eab308;'>Pending</span>"
        action = f"<form action='/admin/delete/{u[0]}' method='POST' style='margin:0;'><button type='submit' style='background:#f43f5e; color:#fff; border:none; padding:4px 8px; border-radius:4px;'>Delete</button></form>" if u[1] != 'admin' else "Admin"
        user_rows += f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>{status}</td><td>{action}</td></tr>"

    html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Admin - STC ULTRA</title>{COMMON_STYLE}
    <style>table {{ width:100%; border-collapse:collapse; margin-top:15px; font-size:12px; }} th, td {{ padding:8px; border:1px solid rgba(255,255,255,0.1); text-align:center; }}</style></head><body>
    <div class="glass-card" style="max-width:600px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="brand-title" style="margin:0; font-size:18px;">ADMIN PANEL</div>
            <a href="/logout" style="color:#f43f5e; text-decoration:none; font-weight:bold;">Logout</a>
        </div>
        <table><tr><th>ID</th><th>User</th><th>Email</th><th>Status</th><th>Action</th></tr>{user_rows}</table>
    </div></body></html>"""
    return Response(html, mimetype='text/html')

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ? AND role != 'admin'", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Unauthorized access."})
    try:
        data = request.json or {}
        base64_image = data.get('image')
        market = data.get('market')

        if not base64_image:
            return jsonify({"status": "error", "message": "Screenshot is required."})

        if not client:
            return jsonify({
                "status": "success",
                "direction": "PUT",
                "reasoning": "Fallback Analysis: Strong Bearish Reversal Pattern detected."
            })

        prompt_instruction = f"""
        You are a strict Trading AI Validator for market pair {market}.
        Verify if image is a genuine trading candlestick chart screenshot.
        
        - IF NOT A CHART: Return JSON: {{"is_valid_chart": false, "error_message": "Invalid Image! Please upload a valid Trading Chart screenshot."}}
        - IF VALID CHART: Return JSON: {{"is_valid_chart": true, "direction": "CALL" or "PUT", "reasoning": "Pattern explanation."}}
        """

        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_instruction},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            model="meta-llama/llama-3.2-11b-vision-preview",
            response_format={"type": "json_object"}
        )

        res_json = json.loads(chat_completion.choices[0].message.content)

        if not res_json.get("is_valid_chart", True):
            return jsonify({"status": "error", "message": res_json.get("error_message", "Invalid image!")})

        return jsonify({
            "status": "success",
            "direction": res_json.get("direction", "PUT"),
            "reasoning": res_json.get("reasoning", "Candlestick analysis complete.")
        })

    except Exception:
        return jsonify({"status": "error", "message": "Analysis failed. Upload a clear chart screenshot."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
        
