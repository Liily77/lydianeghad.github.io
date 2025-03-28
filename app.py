# ---------------------------------- 📦 IMPORTS ---------------------------------- #
import streamlit as st
import tempfile
from chromadb import Client
from chromadb.config import Settings
import numpy as np
import re
import json
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rag_minilm import MiniLMProcessor
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ------------------------------------------------------ ⚙️ PAGE CONFIGURATION ----------------------------- #


st.set_page_config(page_title="SmartReader Chat", page_icon="💬", layout="centered")
st.markdown("<h1 style='text-align: center;'>💬 SmartReader Chat</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Chat with your PDF like a pro — powered by MiniLM & Ollama</h4>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------------------------- 🧠 SESSION STATE INIT ----------------------------- #

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "collection" not in st.session_state:
    st.session_state.collection = None
if "processor" not in st.session_state:
    st.session_state.processor = MiniLMProcessor()
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# ------------------------------------------------------- 📤 SIDEBAR CONTROLS ------------------------------ #


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

model_choice = st.sidebar.selectbox("🧠 Choose Ollama model", ["tinyllama", "phi", "mistral", "gemma:2b"], index=0)



# --------------------------------------------- 📎 PDF UPLOAD UI ---------------------------------- #


st.markdown("### 📤 Step 1: Upload your PDF file")
uploaded_file = st.file_uploader("Upload your scientific PDF", type=["pdf"], label_visibility="collapsed")



# ----------------------------------------------------------- ☁️ WORDCLOUD FUNCTION ----------------------------- #

def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    return fig


# ------------------------------------------------------------- 🧩 PROCESS & EMBED PDF ---------------------------- #


if uploaded_file and st.session_state.collection is None:
    with st.spinner("🔍 Processing document and creating vector DB..."):

        # Enregistre temporairement le fichier PDF uploadé

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        #  Charge le PDF et extrait les pages avec LangChain

        loader = PyPDFLoader(tmp_path)
        docs = loader.load()

        #  Coupe le texte en petits morceaux (chunks)

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_documents(docs)
        chunk_texts = [chunk.page_content for chunk in chunks]

        # Concatène tous les textes pour le WordCloud (visualisation)

        full_text = " ".join(chunk_texts)
        st.session_state.full_text = full_text

        # Embedding des textes avec MiniLM
        processor = st.session_state.processor
        embeddings = [processor.get_embeddings(text) for text in chunk_texts]

        # Chaque chunk de texte est transformé en vecteur numérique pour le rendre "compréhensible" par l'IA

        # Création de la base vectorielle avec ChromaDB

        client = Client(Settings(anonymized_telemetry=False))
        if "uploaded_doc" in [c.name for c in client.list_collections()]:
            client.delete_collection(name="uploaded_doc")
        collection = client.create_collection(name="uploaded_doc")

        #  Ajout de chaque chunk + son embedding dans la base

        progress_bar = st.progress(0, text="Indexing chunks into ChromaDB...")
        for i, (text, embedding) in enumerate(zip(chunk_texts, embeddings)):
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()  # Conversion en liste pour compatibilité
            if isinstance(embedding, list) and all(isinstance(i, (int, float)) for i in embedding):
                collection.add(ids=[str(i)], documents=[text], embeddings=[embedding])
            progress_bar.progress((i + 1) / len(chunk_texts))

        # Sauvegarde la collection dans la session pour les futures requêtes

        st.session_state.collection = collection
        progress_bar.empty()
        st.success("✅ Document uploaded and processed! You can now start chatting.")


# ------------------------------------------------------------- 🌥️ DISPLAY WORD CLOUD ----------------------------- #


if uploaded_file and "full_text" in st.session_state:
    st.markdown("### 🧩 Key Concepts Word Cloud")
    st.pyplot(generate_wordcloud(st.session_state.full_text))


# ----------------------------------------------------------------- 💬 CHAT INTERFACE -------------------------------- #



if st.session_state.collection:

    # Champ de saisie en bas de page pour la question utilisateur

    user_input = st.chat_input("💬 Ask something about the document...")

    # Nettoyage du contexte : réduit à 50 mots max

    def clean_and_truncate_text(text, max_words=50):
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split(" ")
        return " ".join(words[:max_words])

    # Fonction qui appelle le modèle Ollama via son API locale

    def ask_ollama(prompt, model):
        try:
            url = "http://localhost:11434/api/generate"
            headers = {"Content-Type": "application/json"}
            data = {
                "model": model,       # Le modèle sélectionné (mistral, phi, etc.)
                "prompt": prompt,     # Le prompt à envoyer
                "stream": True        # Réponse en flux
            }

            # Requête POST vers Ollama (local)

            response = requests.post(url, headers=headers, json=data, timeout=120, stream=True)

            # Si la requête réussit, on assemble la réponse petit à petit

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
            return f"Error calling Ollama API: {str(e)}"

    # Quand l'utilisateur envoie une question

    if user_input:

        # Sauvegarde la question dans l'historique du chat
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.is_generating = True

        with st.spinner("🤖 Generating answer from Ollama..."):
            processor = st.session_state.processor

            # Embedding de la question utilisateur

            query_embedding = processor.get_embeddings(user_input).tolist()

            # Recherche du chunk le plus pertinent dans la base Chroma

            results = st.session_state.collection.query(query_embeddings=[query_embedding], n_results=1)
            retrieved_chunks = results["documents"]

            # On réduit le contexte à 50 mots max

            context = clean_and_truncate_text(retrieved_chunks[0][0], 50) if retrieved_chunks else ""

            # Création du prompt final pour Ollama

            final_prompt = f"Context:\n{context}\n\nUser question: {user_input}\n\nAnswer clearly:"

            # Appel à Ollama pour générer la réponse

            with st.spinner("🤖 Ollama is thinking..."):
                ollama_response = ask_ollama(final_prompt, model_choice)

            # On ajoute la réponse au chat

            st.session_state.chat_history.append(("assistant", ollama_response))

        st.session_state.is_generating = False

    # Affichage de tout l'historique du chat

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)
else:
    st.info("📄 Please upload a PDF to start chatting with it.")


# -------------------------------------------------------------------- 🖋️ FOOTER ---------------------------------------- #

st.markdown("---")
st.markdown("<p style='text-align: center;'>Built with ❤️ by Millenials Team · SmartReader Chatbot with MiniLM & Ollama</p>", unsafe_allow_html=True)
