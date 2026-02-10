import os
import re
import hashlib
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# -------------------------------------------------
# ENV SETUP
# -------------------------------------------------
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")

if not HF_TOKEN or not MONGODB_URI:
    raise EnvironmentError("Missing HuggingFace token or MongoDB URI")

client = MongoClient(MONGODB_URI)

# ⬇️ KEEPING YOUR EXISTING DB + COLLECTION
db = client["catalog_db"]
collection = db["Embeddings"]

# -------------------------------------------------
# Metadata Enrichment (ONLY ADDING REQUIRED FIELDS)
# -------------------------------------------------
def enrich_metadata(chunk):
    text = chunk.page_content.lower()
    source_path = chunk.metadata.get("source", "")

    brand = os.path.splitext(os.path.basename(source_path))[0].lower()
    product_name = brand.replace("-", " ").title()

    image_dir = "catalog_data/product_images"
    image_path = None

    page_number = chunk.metadata.get("page_number", "N/A")

    # SKU match
    sku_match = re.search(r"\b\d{3,}\b", text)
    if sku_match:
        sku = sku_match.group()
        for file in os.listdir(image_dir):
            if file.startswith(sku):
                image_path = os.path.join(image_dir, file).replace("\\", "/")
                break

    # Model match
    if not image_path:
        model_match = re.search(r"model\s*[:\-]?\s*([a-z0-9\-]+)", text)
        if model_match:
            model = re.sub(r"[^a-z0-9]", "_", model_match.group(1))
            for file in os.listdir(image_dir):
                if file.startswith(model):
                    image_path = os.path.join(image_dir, file).replace("\\", "/")
                    break

    # Page fallback image
    if not image_path and page_number != "N/A":
        for file in os.listdir(image_dir):
            if f"_page{page_number}_" in file:
                image_path = os.path.join(image_dir, file).replace("\\", "/")
                break

    # ✅ YOUR REQUESTED LOGIC (ADDED, NOT CHANGED)
    pdf_filename = os.path.basename(source_path).replace(".txt", ".pdf")
    pdf_path = os.path.join("catalog_data/pdf_catalogs", pdf_filename).replace("\\", "/")

    chunk.metadata.update({
        "brand": "philips",
        "product_name": product_name,
        "image_path": image_path,
        "product_url": None,
        "source_file": os.path.basename(source_path),
        "page_number": page_number,
        "pdf_path": pdf_path
    })

    return chunk

# -------------------------------------------------
# Load Documents
# -------------------------------------------------
def load_documents(docs_path="catalog_data/extracted_text"):
    print("\nLoading documents...")

    loader = DirectoryLoader(
        path=docs_path,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8", "autodetect_encoding": True}
    )

    documents = loader.load()

    for doc in documents:
        doc.metadata["source_text"] = doc.page_content

    print(f"Loaded {len(documents)} documents")
    return documents

# -------------------------------------------------
# Split Documents
# -------------------------------------------------
def split_documents(documents, chunk_size=1000, chunk_overlap=100):
    print("\nSplitting documents...")

    splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_documents(documents)

    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        text_hash = hashlib.md5(chunk.page_content.encode("utf-8")).hexdigest()
        chunk.metadata["chunk_id"] = f"{source}_{text_hash}"

        full_text = chunk.metadata.get("source_text", "")
        page_match = re.search(r"--- Page (\d+) ---", full_text)
        chunk.metadata["page_number"] = page_match.group(1) if page_match else "N/A"

        enrich_metadata(chunk)

    print(f"Created {len(chunks)} chunks")
    return chunks

# -------------------------------------------------
# Store Embeddings
# -------------------------------------------------
def store_embeddings(chunks):
    print("\nGenerating embeddings using Hugging Face...")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    operations = []

    for chunk in chunks:
        vector = embedding_model.embed_query(chunk.page_content)

        operations.append(
            UpdateOne(
                {"chunk_id": chunk.metadata["chunk_id"]},
                {
                    "$set": {
                        "text": chunk.page_content,
                        "embedding": vector,
                        "metadata": chunk.metadata
                    }
                },
                upsert=True
            )
        )

    if operations:
        collection.bulk_write(operations)
        print(f"Stored/Updated {len(operations)} embeddings")

# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    documents = load_documents()
    chunks = split_documents(documents)
    store_embeddings(chunks)

if __name__ == "__main__":
    main()
