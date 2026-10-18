import streamlit as st
import requests
import time

# --- 1. అఫీషియల్ డిఫాల్ట్ లేఅవుట్ కాన్ఫిగరేషన్ (నో హైడింగ్స్ - సూపర్ సేఫ్) ---
st.set_page_config(page_title="AI Movie Studio HD", layout="centered")

st.markdown("""
    <style>
    /* ఎడమ, కుడి వైపులా ఉండే చిహ్నాలను హైడ్ చేయడానికి సురక్షితమైన CSS */
    header, [data-testid="stHeader"], .stAppDeployButton, #MainMenu, [data-testid="collapsedControl"] { 
        display: none !important; 
    }
    footer { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

FAL_API_KEY = "fal_sk_fba7ddbf009141529452771949a7babbf6a8868d86a405e8666ee3f10cdb2773"

# --- 2. ఏపీఐ కనెక్టివిటీ ఫంక్షన్లు ---
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
                        return res_json.get("video", {}).get("url")
                    elif res_json.get("status") == "FAILED":
                        break
        return None
    except Exception:
        return None

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


# --- 3. ఐదు ప్రధాన కోర్ విజెట్స్ (వరుస క్రమంలో పక్కాగా లోడ్ అవుతాయి) ---
st.title("🎬 Movie Demo Workspace")

# టూల్ 1: కథ రాసే బాక్స్
user_prompt = st.text_area("✍️ వీడియో ఐడియా లేదా కథ ఇక్కడ రాయండి:", placeholder="ఉదాహరణ: ఒక సింహం అడవిలో గర్జిస్తున్నట్టు వీడియో ఇవ్వు...", height=150)

# టూల్ 2: ఫోటో అప్‌లోడర్
uploaded_photo = st.file_uploader("📸 ఫోటో ఆధారంగా చేయాలనుకుంటే ఇక్కడ అప్‌లోడ్ చేయండి (Optional):", type=["png", "jpg", "jpeg"])

# టూల్ 3: నిడివి స్లైడర్ (10 సెకన్ల నుండి 20 నిమిషాల వరకు)
video_duration = st.slider("⏱️ వీడియో నిడివి సెలెక్ట్ చేయండి (సెకన్లలో):", min_value=10, max_value=1200, value=10, step=5)
if video_duration < 60:
    duration_text = f"{video_duration} సెకన్లు"
else:
    duration_text = f"{video_duration // 60} నిమిషాల {video_duration % 60} సెకన్లు"
st.write(f"ఎంచుకున్న సమయం: **{duration_text}**")

# టూల్ 4: సైజ్ సెలెక్టర్ ఫార్మాట్ డ్రాప్‌డౌన్
video_type = st.selectbox(
    "📐 వీడియో టైప్ లేదా సైజ్ ఎంచుకోండి:",
    ["📱 Instagram Reel / Shorts (9:16)", "📺 YouTube Full Video (16:9)", "🟩 Square Post / Video (1:1)"]
)
selected_ratio = "9:16" if "9:16" in video_type else ("1:1" if "1:1" in video_type else "16:9")

video_placeholder = st.container()

# 🚀 టూల్ 5: సబ్మిట్ బటన్ (Generate Button)
if st.button("🚀 Generate HD Video", use_container_width=True):
    if user_prompt:
        st.info("🔄 1080p Ultra HD మూవీ టెక్ ఇంజన్లు రన్ అవుతున్నాయి...")
        headers = {"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"}
        
        talk_1 = "వీడియో విజువల్స్ డిజైన్ చేస్తున్నాను బాస్."
        play_elevenlabs_voice(talk_1, headers)
        
        final_photo_url = ""
        if uploaded_photo is None:
            st.info("📸 FLUX/Dev ఆటో-ఫోటో జనరేట్ అవుతోంది...")
            final_photo_url = generate_flux_dev_photo(user_prompt, headers)
            if final_photo_url:
                st.image(final_photo_url, width=250)
        else:
            final_photo_url = "https://unsplash.com"

        boosted_video_prompt = f"High-end cinema tech footage, 1080p ultra realism, dramatic dynamic camera motion, matching: {user_prompt}"

        video_payload = {
            "prompt": boosted_video_prompt, 
            "image_url": final_photo_url, 
            "aspect_ratio": selected_ratio,
            "duration": video_duration,
            "frame_size": "1080p",
            "guidance_scale": 4.5,
            "num_inference_steps": 28
        }
        
        raw_video_url = call_fal_ai_video_api(video_payload, headers, FAL_API_KEY)
        
        if raw_video_url:
            with video_placeholder:
                st.success("🎉 వీడియో రెడీ అయ్యింది!")
                st.video(raw_video_url)
                
                video_bytes = requests.get(raw_video_url).content
                st.download_button(label="📥 Download Video", data=video_bytes, file_name="video.mp4", mime="video/mp4", use_container_width=True)
        else:
            st.error("AI సర్వర్ బిజీగా ఉంది. మళ్లీ ట్రై చేయండి.")
    else:
        st.warning("దయచేసి కథ రాయండి!")
