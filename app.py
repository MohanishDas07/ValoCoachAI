import streamlit as st
import cv2
import pytesseract
import numpy as np
import re
import os

# IMPORTANT: Keep your exact Tesseract path here!
if os.name == 'nt':
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# --- 1. WEB APP SETUP ---
st.set_page_config(page_title="ValoCoach AI", page_icon="🎮", layout="centered")
st.title("🧠 ValoCoach AI")
st.subheader("Upload your post-match scoreboard to get instant coaching.")

# --- 2. FILE UPLOADER ---
# This creates the drag-and-drop box on the website
uploaded_file = st.file_uploader("Drop your Valorant screenshot here", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    # Show a spinning loading wheel while the AI thinks
    with st.spinner("Scanning match data..."):
        
        # --- 3. CONVERT WEB IMAGE TO OPENCV FORMAT ---
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        # --- 4. THE AI VISION PIPELINE (From your scanner.py) ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(thresh, config=custom_config)

        # --- 5. DATA CLEANING (Regex) ---
        # --- 5. DATA CLEANING (Bulletproof OCR Logic) ---
        
        # 1. Clean the raw text: Replace slashes, pipes, and OCR artifacts with spaces
        clean_text = re.sub(r'[/|\\lI]', ' ', extracted_text)

        valid_player_stats = []
        
        # 2. Parse the data line by line
        for line in clean_text.split('\n'):
            # Find all standalone numbers in the current line
            numbers = re.findall(r'\b\d+\b', line)
            
            # A standard Valorant stat line ALWAYS ends with Combat Score, K, D, A
            if len(numbers) >= 4:
                # We slice the array to grab ONLY the last 4 numbers. 
                # This ignores random numbers Tesseract might read in a player's username.
                valid_player_stats.append(numbers[-4:])

        if not valid_player_stats:
            st.error("Could not find clean stat lines. Make sure it's a clear scoreboard screenshot!")
        else:
            # Grab the first valid player's stats
            first_player_stats = valid_player_stats[0]
            combat_score = int(first_player_stats[0])
            kills = int(first_player_stats[1])
            deaths = int(first_player_stats[2])
            assists = int(first_player_stats[3])
            
            kd_ratio = round(kills / deaths, 2) if deaths > 0 else kills
            # --- 6. THE DASHBOARD UI ---
            st.success("Match Data Extracted Successfully!")
            
            import google.generativeai as genai

# ... (Keep your existing imports and setup code at the top) ...

# --- NEW: UI FOR CONTEXT ---
st.markdown("### 📝 Match Context")
col_rank, col_agent = st.columns(2)
user_rank = col_rank.selectbox("What is your current rank?", ["Iron/Bronze", "Silver/Gold", "Platinum/Diamond", "Ascendant+"])
user_agent = col_agent.selectbox("Which Agent did you play?", ["Duelist (Jett/Reyna/Raze)", "Controller (Omen/Clove/Viper)", "Initiator (Sova/Fade/Skye)", "Sentinel (Killjoy/Cypher/Sage)"])

# ... (Keep your existing File Uploader and Regex extraction here) ...

if not valid_player_stats:
            st.error("Could not find clean stat lines. Make sure it's a clear scoreboard screenshot!")
else:
            # Grab the first valid player's stats
            first_player_stats = valid_player_stats[0]
            
            combat_score = int(first_player_stats[0])
            kills = int(first_player_stats[1])
            deaths = int(first_player_stats[2])
            assists = int(first_player_stats[3])
            
            kd_ratio = round(kills / deaths, 2) if deaths > 0 else kills

            st.success("Match Data Extracted Successfully!")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Kills", kills)
            col2.metric("Deaths", deaths)
            col3.metric("Assists", assists)
            col4.metric("K/D Ratio", kd_ratio)

            # --- NEW: THE LLM COACHING ENGINE ---
            st.markdown("### 🧠 AI Coach Analysis")
            
            # We add a button so the AI only generates advice when the user is ready
            if st.button("Generate Custom Coaching Plan"):
                with st.spinner("Consulting Radiant Coach API..."):
                    
                    # 1. Setup the API Key (We will secure this later)
                    # Get a free key from Google AI Studio
                    # Pull the key securely from the Streamlit vault
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-2.5-flash')

                    # 2. Construct the Prompt
                    prompt = f"""
                    You are a professional Radiant-level Valorant coach.
                    Your student is currently in {user_rank} and played a {user_agent} in their last match.
                    Their stats were: {kills} Kills, {deaths} Deaths, {assists} Assists, and a Combat Score of {combat_score}.
                    
                    Please provide a highly structured, analytical response formatted in Markdown:
                    1. **Performance Verdict:** A harsh but fair 2-sentence analysis of their K/D/A based on their role.
                    2. **Actionable Steps:** 3 concrete, step-by-step things they need to practice in the range or deathmatch to fix their specific issues.
                    3. **Recommended Resources:** Specific YouTube creators, aim training routines (like Voltaic), or websites they should use to study their role.
                    """

                    # 3. Fetch and display the response
                    try:
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                    except Exception as e:
                        # This will print the exact technical reason it failed
                        st.error(f"System Error: {e}")