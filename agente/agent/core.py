import os
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

PROMPT_TEMPLATE = """Sos un asistente virtual de BimBam Buy, una tienda online.
Respondé la pregunta del usuario basándote ÚNICAMENTE en el siguiente contexto extraído de los documentos oficiales de la empresa.
Si la respuesta no está en el contexto, decí claramente que no tenés esa información, no inventes nada.

Contexto:
{context}

Pregunta: {question}

Respuesta:"""

def build_agent(vector_store, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.2):
    llm = ChatGroq(
        model=model_name,
        temperature=temperature,
        groq_api_key=os.environ["GROQ_API_KEY"],
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
    return qa_chain

def ask_agent(qa_chain, question: str):
    result = qa_chain.invoke({"query": question})
    answer = result["result"]
    sources = {doc.metadata.get("source", "desconocido") for doc in result["source_documents"]}
    return answer, sources