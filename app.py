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
        stat_pattern = r'\d+\s+\d+\s+\d+\s+\d+'
        matches = re.findall(stat_pattern, extracted_text)

        if not matches:
            st.error("Could not find clean stat lines. Make sure it's a clear scoreboard screenshot!")
        else:
            # Grab the first player's stats
            first_player_stats = matches[0].split()
            combat_score = int(first_player_stats[0])
            kills = int(first_player_stats[1])
            deaths = int(first_player_stats[2])
            assists = int(first_player_stats[3])
            
            kd_ratio = round(kills / deaths, 2) if deaths > 0 else kills

            # --- 6. THE DASHBOARD UI ---
            st.success("Match Data Extracted Successfully!")
            
            # Create 4 columns for a slick stat display
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Kills", kills)
            col2.metric("Deaths", deaths)
            col3.metric("Assists", assists)
            col4.metric("K/D Ratio", kd_ratio)

            # --- 7. THE AI COACHING VERDICT ---
            st.markdown("### 🤖 Coach's Verdict")
            
            if kd_ratio < 1.0:
                st.warning("**Underperforming in pure duels.**\n\nYour K/D is negative. Stop taking fair 50/50 fights. Focus on trading your teammates and using utility to blind/stun before swinging.")
            elif assists > 8:
                st.info("**High Impact Support.**\n\nYou are setting your team up perfectly. If you are losing, you need to communicate your utility timing better to your duelists.")
            elif kills > 20:
                st.success("**Hard Carrying.**\n\nYou are mechanically out-aiming the lobby. If you lost this match, it's a macro-strategy issue, not an aim issue. Start calling rotations.")
            else:
                st.info("**Average Performance.**\n\nYou are trading evenly. To rank up, you need to find ways to secure 2 kills per round, usually by improving crosshair placement.")
            
            # A cool toggle to let users see the black-and-white image the AI processed
            with st.expander("See what the AI saw (Debug View)"):
                st.image(thresh, caption="Thresholded Image processing view")