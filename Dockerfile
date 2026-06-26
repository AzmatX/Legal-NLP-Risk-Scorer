FROM python:3.11-slim

# ⚠️ CRITICAL FIX: OCR (Tesseract) aur PDF (Poppler) ke binaries install kar rahe hain.
# Agar yeh nahi hua toh "pytesseract.pytesseract.TesseractNotFoundError" aayegi.
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependency caching ke liye pehle sirf pyproject.toml copy karo
COPY pyproject.toml README.md /app/

# Python packages install karo
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .

# Baaki source code copy karo
COPY src /app/src

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]