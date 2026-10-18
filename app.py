import streamlit as st
import requests
import sqlite3
import time
from datetime import datetime, timezone

# --- 1. డేటాబేస్ ఇంజిన్ సెటప్ ---
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
                "INSERT INTO payment_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (order_id, current_user, cost_paisa, "INR", provider_name, f"F_{req_id[:6]}", f"P_{int(time.time())}", "PAID", now_str, now_str)
            )
            db_conn.commit()
            return True
        db_conn.rollback()
        return False
    except Exception:
        db_conn.rollback()
        return False
    finally:
        db_conn.close()

def call_fal_ai_video_api(video_payload, headers, FAL_API_KEY):
    try:
        video_res = requests.post("https://fal.run", json=video_payload, headers=headers)
        if video_res.status_code in (200, 202):
            req_id = video_res.json().get("request_id")
            status_url = f"https://fal.run/requests/{req_id}"
            for _ in range(60):
                time.sleep(5)
                check_res = requests.get(status_url, headers={"Authorization": f"Key {FAL_API_KEY}"})
                if check_res.status_code == 200:
                    res_json = check_res.json()
                    if res_json.get("status") == "COMPLETED":
                        return res_json.get("video", {}).get("url"), req_id
                    if res_json.get("status") == "FAILED":
                        break
        return None, None
    except Exception:
        return None, None

def generate_flux_dev_photo(prompt, headers):
    try:
        boosted_img_prompt = f"A deeply detailed cinematic film still, professional hollywood movie set lighting, matching: {prompt}"
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

# --- 2. నార్మల్ లేఅవుట్ & స్టాండర్డ్ CSS (నో లాకింగ్ ఎఫెక్ట్స్) ---
st.set_page_config(page_title="AI Movie Studio HD", layout="centered")

FAL_API_KEY = "fal_sk_fba7ddbf009141529452771949a7babbf6a8868d86a405e8666ee3f10cdb2773"

st.title("🎬 Real Movie Tech AI Studio")
st.write("1080p Ultra HD Cinematic Video Generator")

current_user = "test_user"

conn = sqlite3.connect('ai_movie_studio.db')
user_row = conn.execute("SELECT wallet_balance_paisa FROM users WHERE username = ?", (current_user,)).fetchone()
user_paisa = user_row[0] if user_row else 0
conn.close()

# వాలెట్ మేనేజ్‌మెంట్ సెక్షన్
col_w1, col_w2 = st.columns([2, 1])
with col_w1:
    st.write(f"👤 **యూజర్:** {current_user} | 💳 **బ్యాలెన్స్:** ₹{user_paisa/100:.2f}")
with col_w2:
    recharge_amount = st.selectbox("Topup:", [50, 100, 500])
    if st.button("➕ Topup Wallet"):
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
            st.success(f"Added ₹{recharge_amount}")
            time.sleep(1)
            st.rerun()
        except Exception:
            db_conn.rollback()
            st.error("Topup Failed")
        finally:
            db_conn.close()

st.markdown("---")

# --- 3. ఐదు ప్రధాన కోర్ విజెట్స్ (వరుస క్రమంలో) ---

# టూల్ 1: ప్రాంప్ట్ బాక్స్
user_prompt = st.text_area("✍️ వీడియో ఐడియా లేదా కథ ఇక్కడ రాయండి:", placeholder="ఉదాహరణ: ఒక సింహం అడవిలో గర్జిస్తున్నట్టు వీడియో ఇవ్వు...")

# టూల్ 2: ఫోటో అప్‌లోడర్
uploaded_photo = st.file_uploader("📸 ఫోటో ఆధారంగా చేయాలనుకుంటే ఇక్కడ అప్‌లోడ్ చేయండి (Optional):", type=["png", "jpg", "jpeg"])

# ట్వూల్ 3: నిడివి స్లైడర్ (10 సెకన్ల నుండి 20 నిమిషాల వరకు)
video_duration = st.slider("⏱️ వీడియో నిడివి సెలెక్ట్ చేయండి (సెకన్లలో):", min_value=10, max_value=1200, value=10, step=5)
if video_duration < 60:
    duration_text = f"{video_duration} సెకన్లు"
else:
    duration_text = f"{video_duration // 60} నిమిషాల {video_duration % 60} సెకన్లు"
st.write(f"ఎంచుకున్న సమయం: **{duration_text}**")

# టూల్ 4: సైజ్ సెలెక్టర్ ఫార్మాట్
video_type = st.selectbox(
    "📐 వీడియో టైప్ లేదా సైజ్ ఎంచుకోండి:",
    ["📱 Instagram Reel / Shorts (9:16)", "📺 YouTube Full Video (16:9)", "🟩 Square Post / Video (1:1)"]
)
selected_ratio = "9:16" if "9:16" in video_type else ("1:1" if "1:1" in video_type else "16:9")

VIDEO_COST_PAISA = int((video_duration / 10) * 2000)
st.write(f"💰 **ఈ వీడియో ఖర్చు:** ₹{VIDEO_COST_PAISA/100:.2f} ({VIDEO_COST_PAISA} పైసలు)")

video_placeholder = st.container()

# టూల్ 5: సబ్మిట్ బటన్ (Generate Button)
if st.button(f"🚀 Generate {duration_text} Ultra HD Video", use_container_width=True):
    if user_prompt:
        if user_paisa >= VIDEO_COST_PAISA:
            st.info("🔄 AI ఇంజన్లు రన్ అవుతున్నాయి, దయచేసి వేచి ఉండండి...")
            headers = {"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"}
            
            talk_1 = "అద్భుతం బాస్! మీ సినిమా స్టోరీ చాలా బాగుంది. దీనికి తగ్గట్టు పక్కా మూవీ టెక్ విజువల్స్ డిజైన్ చేస్తున్నాను."
            play_elevenlabs_voice(talk_1, headers)
            
            final_photo_url = ""
            if uploaded_photo is None:
                final_photo_url = generate_flux_dev_photo(user_prompt, headers)
                if final_photo_url:
                    st.image(final_photo_url, caption="📸 AI ఆటో-ఫోటో", width=250)
            else:
                final_photo_url = "https://unsplash.com"

            boosted_video_prompt = f"High-end cinema tech footage, 1080p ultra realism, beautiful dramatic dynamic camera motion, grading style matching: {user_prompt}"
            video_payload = {
