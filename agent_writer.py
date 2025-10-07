# agent_writer.py

import json
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from schemas import PlanningOutput, BlogInput, BlogPost, RelevanceOutput  # Reusamos RelevanceOutput para el QA

# Usamos el modelo rápido para la generación (ya tiene la estrategia definida)
GENERATION_MODEL = 'gemini-2.5-flash'


def run_qa_guardrail(generated_content: str) -> RelevanceOutput:
    """
    Guardrail de Salida: Veta el contenido generado para asegurar la seguridad
    y calidad antes de entregarlo.
    """
    parser = PydanticOutputParser(pydantic_object=RelevanceOutput)
    llm = ChatGoogleGenerativeAI(model=GENERATION_MODEL, temperature=0.1)

    # Prompt para verificar que el contenido es seguro y profesional
    guardrail_prompt = PromptTemplate(
        template=(
            "Eres un clasificador de QA para contenido de marketing. Evalúa el siguiente contenido de blog "
            "para determinar si es seguro, profesional, y si cumple con los estándares éticos (no tóxico, sin PII, no ofensivo). "
            "Si el contenido cumple, establece 'is_relevant' como True. Si viola algún estándar (ej: insultos, información falsa, lenguaje tóxico), establece 'is_relevant' como False. "
            "\n\n[CONTENIDO GENERADO]: {content}"
            "\n\n{format_instructions}"
        ),
        input_variables=["content"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    response = llm.invoke(guardrail_prompt.format(content=generated_content)).content
    return parser.parse(response)


def run_writer_agent(plan: PlanningOutput, user_input: BlogInput) -> Optional[BlogPost]:
    """
    Genera el contenido del blog a partir del plan estratégico y el contexto del usuario,
    y luego aplica el Guardrail de QA.
    """
    # 1. Inicializa el Parser y el Modelo
    parser = PydanticOutputParser(pydantic_object=BlogPost)
    llm = ChatGoogleGenerativeAI(
        model=GENERATION_MODEL,
        temperature=0.7,
    )

    # 2. Construye el Prompt de Escritura (Lógica Modificada)
    ROLE_INSTRUCTION = (
        "Eres un Agente Escritor, un copywriter de élite. Tu misión es escribir un blog persuasivo cuyo objetivo "
        "es vender el Target Product de software. Debes seguir la estrategia al pie de la letra y basarte "
        "EXCLUSIVAMENTE en el conocimiento proporcionado."
    )

    # AJUSTE: El target_product viene del user_input
    STRATEGY_SECTION = (
        "\n\n[PLAN ESTRATÉGICO]:"
        f"\n- PRODUCTO A VENDER: {user_input.target_product}"
        f"\n- TÉCNICA DE PERSUASIÓN: {plan.persuasion_technique}"
        f"\n- METODOLOGÍA: {plan.copywriting_methodology}"
    )

    # ----- CAMBIO FUNDAMENTAL -----
    # El conocimiento ya no es el RAG del planificador, sino el resumen y las fuentes del input.
    # Esto responde a tu pregunta sobre incluir las fuentes.
    summary_text = "\n".join([f"- {key.capitalize()}: {value}" for key, value in user_input.summary.items()])
    sources_text = "\n".join(
        [f"- Título: {s.title}, URL: {s.url}, Fiabilidad: {s.reliability_score}" for s in user_input.sources])

    KNOWLEDGE_SECTION = (
        "\n\n[CONOCIMIENTO BASE PARA ESCRIBIR EL ARTÍCULO]:"
        "\n**Resumen de la Investigación:**\n"
        f"{summary_text}"
        "\n\n**Fuentes de la Investigación (para contexto y atribución):**\n"
        f"{sources_text}"
    )

    TASK_INSTRUCTION = (
        "\n\nInstrucciones Finales:"
        "\n1. El blog debe tener al menos 600 palabras."
        "\n2. Basa todo tu contenido en el [CONOCIMIENTO BASE]. No inventes información."
        "\n3. Sigue la METODOLOGÍA (AIDA, PAS, etc.) para estructurar la introducción, secciones y conclusión."
        "\n4. El `call_to_action` final DEBE presentar el Target Product como la SOLUCIÓN DEFINITIVA."
        f"\n5. Tu respuesta debe ser estrictamente un JSON que se ajuste al esquema de salida. NO incluyas el campo 'sources' en el JSON que generes; será añadido después.\n{parser.get_format_instructions()}"
    )

    full_prompt = ROLE_INSTRUCTION + STRATEGY_SECTION + KNOWLEDGE_SECTION + TASK_INSTRUCTION

    raw_response = llm.invoke(full_prompt).content

    try:
        # --- INICIO DE LA CORRECCIÓN ---

        # 1. Limpiar la respuesta cruda de los fences de markdown
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()

        # 2. Cargar el JSON en un diccionario de Python (sin validar aún)
        blog_dict = json.loads(cleaned_response)

        # 3. Añadir manualmente los datos que faltan al diccionario
        blog_dict['sources'] = user_input.sources

        # 4. AHORA SÍ: Validar el diccionario COMPLETO para crear el objeto Pydantic
        blog_post = BlogPost.model_validate(blog_dict)

        # --- FIN DE LA CORRECCIÓN ---

    except Exception as e:
        print(f"\n❌ ERROR de parsing en la generación. El modelo no devolvió el JSON correcto. Detalle: {e}")
        # print(f"Respuesta cruda que causó el error:\n{raw_response}") # Descomenta para depurar
        return None

        # El resto de la función (el Guardrail de QA) sigue igual...
    print("\n--- Aplicando Guardrail de Validación de Salida (QA) ---")
    qa_check = run_qa_guardrail(blog_post.model_dump_json())

    if not qa_check.is_relevant:
        print(f"❌ GUARDRAIL QA ACTIVADO. Contenido vetado. Razón: {qa_check.reasoning}")
        return None

    print("✅ Guardrail QA superado. Contenido seguro y profesional.")
    return blog_post
