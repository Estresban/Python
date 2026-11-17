from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

raiz = Path(__file__).parent.parent

archivo = raiz / "datos" / "poblacion.xlsx"

df = pd.read_excel(archivo, header=None)

matriz = np.array([
    df.iloc[7, 1:26],
    df.iloc[9, 1:26] 
], dtype=int)

print (matriz)

print("\nDimensiones:", matriz.shape)

anios = matriz[0]
poblacion = matriz[1]

print("\n========== Evolución extranjera España ==========")

plt.figure(figsize=(9, 5))
plt.plot(anios, poblacion, marker="o", linestyle="-", label="Poblacion")
plt.title("Poblacion extrangera España")
plt.xlabel("Años")
plt.ylabel("Población")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()