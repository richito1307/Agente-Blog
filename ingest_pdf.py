import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PDF_FILENAME = "Workbook - Sesión 4_1(1).pdf"
PDF_PATH = os.path.join("data", PDF_FILENAME)
PERSIST_DIRECTORY = './chroma_db_copywriting'

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

embedding_model = GoogleGenerativeAIEmbeddings(model="text-embedding-004")


def create_vector_store():
    """
    Crea la Base de Vectores (ChromaDB) a partir del PDF.
    """
    print("--- 1. INICIANDO PROCESO DE RAG CORE ---")

    print(f"Cargando PDF desde: {PDF_PATH}")
    try:
        loader = PyPDFLoader(PDF_PATH)
        documents = loader.load()
    except Exception as e:
        print(f"ERROR: No se pudo cargar el PDF. Asegúrate de que existe en la ruta '{PDF_PATH}'.")
        print(f"Detalle del error: {e}")
        return None

    print(f"Dividiendo el documento en chunks (tamaño={CHUNK_SIZE}, solapamiento={CHUNK_OVERLAP})...")

    # Usamos un divisor basado en tiktoken para ser compatible con la lógica de tokens de Gemini
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = text_splitter.split_documents(documents)

    print(f"Documento dividido en {len(chunks)} fragmentos.")
    print(f"Creando embeddings e indexando en ChromaDB en '{PERSIST_DIRECTORY}'...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=PERSIST_DIRECTORY
    )

    vectorstore.persist()
    print("\n✅ Indexación completada con éxito.")

    return vectorstore

def test_retrieval(vectorstore):
    """
    Prueba que la base de vectores pueda recuperar información relevante.
    """
    print("\n--- 2. PRUEBA DE RECUPERACIÓN (RAG TEST) ---")

    query = "¿Cuál es el prompt para atrapar la gente si el contenido del blog es emocional?"

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # k=3: trae los 3 chunks más relevantes

    docs = retriever.invoke(query)

    print(f"Pregunta: {query}")
    print("\nDocumentos recuperados (los más relevantes):")

    for i, doc in enumerate(docs):
        content_snippet = doc.page_content[:300].replace('\n', ' ')
        page = doc.metadata.get('page', 'N/A')
        print(f"--- Documento {i+1} (Página: {page}) ---")
        print(f"Contenido: {content_snippet}...")



if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Carpeta 'data' creada. Coloca tu PDF allí.")

    db = create_vector_store()

    if db:
        test_retrieval(db)