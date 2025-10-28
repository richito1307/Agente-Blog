from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

STYLING_MODEL = 'gemini-2.5-flash'

def enrich_markdown_with_llm(base_markdown: str) -> str:
    """
    Toma un Markdown base y usa un LLM para añadir estilos contextuales.

    Args:
        base_markdown (str): El contenido Markdown estructural.

    Returns:
        str: El contenido Markdown enriquecido con estilos.
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