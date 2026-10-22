# STC ULTRA ANALYZER 🚀

A futuristic, AI-powered Binary & OTC Market Chart Screenshot Analyzer web application built with **Flask**, **SQLite**, and **Groq Vision API (`meta-llama/llama-3.2-11b-vision-preview`)**.

---

## 🔥 Key Features

- **2-Step Authentication & License Flow:**
  - **Step 1:** User registration using Full Name, Gmail, and Password, followed by secure login.
  - **Step 2:** Account activation via License Key (`STC-146625-@@-$$` or custom keys starting with `STC-`).
  - Direct connection button to **Telegram Admin** (`t.me/ownerstcsakib`) for obtaining license keys.
- **Strict Image Validation:** Automatically detects and rejects non-trading chart images (e.g., human faces, random screenshots) before analysis.
- **AI Signal Prediction:** Generates real-time **CALL / BUY** or **PUT / SELL** signals based on uploaded candlestick charts.
- **View Logic & Manipulation Breakdown:** Explains price action logic, candlestick patterns, and market trends.
- **Futuristic Animated UI:** Modern Glassmorphism design with 3D neon glow effects and floating card animations.
- **Admin Management Panel:** Allows admins to track user status (`Active` / `Pending`) and manage accounts.

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Flask
- **Database:** SQLite
- **AI Engine:** Groq Vision API (`llama-3.2-11b-vision-preview`)
- **Server:** Gunicorn
- **Frontend:** HTML5, Modern CSS3 (Glassmorphism & Keyframe Animations), JavaScript

---

## ⚙️ Render Deployment Guide

1. Create a **New Web Service** on Render and connect your GitHub repository.
2. Set the following build and start configurations:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
3. Add the following **Environment Variables** in Render settings:
   - `GROQ_API_KEY`: *Your official Groq API key*
   - `SECRET_KEY`: `stc_ultra_secret_key_12345`

---

## 🔐 Default Admin Credentials

- **Username:** `admin`
- **Password:** `admin123`
- 
