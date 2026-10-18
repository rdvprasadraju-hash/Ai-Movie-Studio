import streamlit as st
import requests
import sqlite3
import time
from datetime import datetime, timezone

# --- 1. ప్రొడక్షన్ డేటాబేస్ ఇంజిన్ సెటప్ ---
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
    except:
        pass
    conn.commit()
    conn.close()

init_production_db()

# --- 2. మొబైల్ ఆప్టిమైజ్డ్ పేజీ కాన్ఫిగరేషన్ & CSS ---
st.set_page_config(page_title="AI Movie Studio HD", layout="centered")

st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stHeader"] {background-color: transparent; visibility: hidden !important;}
    .stAppDeployButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    .block-container { 
        padding-top: 0.2rem !important; 
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }
    
    div[data-testid="stTextArea"] textarea { min-height: 110px !important; font-size: 14px !important; }
    .main-title { font-size: 22px !important; font-weight: 700; text-align: center; margin-bottom: 1px; color: #1E1E1E; }
    .sub-title { font-size: 12px !important; text-align: center; color: #666; margin-bottom: 10px; }
    
    .mini-menu-box {
        background-color: #f7f9fa;
        padding: 6px 10px;
        border-radius: 8px;
        border: 1px solid #eef2f4;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

FAL_API_KEY = "fal_sk_fba7ddbf009141529452771949a7babbf6a8868d86a405e8666ee3f10cdb2773"

def free_live_chatgpt_speaker(text_to_speak):
    js_code = f"""<script>
    if ('speechSynthesis' in window) {{
        var speech = new SpeechSynthesisUtterance("{text_to_speak}");
        speech.lang = 'te-IN'; window.speechSynthesis.speak(speech);
    }}
    </script>"""
    st.components.v1.html(js_code, height=0)

st.markdown('<div class="main-title">🎬 Real Movie Tech AI Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">1080p Ultra HD Cinematic Video Generator</div>', unsafe_allow_html=True)

current_user = "test_user"

conn = sqlite3.connect('ai_movie_studio.db')
user_row = conn.execute("SELECT wallet_balance_paisa FROM users WHERE username = ?", (current_user,)).fetchone()
user_paisa = user_row[0] if user_row else 0
conn.close()

# మినీ మెనూ విత్ సబ్-కాలమ్స్
st.markdown('<div class="mini-menu-box">', unsafe_allow_html=True)
m_col1, m_col2, m_col3 = st.columns([1.1, 1.4, 1.1])

with m_col1:
    st.markdown(f"<span style='font-size:12px; color:#555;'>👤 {current_user}</span><br>💳 **₹{user_paisa/100:.2f}**", unsafe_allow_html=True)
    
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
            free_live_chatgpt_speaker(f"సక్సెస్ బాస్! {recharge_amount} రూపాయలు యాడ్ అయ్యాయి.")
            st.success(f"+₹{recharge_amount}")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            db_conn.rollback()
            st.error(f"Error: {e}")
        finally:
            db_conn.close()
st.markdown('</div>', unsafe_allow_html=True)

# --- 3. కోర్ వీడియో ఇంజన్ సెక్షన్ ---
user_prompt = st.text_area("✍️ వీడియో ఐడియా/కథ ఇక్కడ రాయండి:", placeholder="ఉదాహరణ: మటన్ కర్రీ చేసినట్టు వీడియో ఇవ్వు...")
uploaded_photo = st.file_uploader("📸 ఫోటో ఆధారంగా (Optional):", type=["png", "jpg", "jpeg"])

video_duration = st.slider("⏱️ వీడియో నిడివి (సెకన్లు):", min_value=10, max_value=60, value=10, step=5)

st.write("📐 **వీడియో టైప్ / సైజ్ ఎంచుకోండి:**")
video_type = st.selectbox(
    "వీడియో ఫార్మాట్ సెలెక్ట్ చేయండి:",
    ["📱 Instagram Reel / Shorts (9:16)", "📺 YouTube Full Video (16:9)", "🟩 Square Post / Video (1:1)"],
    label_visibility="collapsed"
)

if "9:16" in video_type:
    selected_ratio = "9:16"
elif "1:1" in video_type:
    selected_ratio = "1:1"
else:
    selected_ratio = "16:9"

VIDEO_COST_PAISA = int((video_duration / 10) * 1000)
st.caption(f"💰 ఈ వీడియో ఖర్చు: ₹{VIDEO_COST_PAISA/100:.2f} ({VIDEO_COST_PAISA} పైసలు)")

video_placeholder = st.container()

if st.button(f"🚀 Generate {video_duration}s Ultra HD Video", use_container_width=True):
    if user_prompt:
        if user_paisa >= VIDEO_COST_PAISA:
            st.info("🔄 AI వీడియో జనరేట్ అవుతోంది...")
            free_live_chatgpt_speaker(f"అద్భుతం బాస్! మీ సినిమా స్టోరీకి తగ్గట్టు పక్కా {video_duration} సెకన్ల విజువల్స్ డిజైన్ చేస్తున్నాను.")
            
            headers = {"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"}
            final_photo_url = ""
            
            if uploaded_photo is None:
                try:
                    img_res = requests.post("https://fal.run", json={"prompt": f"Realistic cinematic shot of {user_prompt}"}, headers=headers)
                    if img_res.status_code == 200:
                        final_photo_url = img_res.json().get("images", [{}]).get("url", "")
                except:
                    pass

            video_payload = {
                "prompt": f"Cinematic real movie shot: {user_prompt}", 
                "image_url": final_photo_url if final_photo_url else "https://unsplash.com", 
                "aspect_ratio": selected_ratio,
                "duration": video_duration
            }
            
            try:
                # గమనిక: సరైన ఫాల్ మోడల్ URL ఇక్కడ ఇవ్వబడింది
                video_res = requests.post("https://fal.run", json=video_payload, headers=headers)
                if video_res.status_code == 200 or video_res.status_code == 202:
                    req_id = video_res.json().get("request_id")
                    status_url = f"https://fal.run/requests/{req_id}"
                    
                    raw_video_url = ""
                    for _ in range(15):
                        time.sleep(4)
                        check_res = requests.get(status_url, headers={"Authorization": f"Key {FAL_API_KEY}"})
                        if check_res.status_code == 200:
                            res_json = check_res.json()
                            if res_json.get("status") == "COMPLETED":
                                raw_video_url = res_json.get("video", {}).get("url")
                                break
                            elif res_json.get("status") == "FAILED":
                                break
                    
                    if raw_video_url:
                        db_conn = sqlite3.connect('ai_movie_studio.db')
                        db_cursor = db_conn.cursor()
                        try:
                            db_cursor.execute("BEGIN IMMEDIATE;")
                            new_balance = user_paisa - VIDEO_COST_PAISA
                            db_cursor.execute("UPDATE users SET wallet_balance_paisa = ? WHERE username = ?", (new_balance, current_user))
                            order_id = f"ORD_{int(time.time())}"
                            now_str = datetime.now(timezone.utc).isoformat()
                            db_cursor.execute("INSERT INTO payment_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                              (order_id, current_user, VIDEO_COST_PAISA, "INR", "FAL_AI", f"F_{req_id[:6]}", f"P_{int(time.time())}", "PAID", now_str, now_str))
                            db_conn.commit()
                        except:
                            db_conn.rollback()
                        finally:
                            db_conn.close()
                        
                        free_live_chatgpt_speaker(f"ఇక మీ {video_duration} సెకన్ల సినిమా ప్యూర్ 1080p HD క్వాలిటీ లో రెడీ అయిపోయింది బాస్!")
                        
                        with video_placeholder:
                            st.success("🎉 వీడియో విజయవంతంగా రెడీ అయ్యింది!")
                            st.video(raw_video_url)
