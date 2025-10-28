import json
from typing import List

from shared.schemas import PlanningOutput


def parse_and_validate_plan(raw_response: str, original_rag_chunks: List[str]) -> PlanningOutput | None:
    """
    Limpia, parsea, inyecta el contexto RAG y valida el JSON de salida.

    Args:
        raw_response: La respuesta de texto cruda del LLM (posiblemente con fences).
        original_rag_chunks: La lista de chunks RAG recuperados originalmente.

    Returns:
        PlanningOutput | None: El objeto Pydantic validado o None si falla.
    """
    try:
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()

        plan_dict = json.loads(cleaned_response)
        plan_dict['rag_context'] = original_rag_chunks
        planning_result = PlanningOutput.model_validate(plan_dict)
        return planning_result

    except json.JSONDecodeError as jde:
        print(f"\n❌ ERROR de JSON al parsear la respuesta del modelo. Detalle: {jde}")
        return None
    except Exception as e:
        print(f"\n❌ ERROR al validar o en la lógica de parsing. Detalle: {e}")
        return None