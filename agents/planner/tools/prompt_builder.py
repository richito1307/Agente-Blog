from langchain_core.output_parsers import PydanticOutputParser
from shared.schemas import BlogInput

def create_planner_agent_prompt(rag_context: str, user_input: BlogInput, parser: PydanticOutputParser) -> str:
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