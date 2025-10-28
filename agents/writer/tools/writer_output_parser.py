# tools/writer_output_parser.py
import json
from typing import Optional, List

from agents.writer.tools.qa_guardrail import run_qa_guardrail
from shared.schemas import BlogPost, Source

def parse_and_validate_blog_post(raw_response: str, original_sources: List[Source]) -> Optional[BlogPost]:
    """
    Limpia, parsea, inyecta las fuentes y valida el JSON de salida del blog post,
    y luego ejecuta el Guardrail de QA.

    Args:
        raw_response (str): La respuesta de texto cruda del LLM.
        original_sources (List[Source]): Las fuentes originales recuperadas.

    Returns:
        Optional[BlogPost]: El objeto Pydantic validado o None si falla o es vetado.
    """

    try:
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()

        blog_dict = json.loads(cleaned_response)
        blog_dict['sources'] = original_sources
        blog_post = BlogPost.model_validate(blog_dict)


    except Exception as e:
        print(f"\n❌ ERROR de parsing en la generación. El modelo no devolvió el JSON correcto. Detalle: {e}")
        return None

    print("\n--- Aplicando Guardrail de Validación de Salida (QA) ---")

    qa_check = run_qa_guardrail(blog_post.model_dump_json())

    if not qa_check.is_relevant:
        print(f"❌ GUARDRAIL QA ACTIVADO. Contenido vetado. Razón: {qa_check.reasoning}")
        return None

    print("✅ Guardrail QA superado. Contenido seguro y profesional.")
    return blog_post