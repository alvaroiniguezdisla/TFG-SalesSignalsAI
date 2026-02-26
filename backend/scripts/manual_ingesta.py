# ----------------------------------------------------------------------------------
# SCRIPT MANUAL: Ejecucion de la ingesta de noticias
#
# Uso: python -m scripts.manual_ingesta
#
# Que hace: Ejecuta unicamente la fase de extraccion (RSS -> Scraper -> Browser)
# para verificar que las fuentes responden y se obtienen noticias correctamente,
# sin pasar por la IA ni guardar en base de datos.
#
# Requisitos:
#   - Internet activo
#   - Fuentes RSS configuradas en config.py
# ----------------------------------------------------------------------------------

from app.services.extraccion.manager import get_extractor_manager

def ejecutar():
    print("Conectando con fuentes configuradas...")

    try:
        extractor = get_extractor_manager()
        noticias = extractor.obtener_noticias()
        print(f"\nResultado: {len(noticias)} noticias obtenidas.")

        fuentes_caidas = extractor.get_ultimas_fuentes_caidas()
        if fuentes_caidas:
            print(f"\n[FUENTES_CAIDAS] {len(fuentes_caidas)} fuente(s) con incidencias:")
            for item in fuentes_caidas:
                detalle = "; ".join(item.get("errores", []))
                print(f"  - {item.get('fuente', 'Desconocida')}: {detalle}")

        if noticias:
            print(f"\nDetalle de las primeras {min(5, len(noticias))} noticias:\n")

            for i, noticia in enumerate(noticias[:5]):
                print(f"[Noticia #{i + 1}]")
                for clave, valor in noticia.items():
                    valor_str = str(valor)
                    if len(valor_str) > 100:
                        valor_str = valor_str[:97] + "..."
                    print(f"  {clave}: {valor_str}")
                print("  -----------------------")

    except Exception as e:
        print(f"\nError durante la ingesta: {e}")

    print("\nFin de la ingesta manual.")


if __name__ == "__main__":
    ejecutar()
