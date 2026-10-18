import streamlit as st
import requests
import sqlite3
import time

# --- 1. డేటాబేస్ సెటప్ (SQLite Engine) ---
conn = sqlite3.connect('ai_movie_studio.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, wallet_balance_paisa INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS payment_orders 
                  (order_id TEXT PRIMARY KEY, username TEXT, amount_paisa INTEGER, currency TEXT, status TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS refund_queue 
                  (refund_job_id TEXT PRIMARY KEY, order_id TEXT, status TEXT, retry_count INTEGER)''')
conn.commit()

# సాంపుల్ యూజర్ (బాలెన్స్ ₹500 = 50000 పైసలు)
try:
    cursor.execute("INSERT OR IGNORE INTO users (username, wallet_balance_paisa) VALUES (?, ?)", ("test_user", 50000))
    conn.commit()
except:
    pass

st.set_page_config(page_title="AI Movie Studio HD", layout="centered")
st.title("🎬 Real Movie Tech AI Studio (1080p Ultra HD)")

# మీ ఒరిజినల్ FAL.AI API KEY
FAL_API_KEY = "fal_sk_fba7ddbf009141529452771949a7babbf6a8868d86a405e8666ee3f10cdb2773"

# --- 2. ఉచిత ChatGPT స్టైల్ వాయిస్ స్పీకర్ (Web Speech API) ---
def free_live_chatgpt_speaker(text_to_speak):
    js_code = f"""
    <script>
    if ('speechSynthesis' in window) {{
        var speech = new SpeechSynthesisUtterance("{text_to_speak}");
        speech.lang = 'te-IN'; // ప్యూర్ తెలుగు వాయిస్
        speech.pitch = 1.0;
        speech.rate = 0.95;
        window.speechSynthesis.speak(speech);
    }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

tab1, tab2 = st.tabs(["✨ AI HD Video Studio", "📊 Database Ledger"])

# --- TAB 1: AI VIDEO STUDIO ---
with tab1:
    st.subheader("Cinematic Text-to-Video Engine")
    
    user_prompt = st.text_area("✍️ వీడియో కోసం మీ ఐడియా/కథ ఇక్కడ రాయండి:", placeholder="ఉదాహరణ: మటన్ కర్రీ చేసినట్టు 1 నిమిషం వీడియో ఇవ్వు...")
    uploaded_photo = st.file_uploader("📸 ఫోటో ఆధారంగా చేయాలనుకుంటే ఇక్కడ అప్‌లోడ్ చేయండి (Optional):", type=["png", "jpg", "jpeg"])
    
    current_user = "test_user"
    user_row = cursor.execute("SELECT wallet_balance_paisa FROM users WHERE username = ?", (current_user,)).fetchone()
    user_paisa = user_row[0] if user_row else 50000
    st.write(f"💳 **మీ వాలెట్ బ్యాలెన్స్:** ₹{user_paisa/100:.2f} ({user_paisa} పైసలు)")

    if st.button("🚀 Generate 1 Minute Ultra HD Video", use_container_width=True):
        if user_prompt:
            VIDEO_COST_PAISA = 5000 # ₹50 = 5000 పైసలు
            
            if user_paisa >= VIDEO_COST_PAISA:
                st.info("🔄 వాలెట్ వెరిఫై అయింది. AI మూవీ సర్వర్లు రన్ అవుతున్నాయి...")
                
                talk_1 = "అద్భుతం బాస్! మీ సినిమా స్టోరీ చాలా బాగుంది. దీనికి తగ్గట్టు పక్కా విజువల్స్ డిజైన్ చేస్తున్నాను."
                free_live_chatgpt_speaker(talk_1)
                st.write(f"🗣️ **AI Speaker (Free):** '{talk_1}'")
                time.sleep(3)
                
                final_photo_url = ""
                headers = {"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"}
                
                # ఫేక్ ఇమేజ్ లింక్ బదులు క్లౌడ్ స్టోరేజ్ అప్‌లోడ్ లాజిక్ (టెస్టింగ్ కోసం శాంపుల్)
                if uploaded_photo is not None:
                    # ఒకవేళ యూజర్ ఫోటో ఇస్తే దాన్ని ఇక్కడ లింక్ లాగా వాడతాం
                    final_photo_url = "https://unsplash.com" 
                else:
                    talk_photo = "మీరు ఫోటో ఇవ్వలేదు, కాబట్టి నేనే ఒక రియలిస్టిక్ ఫోటోను సృష్టిస్తున్నాను."
                    free_live_chatgpt_speaker(talk_photo)
                    st.write(f"🗣️ **AI Speaker (Free):** '{talk_photo}'")
                    
                    img_payload = {"prompt": f"A realistic cinematic photo of {user_prompt}"}
                    try:
                        # FIXED: Flux Endpoint URL
                        img_res = requests.post("https://fal.run", json=img_payload, headers=headers)
                        if img_res.status_code in:
                            # FIXED: List array parsing error solved
                            final_photo_url = img_res.json().get("images", [{}])[0].get("url", "")
                            if final_photo_url:
                                st.image(final_photo_url, caption="AI ఆటో-ఫోటో", width=250)
                    except Exception as e:
                        print(f"Image error: {e}")
                
                talk_joke = "వీడియో బ్యాక్‌గ్రౌండ్‌లో లోడ్ అవుతోంది, మన సినిమా చాలా అద్భుతంగా రాబోతోంది బాస్!"
                free_live_chatgpt_speaker(talk_joke)
                st.write(f"🗣️ **AI Speaker (Free):** '{talk_joke}'")
                
                # --- 1 నిమిషం రియల్ వీడియో జనరేషన్ ---
                # FIXED: Kling Video payload matching requirements
                video_payload = {
                    "prompt": f"Cinematic real-life movie shot, beautiful lighting, matching context: {user_prompt}", 
                    "image_url": final_photo_url if final_photo_url else "https://unsplash.com", 
                    "aspect_ratio": "16:9"
                }
                
                st.info("🎬 మూవీ విజువల్స్ జనరేట్ అవుతున్నాయి...")
                try:
                    # FIXED: Kling Video Endpoint URL
                    video_res = requests.post("https://fal.run", json=video_payload, headers=headers)
                    if video_res.status_code in:
                        # Fal AI Queue handling wait state
                        res_data = video_res.json()
                        req_id = res_data.get("request_id")
                        
                        # Status check loop
                        final_hd_video_url = ""
                        status_url = f"https://fal.run/requests/{req_id}"
                        
                        for _ in range(10):
                            time.sleep(6)
                            check_res = requests.get(status_url, headers={"Authorization": f"Key {FAL_API_KEY}"})
                            if check_res.status_code == 200 and check_res.json().get("status") == "COMPLETED":
                                final_hd_video_url = check_res.json().get("video", {}).get("url")
                                break
                        
                        if final_hd_video_url:
                            # --- డేటాబేస్ వాలెట్ కటింగ్ ---
                            new_balance = user_paisa - VIDEO_COST_PAISA
                            cursor.execute("UPDATE users SET wallet_balance_paisa = ? WHERE username = ?", (new_balance, current_user))
                            cursor.execute("INSERT INTO payment_orders VALUES (?, ?, ?, ?, ?)", 
                                           (str(time.time()), current_user, VIDEO_COST_PAISA, "INR", "PAID"))
                            conn.commit()
                            
                            talk_done = "ఇక మీ నిమిషం సినిమా ప్యూర్ 1080p HD క్వాలిటీ లో రెడీ అయిపోయింది బాస్!"
                            free_live_chatgpt_speaker(talk_done)
                            
                            st.success("🎉 1080p Ultra HD AI వీడియో రెడీ అయ్యింది!")
                            st.video(final_hd_video_url)
                        else:
                            st.warning("AI క్యూ ప్రాసెసింగ్ లో ఉంది, దయచేసి మళ్లీ ట్రై చేయండి.")
                    else:
                        st.error(f"API Error ({video_res.status_code}): దయచేసి మీ API Key / Credits చెక్ చేయండి.")
                except Exception as e:
                    st.error(f"కనెక్షన్ ఫెయిల్ అయింది: {e}")
            else:
                st.error("❌ మీ వాలెట్ లో తగినంత బ్యాలెన్స్ లేదు! దయచేసి రీఛార్జ్ చేయండి.")
        else:
            st.warning("దయచేసి స్టోరీ లేదా ప్రాంప్ట్ రాయండి!")

# --- TAB 2: DATABASE LEDGER ---
with tab2:
    st.subheader("Real-time Database Ledger Profile")
    st.write("#### 1. Users Table (`users`)")
    users = cursor.execute("SELECT * FROM users").fetchall()
    st.dataframe(users, use_container_width=True)
    
    st.write("#### 2. Payment Orders Table (`payment_orders`)")
    payments = cursor.execute("SELECT * FROM payment_orders").fetchall()
    st.dataframe(payments, use_container_width=True)
