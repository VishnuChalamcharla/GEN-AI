import os
from groq import Groq
from dotenv import load_dotenv
 
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
 
def generate_answer(query, context):
    prompt = f"""
You are a product catalog assistant.
Answer ONLY from the context below.
Mention page numbers clearly.
 
Context:
{context}
 
Question:
{query}
"""
 
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
 
    return response.choices[0].message.content