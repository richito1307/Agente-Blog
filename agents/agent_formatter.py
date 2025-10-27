from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from shared.schemas import BlogPost, MarkdownOutput

STYLING_MODEL = 'gemini-2.5-flash'

def _create_base_markdown(blog_post: BlogPost) -> str:
    """
    (Función interna) Crea el string de Markdown base de forma determinista.
    Este es tu código original, ahora refactorizado en una función auxiliar.
    """
    markdown_parts = []

    markdown_parts.append(f"# {blog_post.main_title}\n")
    markdown_parts.append(f"{blog_post.introduction}\n")
    for section in blog_post.sections:
        markdown_parts.append(f"## {section.section_title}\n")
        markdown_parts.append(f"{section.content}\n")
    markdown_parts.append(f"{blog_post.call_to_action}\n")
    if blog_post.sources:
        markdown_parts.append("---\n")
        markdown_parts.append("### Fuentes\n")
        for source in blog_post.sources:
            markdown_parts.append(f"* [{source.title}]({source.original_url})")

    return "\n".join(markdown_parts)


def _enrich_markdown_with_llm(base_markdown: str) -> str:
    """
    (Función interna) Toma un Markdown base y usa un LLM para añadir estilos contextuales.
    """
    llm = ChatGoogleGenerativeAI(model=STYLING_MODEL, temperature=0.5)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Eres un editor de contenido web de élite. Tu misión es transformar un texto en Markdown en un documento dinámico y fácil de leer. "
         "REGLAS CRÍTICAS: "
         "1. Mantén intacto el contenido, el significado y la estructura original (títulos H1/H2/H3). "
         "2. Tu trabajo es aplicar formato de manera inteligente y distribuida. "
         "INSTRUCCIONES DE ESTILO: "
         "   - **Analiza cada sección o párrafo principal de forma independiente.** "
         "   - En **CADA** sección, pon en **negrita** al menos una o dos frases o conceptos cruciales para resaltar la idea principal de esa sección. "
         "   - Usa *cursivas* para dar énfasis a palabras sueltas, términos técnicos o anglicismos. "
         "   - Para romper la monotonía, identifica la oración más impactante o una cita clave en las secciones más largas y transfórmala en un **bloque de cita** (usando `>`). "
         "3. Devuelve ÚNICA Y EXCLUSIVAMENTE el texto Markdown mejorado, sin añadir comentarios ni explicaciones."),
        ("human", "{markdown_input}")
    ])

    chain = prompt | llm | StrOutputParser()
    enriched_markdown = chain.invoke({"markdown_input": base_markdown})

    return enriched_markdown


def run_formatter_agent(blog_post: BlogPost) -> MarkdownOutput:
    """
    Orquesta el proceso de formateo en dos pasos:
    1. Crea un Markdown estructuralmente perfecto.
    2. Usa un LLM para enriquecerlo con estilos contextuales.
    """
    print("\n--- PASO 3.1: Creando Markdown base estructural ---")
    base_markdown = _create_base_markdown(blog_post)

    print("--- PASO 3.2: Enriqueciendo con estilos contextuales (LLM) ---")
    try:
        enriched_markdown = _enrich_markdown_with_llm(base_markdown)
        final_markdown = enriched_markdown
        print("✅ Estilos contextuales aplicados con éxito.")
    except Exception as e:
        print(f"⚠️ ADVERTENCIA: Falló el enriquecimiento con LLM. Se devolverá el Markdown base. Detalle: {e}")
        # Si el LLM falla, nos aseguramos de no romper el pipeline y devolvemos el formato base.
        final_markdown = base_markdown

    return MarkdownOutput(markdown_content=final_markdown)