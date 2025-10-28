from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from shared.schemas import BlogInput, PlanningOutput

from .tools.chroma_loader import load_chroma_db
from .tools.prompt_builder import create_planner_agent_prompt
from .tools.output_parser import parse_and_validate_plan

load_dotenv()
DEFAULT_MODEL = 'gemini-2.5-pro'

def run_planner_agent(user_input: BlogInput, model: str = DEFAULT_MODEL) -> PlanningOutput | None:
    """
    Orquesta la ejecución del Agente Planificador:
    1. Carga el Vector Store.
    2. Ejecuta el paso RAG para recuperar el contexto.
    3. Inicializa el LLM y el Prompt.
    4. Ejecuta el LLM.
    5. Parsea, valida y devuelve el plan.
    """

    vectorstore = load_chroma_db()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    rag_query = (
        f"Producto de software: '{user_input.target_product}', Audiencia: '{user_input.target_audience}'. "
        f"¿Qué Técnicas de Persuasión y Metodologías de Copywriting del manual son las más efectivas para generar conversión?"
    )

    print("\n--- PASO 2.1: Recuperación RAG ---")
    docs = retriever.invoke(rag_query)
    original_chunks = [doc.page_content for doc in docs]
    rag_context_for_llm = "\n---\n".join(original_chunks)
    print(f"✅ {len(original_chunks)} Chunks recuperados.")

    parser = PydanticOutputParser(pydantic_object=PlanningOutput)
    llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=0.3,
    )

    print("\n--- PASO 2.2: Ejecución del LLM ---")
    full_prompt = create_planner_agent_prompt(rag_context_for_llm, user_input, parser)

    try:
        raw_response = llm.invoke(full_prompt).content
    except Exception as e:
        print(f"❌ ERROR: Falló la invocación del LLM. Detalle: {e}")
        return None

    planning_result = parse_and_validate_plan(raw_response, original_chunks)

    if planning_result:
        print("✅ Planificación de Copywriting Generada y Validada.")
    else:
        print("❌ Falló la planificación o validación.")

    return planning_result