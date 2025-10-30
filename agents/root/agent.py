from dotenv import load_dotenv

from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from .tools.orchestrator_tools import planificar_blog, ejecutar_escritura, guardar_markdown_y_recursos
from .tools.relevance_guardrail import run_relevance_guardrail

load_dotenv()
GEMINI_MODEL = 'gemini-2.5-flash'

def root_manager(user_input_json: str):
    """
    Orquesta el flujo completo de planificación, escritura y formateo usando un AgentExecutor.
    """

    print("--- 1. EJECUTANDO GUARDRAIL DE RELEVANCIA (ENTRADA) ---")
    try:
        relevance_check = run_relevance_guardrail(user_input_json)
    except Exception as e:
        return f"❌ ERROR CRÍTICO: El guardrail falló en la clasificación. Detalle: {e}"

    if not relevance_check.is_relevant:
        print(f"❌ GUARDRAIL ACTIVADO. Razón: {relevance_check.reasoning}")
        return f"Lo siento, tu solicitud no cumple con nuestras políticas de contenido. Razón: {relevance_check.reasoning}"

    print(f"✅ Guardrail superado. Razón: {relevance_check.reasoning}")

    tools = [planificar_blog, ejecutar_escritura, guardar_markdown_y_recursos]
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.0)

    manager_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Eres el Agente Manager Orquestador, experto en pipelines de 3 etapas. Tu misión es guiar la solicitud de usuario a través de la secuencia EXACTA de herramientas. Tu primer y más importante objetivo es **INICIAR la Fase 1**."
         "Fases del Pipeline (Secuencia OBLIGATORIA): "
         "1. **FASE 1: PLANIFICACIÓN**: Llama a 'planificar_blog' usando el JSON de entrada del usuario como argumento. El agente NO puede saltarse esta fase."
         "2. **FASE 2: ESCRITURA**: Llama a 'ejecutar_escritura' usando la salida de la Fase 1 (el plan JSON) y el Input JSON original. Esta herramienta devolverá el BlogPost en formato JSON."
         "3. **FASE 3: GUARDADO/FINALIZACIÓN**: **OBLIGATORIAMENTE** debes llamar a 'guardar_markdown_y_recursos' utilizando el JSON devuelto por la Fase 2. Esta es la única herramienta que puede generar el resultado final para el usuario."
         "Tu trabajo termina solo cuando obtienes el resultado de la herramienta 'guardar_markdown_y_recursos'. NO termines antes de la Fase 3."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, manager_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    try:
        print("\n--- 2. ORQUESTANDO EL FLUJO (AgentExecutor) ---")

        manager_input = (
            "INICIA LA FASE 1 AHORA. El Input JSON es: "
            f"{user_input_json}. "
            "Una vez que las 3 Fases obligatorias estén completas, comunica el resultado FINAL y la ruta del archivo Markdown al usuario."
        )

        final_result = agent_executor.invoke({"input": manager_input})

        return f"Orquestación completa. El resultado final es: \n{final_result['output']}"
    except Exception as e:
        return f"❌ ERROR CRÍTICO durante la orquestación: {e}"

