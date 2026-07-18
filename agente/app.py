import os
from dotenv import load_dotenv
import gradio as gr
from agent import load_and_split_documents, get_or_create_vector_store, build_agent, ask_agent

load_dotenv()

print("Inicializando agente...")
chunks = load_and_split_documents("data")
vector_store = get_or_create_vector_store(chunks)
qa_chain = build_agent(vector_store)
print("Agente listo.")

def responder(pregunta, historial):
    respuesta, fuentes = ask_agent(qa_chain, pregunta)
    fuentes_str = ", ".join(os.path.basename(f) for f in fuentes)
    return f"{respuesta}\n\n📄 *Fuentes: {fuentes_str}*"

demo = gr.ChatInterface(
    fn=responder,
    title="Asistente Virtual BimBam Buy",
    description="Preguntame sobre garantías, envíos, reembolsos, métodos de pago o el programa de afiliados.",
    examples=[
        "¿Cuánto tarda en llegar mi pedido?",
        "¿Cómo funciona la política de reembolsos?",
        "¿Qué métodos de pago aceptan?",
    ],
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)