from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from shared.schemas import RelevanceOutput

GENERATION_MODEL = 'gemini-2.5-flash'

def run_qa_guardrail(generated_content: str) -> RelevanceOutput:
    """
    Guardrail de Salida: Veta el contenido generado para asegurar la seguridad
    y calidad antes de entregarlo.
    """
    parser = PydanticOutputParser(pydantic_object=RelevanceOutput)
    llm = ChatGoogleGenerativeAI(model=GENERATION_MODEL, temperature=0.1)

    guardrail_prompt = PromptTemplate(
        template=(
            "Eres un clasificador de QA para contenido de marketing. Evalúa el siguiente contenido de blog "
            "para determinar si es seguro, profesional, y si cumple con los estándares éticos (no tóxico, sin PII, no ofensivo). "
            "Si el contenido cumple, establece 'is_relevant' como True. Si viola algún estándar (ej: insultos, información falsa, lenguaje tóxico), establece 'is_relevant' como False. "
            "\n\n[CONTENIDO GENERADO]: {content}"
            "\n\n{format_instructions}"
        ),
        input_variables=["content"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    response = llm.invoke(guardrail_prompt.format(content=generated_content)).content

    cleaned_response = response.strip()
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:].strip()
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3].strip()

    return parser.parse(cleaned_response)