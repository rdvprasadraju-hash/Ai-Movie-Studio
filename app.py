import streamlit as st
import requests
import sqlite3
import time
from datetime import datetime, timezone

# --- 1. ప్రొడクション డేటాబేస్ ఇంజిన్ ---
def init_production_db():
    conn = sqlite3.connect('ai_movie_studio.db', check_same_thread=False)
    cursor = conn.cursor()
    conn.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE NOT NULL, 
            wallet_balance_paisa INTEGER NOT NULL CHECK(wallet_balance_paisa >= 0)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_orders (
            order_id TEXT PRIMARY KEY, username TEXT NOT NULL, amount_paisa INTEGER NOT NULL CHECK(amount_paisa > 0),
            currency TEXT NOT NULL DEFAULT 'INR', provider TEXT NOT NULL DEFAULT 'UNSELECTED',
            provider_order_id TEXT UNIQUE, provider_payment_id TEXT UNIQUE, status TEXT NOT NULL,
            created_at TEXT NOT NULL, paid_at TEXT, FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    try:
        cursor.execute("INSERT OR IGNORE INTO users (username, wallet_balance_paisa) VALUES (?, ?)", ("test_user", 50000))
    except Exception:
        pass
    conn.commit()
    conn.close()

# వాలెట్ ట్రాన్సాక్షన్ ఫంక్షన్
def execute_wallet_transaction(current_user, cost_paisa, req_id, provider_name):
    db_conn = sqlite3.connect('ai_movie_studio.db')
    db_cursor = db_conn.cursor()
    db_conn.execute("PRAGMA foreign_keys = ON;")
    try:
        db_cursor.execute("BEGIN IMMEDIATE;")
        user_row = db_cursor.execute("SELECT wallet_balance_paisa FROM users WHERE username = ?", (current_user,)).fetchone()
        user_paisa = user_row[0] if user_row else 0
        
        if user_paisa >= cost_paisa:
            new_balance = user_paisa - cost_paisa
            db_cursor.execute("UPDATE users SET wallet_balance_paisa = ? WHERE username = ?", (new_balance, current_user))
            order_id = f"ORD_{int(time.time())}"
            now_str = datetime.now(timezone.utc).isoformat()
            db_cursor.execute(
                """INSERT INTO payment_orders 
                (order_id, username, amount_paisa, currency, provider, provider_order_id, provider_payment_id, status, created_at, paid_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (order_id, current_user, cost_paisa, "INR", provider_name, f"F_{req_id[:6]}", f"P_{int(time.time())}", "PAID", now_str, now_str)
            )
            db_conn.commit()
            return True
        else:
            db_conn.rollback()
            return False
    except Exception:
        db_conn.rollback()
        return False
    finally:
        db_conn.close()

# API రన్ చేయడానికి ప్రత్యేక ఫంక్షన్
def call_fal_ai_video_api(video_payload, headers, FAL_API_KEY):
    try:
        video_res = requests.post("https://fal.run", json=video_payload, headers=headers)
        if video_res.status_code in (200, 202):
            req_id = video_res.json().get("request_id")
            status_url = f"https://fal.run/requests/{req_id}"
            
            for _ in range(25):
                time.sleep(4)
                check_res = requests.get(status_url, headers={"Authorization": f"Key {FAL_API_KEY}"})
                if check_res.status_code == 200:
                    res_json = check_res.json()
                    if res_json.get("status") == "COMPLETED":
                        return res_json.get("video", {}).get("url"), req_id
                    elif res_json.get("status") == "FAILED":
                        break
        return None, None
    except Exception:
        return None, None

# FLUX/Dev ఆటో-ఫోటో ఇంజన్ ఫంక్షన్
def generate_flux_dev_photo(prompt, headers):
    try:
        boosted_img_prompt = f"A deeply detailed cinematic film still, 35mm photograph, professional hollywood movie set lighting, highly realistic human textures, matching: {prompt}"
        img_payload = {"prompt": boosted_img_prompt}
        img_res = requests.post("https://fal.run", json=img_payload, headers=headers)
        if img_res.status_code in (200, 202):
            req_id = img_res.json().get("request_id")
            status_url = f"https://fal.run/requests/{req_id}"
            for _ in range(12):
                time.sleep(2)
                check_res = requests.get(status_url, headers=headers)
                if check_res.status_code == 200 and check_res.json().get("status") == "COMPLETED":
                    return check_res.json().get("images", [{}]).get("url", "")
        return ""
    except Exception:
        return ""

# ElevenLabs ప్రీమియం వాయిస్ ఫంక్షన్
def play_elevenlabs_voice(text_to_speak, headers):
    try:
        voice_payload = {
            "text": text_to_speak,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.75}
        }
        voice_res = requests.post("https://fal.run", json=voice_payload, headers=headers)
        if voice_res.status_code in (200, 202):
            req_id = voice_res.json().get("request_id")
            status_url = f"https://fal.run/requests/{req_id}"
            for _ in range(10):
                time.sleep(2)
                check_res = requests.get(status_url, headers=headers)
                if check_res.status_code == 200 and check_res.json().get("status") == "COMPLETED":
                    audio_url = check_res.json().get("audio", {}).get("url", "")
                    if audio_url:
                        st.audio(audio_url, format="audio/mp3", autoplay=True)
                        return
    except Exception:
        pass
    
    js_code = f'<script>if("speechSynthesis" in window){{var speech=new SpeechSynthesisUtterance("{text_to_speak}");speech.lang="te-IN";window.speechSynthesis.speak(speech);}}</script>'
    st.components.v1.html(js_code, height=0)

init_production_db()

# --- 2. మొబైల్ ఆప్టిమైజ్డ్ పేజీ కాన్ఫిగరేషన్ & CSS ---
st.set_page_config(page_title="AI Movie Studio HD", layout="centered")

st.markdown("""
    <style>
    [data-testid="stHeader"] { opacity: 0 !important; pointer-events: none !important; height: 0px !important; }
    .stAppDeployButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    html, body, [data-testid="stAppViewContainer"] {
        overflow-y: auto !important;
        scroll-behavior: smooth;
    }
    .block-container { 
        padding-top: 0.5rem !important; padding-bottom: 2rem !important;
        padding-left: 0.6rem !important; padding-right: 0.6rem !important; max-width: 100% !important;
    }
    div[data-testid="stTextArea"] textarea { min-height: 110px !important; font-size: 14px !important; }
    .main-title { font-size: 22px !important; font-weight: 700; text-align: center; margin-bottom: 1px; color: #1E1E1E; }
    .sub-title { font-size: 12px !important; text-align: center; color: #666; margin-bottom: 10px; }
    .mini-menu-box { background-color: #f7f9fa; padding: 8px 10px; border-radius: 8px; border: 1px solid #eef2f4; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

FAL_API_KEY = "fal_sk_fba7ddbf009141529452771949a7babbf6a8868d86a405e8666ee3f10cdb2773"

st.markdown('<div class="main-title">🎬 Real Movie Tech AI Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">1080p Ultra HD Cinematic Video Generator</div>', unsafe_allow_html=True)

current_user = "test_user"

conn = sqlite3.connect('ai_movie_studio.db')
user_row = conn.execute("SELECT wallet_balance_paisa FROM users WHERE username = ?", (current_user,)).fetchone()
user_paisa = user_row[0] if user_row else 0
conn.close()

# మినీ మెనూ విత్ సబ్-కాలమ్స్
st.markdown('<div class="mini-menu-box">', unsafe_allow_html=True)
m_col1, m_col2, m_col3 = st.columns([1.2, 1.4, 1.2])

with m_col1:
    st.markdown(f"<span style='font-size:11px; color:#555;'>👤 {current_user}</span><br><span style='font-size:14px; font-weight:bold; color:#2E7D32;'>₹{user_paisa/100:.2f}</span>", unsafe_allow_html=True)
    
with m_col2:
    recharge_amount = st.selectbox("Topup Amt:", [50, 100, 500], label_visibility="collapsed")
    
with m_col3:
    if st.button("➕ Topup", use_container_width=True):
        recharge_paisa = recharge_amount * 100
        db_conn = sqlite3.connect('ai_movie_studio.db')
        db_cursor = db_conn.cursor()
        try:
            db_cursor.execute("BEGIN IMMEDIATE;")
            db_cursor.execute("UPDATE users SET wallet_balance_paisa = wallet_balance_paisa + ? WHERE username = ?", (recharge_paisa, current_user))
            topup_order_id = f"TOP_{int(time.time())}"
            now_str = datetime.now(timezone.utc).isoformat()
            db_cursor.execute("INSERT INTO payment_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                              (topup_order_id, current_user, recharge_paisa, "INR", "LOCAL", f"T_{int(time.time())}", f"P_{int(time.time())}", "PAID", now_str, now_str))
            db_conn.commit()
            st.success(f"+₹{recharge_amount}")
            time.sleep(1)
            st.rerun()
        except Exception:
            db_conn.rollback()
            st.error("Topup Failed")
        finally:
            db_conn.close()
st.markdown('</div>', unsafe_allow_html=True)

# --- 3. కోర్ వీడియో ఇంజన్ సెక్షన్ (ఇక్కడ టూల్స్ అన్నీ తిరిగి యాడ్ చేయబడ్డాయి) ---
user_prompt = st.text_area("✍️ వీడియో ఐడియా/కథ ఇక్కడ రాయండి:", placeholder="ఉదాహరణ: మటన్ కర్రీ చేసినట్టు వీడియో ఇవ్వు...")

# 📸 1. ఫోటో అప్‌లోడర్ టూల్
uploaded_photo = st.file_uploader("📸 ఫోటో ఆధారంగా చేయాలనుకుంటే ఇక్కడ అప్‌లోడ్ చేయండి (Optional):", type=["png", "jpg", "jpeg"])

# ⏱️ 2. వీడియో నిడివి స్లైడర్ టూల్
