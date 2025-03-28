# ---------------------------------- 📦 IMPORTS ---------------------- #

import streamlit as st
import tempfile
import numpy as np
import re
import json
import requests
import faiss  # 🔁 remplacement de chromadb par FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rag_minilm import MiniLMProcessor
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------------------------------- ⚙️ CONFIGURATION ---------------------- #

st.set_page_config(page_title="SmartReader Chat", page_icon="💬", layout="centered")

st.markdown("<h1 style='text-align: center;'>💬 SmartReader Chat</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Chat with your PDF like a pro — powered by MiniLM & Ollama</h4>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------- 🧠 SESSION STATE INIT ---------------------- #

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None
if "documents" not in st.session_state:
    st.session_state.documents = []
if "processor" not in st.session_state:
    st.session_state.processor = MiniLMProcessor()
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# ---------------------------------- 💾 EXPORT CHAT ---------------------- #

if st.sidebar.button("💾 Export Chat as .txt"):
    if st.session_state.chat_history:
        with open("chat_history.txt", "w", encoding="utf-8") as f:
            for role, message in st.session_state.chat_history:
                f.write(f"[{role.upper()}]\n{message}\n\n")
        with open("chat_history.txt", "r", encoding="utf-8") as file:
            st.sidebar.download_button(
                label="⬇️ Download chat_history.txt",
                data=file.read(),
                file_name="chat_history.txt",
                mime="text/plain"
            )
    else:
        st.sidebar.warning("No chat history to export.")

if st.sidebar.button("🗑️ Reset Chat"):
    st.session_state.chat_history = []

# ---------------------------------- 🤖 MODEL CHOICE ---------------------- #

model_choice = st.sidebar.selectbox("🧠 Choose Ollama model", ["tinyllama", "phi", "mistral", "gemma:2b"], index=0)

# ---------------------------------- 📤 PDF UPLOAD ---------------------- #

st.markdown("### 📤 Step 1: Upload your PDF file")
uploaded_file = st.file_uploader("Upload your scientific PDF", type=["pdf"], label_visibility="collapsed")

# ---------------------------------- ☁️ WORD CLOUD ---------------------- #

def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    return fig

# ---------------------------------- 🔍 PROCESS PDF + FAISS DB ---------------------- #

if uploaded_file and st.session_state.faiss_index is None:
    with st.spinner("🔍 Processing document and indexing chunks..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_documents(docs)
        chunk_texts = [chunk.page_content for chunk in chunks]

        full_text = " ".join(chunk_texts)
        st.session_state.full_text = full_text

        processor = st.session_state.processor
        embeddings = [processor.get_embeddings(text).astype('float32') for text in chunk_texts]

        index = faiss.IndexFlatL2(embeddings[0].shape[0])
        index.add(np.array(embeddings))

        st.session_state.faiss_index = index
        st.session_state.documents = chunk_texts

        st.success("✅ Document uploaded and processed! You can now start chatting.")

if uploaded_file and "full_text" in st.session_state:
    st.markdown("### 🧩 Key Concepts Word Cloud")
    st.pyplot(generate_wordcloud(st.session_state.full_text))

# ---------------------------------- 💬 CHAT INTERFACE ---------------------- #

if st.session_state.faiss_index:
    user_input = st.chat_input("💬 Ask something about the document...")

    def clean_and_truncate_text(text, max_words=50):
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split(" ")
        return " ".join(words[:max_words])

    def ask_ollama(prompt, model):
        try:
            url = "http://localhost:11434/api/generate"
            headers = {"Content-Type": "application/json"}
            data = {
                "model": model,
                "prompt": prompt,
                "stream": True
            }
            response = requests.post(url, headers=headers, json=data, timeout=120, stream=True)

            if response.status_code == 200:
                partial = ""
                for line in response.iter_lines():
                    if line:
                        line_data = line.decode("utf-8")
                        if line_data.startswith("data: "):
                            line_data = line_data[6:]
                        try:
                            chunk = json.loads(line_data)
                            partial += chunk.get("response", "")
                        except:
                            continue
                return partial.strip() if partial else "⚠️ Empty response from Ollama."
            else:
                return f"Ollama API Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f" Error calling Ollama API: {str(e)}"

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.is_generating = True
        with st.spinner("🤖 Generating answer from Ollama..."):
            processor = st.session_state.processor
            query_embedding = processor.get_embeddings(user_input).astype('float32')
            D, I = st.session_state.faiss_index.search(np.array([query_embedding]), k=1)
            top_result = st.session_state.documents[I[0][0]] if I[0][0] < len(st.session_state.documents) else ""

            context = clean_and_truncate_text(top_result, 50)
            final_prompt = f"Context:\n{context}\n\nUser question: {user_input}\n\nAnswer clearly:"

            with st.spinner("🤖 Ollama is thinking..."):
                ollama_response = ask_ollama(final_prompt, model_choice)
            st.session_state.chat_history.append(("assistant", ollama_response))
        st.session_state.is_generating = False

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)
else:
    st.info("📄 Please upload a PDF to start chatting with it.")

# ---------------------------------- 🖤 FOOTER ---------------------- #

st.markdown("---")
st.markdown("<p style='text-align: center;'>Built with ❤️ by Millenials Team · SmartReader Chatbot with MiniLM, FAISS & Ollama</p>", unsafe_allow_html=True)

