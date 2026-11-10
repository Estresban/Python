from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de rutas y archivos
CARPETA_DATOS = Path("datos")
ARCHIVO_ENTRADA = CARPETA_DATOS / "loteriafiltro1.csv"


def main():
    print("Iniciando el entorno de análisis de datos...")

    if not ARCHIVO_ENTRADA.exists():
        print(
            f"Error: No se encontró el archivo en {ARCHIVO_ENTRADA.resolve()}"
        )
        return

    try:
        # Leer el CSV
        datos = pd.read_csv(
            ARCHIVO_ENTRADA,
            sep=None,
            engine="python",
            parse_dates=["FECHA"],
            encoding="utf-8-sig",
        )

        if datos.empty:
            print("El archivo CSV está vacío.")
            return

        print("¡Datos cargados correctamente!")

        # 1. SELECCIONAR Y UNIFICAR LOS NÚMEROS PRINCIPALES
        # Tomamos las columnas de N1 a N6 y las convertimos en una sola columna larga
        columnas_numeros = ["N1", "N2", "N3", "N4", "N5", "N6"]

        # Validar que todas las columnas existan en el archivo
        if not all(col in datos.columns for col in columnas_numeros):
            print(
                "Error: No se encontraron todas las columnas de números (N1 a N6) en el archivo."
            )
            return

        # .melt() transforma el formato ancho a formato largo
        numeros_unificados = datos[columnas_numeros].melt()["value"]

        # 2. CONTAR FRECUENCIAS
        # .value_counts() cuenta cuántas veces sale cada número
        frecuencia_numeros = numeros_unificados.value_counts().sort_index()

        print("\nResumen de apariciones (Top 5 números más frecuentes):")
        print(frecuencia_numeros.nlargest(5).to_string())

        # 3. CREAR LA GRÁFICA DE BARRAS
        plt.figure(figsize=(12, 6))

        # Graficamos todos los números ordenados por su propio valor (del 1 al 49, o el rango que sea)
        frecuencia_numeros.plot(kind="bar", color="royalblue", edgecolor="black")

        # Configuración de etiquetas y diseño
        plt.title(
            "Frecuencia de Aparición de los Números (N1 - N6)",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Número", fontsize=12)
        plt.ylabel("Cantidad de veces que ha salido", fontsize=12)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        # Ajustar el diseño para que no se corten las etiquetas
        plt.tight_layout()

        # Mostrar la gráfica en pantalla
        print("\nMostrando gráfico de frecuencias...")
        plt.show()

    except Exception as error:
        print(f"Error durante el análisis: {error}")


if __name__ == "__main__":
    main()
