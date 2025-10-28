from dotenv import load_dotenv

from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from .tools.orchestrator_tools import planificar_blog, ejecutar_escritura, guardar_markdown_y_recursos
from .tools.relevance_guardrail import run_relevance_guardrail

load_dotenv()
GEMINI_MODEL = 'gemini-2.5-flash' # Modelo para orquestación

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
         "Eres el Agente Manager Orquestador. Tu misión es guiar un input de usuario a través de un pipeline de TRES FASES: "
         "1. **Planificar**: Llama a 'planificar_blog' con el input del usuario. "
         "2. **Escribir**: Llama a 'ejecutar_escritura' con el resultado del plan y el input original. "
         "3. **Formatear y crear archivo**: Llama a 'guardar_markdown_y_recursos' con la salida de la fase de escritura. "
         "El resultado final que debes devolver al usuario es el archivo en formato Markdown."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, manager_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    try:
        print("\n--- 2. ORQUESTANDO EL FLUJO (AgentExecutor) ---")
        final_result = agent_executor.invoke({
            "input": f"Aquí está la solicitud del usuario. Por favor, procesala a través del pipeline completo. Input JSON: {user_input_json}"
        })

        return f"Orquestación completa. El resultado final es: \n{final_result['output']}"
    except Exception as e:
        return f"❌ ERROR CRÍTICO durante la orquestación: {e}"

