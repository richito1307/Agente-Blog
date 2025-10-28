import os
import re

OUTPUT_DIR = "output_blogs"


def _create_slug(title: str) -> str:
    """
    Convierte un título en una cadena limpia y amigable para URL (slug).
    - Convierte tildes y ñ a sus equivalentes sin acento.
    - Convierte a minúsculas.
    - Reemplaza espacios y caracteres no alfanuméricos por guiones.
    - Limita la longitud.
    """
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ü': 'u', 'ñ': 'n',
        'Á': 'a', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'Ñ': 'N'
    }

    slug = title
    for original, replacement in replacements.items():
        slug = slug.replace(original, replacement)

    slug = slug.lower()

    slug = re.sub(r'[^a-z0-9\s-]', '', slug)

    slug = re.sub(r'[\s-]+', '-', slug).strip('-')

    MAX_SLUG_LENGTH = 50
    if len(slug) > MAX_SLUG_LENGTH:
        last_hyphen = slug.rfind('-', 0, MAX_SLUG_LENGTH)
        if last_hyphen > 0:
            slug = slug[:last_hyphen]
        else:
            slug = slug[:MAX_SLUG_LENGTH]

    return slug


def save_content_and_resources(title: str, markdown_content: str) -> str:
    """
    Crea una carpeta única (con nombre de slug), guarda el Markdown y simula la creación de un archivo de imagen.

    Returns: La ruta completa de la carpeta creada.
    """

    blog_folder_name = _create_slug(title)

    base_dir = os.path.join(os.getcwd(), OUTPUT_DIR)
    final_path = os.path.join(base_dir, blog_folder_name)

    os.makedirs(final_path, exist_ok=True)

    markdown_filename = os.path.join(final_path, "index.md")
    with open(markdown_filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    image_filename = os.path.join(final_path, "featured_image.jpg")
    with open(image_filename, 'w', encoding='utf-8') as f:
        f.write("Placeholder de imagen. Archivo creado para simular recursos.")

    return final_path
