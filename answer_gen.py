from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from Retrieval import retrieve_documents
 
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)
 
chat_history = [
    SystemMessage(content="You are a product catalog assistant. Answer ONLY using provided catalog data and always cite source file and page number.")
]
 
def answer_question(query):
    docs = retrieve_documents(query)
 
    if not docs:
        return "No relevant catalog data found in the catalog.", []
 
    context_blocks = []
    for d in docs:
        citation = f"(Source: {d.get('source_file')} | Page: {d.get('page_number')})"
        context_blocks.append(d["text"] + "\n" + citation)
 
    context = "\n\n".join(context_blocks)
 
    prompt = f"""
Use ONLY the product catalog data below to answer.
Always include citation like (Source: file | Page X).
 
Catalog Data:
{context}
 
User Question: {query}
"""
 
    chat_history.append(HumanMessage(content=prompt))
    response = llm.invoke(chat_history)
    chat_history.append(AIMessage(content=response.content))
 
    return response.content, docs
