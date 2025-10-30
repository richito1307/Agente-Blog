import os
import asyncio

import sys

sys.path.insert(0, os.path.abspath('.'))

from agents.root.agent import root_manager
from agents.researcher.agent import search_agent

if __name__ == "__main__":
    print("=====================================================================")
    print("               INICIO DEL PROCESO DE ORQUESTACIÓN COMPLETO           ")
    print("=====================================================================")

    try:
        investigation = asyncio.run(search_agent.run_task("Investiga sobre las ultimas noticias de AML/FT"))
        print(investigation)
        final_output = root_manager(investigation)

        print("\n" + "=" * 80)
        print("RESULTADO FINAL DEL PIPELINE COMPLETO:")
        print("=" * 80)
        print(final_output)

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ ERROR CRÍTICO AL EJECUTAR EL PIPELINE: {e}")
        print("Asegúrese de que su archivo .env esté cargado y las importaciones estén configuradas correctamente.")
        print("=" * 80)

    print("\n=====================================================================")
    print("               FIN DEL PROCESO DE ORQUESTACIÓN                       ")
    print("=====================================================================")
