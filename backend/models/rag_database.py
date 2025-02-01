import faiss
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer

# Load sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Define FAISS index path
INDEX_PATH = "database/vector_store.faiss"
DOC_MAP_PATH = "database/doc_map.pkl"

# Initialize FAISS index
embedding_dim = 384  # Dimension of embeddings for "all-MiniLM-L6-v2"
index = faiss.IndexFlatL2(embedding_dim)
doc_map = {}

# Load existing FAISS index and doc_map if available
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(DOC_MAP_PATH, "rb") as f:
        doc_map = pickle.load(f)

def add_document(doc_id, text):
    """Encodes and adds a document to the FAISS index."""
    global doc_map
    vector = model.encode([text], convert_to_numpy=True)
    index.add(vector)
    doc_map[len(doc_map)] = {"id": doc_id, "text": text}

    # Save index and mapping
    faiss.write_index(index, INDEX_PATH)
    with open(DOC_MAP_PATH, "wb") as f:
        pickle.dump(doc_map, f)

def search(query, top_k=2):
    """Search for the most relevant documents."""
    if len(doc_map) == 0:
        return ["No documents found"]

    query_vector = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_vector, top_k)

    results = [doc_map[idx]["text"] for idx in indices[0] if idx in doc_map]
    return results
