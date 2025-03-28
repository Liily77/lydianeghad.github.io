# ---------------------------- IMPORTS ---------------------------- #

import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss

# -------------------- STEP 1 = EMBEDDINGS ------------------------- #

class MiniLMProcessor:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def get_embeddings(self, text: str) -> np.ndarray:
        return np.array(self.model.encode(text, normalize_embeddings=True))

# -------------------- STEP 2 = DATABASE CREATION (FAISS) ---------------------------- #

def setup_faiss_index(dimension=384):
    index = faiss.IndexFlatL2(dimension)
    return index

# ----------------------- STEP 3 = CHUNK INDEXING ---------------------- #

def index_documents_in_faiss(index, texts, embeddings):
    index.add(np.array(embeddings))
    return index

# ------------------------ STEP 4 = INFORMATION RETRIEVAL ---------------------- #

def retrieve_relevant_chunks(index, query, texts, processor, k=3):
    query_embedding = processor.get_embeddings(query).reshape(1, -1)
    distances, indices = index.search(query_embedding, k)
    return [texts[i] for i in indices[0]]

