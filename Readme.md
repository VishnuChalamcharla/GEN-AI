# 🤖 Product Catalogue Assistant (RAG-Based)

This project is a **Retrieval-Augmented Generation (RAG)** based Product Catalogue Assistant built using **Python**.  
It allows users to ask natural language questions and get accurate answers **only from product catalog PDFs**, using embeddings and semantic search.

---

## 🚀 Features

- 📄 Ingest product catalog PDFs
- 🔍 Semantic search using vector embeddings
- 🧠 Context-aware question answering
- ❌ Avoids hallucinations by answering strictly from retrieved context
- 🧩 Modular and clean code structure
- 🔐 Environment-based configuration

---

## 🏗️ Project Structure



.
├── app.py # Main application entry point
├── ingestion.py # PDF ingestion & chunking
├── Embedding.py # Embedding generation logic
├── Retrieval.py # Vector search & retrieval
├── History_aware.py # Chat history aware retrieval
├── answer_gen.py # LLM-based answer generation
├── requirements.txt # Python dependencies
├── .env # Environment variables (NOT committed)
└── README.md # Project documentation


---

## ⚙️ Tech Stack

- **Python 3.9+**
- **LangChain**
- **Vector Database (FAISS / MongoDB / Chroma – based on config)**
- **LLM (Groq / OpenAI / HuggingFace)**
- **PDF loaders**
- **Dotenv for secrets**

---

## 🔧 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/product-catalog-rag.git
cd product-catalog-rag

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create a .env file in the root directory:

GROQ_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
MONGODB_URI=your_mongodb_uri_here


⚠️ Never commit .env to GitHub

📥 Data Ingestion

Place your product catalog PDFs in the configured data folder and run:

python ingestion.py


This will:

Load PDFs

Split text into chunks

Generate embeddings

Store them in the vector database

💬 Run the Application
python app.py


Ask questions like:

“List available LED downlights”

“What is the wattage of model LD98?”

“Show slim square downlighter details”

🧠 How It Works (RAG Flow)

User asks a question

Question is converted to embeddings

Relevant chunks are retrieved from vector DB

LLM generates an answer only from retrieved context

Page numbers are included (if available)
