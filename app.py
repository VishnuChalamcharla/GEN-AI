import streamlit as st
import os
from Retrieval import retrieve
from answer_gen import generate_answer
 
# ==========================
# PAGE CONFIG
# ==========================
 
st.set_page_config(page_title="Catalogue RAG", layout="wide")
st.title("📦 Catalogue Management RAG Assistant")
 
# ==========================
# PDF HTTP CONFIG
# ==========================
 
PDF_HTTP_BASE = (
    "http://localhost:8000/docs/pdf/"
    "IT-Product-Guide-April-2020-to-June-2020.pdf"
)
 
# ==========================
# SESSION STATE
# ==========================
 
if "messages" not in st.session_state:
    st.session_state.messages = []
 
# ==========================
# CHAT HISTORY
# ==========================
 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
 
        if msg.get("image"):
            st.image(msg["image"], width=300)
 
        if msg.get("link"):
            st.markdown(msg["link"], unsafe_allow_html=True)
 
# ==========================
# CHAT INPUT
# ==========================
 
query = st.chat_input("Ask about the product catalog...")
 
if query:
    # USER MESSAGE
    st.session_state.messages.append(
        {"role": "user", "content": query}
    )
 
    with st.chat_message("user"):
        st.markdown(query)
 
    # ==========================
    # RETRIEVE CONTEXT
    # ==========================
 
    results = retrieve(query)
 
    context_text = ""
    images = []
    links = []
 
    for doc, meta in results:
        page = meta.get("page")
 
        context_text += f"\n(Page {page}) {doc}\n"
 
        # Images
        image_path = meta.get("image_path")
        if image_path and image_path != "NO_IMAGE" and os.path.exists(image_path):
            images.append(image_path)
 
        # HTTP PDF link
        if page:
            pdf_link = f"{PDF_HTTP_BASE}#page={page}"
            links.append(
                f'<a href="{pdf_link}" target="_blank">🔗 Open PDF – Page {page}</a>'
            )
 
    # ==========================
    # GENERATE ANSWER
    # ==========================
 
    answer = generate_answer(query, context_text)
 
    with st.chat_message("assistant"):
        st.markdown(answer)
 
        for img in images:
            st.image(img, width=280)
 
        for link in links:
            st.markdown(link, unsafe_allow_html=True)
 
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "image": images[0] if images else None,
        "link": links[0] if links else None
    })
 