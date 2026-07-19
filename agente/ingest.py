"""
ingest.py — Pipeline de ingesta RAG | BimBam Buy Assistant
Procesa los PDFs de data/, genera embeddings y persiste el índice FAISS en db/.
Se corre UNA VEZ (o cada vez que cambian los documentos), no en cada arranque de la app.
"""

import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent
#DATA_DIR = ROOT_DIR / "data"
DATA_DIR = ROOT_DIR.parent / "data"
DB_DIR = ROOT_DIR / "db"

#EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2" (anda mal en español)
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def run_ingestion():
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        log.error(f"No se encontraron PDFs en {DATA_DIR}")
        return

    log.info(f"Documentos detectados ({len(pdf_files)}):")
    for f in pdf_files:
        log.info(f"  * {f.name}")

    documents = []
    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        documents.extend(docs)
        log.info(f"Cargado: {pdf_path.name} ({len(docs)} páginas)")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    log.info(f"Total de chunks generados: {len(chunks)}")

    log.info(f"Cargando modelo de embeddings: {EMBED_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    DB_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(DB_DIR))
    log.info(f"Índice FAISS guardado en: {DB_DIR}")


if __name__ == "__main__":
    run_ingestion()