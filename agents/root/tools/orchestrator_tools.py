import json
from langchain.tools import tool
from agents.formatter.agent import run_formatter_agent
from shared.schemas import BlogInput, PlanningOutput, BlogPost
from agents.planner.agent import run_planner_agent
from agents.writer.agent import run_writer_agent

GEMINI_REASONING_MODEL = 'gemini-2.5-pro'

@tool
def planificar_blog(user_input_json: str) -> str:
    """
    Analiza el tema y la audiencia del usuario para generar un Plan de Copywriting estructurado (PlanningOutput).
    Este plan incluye la técnica de persuasión, la metodología de copywriting y el contexto RAG.
    """
    print("\n[Manager] -> Invocando Agente Planificador...")
    try:
        user_input = BlogInput.model_validate_json(user_input_json)
        plan_output = run_planner_agent(user_input, model=GEMINI_REASONING_MODEL)

        if plan_output:
            print("✅ [Manager] -> Planificación completada con éxito.")
            return plan_output.model_dump_json()
        else:
            return "ERROR: Falló la planificación del blog. Revise los logs del Agente Planificador."
    except Exception as e:
        return f"ERROR: El input JSON es inválido o faltan campos: {e}"


@tool
def ejecutar_escritura(plan_output_json: str, user_input_json: str) -> str:
    """
    Toma el PlanningOutput (el plan estratégico) y el BlogInput original para generar el BlogPost final.
    Aplica las técnicas, la estructura persuasiva y el Guardrail de QA.
    """
    print("\n[Manager] -> Invocando Agente Escritor...")
    try:
        cleaned_plan_json = plan_output_json.replace("\\'", "'")
        plan = PlanningOutput.model_validate_json(cleaned_plan_json)
        user_input = BlogInput.model_validate_json(user_input_json)
    except Exception as e:
        return f"ERROR: Falló la deserialización del Plan o Input: {e}"

    blog_post = run_writer_agent(plan, user_input)

    if blog_post:
        print("✅ [Manager] -> Escritura completada con éxito.")
        # Usamos un prefijo para que el formateador sepa que debe limpiarlo (guardarraíl de comunicación)
        return f"SUCCESS_BLOG_POST: {blog_post.model_dump_json(indent=2)}"
    else:
        return "ERROR_WRITING: Falló la generación del blog o no superó el Guardrail de Calidad (QA)."


@tool
def formatear_a_markdown(blog_post_json: str) -> str:
    """
    Toma el JSON de un BlogPost y lo convierte a un formato de texto Markdown bien estructurado.
    Este es el paso final para formatear la salida para el usuario.
    """
    print("\n[Manager] -> Invocando Formateador a Markdown...")
    try:
        cleaned_json = blog_post_json
        if cleaned_json.startswith("SUCCESS_BLOG_POST: "):
            cleaned_json = cleaned_json.replace("SUCCESS_BLOG_POST: ", "", 1)

        decoder = json.JSONDecoder()
        blog_dict, _ = decoder.raw_decode(cleaned_json.strip())

        blog_post = BlogPost.model_validate(blog_dict)

        markdown_output = run_formatter_agent(blog_post)

        print("✅ [Manager] -> Conversión a Markdown completada.")
        return markdown_output.markdown_content

    except Exception as e:
        print(f"Respuesta cruda que causó el error (Extracto):\n{blog_post_json[:500]}...")
        return f"ERROR_MARKDOWN: No se pudo convertir el blog a Markdown. Detalle: {e}"