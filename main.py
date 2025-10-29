import os
from datetime import date

import sys

sys.path.insert(0, os.path.abspath('.'))

from agents.root.agent import root_manager
from shared.schemas import BlogInput, Source

if __name__ == "__main__":
    print("=====================================================================")
    print("               INICIO DEL PROCESO DE ORQUESTACIÓN COMPLETO           ")
    print("=====================================================================")

    sources_data = [
        Source(title="turke-watchdog-power-freeze-crypto-accounts-crackdown",
               url="https://es.cointelegraph.com/news/turke-watchdog-power-freeze-crypto-accounts-crackdown",
               resolved_url="https://es.cointelegraph.com/news/turke-watchdog-power-freeze-crypto-accounts-crackdown",
               domain="cointelegraph.com", reliability_score=0.9)
    ]
    safe_input = BlogInput(
        query="Turquía facultará a su organismo de control para congelar cuentas de criptomonedas en la lucha contra el lavado de dinero",
        date=date(2025, 10, 3), status="verified",
        summary={
            "headline": "Turquía planea una nueva legislación que permitirá a Masak congelar cuentas de criptomonedas para combatir el lavado de dinero, en línea con los estándares del FATF.",
            "facts": [
                "los cambios propuestos ampliarían el mandato de Masak contra el lavado de dinero (AML), permitiéndole congelar tanto cuentas de criptomonedas como cuentas bancarias tradicionales.",
                "Se espera que el proyecto de ley sea presentado en la Gran Asamblea Nacional, aunque no se proporcionó un cronograma"],
            "context": "Financial Crimes Investigation Board (abbreviation: MASAK, in Turkish: Mali Suçlar Araştırma Kurulu), is a Turkish financial intelligence unit attached to the Ministry of Finance and Treasury",
            "uncertainties": "En 2020, Bitcoin valía aproximadamente 100.000 liras turcas.",
            "implications": "uno de los mayores impulsores de la adopción ha sido la fuerte depreciación de la lira turca, que ha estado en constante declive desde 2018 en medio de una prolongada crisis financiera y económica marcada por una alta inflación, el aumento de los costos de endeudamiento y los impagos de préstamos."},
        sources=sources_data
    )

    user_input_json = safe_input.model_dump_json()
    print("\n[Input JSON al Manager]:", user_input_json[:100], "...")

    try:
        final_output = root_manager(user_input_json)

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