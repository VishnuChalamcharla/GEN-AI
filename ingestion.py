"""
========================================================
CMS PDF INGESTION PIPELINE
(OCR + SMART IMAGE NAMING + STRUCTURED DATA + MONGODB)
========================================================
"""

# ---------------- IMPORTS ----------------
import os
import re
import fitz  # PyMuPDF
import pytesseract
import pandas as pd
from pdf2image import convert_from_path
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=ENV_PATH, override=True)

MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise RuntimeError("❌ MONGODB_URI not found in .env file")

print("✅ MongoDB URI loaded")

# ---------------- CONFIG ----------------
PDF_FOLDER = "catalog_data/pdf_catalogs"
TEXT_OUTPUT_FOLDER = "catalog_data/extracted_text"
IMAGE_OUTPUT_FOLDER = "catalog_data/product_images"
STRUCTURED_FOLDER = "catalog_data/structured_data"

os.makedirs(TEXT_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(IMAGE_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(STRUCTURED_FOLDER, exist_ok=True)

# OCR tools
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")
POPPLER_PATH = os.getenv("POPPLER_PATH")

if not pytesseract.pytesseract.tesseract_cmd or not POPPLER_PATH:
    raise RuntimeError("❌ TESSERACT_PATH or POPPLER_PATH missing in .env")

# ---------------- MONGODB (REQUIRED) ----------------
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # force connection
    db = client["catalog_db"]
    print("✅ Connected to MongoDB successfully")
except Exception as e:
    raise RuntimeError(f"❌ MongoDB connection failed: {e}")

# ---------------- STEP 1: OCR TEXT ----------------
def extract_text_with_ocr(pdf_path, brand_name):
    print(f"📄 OCR processing: {brand_name}")

    pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    full_text = ""

    for i, page_image in enumerate(pages):
        text = pytesseract.image_to_string(page_image, lang="eng")
        full_text += f"\n\n--- Page {i+1} ---\n{text}"

    text_path = os.path.join(TEXT_OUTPUT_FOLDER, f"{brand_name}.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"✅ OCR text saved → {text_path}")

# ---------------- STEP 2: SMART IMAGE EXTRACTION ----------------
def extract_images_from_pdf(pdf_path, brand_name):
    print(f"🖼 Extracting images: {brand_name}")
    doc = fitz.open(pdf_path)

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_text = page.get_text("text").lower()

        detected_name = None

        sku_match = re.search(r"\b\d{3,}\b", page_text)
        if sku_match:
            detected_name = sku_match.group()

        if not detected_name:
            model_match = re.search(r"(model\s*[:\-]?\s*[a-z0-9\-]+)", page_text)
            if model_match:
                detected_name = model_match.group().replace("model", "").strip()

        if not detected_name:
            detected_name = f"{brand_name}_page{page_index+1}"

        detected_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", detected_name)

        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base = doc.extract_image(xref)

            image_path = os.path.join(
                IMAGE_OUTPUT_FOLDER,
                f"{detected_name}_{img_index+1}.{base['ext']}"
            )
            with open(image_path, "wb") as f:
                f.write(base["image"])

    print(f"✅ Images extracted for {brand_name}")

# ---------------- STEP 3: STRUCTURED DATA ----------------
def extract_structured_data(brand_name):
    txt_path = os.path.join(TEXT_OUTPUT_FOLDER, f"{brand_name}.txt")
    if not os.path.exists(txt_path):
        return

    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    products = []
    current = {
        "brand": brand_name,
        "product_name": "",
        "sku": "",
        "price": "",
        "specs": []
    }

    price_pattern = r"(₹\s?\d+[,\d]*\.?\d*|Rs\.?\s?\d+[,\d]*\.?\d*)"
    sku_pattern = r"(SKU[:\s\-]*[A-Z0-9\-]+)"
    model_pattern = r"(Model[:\s\-]*[A-Z0-9\-]+)"

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.search(sku_pattern, line, re.I):
            current["sku"] = re.sub(r"SKU|:", "", line, flags=re.I).strip()

        if re.search(model_pattern, line, re.I):
            current["product_name"] = re.sub(r"Model|:", "", line, flags=re.I).strip()

        price_match = re.search(price_pattern, line)
        if price_match:
            current["price"] = price_match.group()
            current["specs"] = "; ".join(current["specs"])
            products.append(current.copy())
            current = {
                "brand": brand_name,
                "product_name": "",
                "sku": "",
                "price": "",
                "specs": []
            }
            continue

        if any(k in line.lower() for k in ["watt", "volt", "mm", "kg", "capacity", "power"]):
            current["specs"].append(line)

    if not products:
        return

    csv_path = os.path.join(STRUCTURED_FOLDER, "price_list.csv")
    new_df = pd.DataFrame(products)

    if os.path.exists(csv_path):
        old = pd.read_csv(csv_path)
        old = old[old["brand"] != brand_name]
        pd.concat([old, new_df]).to_csv(csv_path, index=False)
    else:
        new_df.to_csv(csv_path, index=False)

    print(f"✅ Structured data saved for {brand_name}")

# ---------------- STEP 4: MONGODB UPSERT ----------------
def sync_csv_to_mongodb(csv_name, collection, keys):
    path = os.path.join(STRUCTURED_FOLDER, csv_name)
    if not os.path.exists(path):
        return

    df = pd.read_csv(path)
    if df.empty:
        return

    ops = []
    for row in df.to_dict("records"):
        query = {k: row.get(k) for k in keys}
        ops.append(UpdateOne(query, {"$set": row}, upsert=True))

    collection.bulk_write(ops)
    print(f"🗄 MongoDB synced → {csv_name}")

# ---------------- MAIN PIPELINE ----------------
def process_all_pdfs():
    for file in os.listdir(PDF_FOLDER):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(PDF_FOLDER, file)
            brand = os.path.splitext(file)[0]

            print(f"\n🚀 Processing catalog: {brand}")
            extract_text_with_ocr(pdf_path, brand)
            extract_images_from_pdf(pdf_path, brand)
            extract_structured_data(brand)

    # MongoDB sync (MANDATORY)
    sync_csv_to_mongodb("price_list.csv", db.prices, ["sku"])

# ---------------- RUN ----------------
if __name__ == "__main__":
    print("\n🔥 CMS PDF INGESTION STARTED\n")
    process_all_pdfs()
    print("\n🎉 CMS INGESTION COMPLETED SUCCESSFULLY\n")
