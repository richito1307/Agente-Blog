# 🤖 Agente Copilot de Creación de Contenido

Este proyecto es un sistema multiagente diseñado para generar artículos de blog de alta calidad, desde la planificación estratégica hasta la redacción final, utilizando modelos generativos de Google (Gemini).

## ✨ Características

-   **Arquitectura Multiagente:** Utiliza un patrón Manager/Worker con agentes especializados para planificar, escribir y (próximamente) formatear.
-   **Planificación Estratégica con RAG:** El Agente Planificador consulta una base de datos vectorial (ChromaDB) con un manual de copywriting para definir la mejor técnica de persuasión y metodología para el blog.
-   **Generación Estructurada:** La salida es un objeto `BlogPost` bien definido y validado con Pydantic, asegurando consistencia.
-   **Guardrails de Seguridad:** Incluye clasificadores para validar la relevancia y seguridad de las entradas del usuario y la calidad del contenido generado.
-   **Orquestación Inteligente:** Un agente "Manager" utiliza LangChain `AgentExecutor` para gestionar el flujo de trabajo entre los demás agentes.

## 🏗️ Diagrama de Arquitectura (Flujo Actual)

```
[Input: BlogInput JSON] -> [Guardrail de Entrada] -> [Agente Manager]
                                                           |
                                                           V
                                             1. Invoca [Agente Planificador] (Usa RAG) -> [Output: Plan Estratégico JSON]
                                                           |
                                                           V
                                             2. Invoca [Agente Escritor] (Usa Plan) -> [Output: BlogPost JSON]
```

## 🛠️ Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto.

### **1. Prerrequisitos**

-   Python 3.9 o superior
-   Git

### **2. Clonar el Repositorio**

```bash
git clone <URL_DE_TU_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```

### **3. Crear y Activar Entorno Virtual**

```bash
# Crear el entorno
python -m venv .venv

# Activar en Windows
.\.venv\Scripts\activate

# Activar en macOS/Linux
source .venv/bin/activate
```

### **4. Instalar Dependencias**

Asegúrate de tener tu archivo `requirements.txt` actualizado.
```bash
pip install -r requirements.txt
```

### **5. Configurar Variables de Entorno**

Crea un archivo llamado `.env` en la raíz del proyecto. Puedes copiar el archivo de ejemplo `.env.example` si lo tienes.
```
# .env
GOOGLE_API_KEY="aqui_va_tu_clave_secreta_de_google_ai_studio"
```

### **6. Crear la Base de Datos Vectorial**

Para que el Agente Planificador funcione, necesita su base de conocimientos.

1.  Crea una carpeta llamada `data` en la raíz del proyecto.
2.  Coloca tu documento de referencia (ej. `manual_copywriting.pdf`) dentro de la carpeta `data`.
3.  Ejecuta el script para crear la base de datos (asegúrate de tener un script para esto, como `create_db.py` o similar).

    ```bash
    python create_db.py
    ```

    Esto creará una carpeta `chroma_db_copywriting/` que será utilizada por el agente.

## 🚀 Uso

Para ejecutar el pipeline completo, simplemente ejecuta el script del orquestador principal:

```bash
python root_manager.py
```

El script ejecutará las pruebas definidas en el bloque `if __name__ == "__main__":` y verás en la consola el progreso del agente y el `BlogPost` final en formato JSON.

## 📂 Estructura del Proyecto

```
.
├── .venv/                     # Entorno virtual
├── chroma_db_copywriting/     # Base de datos vectorial (ignorada por Git)
├── data/                      # PDFs de origen (ignorada por Git)
├── .env                       # Claves de API (ignorada por Git)
├── .gitignore                 # Archivos a ignorar por Git
├── agent_planner.py           # Lógica del Agente Planificador
├── agent_writer.py            # Lógica del Agente Escritor
├── root_manager.py            # Orquestador principal y herramientas
├── schemas.py                 # Definiciones de Pydantic (BlogInput, BlogPost, etc.)
└── requirements.txt           # Dependencias de Python
```

## 🔮 Próximos Pasos

-   [ ] Implementar un nuevo agente/herramienta para convertir la salida final JSON a formato **Markdown**.
