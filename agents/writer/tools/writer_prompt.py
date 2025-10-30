from langchain_core.output_parsers import PydanticOutputParser
from shared.schemas import PlanningOutput, BlogInput

def create_writer_agent_prompt(plan: PlanningOutput, user_input: BlogInput, parser: PydanticOutputParser) -> str:
    """Genera el prompt maestro para el Agente Escritor."""

    ROLE_INSTRUCTION = (
        "Eres un Agente Escritor, un copywriter de élite. Tu misión es escribir un blog persuasivo cuyo objetivo "
        "es vender el Target Product de software. Debes seguir la estrategia al pie de la letra y basarte "
        "EXCLUSIVAMENTE en el conocimiento proporcionado."
    )

    STRATEGY_SECTION = (
        "\n\n[PLAN ESTRATÉGICO]:"
        f"\n- PRODUCTO A VENDER: {user_input.target_product}"
        f"\n- TÉCNICA DE PERSUASIÓN: {plan.persuasion_technique}"
        f"\n- METODOLOGÍA: {plan.copywriting_methodology}"
    )

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
        "\n5. Genera de 5 a 8 palabras clave o frases cortas (tags) altamente relevantes para SEO, basadas en el tema y el producto."
        "\n5. Genera texto legible sin formato. Para los titulos, evita usar dos puntos `:`"
        f"\n6. Tu respuesta debe ser estrictamente un JSON que se ajuste al esquema de salida. NO incluyas el campo 'sources' en el JSON que generes; será añadido después.\n{parser.get_format_instructions()}"
    )

    full_prompt = ROLE_INSTRUCTION + STRATEGY_SECTION + KNOWLEDGE_SECTION + TASK_INSTRUCTION
    return full_prompt