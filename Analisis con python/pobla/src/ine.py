from pathlib import Path
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

archivo = Path(__file__).resolve().parent.parent / "datos/65334.xlsx"
df = pd.read_excel(archivo, header=None)


años = df.iloc[7, 1:100].dropna().to_numpy(dtype=str)
valores = df.iloc[17, 1 : len(años) + 1].to_numpy(dtype=float)

tri = años[::-1]
val = valores[::-1]

print(f"Total trimestres: {len(tri)} ({tri} -> {tri[-1]})")

df_exportar = pd.DataFrame({"Trimestre": tri, "Tasa_Paro": val})

archivo_csv = Path(__file__).resolve().parent.parent / "datos/INE.csv"
df_exportar.to_csv(archivo_csv, index=False)

archivo_db = Path(__file__).resolve().parent.parent / "datos/INE.db"
with sqlite3.connect(archivo_db) as conexion:
    df_exportar.to_sql("INE_CLM", conexion, if_exists="replace", index=False)

plt.figure(figsize=(14, 6))
plt.plot(tri, val, marker="o", markersize=4, linestyle="-", label="Tasa de paro CLM (%)")
plt.title("Tasa de paro en CLM (2002 - 2026)")
plt.xlabel("Año / Trimestre")
plt.ylabel("Tasa de paro (%)")
plt.xticks(tri[::4], rotation=45, ha="right")
plt.yticks(range(int(min(val)) - 1, int(max(val)) + 3, 2))
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()
