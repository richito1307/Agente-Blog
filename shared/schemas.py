from pydantic import BaseModel, Field
from typing import List, Annotated
from datetime import date

class Source(BaseModel):
    """Define la estructura de una fuente/URL utilizada en el blog."""
    title: str = Field(description="Título del artículo fuente")
    url: str = Field(description="URL de la fuente")
    resolved_url: str = Field(description="URL original sin modificaciones")
    domain: str = Field(description="Dominio de la fuente")
    reliability_score: float = Field(description="Puntuación de confiabilidad de 0.0 a 1.0")

class BlogInput(BaseModel):
    """Define la información que el usuario provee al sistema."""
    query: str = Field(description="La consulta o tema específico del blog")
    date: Annotated[date, Field(description="Fecha para la que se escribe el blog (formato YYYY-MM-DD)")]
    status: str = Field(description="Estado de verificación: 'verified', 'unverified', 'pending'")
    summary: dict = Field(description="Resumen estructurado con headline, facts, context, uncertainties, implications")
    target_product: str = Field(description="El producto de software que el blog debe promocionar.", default="Plataforma AML, alertas en transacciones u automatizacion de procesos")
    target_audience: str = Field(description="La audiencia objetivo para el blog.", default="Empresas que quieran sistematizarse")
    sources: List[Source] = Field(description="Lista de fuentes y URLs utilizadas en la investigación del blog.")

class PlanningOutput(BaseModel):
    """El plan estratégico generado por el Agente Planificador."""
    persuasion_technique: str = Field(description="La principal técnica de persuasión seleccionada del manual RAG (Ej: 'Miedo/Preocupación', 'Prueba Social').")
    copywriting_methodology: str = Field(description="La metodología de copywriting a seguir (Ej: 'AIDA', 'PAS', 'BAB').")
    rationale: str = Field(description="Justificación de por qué se eligieron esa técnica y metodología para vender el software.")

class RelevanceOutput(BaseModel):
    """Usado por el Manager Agent para validar si la entrada del usuario es relevante y segura."""
    is_relevant: bool = Field(description="True si el input es seguro y relevante para la creación de un blog de negocios/marketing.")
    reasoning: str = Field(description="Justificación de la clasificación.")

class BlogSection(BaseModel):
    """Define la estructura de cada sección del blog."""
    section_title: str = Field(description="Título corto y llamativo para la sección (subtítulo H2).")
    content: str = Field(description="Contenido detallado y persuasivo de la sección.")

class BlogPost(BaseModel):
    """Define la estructura final y completa del artículo del blog."""
    main_title: str = Field(description="El título principal (H1) del blog.")
    introduction: str = Field(description="Párrafo inicial que engancha al lector y plantea el problema.")
    sections: List[BlogSection] = Field(description="Una lista de secciones que desarrollan el tema.")
    call_to_action: str = Field(description="El párrafo final donde se presenta el Target Product de software y la llamada a la acción clara.")
    sources: List[Source] = Field(description="Lista de fuentes y URLs utilizadas en la investigación del blog.")
    tags: List[str] = Field(description="Lista de 5 a 8 palabras clave o frases cortas relevantes para SEO.")

class MarkdownOutput(BaseModel):
    """Define la estructura de la salida final en formato Markdown."""
    markdown_content: str = Field(description="El contenido completo del blog post, formateado en Markdown.")