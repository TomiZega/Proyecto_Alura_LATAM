"""
BimBam Buy Assistant — app.py
Interfaz Streamlit para el agente RAG.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import re

from agent.vector_store_manager import load_vector_store
from agent.core import build_agent, ask_agent

load_dotenv()  # no-op en Streamlit Cloud, activo en desarrollo local

st.set_page_config(page_title="Asistente BimBam Buy", page_icon="🛒")

# ── Carga del backend RAG (una sola vez por sesión del servidor) ──
@st.cache_resource(show_spinner="Cargando base de conocimiento...")
def get_agent():
    vector_store = load_vector_store()
    chain = build_agent(vector_store)
    return chain

try:
    rag_chain = get_agent()
    agent_ok = True
except Exception as e:
    rag_chain = None
    agent_ok = False
    st.error(f"No se pudo cargar el agente: {e}")

st.title("🛒 Asistente Virtual BimBam Buy")
st.caption("🤖 Estás hablando con un agente de IA, no con una persona. Preguntame sobre garantías, envíos, reembolsos, métodos de pago o el programa de afiliados.")

# ── Historial de conversación ──
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption(f"📄 Fuentes: {msg['sources']}")

# ── Input del usuario ──
if pregunta := st.chat_input("Escribí tu pregunta..."):
    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        if not agent_ok:
            respuesta = "⚠️ El agente no está disponible en este momento."
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        else:
            with st.spinner("Consultando documentos..."):
                respuesta, fuentes = ask_agent(rag_chain, pregunta)
                fuentes_str = ", ".join(re.split(r'[\\/]', f)[-1] for f in fuentes)
                st.markdown(respuesta)
                if fuentes_str:
                    st.caption(f"📄 Fuentes: {fuentes_str}")
                # Feedback simple
                col1, col2 = st.columns([1, 10])
                with col1:
                    st.button("👍", key=f"up_{len(st.session_state.messages)}")
                    st.button("👎", key=f"down_{len(st.session_state.messages)}")

            st.session_state.messages.append({
                "role": "assistant",
                "content": respuesta,
                "sources": fuentes_str,
            })