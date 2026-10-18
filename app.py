import streamlit as st
import requests
import sqlite3
import time

# --- 1. డేటాబేస్ సెటప్ (SQLite Engine) ---
conn = sqlite3.connect('ai_movie_studio.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, wallet_balance_paisa INTEGER)')
cursor.execute('CREATE TABLE IF NOT EXISTS payment_orders (order_id TEXT PRIMARY KEY, username TEXT, amount_paisa INTEGER, currency TEXT, status TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS refund_queue (refund_job_id TEXT PRIMARY KEY, order_id TEXT, status TEXT, retry_count INTEGER)')
conn.commit()

try:
    cursor.execute("INSERT OR IGNORE INTO users (username, wallet_balance_paisa) VALUES (?, ?)", ("test_user", 50000))
    conn.commit()
except:
    pass

st.set_page_config(page_title="AI Movie Studio HD", layout="centered")
st.title("🎬 Real Movie Tech AI Studio (1080p Ultra HD)")

# ⚠️ మీ ఒరిజినల్ FAL.AI API KEY ని ఇక్కడ ఇవ్వండి లేదా st.secrets లో సెట్ చేయండి
FAL_API_KEY = st.secrets.get("FAL_API_KEY", "fal_sk_fba7ddbf009141529452771949a7babbf6a8868d86a405e8666ee3f10cdb2773")

def free_live_chatgpt_speaker(text_to_speak):
    js_code = f"""<script>
    if ('speechSynthesis' in window) {{
        var speech = new SpeechSynthesisUtterance("{text_to_speak}");
        speech.lang = 'te-IN';
        speech.pitch = 1.0;
        speech.rate = 0.95;
        window.speechSynthesis.speak(speech);
    }}
    </script>"""
    st.components.v1.html(js_code, height=0)

tab1, tab2 = st.tabs(["✨ AI HD Video Studio", "📊 Database Ledger"])

with tab1:
    st.subheader("Cinematic Text-to-Video Engine")
    user_prompt = st.text_area("✍️ व्हिडिओ కోసం మీ ఐడియా/కథ ఇక్కడ రాయండి:", placeholder="ఉదాహరణ: మటన్ కర్రీ చేసినట్టు 1 నిమిషం వీడియో ఇవ్వు...")
    uploaded_photo = st.file_uploader("📸 ఫోటో ఆధారంగా చేయాలనుకుంటే ఇక్కడ అప్‌లోడ్ చేయండి (Optional):", type=["png", "jpg", "jpeg"])
    
    current_user = "test_user"
    user_paisa = cursor.execute("SELECT wallet_balance_paisa FROM users WHERE username = ?", (current_user,)).fetchone()[0]
    st.write(f"💳 **మీ వాలెట్ బ్యాలెన్స్:** ₹{user_paisa/100:.2f} ({user_paisa} పైసలు)")

    if st.button("🚀 Generate 1 Minute Ultra HD Video", use_container_width=True):
        if user_prompt:
            VIDEO_COST_PAISA = 5000 
            if user_paisa >= VIDEO_COST_PAISA:
                st.info("🔄 వాలెట్ వెరిఫై అయింది. AI మూవీ సర్వర్లు రన్ అవుతున్నాయి...")
                
                talk_1 = "అద్భుతం బాస్! మీ సినిమా స్టోరీ చాలా బాగుంది. దీనికి తగ్గట్టు పక్కా విజువల్స్ డిజైన్ చేస్తున్నాను."
                free_live_chatgpt_speaker(talk_1)
                st.write(f"🗣️ **AI Speaker (Free):** '{talk_1}'")
                time.sleep(3)
                
                final_photo_url = ""
                headers = {"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"}
                
                if uploaded_photo is None:
                    talk_photo = "మీరు ఫోటో ఇవ్వలేదు, కాబట్టి నేనే ఒక మంచి రియలిస్టిక్ ఫోటోను సృష్టిస్తున్నాను."
                    free_live_chatgpt_speaker(talk_photo)
                    st.write(f"🗣️ **AI Speaker (Free):** '{talk_photo}'")
                    
                    img_payload = {"prompt": f"A realistic cinematic photo of {user_prompt}"}
                    try:
                        # FIXED: URL changed to real Flux Model Endpoint
                        img_res = requests.post("https://fal.run", json=img_payload, headers=headers)
                        if img_res.status_code in:
                            final_photo_url = img_res.json().get("images", [{}])[0].get("url")
                            st.image(final_photo_url, caption="AI ఆటో-ఫోటో", width=250)
                    except Exception as e:
                        print(f"Image error: {e}")
                
                talk_joke = "వీడియో బ్యాక్‌గ్రౌండ్‌లో లోడ్ అవుతోంది, మన సినిమా చాలా అద్భుతంగా రాబోతోంది బాస్!"
                free_live_chatgpt_speaker(talk_joke)
                st.write(f"🗣️ **AI Speaker (Free):** '{talk_joke}'")
                
                # FIXED: URL & payload mapping for Kling Video Engine
                video_payload = {
                    "prompt": f"Cinematic real-life movie shot, beautiful lighting, matching context: {user_prompt}", 
                    "image_url": final_photo_url if final_photo_url else "https://unsplash.com", 
                    "aspect_ratio": "16:9"
                }
                st.info("🎬 మూవీ విజువల్స్ జనరేట్ అవుతున్నాయి...")
                
                try:
                    video_res = requests.post("https://fal.run", json=video_payload, headers=headers)
                    if video_res.status_code in:
                        req_id = video_res.json().get("request_id")
                        status_url = f"https://fal.run/requests/{req_id}"
                        
                        raw_video_url = ""
                        # Fal AI Queue processing loop
                        for _ in range(12):
                            time.sleep(5)
                            check_res = requests.get(status_url, headers={"Authorization": f"Key {FAL_API_KEY}"})
                            if check_res.status_code == 200 and check_res.json().get("status") == "COMPLETED":
                                raw_video_url = check_res.json().get("video", {}).get("url")
                                break
                        
                        if raw_video_url:
                            st.info("✨ పిక్సెల్స్ అప్‌గ్రేడ్ అవుతున్నాయి... 1080p Full HD క్వాలిటీ లోకల్ బూస్ట్ అవుతోంది...")
                            upscale_payload = {"video_url": raw_video_url}
                            # FIXED: Lumina Video Upscaler Endpoint URL
                            upscale_res = requests.post("https://fal.run", json=upscale_payload, headers=headers)
                            
                            final_hd_video_url = raw_video_url
                            if upscale_res.status_code in:
                                up_req_id = upscale_res.json().get("request_id")
                                up_status_url = f"https://fal.run/requests/{up_req_id}"
                                for _ in range(10):
                                    time.sleep(5)
                                    up_check = requests.get(up_status_url, headers={"Authorization": f"Key {FAL_API_KEY}"})
                                    if up_check.status_code == 200 and up_check.json().get("status") == "COMPLETED":
                                        final_hd_video_url = up_check.json().get("video", {}).get("url")
                                        break
                            
                            new_balance = user_paisa - VIDEO_COST_PAISA
                            cursor.execute("UPDATE users SET wallet_balance_paisa = ? WHERE username = ?", (new_balance, current_user))
                            cursor.execute("INSERT INTO payment_orders VALUES (?, ?, ?, ?, ?)", (str(time.time()), current_user, VIDEO_COST_PAISA, "INR", "PAID"))
                            conn.commit()
                            
                            talk_done = "ఇక మీ నిమిషం సినిమా ప్యూర్ 1080p HD క్వాలిటీ లో రెడీ అయిపోయింది బాస్! డౌน์โหลด చేసుకోండి!"
                            free_live_chatgpt_speaker(talk_done)
                            
                            # FIXED: Marathi typo 'व्हिडिओ' changed to Telugu 'వీడియో'
                            st.success("🎉 1080p Ultra HD AI వీడియో మరియు తెలుగు వాయిస్ రెడీ అయ్యింది!")
                            st.video(final_hd_video_url)
                        else:
                            st.error("AI సర్వర్ చాలా బిజీగా ఉంది. దయచేసి కాసేపటి తర్వాత మళ్లీ ట్రై చేయండి.")
                    else:
                        st.error(f"fal.ai API Error ({video_res.status_code}). దయచేసి మీ API Key ని చెక్ చేయండి.")
                except Exception as e:
                    st.error(f"కనెక్షన్ ఫెయిల్ అయింది: {e}")
            else:
                st.error("మీ వాలెట్‌లో తగినంత బ్యాలెన్స్ లేదు! దయచేసి ₹50 రీఛార్జ్ చేసుకోండి.")
        else:
            st.warning("దయచేసి స్టోరీ లేదా ప్రాంప్ట్ రాయండి!")

with tab2:
    st.subheader("Real-time Database Ledger Profile")
    st.write("#### 1. Users Table (`users`)")
    st.dataframe(cursor.execute("SELECT * FROM users").fetchall(), use_container_width=True)
    st.write("#### 2. Payment Orders Table (`payment_orders`)")
    st.dataframe(cursor.execute("SELECT * FROM payment_orders").fetchall(), use_container_width=True)
