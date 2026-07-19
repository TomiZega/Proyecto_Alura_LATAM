# debug_retrieval.py
from agent.vector_store_manager import load_vector_store

vs = load_vector_store()

preguntas = [
    #"cuales son los metodos de pago?",
    #"que es el programa de afiliados?",
    #"cual es la politica de reembolsos?",
    "cuál es el propósito del programa de afiliados de la empresa?",
    "quiero saber sobre el programa de afiliados",
]

for q in preguntas:
    print(f"\n{'='*60}\nPregunta: {q}\n{'='*60}")
    resultados = vs.similarity_search_with_score(q, k=4)
    for i, (doc, score) in enumerate(resultados):
        fuente = doc.metadata.get("source", "?")
        print(f"\n--- Chunk {i+1} (score: {score:.4f}) — {fuente} ---")
        print(doc.page_content[:300])