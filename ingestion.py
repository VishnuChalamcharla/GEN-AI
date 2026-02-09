import os
import re
from pdf2image import convert_from_path
import pytesseract
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PDF_PATH = os.path.join(
    BASE_DIR,
    "catalog_data",
    "pdf_catalogs",
    "WIPRO-Cleanray-Pricelist-1-June-2021-JUNE-1-2021-1.pdf"
)

IMAGE_DIR = os.path.join(
    BASE_DIR,
    "catalog_data",
    "images"
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "structured_data",
    "chroma_db"
)

COLLECTION_NAME = "catalog_pages"
 
POPPLER_PATH = r"C:\Users\Vishnu\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
 
os.makedirs(IMAGE_DIR, exist_ok=True)
 
def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()
 
def main():
    print("📄 Reading PDF...")
    reader = PdfReader(PDF_PATH)
 
    print("🖼️ Converting pages to images...")
    images = convert_from_path(PDF_PATH, dpi=200, poppler_path=POPPLER_PATH)
 
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(COLLECTION_NAME)
 
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
 
    documents, metadatas, ids = [], [], []
 
    for i, img in enumerate(images):
        page_no = i + 1
        print(f"🔍 OCR page {page_no}")
 
        image_path = os.path.join(IMAGE_DIR, f"page_{page_no}.png")
        img.save(image_path)
 
        text = pytesseract.image_to_string(img)
        text = clean_text(text)
 
        if len(text) < 50:
            continue
 
        documents.append(text)
        metadatas.append({
            "page": page_no,
            "image_path": image_path,
            "pdf_path": PDF_PATH
        })
        ids.append(f"page_{page_no}")
 
    print("🧠 Creating embeddings...")
    embeddings = embedder.encode(documents, show_progress_bar=True)
 
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
 
    print("✅ INGESTION COMPLETED")
    print("📦 Total pages indexed:", collection.count())
 
if __name__ == "__main__":
    main()