from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

PERSIST_DIRECTORY = './chroma_db_copywriting'

def load_chroma_db():
    """Carga la base de vectores persistente e inicializa el modelo de embedding."""
    print("Iniciando la carga del Vector Store (Chroma)...")
    embedding_model = GoogleGenerativeAIEmbeddings(model="text-embedding-004")
    vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embedding_model)

    print("✅ Chroma DB cargada.")
    return vectorstore