# ---------------------------- IMPORTS ---------------------------- #

import os
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb import Client
from chromadb.config import Settings

# -------------------- STEP 1 = EMBEDDINGS ------------------------- #

class MiniLMProcessor:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def get_embeddings(self, text: str) -> np.ndarray:
        return np.array(self.model.encode(text, normalize_embeddings=True))

# -------------------- STEP 2 = DATABASE CREATION (CHROMADB) ---------------------------- #

def setup_chroma_db():
    persist_directory = "./chroma_db"
    client = Client(Settings(persist_directory=persist_directory, anonymized_telemetry=False))
    collection = client.get_or_create_collection(name="scientific_papers")
    return collection

# ----------------------- STEP 3 = CHUNK INDEXING ---------------------- #

def index_documents_in_chroma(collection, texts, embeddings):
    for i, (text, embedding) in enumerate(zip(texts, embeddings)):
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        if isinstance(embedding, list) and all(isinstance(i, (int, float)) for i in embedding):
            collection.add(ids=[str(i)], documents=[text], embeddings=[embedding])
        else:
            print(f"❌ Invalid embedding format for chunk {i + 1}. Skipping...")

# ------------------------ STEP 4 = INFORMATION RETRIEVAL ---------------------- #

def retrieve_relevant_chunks(collection, query, processor, k=3):
    query_embedding = processor.get_embeddings(query).squeeze(0).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    return results["documents"]
