import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise EnvironmentError("MONGODB_URI not found in .env file")

# -------------------------------------------------
# MongoDB connection
# -------------------------------------------------
try:
    client = MongoClient(MONGODB_URI)
    db = client["catalog_db"]
    collection = db["Embeddings"]
    print("Connected to MongoDB")
except Exception as e:
    raise ConnectionError(f"Failed to connect to MongoDB: {e}")

# -------------------------------------------------
# Embedding model
# -------------------------------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -------------------------------------------------
# Retrieval function (FINAL)
# -------------------------------------------------
def retrieve_documents(query, k=5):
    print(f"\nUser Query: {query}")

    query_vector = embedding_model.embed_query(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": k
            }
        },
        {
            "$project": {
                "_id": 0,
                "text": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    print(f"Retrieved {len(results)} documents")

    if not results:
        return []

    formatted_results = []
    for r in results:
        meta = r.get("metadata", {})

        formatted_results.append({
            "text": r.get("text", ""),
            "score": r.get("score", 0),
            "product_name": meta.get("product_name"),
            "page_number": meta.get("page_number"),
            "image_path": meta.get("image_path"),
            "pdf_path": meta.get("pdf_path"),
            "source_file": meta.get("source_file")
        })

    return formatted_results
