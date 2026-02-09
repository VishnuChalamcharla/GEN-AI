import os
import chromadb
from sentence_transformers import SentenceTransformer
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "db", "chroma_db")
COLLECTION_NAME = "catalog_pages"
 
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(COLLECTION_NAME)
 
embedder = SentenceTransformer("all-MiniLM-L6-v2")
 
def retrieve(query, top_k=3):
    embedding = embedder.encode(query).tolist()
 
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents", "metadatas"]
    )
 
    docs = results["documents"][0]
    metas = results["metadatas"][0]
 
    return list(zip(docs, metas))
 
if __name__ == "__main__":
    results = retrieve("Intel Core i7 NVIDIA graphics laptop")
    for doc, meta in results:
        print("\n📄 Page:", meta["page"])
        print(doc[:300])
 