import streamlit as st
from answer_gen import answer_question
from langchain_core.messages import HumanMessage, AIMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="📘 CMS Catalog Assistant",
    layout="wide"
)

st.title("📘 CMS Product Catalog Assistant")
st.caption("Ask questions from Philips / Legrand product catalogs")

# ---------------- SESSION STATE ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# ---------------- USER INPUT ----------------
user_query = st.chat_input("Ask about products, prices, specs...")

if user_query:
    # Show user message
    st.chat_message("user").markdown(user_query)
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_query
    })

    with st.spinner("🔍 Searching catalog..."):
        answer, docs = answer_question(user_query)

    # Show assistant answer
    st.chat_message("assistant").markdown(answer)
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer
    })

    # ---------------- SOURCES ----------------
    if docs:
        with st.expander("📚 View Sources"):
            for i, d in enumerate(docs, start=1):
                st.markdown(f"### 🔹 Source {i}")
                st.markdown(f"**Product:** {d.get('product_name', 'N/A')}")
                st.markdown(f"**File:** `{d.get('source_file')}`")
                st.markdown(f"**Page:** {d.get('page_number')}")
                st.markdown(f"**Relevance Score:** `{round(d.get('score', 0), 4)}`")

                if d.get("image_path"):
                    st.image(d["image_path"], width=250)

                st.markdown("---")
