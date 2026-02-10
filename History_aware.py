
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from Retrieval import retrieve_documents
 
chat_history = []
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
 
def ask(query):
    original_query = query  # keep for history
 
    # Step 1 — Rewrite follow-up question if history exists
    if chat_history:
        rewrite_prompt = [
            SystemMessage(content="Rewrite the user question into a standalone question using the conversation history. Only return the rewritten question.")
        ] + chat_history + [
            HumanMessage(content=query)
        ]
 
        query = llm.invoke(rewrite_prompt).content.strip()
        print(f"[Rewritten Query]: {query}")
 
    # Step 2 — Retrieve documents
    docs = retrieve_documents(query)
 
    if not docs:
        return "No relevant catalog data found.", []
 
    # Combine retrieved text
    context = "\n\n".join(doc["text"] for doc in docs)
 
    # Step 3 — Answer using retrieved context
    answer_prompt = f"""
You are a helpful product catalog assistant for Philips and Legrand products.
 
Your job is to help users choose products using ONLY the catalog data provided.
 
Guidelines:
- You MAY suggest suitable products from the catalog based on user needs.
- If the user request is vague (e.g., "good light"), recommend popular or general-purpose options from the catalog.
- If the user adds more details (like "for party" or "for bedroom"), refine your recommendation.
- DO NOT invent products, prices, or features not present in the catalog.
- If the catalog truly has nothing relevant, say you don't have enough information.
 
Catalog Context:
{context}
 
User Question: {query}
"""
 
    answer = llm.invoke([HumanMessage(content=answer_prompt)]).content
 
    # Step 4 — Save conversation (use ORIGINAL user wording)
    chat_history.append(HumanMessage(content=original_query))
    chat_history.append(AIMessage(content=answer))
 
    # IMPORTANT CHANGE: return answer + source docs
    return answer, docs
 
 
if __name__ == "__main__":
    print("History-Aware Catalog Assistant Ready! Type 'exit' to stop.\n")
 
    while True:
        user_q = input("You: ")
 
        if user_q.lower() in ["exit", "quit"]:
            break
 
        response, _ = ask(user_q)   # ignore docs in terminal mode
        print(f"Assistant: {response}\n")
 