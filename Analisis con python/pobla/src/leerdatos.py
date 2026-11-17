from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

raiz = Path(__file__).parent.parent
archivo = raiz / "datos" / "poblacion.xlsx"  # Ejecutar desde /src

df = pd.read_excel(archivo, header=None)

matriz = np.array([
    df.iloc[7, 1:26],
    df.iloc[9, 1:26] 
], dtype=int)

print (matriz)
print("\nDimensiones:", matriz.shape)

años = matriz[0]
poblacion = matriz[1]

print("\n==== Evolución extranjera España ====")

plt.figure(figsize=(9, 5))
plt.plot(años, poblacion, marker="o", linestyle="-", label="Poblacion")
plt.title("Poblacion extranjera España")
plt.xlabel("Años")
plt.ylabel("Población")
plt.grid(True)
plt.legend()
#plt.tight_layout()
plt.ticklabel_format(style='plain', axis='y')
plt.show()

# SACO LA MATRIZ A UN TXT
with open('matrizpoblacion.txt', 'w', encoding='utf-8') as f:
    f.write(pd.DataFrame(matriz).to_string(index=False, header=False))
