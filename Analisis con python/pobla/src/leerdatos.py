from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

from pathlib import Path

archivo = Path(__file__).resolve().parent.parent / "datos/poblacion.xlsx"

df = pd.read_excel(archivo, header=None)

matriz = np.array([
    df.iloc[7, 1:26],
    df.iloc[9, 1:26] 
], dtype=int)


np.set_printoptions(suppress=True, precision=0)
print ("MATRIZ DE DATOS")
print (matriz)
print("\nDimensiones:", matriz.shape)

años = matriz[0]
poblacion = matriz[1]

df_exportar =pd.DataFrame({
    "Año":años,
    "Poblacion":poblacion
})

archivo_csv = Path(__file__).resolve().parent.parent / "datos/poblacion.csv"
df_exportar.to_csv(archivo_csv, index=False)

archivo_db = Path(__file__).resolve().parent.parent / "datos/poblacion.db"
conexion = sqlite3.connect(archivo_db)

df_exportar.to_sql("evolucion_poblacion", conexion, if_exists="replace",index=False)

conexion.close()

print("\n==== Evolución extranjera España ====")

plt.figure(figsize=(9, 5))
plt.plot(años, poblacion, marker="o", linestyle="-", label="Poblacion")
plt.title("Poblacion extranjera España")
plt.xlabel("Años")
plt.xticks(años, rotation=45)
plt.yticks(poblacion, rotation=45)
plt.yticks(range(1_000_000, 8_000_000, 500_000))
plt.ylabel("Población")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.ticklabel_format(style='plain', axis='y')
plt.show()

# SACO LA MATRIZ A UN TXT
with open('matrizpoblacion.txt', 'w', encoding='utf-8') as f:
    f.write(pd.DataFrame(matriz).to_string(index=False, header=False))
