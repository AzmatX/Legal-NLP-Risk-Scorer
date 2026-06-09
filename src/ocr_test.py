import os
import glob
import cv2
import pytesseract
from PIL import Image
from autocorrect import Speller # Auto-correct library

# 1. Tesseract Windows Path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 2. Auto-speller initialize karo
spell = Speller(lang='en')

print("--- OCR Pipeline with Corrections Started ---")

# 3. Folder ki saari PNG aur JPG images par loop
for img_path in glob.glob("*.png") + glob.glob("*.jpg"):
    print(f"\n[Scanning File]: {img_path}")
    
    # Raw text extract karo
    raw_text = pytesseract.image_to_string(Image.open(img_path))
    
    # --- TARIKA 1: Direct Replace (Specific text theek karne ke liye) ---
    replaced_text = raw_text.replace("sURLNGTON", "BURLINGTON")
    replaced_text = replaced_text.replace("bse", "base")
    
    # --- TARIKA 2: Auto Spelling Checker (Baaki chhoti mistakes ke liye) ---
    final_text = spell(replaced_text)
    
    print("\n--- FINAL CORRECTED TEXT ---")
    print(final_text)
    
    # --- STEP 3: RISK SCORING SYSTEM ---
    # Risk waale shabdo ki list aur unke points
    risk_keywords = {
        "termination": 20,
        "penalty": 15,
        "breach": 25,
        "liability": 20,
        "damage": 10
    }
    
    total_risk_score = 0
    found_risks = []
    
    # Text ko lowercase mein badlo taaki scanning sahi se ho
    text_lower = final_text.lower()
    
    # Shabdo ko scan karo
    for word, score in risk_keywords.items():
        if word in text_lower:
            total_risk_score += score
            found_risks.append(f"{word.upper()} (+{score})")
            
    # Risk Report Print Karo
    print("\n📊 --- RISK SCORING REPORT ---")
    print(f"Total Risk Score: {total_risk_score}/100")
    if found_risks:
        print(f"Risk Factors Found: {', '.join(found_risks)}")
    else:
        print("✅ No major risk keywords detected.")
    print("==================================")
    