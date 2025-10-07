# agent_planner.py (CORREGIDO)

import os
from dotenv import load_dotenv
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
import json

from schemas import BlogInput, PlanningOutput

load_dotenv()

# Rutas y Modelos
PERSIST_DIRECTORY = './chroma_db_copywriting'
DEFAULT_MODEL = 'gemini-2.5-pro'


# --- Funciones de Utilidad ---

def load_chroma_db():
    """Carga la base de vectores persistente."""
    embedding_model = GoogleGenerativeAIEmbeddings(model="text-embedding-004")
    # Nota: LangChain muestra una advertencia sobre Chroma, pero es funcional.
    vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embedding_model)
    return vectorstore


def create_planner_agent_prompt(rag_context: str, user_input: BlogInput, parser: PydanticOutputParser):
    """Genera el prompt maestro para el Agente Planificador."""

    ROLE_INSTRUCTION = (
        "Eres un Agente Planificador de Copywriting experto. Tu misión es definir la estrategia "
        "de un blog cuyo objetivo es vender el Target Product de software. Debes basar tu análisis "
        "exclusivamente en el 'Manual de Copywriting' (RAG Context)."
    )

    SALES_CONTEXT = (
        f"\n[OBJETIVO DE VENTA]: El blog debe vender el producto: '{user_input.target_product}'."
        f"\n[TEMA PRINCIPAL]: '{user_input.query}'."
        f"\n[AUDIENCIA OBJETIVO]: '{user_input.target_audience}'."
    )

    RAG_SECTION = f"\n[MANUAL DE COPYWRITING - CONTEXTO RAG RECUPERADO]:\n{rag_context}"

    TASK_INSTRUCTION = (
        "\n\nInstrucciones Clave:"
        "\n1. Analiza el Objetivo de Venta y el RAG Context para seleccionar la mejor 'persuasion_technique' y 'copywriting_methodology'."
        "\n2. Genera una 'rationale' clara."
        "\n3. **CRUCIAL**: En el campo 'rag_context', solo coloca un placeholder vacío (ej. []) en el JSON. La lista final será inyectada después."
        f"\n4. Tu respuesta debe ser estrictamente un JSON que se ajuste al siguiente esquema de salida:\n{parser.get_format_instructions()}"
    )

    full_prompt = ROLE_INSTRUCTION + SALES_CONTEXT + RAG_SECTION + TASK_INSTRUCTION
    return full_prompt


# --- Función Principal del Agente ---

def run_planner_agent(user_input: BlogInput, model: str = DEFAULT_MODEL) -> PlanningOutput | None:
    """Ejecuta el Agente Planificador."""

    vectorstore = load_chroma_db()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 1. Paso RAG
    rag_query = (
        f"Producto de software: '{user_input.target_product}', Audiencia: '{user_input.target_audience}'. "
        f"¿Qué Técnicas de Persuasión y Metodologías de Copywriting del manual son las más efectivas para generar conversión?"
    )

    docs = retriever.invoke(rag_query)
    original_chunks = [doc.page_content for doc in docs]
    rag_context_for_llm = "\n---\n".join(original_chunks)

    # 2. Inicializa el Parser y el Modelo
    parser = PydanticOutputParser(pydantic_object=PlanningOutput)
    llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=0.3,
    )

    # 3. Construye y Ejecuta el Prompt
    full_prompt = create_planner_agent_prompt(rag_context_for_llm, user_input, parser)
    raw_response = llm.invoke(full_prompt).content

    # 4. Parsear y devolver el Plan (Lógica Corregida para JSON)
    try:
        # 1. CORRECCIÓN: Limpiar la respuesta cruda de los fences de markdown
        # Elimina ```json, ```, y cualquier whitespace adicional
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()

        # 2. Usamos json.loads() para parsear la respuesta limpia
        plan_dict = json.loads(cleaned_response)

        # GUARDRAIL INTERNO: Aseguramos la fidelidad de los datos RAG
        plan_dict['rag_context'] = original_chunks

        # 3. Validamos el diccionario modificado
        planning_result = PlanningOutput.model_validate(plan_dict)
        print("\n✅ Planificación de Copywriting Generada con Éxito.")
        return planning_result
    except Exception as e:
        # Aquí puedes decidir si reintentar o simplemente loggear
        print(f"\n❌ ERROR al parsear o validar la respuesta del modelo. Detalle: {e}")
        # print(f"Respuesta cruda que causó el error (revisa si es JSON válido):\n{raw_response}")
        return None


if __name__ == "__main__":
    # --- PRUEBA DEL AGENTE PLANIFICADOR ---

    test_input = BlogInput(
        topic="La deuda técnica y cómo está matando tu crecimiento",
        target_product="Consultoría de Refactorización de Código",
        target_audience="CTOs y Gerentes de Ingeniería",
        desired_tone="Urgente y Autoritaria"
    )

    plan = run_planner_agent(test_input)

    if plan:
        print("\n✅ PASO 2 COMPLETADO: Planificación Generada.")
        print("=======================================================")
        print(f"Técnica Persuasiva: {plan.persuasion_technique}")
        print(f"Metodología de Copy: {plan.copywriting_methodology}")
        print(f"Racional: {plan.rationale}")
        print("\n--- CONTEXTO RAG RECUPERADO ---")
        for i, chunk in enumerate(plan.rag_context):
            print(f"Chunk {i + 1} (Inicio): {chunk[:100]}...")