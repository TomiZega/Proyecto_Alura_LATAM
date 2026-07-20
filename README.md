# 🛒 Asistente Virtual BimBam Buy

Agente de inteligencia artificial (RAG) que responde consultas de clientes sobre las políticas y procesos de BimBam Buy (tienda online ficticia), basándose exclusivamente en la documentación oficial de la empresa.

Proyecto desarrollado para el **Challenge Alura Agente** (Alura LATAM).

🌐 **Demo en vivo:** https://proyectoaluralatam-efw9fkmjhjtm2sjdywr4te.streamlit.app/

---

## 📋 Descripción general

El asistente utiliza una arquitectura RAG (*Retrieval-Augmented Generation*) para responder preguntas sobre garantías, envíos, reembolsos, métodos de pago y el programa de afiliados de BimBam Buy, citando siempre el documento y la sección de origen de cada respuesta.

Cuando la información solicitada no se encuentra en los documentos disponibles, el agente lo indica explícitamente en lugar de inventar una respuesta, priorizando la confiabilidad sobre la completitud.

---

## 🏗️ Arquitectura de la solución

```
Usuario → Interfaz Streamlit → Agente RAG (LangChain)
                                      │
                        ┌─────────────┴─────────────┐
                  Retriever (FAISS)           LLM (Groq · Llama 3.1)
                        │
     Documentos (PDF) → limpieza de índice → chunking → embeddings (HuggingFace)
```

**Flujo de una consulta:**
1. El usuario escribe una pregunta en la interfaz de chat.
2. La pregunta se convierte en un vector (embedding) con el mismo modelo usado para indexar los documentos.
3. Se recuperan los fragmentos (chunks) más relevantes semánticamente desde el índice FAISS.
4. Los fragmentos recuperados se insertan como contexto en un prompt junto con la pregunta.
5. El LLM (Groq) genera una respuesta basada únicamente en ese contexto.
6. La respuesta se muestra junto con los documentos fuente utilizados.
7. La interacción se registra en un log (`logs/ejecucion.jsonl`) con timestamp, pregunta, respuesta, fuentes y tiempo de respuesta.

**Pipeline de ingesta** (`ingest.py`, se ejecuta una vez, no en cada arranque):
- Carga de los PDFs desde `data/`.
- Limpieza del índice/tabla de contenidos de cada documento (ruido que competía con el contenido real en la búsqueda semántica).
- División en chunks de 700 caracteres con 200 de solapamiento.
- Generación de embeddings y persistencia del índice FAISS en `db/`.

---

## 🛠️ Tecnologías utilizadas

| Categoría | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Orquestación RAG | LangChain (componentes manuales / LCEL, por compatibilidad con LangChain 1.x) |
| LLM | Groq API — Llama 3.1 8B Instant |
| Embeddings | HuggingFace — `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` |
| Base de datos vectorial | FAISS (local) |
| Procesamiento de PDFs | pypdf (`PyPDFLoader`) |
| Interfaz | Streamlit |
| Despliegue | Streamlit Community Cloud |

---

## ⚙️ Instrucciones para ejecutar el proyecto

### Requisitos previos
- Python 3.11 o superior
- Cuenta gratuita en [Groq Console](https://console.groq.com) para obtener una API key

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/TomiZega/Proyecto_Alura_LATAM/tree/main
cd Proyecto_Alura_LATAM

# Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración

Crear un archivo `.env` en la raíz del proyecto:
```
GROQ_API_KEY=tu_api_key_aca
```

### Ejecución

```bash
# 1. Generar el índice vectorial (solo la primera vez, o si cambian los documentos)
cd agente
python ingest.py

# 2. Levantar la aplicación
streamlit run app.py
```

La aplicación queda disponible en `https://proyectoaluralatam-efw9fkmjhjtm2sjdywr4te.streamlit.app/`.

---

## 💬 Ejemplos de preguntas que el agente puede responder

- ¿Cuáles son los métodos de pago disponibles?
- ¿Cuál es el propósito del programa de afiliados?
- ¿Cuál es la política de reembolsos?
- ¿Cómo funciona la garantía de un producto?
- ¿Qué material no está permitido usar a los afiliados?
- ¿Cómo pido que me devuelvan la plata? *(paráfrasis de "reembolso", para probar búsqueda semántica)*
- ¿Tienen tienda física en Bogotá? *(pregunta fuera de alcance, para probar el fallback)*
- Teniendo en cuenta todos los documentos, ¿cuál es la relación entre ellos? *(pregunta que cruza múltiples fuentes)*

---

## 🤖 Ejemplos de respuestas generadas

**Pregunta:** ¿Cuáles son los métodos de pago?

> Según el documento "3. Métodos de pago disponibles", BimBam Buy puede aceptar los siguientes métodos de pago:
> - Tarjeta de crédito
> - Tarjeta de débito
> - Transferencia bancaria
> - Pago en efectivo en puntos habilitados
> - Billeteras digitales disponibles por país
> - Cuotas o financiamiento, cuando aplique
>
> La disponibilidad de estos métodos puede variar según país, categoría y monto.
>
> 📄 Fuentes: Preguntas Frecuentes sobre Métodos de Pago de BimBam Buy.pdf

---

**Pregunta:** ¿Tienen tienda física en Bogotá?

> No encontré esta información en los documentos disponibles. Te recomiendo contactar directamente a atención al cliente.
>
> 📄 Fuentes: Guía de Tiempos y Costos de Envío de BimBam Buy.pdf, Programa de Afiliados de BimBam Buy.pdf, Preguntas Frecuentes sobre Métodos de Pago de BimBam Buy.pdf, Política de reembolsos y devoluciones de BimBam Buy.pdf

*(Correctamente evita inventar una respuesta, cumpliendo la regla de no alucinar información fuera del contexto documentado.)*

---

**Pregunta:** Teniendo en cuenta todos los documentos, ¿cuál es la relación entre ellos?

> Basándome en los documentos proporcionados, puedo identificar algunas relaciones entre ellos:
>
> **Política de Reembolsos y Devoluciones:** se relaciona con la Guía de Tiempos y Costos de Envío (cancelaciones, reversos y devoluciones), el Manual de Garantía de Productos (cuando el reembolso depende de una falla cubierta) y las Preguntas Frecuentes sobre Métodos de Pago (reembolsos y conciliación financiera).
>
> **Guía de Tiempos y Costos de Envío:** se relaciona con la Política de Reembolsos, las Preguntas Frecuentes sobre Métodos de Pago y el Manual de Garantía.
>
> **Manual de Garantía de Productos:** se relaciona con la Política de Reembolsos, la Guía de Envíos y las Preguntas Frecuentes sobre Métodos de Pago.
>
> **Preguntas Frecuentes sobre Métodos de Pago:** se relaciona con la Política de Reembolsos, la Guía de Envíos y el Manual de Garantía.
>
> En resumen, estos documentos se relacionan entre sí en función de las políticas y procedimientos que se establecen para manejar diferentes situaciones, coordinando reembolsos, devoluciones, garantías y pagos de forma coherente.
>
> 📄 Fuentes: Preguntas Frecuentes sobre Métodos de Pago de BimBam Buy.pdf, Manual de Garantía de Productos de BimBam Buy.pdf, Programa de Afiliados de BimBam Buy.pdf, Política de reembolsos y devoluciones de BimBam Buy.pdf

*(Este ejemplo muestra la capacidad del agente para sintetizar información de múltiples documentos en una sola respuesta, identificando las referencias cruzadas explícitas entre las políticas de la empresa.)*

---

**Pregunta:** Necesito información sobre las garantías

> Claro, puedo proporcionarte información sobre las garantías según el contexto documentado.
>
> **Plazos de garantía**
> El plazo de garantía puede variar según el tipo de producto, categoría y país. El plazo aplicable será el informado en la ficha del producto o en la confirmación de compra. (Documento 5. Plazos de garantía)
>
> **Cobertura general**
> La garantía puede cubrir: falla de encendido, mal funcionamiento de componentes, defectos de ensamblaje, problemas de fabricación, inconsistencias técnicas no originadas por el cliente, y fallas intermitentes con evidencia suficiente. (Documento 6. Cobertura general)
>
> **Exclusiones**
> La garantía no cubre: daño por golpes o caídas, humedad o exposición a fuego, manipulación por terceros no autorizados, reparaciones externas, accesorios consumibles, instalación incorrecta o uso fuera de especificación. (Documento 7. Exclusiones)
>
> 📄 Fuentes: Manual de Garantía de Productos de BimBam Buy.pdf, Preguntas Frecuentes sobre Métodos de Pago de BimBam Buy.pdf

*(Ejemplo de respuesta extensa: el agente organiza automáticamente la información en secciones temáticas — plazos, cobertura, exclusiones — a partir de múltiples chunks recuperados del mismo documento.)*

---

## 🧠 Decisiones técnicas y alcance del proyecto

Durante el desarrollo se identificaron y corrigieron varios problemas de calidad de recuperación (retrieval), documentados aquí como parte del proceso de validación:

- **Modelo de embeddings multilingüe:** se reemplazó el modelo inicial (`all-MiniLM-L6-v2`, orientado a inglés) por `paraphrase-multilingual-mpnet-base-v2`, mejorando notablemente la precisión semántica en español.
- **Limpieza de índice/TOC:** los documentos fuente incluyen una tabla de contenidos al inicio que competía con el contenido real en la búsqueda vectorial. Se implementó un filtro en `ingest.py` que la descarta antes del chunking.
- **Ajuste de chunking:** se calibró `chunk_size=700` / `chunk_overlap=200` tras detectar que listas largas (ej. métodos de pago) quedaban cortadas con valores menores.
- **Migración de API de LangChain:** se optó por implementar el pipeline RAG con componentes manuales (retriever + prompt + LLM desacoplados) en lugar de `RetrievalQA` o `create_retrieval_chain`, por incompatibilidad de esas clases con LangChain 1.x.

**Fuera de alcance:** reranking de resultados, filtrado por metadatos, base de datos vectorial gestionada (Pinecone/Qdrant), integración con Slack/Teams, CI/CD y carga dinámica de documentos por el usuario final.

---

## ☁️ Evidencia del Deploy

**Aplicación desplegada:** https://proyectoaluralatam-efw9fkmjhjtm2sjdywr4te.streamlit.app/

**Nota sobre la nube:** el uso de Oracle Cloud Infrastructure (OCI) fue evaluado durante el desarrollo, pero se optó por Streamlit Community Cloud para el despliegue, dado que la consigna del challenge no exige una plataforma específica, solo que el proyecto esté disponible mediante una URL pública.

Capturas de la aplicación en funcionamiento: ver carpeta `Capturas_Aplicacion`

Registro de ejecución: `agente/logs/ejecucion.jsonl`

---

## 📁 Estructura del proyecto

```
Proyecto_Alura_LATAM/
├── data/                          # PDFs fuente
├── agente/
│   ├── agent/
│   │   ├── core.py                # Cadena RAG (retriever + prompt + LLM) + logging
│   │   └── vector_store_manager.py
│   ├── db/                        # Índice FAISS persistido
│   ├── logs/                      # Registro de ejecución (JSONL)
│   ├── app.py                     # Interfaz Streamlit
│   └── ingest.py                  # Pipeline de ingesta
├── requirements.txt
└── README.md
```

## 👤 Autor

Tomás Zegatti
Estudiante de Ingeniería en Sistemas de Información — UTN FRVM
Proyecto desarrollado para el Challenge Alura Agente (Alura LATAM)
🔗 https://github.com/TomiZega