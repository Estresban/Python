from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

ruta_actual = Path(__file__).parent
ruta_csv = ruta_actual / "datos" / "sp500_indice_2021_2026.csv"

# Cargar los datos del CSV
df = pd.read_csv(ruta_csv)

# Convertir la columna 'Date' a tipo datetime para ordenarla
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")

# Configurar el tamaño de la gráfica
plt.figure(figsize=(12, 6))
plt.plot(df["Date"], df["Close"], label="Precio de Cierre", color="blue", linewidth=1.5)
# títulos y etiquetas
plt.title("Evolución del S&P 500 - Precio de Cierre", fontsize=14, fontweight="bold")
plt.xlabel("Fecha", fontsize=12)
plt.ylabel("Precio de Cierre ($)", fontsize=12)
# Añadir cuadrícula de fondo y leyenda
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(loc="upper left")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
