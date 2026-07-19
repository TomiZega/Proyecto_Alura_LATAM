from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DB_DIR = Path(__file__).resolve().parents[1] / "db"


def load_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    if not DB_DIR.exists():
        raise FileNotFoundError(
            f"No se encontró el índice FAISS en {DB_DIR}. Corré 'python ingest.py' primero."
        )
    return FAISS.load_local(str(DB_DIR), embeddings, allow_dangerous_deserialization=True)