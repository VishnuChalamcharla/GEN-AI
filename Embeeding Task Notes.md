# 📌 Embeddings 

## What is an Embedding?
An **embedding** is a numerical vector that represents the **meaning** of text, images, audio, or video.


Similar meaning → vectors are closer in space.

---

## Why Embeddings are Needed
- LLMs have **token limits**
- Images & videos are large
- Raw media cannot be sent to LLMs
- Enables **semantic search** and **retrieval**

---

## Embedding Types

| Data | Embedding Used |
|----|----|
| Text | Text embedding model |
| Image | Vision embedding (CLIP, ViT) |
| Video Frame | Image embedding |
| Video Clip | Aggregated frame embeddings |
| Audio | Audio embeddings (optional) |

---

## Embedding Dimensions
**Dimension = number of values in the embedding vector**

Example:
[0.1, 0.9, -0.3] → 3 dimensions


### Typical Dimensions

| Model | Dimensions |
|----|----|
| CLIP (Image/Text) | 512 |
| Vision Transformer | 768 / 1024 |
| Text Embeddings | 768 / 1536 |
| Video Embeddings | 1024–4096 |

Higher dimensions → richer meaning (but more cost).

---

## Embedding Strategy

### Image
1 image → 1 embedding


### Video
### Video
Video
→ Split into frames (every N seconds)
→ Each frame → embedding
→ Store with timestamp

Example metadata:
{ "video_id": "vid1", "time": "00:01:32" }


###Task 1: 1.Determine the requirements for building a video or image chatbot with streaming capabilities for images and videos using the concept of embeddings. Embedding Requirements Embedding Types Needed Data Type Embedding Model Image Vision embedding model (CLIP, ViT) Video frame Image embedding model Video clip Aggregated frame embeddings Audio (optional) Audio embeddings Text Text embedding model

Embedding Dimensions (Typical) Model Type Dimensions Image (CLIP) 512 Vision Transformer 768 / 1024 Text embeddings 768 / 1536

Each image/frame → 1 vector Each video → many vectors

Embedding Strategy Image 1 image → 1 embedding

Video → Frames (every N seconds) → Each frame → embedding → Store with timestamp metadata

Example metadata: { "video_id": "vid123", "frame_time": "00:01:32", "embedding": [...] }

Vector Database Requirements Capabilities Needed

High-dimensional vector storage Cosine similarity / dot product Metadata filtering Fast ANN (Approximate Nearest Neighbor) Horizontal scaling

Suitable Databases Pinecone Weaviate FAISS Milvus MongoDB Atlas Vector Search

Query Flow (User Interaction) Example Query “Show me scenes where a person is holding a phone” Steps: Convert query → text embedding Search vector DB against image/video embeddings Retrieve top-K matching frames Group frames → scenes Send context to LLM Stream response + thumbnails
