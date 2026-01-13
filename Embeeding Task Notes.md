# 📌 Embeddings – Ultra-Short Revision Notes

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
```json
{ "video_id": "vid1", "time": "00:01:32" }

Task 1: Video/Image Chatbot Requirements

Frame extraction from video

Multimodal embedding generation

Vector database for search

Metadata (time, frame ID)

Parallel processing for streaming

LLM for response generation

Query Flow

User Query → Text Embedding
→ Vector DB Search
→ Top-K Frames Retrieved
→ Group into Scenes
→ Context sent to LLM
→ Response streamed to user

LLM never processes raw video.

Task 2: Models & Dimensions

Embedding = vector of numbers

Dimensions = size of the vector

All compared embeddings must have the same dimension
