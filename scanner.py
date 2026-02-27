import cv2
import pytesseract
import re # NEW: Import Regular Expressions for data cleaning

# Point Python to your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_stats(image_path):
    print("[System] Initializing AI Vision...")
    img = cv2.imread(image_path)

    if img is None:
        print("Error: Could not load image.")
        return

    # 1. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # 3. OCR Extraction
    print("[System] Scanning image...\n")
    custom_config = r'--oem 3 --psm 6'
    extracted_text = pytesseract.image_to_string(thresh, config=custom_config)

    # ---------------------------------------------------------
    # NEW: DATA CLEANING & AI COACH LOGIC
    # ---------------------------------------------------------
    print("=== RAW DATA CLEANUP ===")
    
    # Regex Pattern: Looks for "Number Space Number Space Number Space Number"
    # Example match: "189 14 15 5"
    stat_pattern = r'\d+\s+\d+\s+\d+\s+\d+'
    matches = re.findall(stat_pattern, extracted_text)

    if not matches:
        print("Could not find clean stat lines. Image might be too messy.")
        return

    # Let's just look at the first player's stats (usually YOU on the tracker app)
    first_player_stats = matches[0].split()
    
    combat_score = int(first_player_stats[0])
    kills = int(first_player_stats[1])
    deaths = int(first_player_stats[2])
    assists = int(first_player_stats[3])

    print(f"Data Extracted Successfully!")
    print(f"Kills: {kills} | Deaths: {deaths} | Assists: {assists}")
    print("========================\n")

    # --- THE AI COACH ENGINE ---
    print("🧠 VALOCOACH AI ANALYSIS 🧠")
    kd_ratio = round(kills / deaths, 2) if deaths > 0 else kills
    print(f"K/D Ratio: {kd_ratio}")

    if kd_ratio < 1.0:
        print("Verdict: Underperforming in pure duels.")
        print("Advice: Your K/D is negative. Stop taking fair 50/50 fights. Focus on trading your teammates and using utility to blind/stun before swinging.")
    elif assists > 8:
        print("Verdict: High Impact Support.")
        print("Advice: You have great assist numbers. You are setting your team up perfectly. If you are losing, you need to communicate your utility timing better to your duelists.")
    elif kills > 20:
        print("Verdict: Hard Carrying.")
        print("Advice: You are mechanically out-aiming the lobby. If you lost this match, it's a macro-strategy issue, not an aim issue. Start calling rotations.")
    else:
        print("Verdict: Average Performance.")
        print("Advice: You are trading evenly. To rank up, you need to find ways to secure 2 kills per round, usually by improving crosshair placement.")

if __name__ == "__main__":
    extract_stats('scoreboard.jpg')