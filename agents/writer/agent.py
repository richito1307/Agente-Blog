from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from shared.schemas import PlanningOutput, BlogInput, BlogPost

from .tools.writer_prompt import create_writer_agent_prompt
from .tools.writer_output_parser import parse_and_validate_blog_post

GENERATION_MODEL = 'gemini-2.5-flash'

def run_writer_agent(plan: PlanningOutput, user_input: BlogInput) -> Optional[BlogPost]:
    """
    Orquesta la generación del contenido del blog a partir del plan estratégico y el contexto del usuario.

    1. Inicializa el LLM y el Parser.
    2. Construye el Prompt maestro.
    3. Ejecuta el LLM.
    4. Parsea, inyecta las fuentes y ejecuta el Guardrail de QA.
    """

    parser = PydanticOutputParser(pydantic_object=BlogPost)
    llm = ChatGoogleGenerativeAI(
        model=GENERATION_MODEL,
        temperature=0.7,
    )

    full_prompt = create_writer_agent_prompt(plan, user_input, parser)
    print("\n--- PASO 3.1: Ejecutando el Agente Escritor (LLM) ---")

    try:
        raw_response = llm.invoke(full_prompt).content
    except Exception as e:
        print(f"❌ ERROR: Falló la invocación del LLM. Detalle: {e}")
        return None

    blog_post = parse_and_validate_blog_post(raw_response, user_input.sources)
    return blog_post
