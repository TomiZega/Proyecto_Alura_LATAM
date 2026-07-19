import os
import json
import time
import warnings
from datetime import datetime, timezone

warnings.filterwarnings("ignore")

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

GROQ_MODEL = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")
TOP_K = 4
TEMPERATURE = 0.2

SYSTEM_PROMPT = """Sos el asistente virtual de BimBam Buy, una tienda online.

Tu función es responder consultas de clientes ESTRICTAMENTE basándote en los \
fragmentos de documentación oficial que se te proporcionan como contexto.

REGLAS OBLIGATORIAS:
1. Respondé ÚNICAMENTE con información presente en el contexto proporcionado.
2. Si la información solicitada NO está en el contexto, respondé exactamente: \
"No encontré esta información en los documentos disponibles. Te recomiendo \
contactar directamente a atención al cliente."
3. No inventes ni supongas información que no esté en el contexto.
4. Respondé siempre en español, de forma clara y directa.
5. Cuando sea relevante, indicá de qué documento sale la información.

CONTEXTO DOCUMENTADO:
{context}"""

LOG_PATH = "logs/ejecucion.jsonl"


class RAGChain:
    """Envoltura manual del pipeline RAG (retriever + prompt + LLM),
    sin depender de langchain.chains para evitar problemas de compatibilidad
    con LangChain 1.x."""

    def __init__(self, retriever, llm, prompt):
        self.retriever = retriever
        self.llm = llm
        self.prompt = prompt
        

    def invoke(self, inputs: dict) -> dict:
        query = inputs["input"]
        docs = self.retriever.invoke(query)
        context = "\n\n".join(doc.page_content for doc in docs)

        messages = self.prompt.format_messages(context=context, input=query)
        response = self.llm.invoke(messages)

        return {"answer": response.content, "context": docs}


def build_agent(vector_store, model_name: str = GROQ_MODEL, temperature: float = TEMPERATURE) -> RAGChain:
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )

    llm = ChatGroq(
        model=model_name,
        temperature=temperature,
        #api_key=os.environ["GROQ_API_KEY"],
        api_key=_get_secret("GROQ_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    return RAGChain(retriever, llm, prompt)


def _log_interaction(question, answer, sources, elapsed_seconds):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": question,
        "respuesta": answer,
        "fuentes": list(sources),
        "tiempo_respuesta_seg": round(elapsed_seconds, 2),
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def ask_agent(chain: RAGChain, question: str):
    start = time.time()
    result = chain.invoke({"input": question})
    elapsed = time.time() - start

    answer = result["answer"]
    sources = {doc.metadata.get("source", "desconocido") for doc in result["context"]}

    _log_interaction(question, answer, sources, elapsed)

    return answer, sources

def _get_secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)