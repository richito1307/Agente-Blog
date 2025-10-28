from .tools.markdown_builder import create_base_markdown
from .tools.markdown_enricher import enrich_markdown_with_llm
from shared.schemas import BlogPost, MarkdownOutput

def run_formatter_agent(blog_post: BlogPost) -> MarkdownOutput:
    """
    Orquesta el proceso de formateo en dos pasos:
    1. Crea un Markdown estructuralmente perfecto usando `create_base_markdown`.
    2. Usa un LLM (a través de `enrich_markdown_with_llm`) para enriquecerlo con estilos contextuales.
    """
    print("\n--- PASO 3.1: Creando Markdown base estructural ---")
    base_markdown = create_base_markdown(blog_post)

    print("--- PASO 3.2: Enriqueciendo con estilos contextuales (LLM) ---")
    try:
        enriched_markdown = enrich_markdown_with_llm(base_markdown)
        final_markdown = enriched_markdown
        print("✅ Estilos contextuales aplicados con éxito.")
    except Exception as e:
        print(f"⚠️ ADVERTENCIA: Falló el enriquecimiento con LLM. Se devolverá el Markdown base. Detalle: {e}")
        final_markdown = base_markdown

    return MarkdownOutput(markdown_content=final_markdown)
