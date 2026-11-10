from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# Ajuste de ruta profesional: Detecta la raíz del proyecto estando en 'src/'
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_PROYECTO / "datos"
ARCHIVO_ENTRADA = CARPETA_DATOS / "Loteriafiltro1.csv"


def main():
    print("Iniciando el entorno de análisis de datos...")

    # Verificar si el archivo existe antes de intentar leerlo
    if not ARCHIVO_ENTRADA.exists():
        print(
            f"Error: No se encontró el archivo en {ARCHIVO_ENTRADA.resolve()}"
        )
        print(
            "Por favor, coloca tu archivo CSV en la carpeta 'datos' e inténtalo de nuevo."
        )
        return

    try:
        print(f"Cargando datos desde: {ARCHIVO_ENTRADA.name}...")

        # 1. Leer el CSV de forma normal
        datos = pd.read_csv(
            ARCHIVO_ENTRADA, sep=None, engine="python", encoding="utf-8-sig"
        )

        if datos.empty:
            print("El archivo CSV está vacío.")
            return

        # 2. CORRECCIÓN DEFINITIVA: Forzar la conversión de fechas limpiando errores
        datos["FECHA"] = pd.to_datetime(
            datos["FECHA"], format="%d/%m/%Y", errors="coerce"
        )

        # Eliminar las filas que se hayan quedado con la fecha rota o vacía
        datos = datos.dropna(subset=["FECHA"])

        # 3. CONVERTIR LAS COLUMNAS A ENTEROS
        columnas_numeros = [
            "N1",
            "N2",
            "N3",
            "N4",
            "N5",
            "N6",
            "COMP"
        ]
        columnas_a_convertir = [
            col for col in columnas_numeros if col in datos.columns
        ]

        # Convertimos las columnas eliminando antes cualquier fila que tenga un número vacío
        datos = datos.dropna(subset=columnas_a_convertir)
        datos[columnas_a_convertir] = datos[columnas_a_convertir].astype(int)

        # Ordenar los datos cronológicamente
        datos = datos.sort_values(by="FECHA")

        # Definir y validar las columnas esperadas según tu encabezado
        columnas_esperadas = [
            "SORTEO",
            "FECHA",
            "N1",
            "N2",
            "N3",
            "N4",
            "N5",
            "N6",
            "COMP"
        ]
        columnas_disponibles = [
            col for col in columnas_esperadas if col in datos.columns
        ]
        datos = datos[columnas_disponibles]

        # --- Reporte por consola ---
        print("\n¡Datos cargados y formateados correctamente!")
        print(f"Total de sorteos válidos registrados: {len(datos)}")
        print(
            f"Rango de fechas: desde {datos['FECHA'].min().strftime('%d/%m/%Y')} hasta {datos['FECHA'].max().strftime('%d/%m/%Y')}"
        )

        print("\nÚltimos sorteos en el archivo:")
        print(datos.tail().to_string(index=False))



if __name__ == "__main__":
    main()
