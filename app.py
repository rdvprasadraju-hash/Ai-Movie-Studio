import streamlit as st
import requests
import sqlite3
import time

# --- 1. డేటాబేస్ సెటప్ ---
def get_db_connection():
    conn = sqlite3.connect('ai_movie_studio.db', check_same_thread=False)
    return conn

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, wallet_balance_paisa INTEGER)')
cursor.execute('CREATE TABLE IF NOT EXISTS payment_orders (order_id TEXT PRIMARY KEY, username TEXT, amount_paisa INTEGER, currency TEXT, status TEXT)')
conn.commit()
conn.close()

# --- 2. పేజీ కాన్ఫిగరేషన్ (యాప్ లోగో & టైటిల్) ---
st.set_page_config(page_title="AI Movie Studio HD", page_icon="🎬", layout="centered")

# --- 🔥 3. ప్రొఫెషనల్ లుక్ కోసం CSS (లోగోలు, గిట్‌హబ్, కోడింగ్ ఆప్షన్స్ దాచడానికి) ---
st.markdown("""
    <style>
    /* పైన ఉండే స్ట్రీమ్‌లిట్ హెడర్, గిట్‌హబ్ లోగో, Fork ఆప్షన్లను పూర్తిగా దాచడానికి */
    header {visibility: hidden !important;}
    
    /* కింద ఉండే "Hosted with Streamlit" బ్యానర్‌ను దాచడానికి */
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    
    /* యాప్ స్క్రీన్ పైకి జరగడానికి టాప్ మార్జిన్ సర్దుబాటు */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* వీడియో ప్లేయర్ చుట్టూ అందమైన బార్డర్ */
    .stVideo {
        border-radius: 10px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_index=True)

# టెక్స్ట్ టు స్పీచ్ ఫంక్షన్
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

# యాప్ ముఖచిత్రం
st.title("🎬 Real Movie Tech AI Studio")
st.caption("1080p Ultra HD Cinematic Video Generator")

tab1, tab2 = st.tabs(["✨ AI HD Video Studio", "📊 Database Ledger"])

with tab1:
    st.subheader("Cinematic Text-to-Video Engine")
    user_prompt = st.text_area("✍️ వీడియో కోసం మీ ఐడియా/కథ ఇక్కడ రాయండి:", placeholder="ఉదాహరణ: మటన్ కర్రీ చేసినట్టు 1 నిమిషం వీడియో ఇవ్వు...")
    uploaded_photo = st.file_uploader("📸 ఫోటో ఆధారంగా చేయాలనుకుంటే ఇక్కడ అప్‌లోడ్ చేయండి (Optional):", type=["png", "jpg", "jpeg"])
    
    current_user = "test_user"
    conn = get_db_connection()
    cursor = conn.cursor()
    user_row = cursor.execute("SELECT wallet_balance_paisa FROM users WHERE username = ?", (current_user,)).fetchone()
    user_paisa = user_row[0] if user_row else 50000
    conn.close()
    
    st.write(f"💳 **మీ వాలెట్ బ్యాలెన్స్:** ₹{user_paisa/100:.2f}")

    # వీడియో ప్లేస్ కోసం ఒక ఖాళీ కంటైనర్ క్రియేట్ చేస్తున్నాం (ఇది వీడియోను కరెక్ట్ ప్లేస్‌లో చూపిస్తుంది)
    video_placeholder = st.container()

    if st.button("🚀 Generate 1 Minute Ultra HD Video", use_container_width=True):
        if user_prompt:
            VIDEO_COST_PAISA = 5000 
            if user_paisa >= VIDEO_COST_PAISA:
                st.info("🔄 వాలెట్ వెరిఫై అయింది. AI వీడియో జనరేట్ అవుతోంది, దయచేసి వేచి ఉండండి...")
                
                # (ఇక్కడ మీ ఒరిజినల్ FAL_API కీ మరియు రిక్వెస్ట్ లాజిక్ ఉంటుంది)
                # ఉదాహరణకు ఒక డెమో వీడియో యుటిలైజ్ చేస్తున్నాము టెస్టింగ్ కోసం:
                time.sleep(3) 
                raw_video_url = "https://w3schools.com" # మీ API నుండి వచ్చే వీడియో URL ఇక్కడ వస్తుంది
                
                if raw_video_url:
                    # డేటాబేస్ అప్‌డేట్
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    new_balance = user_paisa - VIDEO_COST_PAISA
                    cursor.execute("UPDATE users SET wallet_balance_paisa = ? WHERE username = ?", (new_balance, current_user))
                    cursor.execute("INSERT INTO payment_orders VALUES (?, ?, ?, ?, ?)", (str(time.time()), current_user, VIDEO_COST_PAISA, "INR", "PAID"))
                    conn.commit()
                    conn.close()
                    
                    # 🎯 వీడియో ప్లే అయ్యే కరెక్ట్ ప్లేస్ ఇక్కడ డిజైన్ చేసాం
                    with video_placeholder:
                        st.success("🎉 మీ 1080p Ultra HD AI వీడియో రెడీ అయ్యింది!")
                        # వీడియో ప్లేయర్
                        st.video(raw_video_url)
                        
                        # డౌన్‌లోడ్ బటన్ కూడా ఇక్కడే వస్తుంది
                        st.download_button(
                            label="📥 Download Video",
                            data=requests.get(raw_video_url).content,
                            file_name="ai_movie_1080p.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                        
                    talk_done = "ఇక మీ నిమిషం సినిమా ప్యూర్ టెన్ ఎయిటీ పీ హెచ్ డీ క్వాలిటీ లో రెడీ అయిపోయింది బాస్!"
                    free_live_chatgpt_speaker(talk_done)
                else:
                    st.error("వీడియో జనరేషన్ విఫలమైంది.")
            else:
                st.error("మీ వాలెట్‌లో తగినంత బ్యాలెన్స్ లేదు!")
        else:
            st.warning("దయచేసి స్టోరీ లేదా ప్రాంప్ట్ రాయండి!")

with tab2:
    st.subheader("Database Ledger")
    conn = get_db_connection()
    cursor = conn.cursor()
    st.write("#### Users")
    st.dataframe(cursor.execute("SELECT * FROM users").fetchall(), use_container_width=True)
    conn.close()
