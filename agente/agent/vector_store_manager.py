import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_PATH = "faiss_index"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def build_vector_store(chunks, save=True):
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    if save:
        vector_store.save_local(INDEX_PATH)
        print(f"Índice FAISS guardado en '{INDEX_PATH}'")
    return vector_store

def load_vector_store():
    embeddings = get_embeddings()
    return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

def get_or_create_vector_store(chunks):
    if os.path.exists(INDEX_PATH):
        print("Cargando índice FAISS existente...")
        return load_vector_store()
    print("Creando índice FAISS nuevo...")
    return build_vector_store(chunks)