import json
from langchain.tools import tool
from agents.formatter.agent import run_formatter_agent
from agents.formatter.tools.file_saver import save_content_and_resources
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
        print("✅ [Manager] -> Escritura completada con éxito. Devolviendo JSON para guardado.")
        return blog_post.model_dump_json(indent=2)
    else:
        return "ERROR_WRITING: Falló la generación del blog o no superó el Guardrail de Calidad (QA)."

@tool
def guardar_markdown_y_recursos(blog_post_json: str) -> str:
    """
    Toma el JSON del BlogPost, llama al Formateador para obtener el Markdown,
    y guarda el resultado en una carpeta junto con archivos de imagen simulados.
    """
    print("\n[Manager] -> Invocando Formateador y Guardado de Recursos...")
    try:
        decoder = json.JSONDecoder()
        blog_dict, _ = decoder.raw_decode(blog_post_json.strip())

        blog_post = BlogPost.model_validate(blog_dict)
        markdown_output = run_formatter_agent(blog_post)
        output_path = save_content_and_resources(blog_post.main_title, markdown_output.markdown_content)

        return f"ÉXITO: El pipeline finalizó el guardado y el Markdown fue creado en la ruta: {output_path}. Ahora, por favor, comunica al usuario el resultado final y dónde se encuentra su archivo."

    except Exception as e:
        # Imprime el inicio del JSON para depurar si falla
        print(f"Respuesta cruda que causó el error (Extracto):\n{blog_post_json[:500]}...")
        return f"ERROR_FINAL_SAVE: No se pudo guardar el blog y sus recursos. Detalle: {e}"