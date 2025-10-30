import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def resolve_url(redirect_url: str) -> dict:
    """Resuelve una URL de redirección de Google Search (grounding-api-redirect) a su URL final real."""
    try:
        # Paso 1: Intentar redirección HTTP normal
        r = requests.get(redirect_url, timeout=8, allow_redirects=True)
        final_url = r.url

        # Si sigue en dominio de Google (ej. vertexaisearch.cloud.google.com), buscar dentro del HTML
        if "google.com" in final_url or "vertexaisearch.cloud.google.com" in final_url:
            soup = BeautifulSoup(r.text, "html.parser")

            # Buscar meta refresh (ej: <meta http-equiv="refresh" content="0;URL=https://sana.sy/...">)
            meta = soup.find("meta", attrs={"http-equiv": "refresh"})
            if meta and "URL=" in meta.get("content", ""):
                final_url = meta["content"].split("URL=")[-1].strip()

            # Buscar enlace directo (<a href="https://sana.sy/...">Continuar</a>)
            if not final_url or "google.com" in final_url:
                a_tag = soup.find("a", href=True)
                if a_tag and "http" in a_tag["href"]:
                    final_url = a_tag["href"]

        # Paso 2: Calcular dominio limpio
        domain = urlparse(final_url).netloc.lower()

        return {
            "status": "ok",
            "url_redirect": redirect_url,
            "url_resolved": final_url,
            "domain": domain
        }

    except Exception as e:
        return {
            "status": "error",
            "url_redirect": redirect_url,
            "error": str(e)
        }
