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
    outline: none
    
