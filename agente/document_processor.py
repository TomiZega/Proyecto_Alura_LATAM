import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_split_documents(data_dir: str = "data", chunk_size: int = 1000, chunk_overlap: int = 150):
    """Carga todos los PDFs de data_dir y los divide en chunks."""
    documents = []

    for filename in os.listdir(data_dir):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(data_dir, filename)
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            documents.extend(docs)
            print(f"Cargado: {filename} ({len(docs)} páginas)")

    if not documents:
        raise ValueError(f"No se encontraron PDFs en '{data_dir}'")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"Total de chunks generados: {len(chunks)}")
    return chunks