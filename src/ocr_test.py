import glob
import cv2
import pytesseract
from PIL import Image
from autocorrect import Speller
from pypdf import PdfReader

# 1. Tesseract Windows Path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 2. Auto-speller initialize karo
spell = Speller(lang='en')

print("--- Smart Contract Intelligence Pipeline with OpenCV Started ---")

# 3. Saari Files par loop chalao
all_files = glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("*.pdf")

for file_path in all_files:
    print(f"\n[Scanning File]: {file_path}")
    raw_text = ""
    
    # --- IF FILE IS PDF ---
    if file_path.lower().endswith('.pdf'):
        print("-> Format: PDF Document. Extracting digital text...")
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    raw_text += page_text + "\n"
        except Exception as e:
            print(f"❌ PDF Read Error: {e}")
            
    # --- IF FILE IS IMAGE (PNG/JPG) -> OpenCV Preprocessing ---
    else:
        print("-> Format: Image. Applying OpenCV Preprocessing filters...")
        try:
            # 1. Image ko OpenCV se load karo
            img = cv2.imread(file_path)
            
            # 2. Convert to Grayscale (Black & White shades)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 3. Apply Adaptive Thresholding (Noise hatane ke liye aur text dark karne ke liye)
            processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # 4. Saaf ki hui image ko temporarily save karo scan karne ke liye
            temp_filename = "temp_processed.png"
            cv2.imwrite(temp_filename, processed_img)
            
            # 5. Tesseract ko processed image do
            raw_text = pytesseract.image_to_string(Image.open(temp_filename))
        except Exception as e:
            print(f"❌ Image OCR/OpenCV Error: {e}")

    # Agar text nahi mila toh agli file par jao
    if not raw_text.strip():
        print("⚠️ No text could be extracted from this file.")
        continue

    # --- STEP 2: TEXT CORRECTIONS ---
    replaced_text = raw_text.replace("SURLNGTON", "BURLINGTON")
    replaced_text = replaced_text.replace("bse", "base")
    final_text = spell(replaced_text)
    
    print("\n--- FINAL CORRECTED TEXT ---")
    print(final_text)
    print("----------------------------")

    # --- STEP 3: RISK SCORING SYSTEM ---
    risk_keywords = {
        "termination": 20,
        "penalty": 15,
        "breach": 25,
        "liability": 20,
        "damage": 10
    }
    
    total_risk_score = 0
    found_risks = []
    text_lower = final_text.lower()
    
    for word, score in risk_keywords.items():
        if word in text_lower:
            total_risk_score += score
            found_risks.append(f"{word.upper()} (+{score})")
            
    print("\n📊 --- RISK SCORING REPORT ---")
    print(f"Total Risk Score: {total_risk_score}/100")
    if found_risks:
        print(f"Risk Factors Found: {', '.join(found_risks)}")
    else:
        print("✅ No major risk keywords detected.")
    print("==================================================")