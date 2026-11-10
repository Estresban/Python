# ==========================================================
# EJEMPLOS DE MATPLOTLIB - VISUALIZACION DE DATOS
# Modulo 5101 - Analisis de datos con Python
#
# Instalacion:
#     pip install matplotlib numpy
#
# Ejecucion desde la raiz del proyecto:
#     python src/ejemplo_matplotlib.py
# ==========================================================

import matplotlib.pyplot as plt
import numpy as np


# ==========================================================
# 1. GRAFICO DE LINEAS
# ==========================================================

print("\n========== 1. GRAFICO DE LINEAS ==========")

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"]
ventas = [120, 150, 135, 180, 210, 240]

plt.figure(figsize=(9, 5))
plt.plot(meses, ventas, marker="o", linestyle="-", label="Ventas")
plt.title("Evolucion de las ventas")
plt.xlabel("Mes")
plt.ylabel("Unidades vendidas")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# Rotamos 45 grados y alineamos el final del texto con la marca del eje (ha='right')
# plt.xticks(rotation=45, ha='right')

# ==========================================================
# 2. GRAFICO DE BARRAS
# ==========================================================

print("\n========== 2. GRAFICO DE BARRAS ==========")

productos = ["Portatil", "Monitor", "Teclado", "Raton"]
unidades = [25, 40, 60, 85]

plt.figure(figsize=(9, 5))
plt.bar(productos, unidades, label="Unidades")
plt.title("Unidades vendidas por producto")
plt.xlabel("Producto")
plt.ylabel("Unidades")
plt.legend()
plt.tight_layout()
plt.show()


# ==========================================================
# 3. GRAFICO DE BARRAS HORIZONTALES
# ==========================================================

print("\n========== 3. BARRAS HORIZONTALES ==========")

ciudades = ["Madrid", "Toledo", "Sevilla", "Valencia"]
facturacion = [5200, 3100, 4200, 2800]

plt.figure(figsize=(9, 5))
plt.barh(ciudades, facturacion)
plt.title("Facturacion por ciudad")
plt.xlabel("Facturacion (euros)")
plt.ylabel("Ciudad")
plt.tight_layout()
plt.show()


# ==========================================================
# 4. GRAFICO CIRCULAR
# ==========================================================

print("\n========== 4. GRAFICO CIRCULAR ==========")

categorias = ["Informatica", "Mobiliario", "Telefonia", "Otros"]
porcentajes = [45, 25, 20, 10]

plt.figure(figsize=(7, 7))
plt.pie(
    porcentajes,
    labels=categorias,
    autopct="%1.1f%%",
    startangle=90
)
plt.title("Distribucion de las ventas por categoria")
plt.tight_layout()
plt.show()


# ==========================================================
# 5. HISTOGRAMA
# ==========================================================

print("\n========== 5. HISTOGRAMA ==========")

# Edades ficticias de 30 clientes
edades = [
    18, 20, 21, 22, 22, 23, 24, 25, 25, 26,
    27, 28, 29, 30, 30, 31, 32, 33, 34, 35,
    36, 38, 40, 42, 45, 46, 48, 50, 55, 60
]

plt.figure(figsize=(9, 5))
plt.hist(edades, bins=18, edgecolor="black")
plt.title("Distribucion de edades de los clientes")
plt.xlabel("Edad")
plt.ylabel("Numero de clientes")
plt.grid(axis="y")
plt.tight_layout()
plt.show()


# ==========================================================
# 6. DIAGRAMA DE DISPERSION
# ==========================================================

print("\n========== 6. DIAGRAMA DE DISPERSION ==========")

horas_estudio = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
notas = [3, 4, 5, 5, 6, 7, 7, 8, 9, 10]

plt.figure(figsize=(9, 5))
plt.scatter(horas_estudio, notas, label="Alumnos")
plt.title("Relacion entre horas de estudio y nota")
plt.xlabel("Horas de estudio")
plt.ylabel("Nota")
plt.xlim(0, 11)
plt.ylim(0, 10.5)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# ==========================================================
# 7. GRAFICO DE CAJA (BOXPLOT)
# ==========================================================

print("\n========== 7. GRAFICO DE CAJA ==========")

notas_grupos = [
    [5, 6, 6, 7, 7, 8, 8, 9],
    [4, 5, 5, 6, 6, 7, 8, 9],
    [6, 7, 7, 8, 8, 8, 9, 10]
]

plt.figure(figsize=(8, 5))
plt.boxplot(notas_grupos, tick_labels=["Grupo A", "Grupo B", "Grupo C"])
plt.title("Distribucion de notas por grupo")
plt.xlabel("Grupo")
plt.ylabel("Nota")
plt.grid(axis="y")
plt.tight_layout()
plt.show()


# ==========================================================
# 8. DOS SERIES EN EL MISMO GRAFICO
# ==========================================================

print("\n========== 8. COMPARACION DE SERIES ==========")

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo"]
ventas_2025 = [100, 130, 125, 160, 190]
ventas_2026 = [120, 140, 150, 175, 220]

plt.figure(figsize=(9, 5))
plt.plot(meses, ventas_2025, marker="o", label="2025")
plt.plot(meses, ventas_2026, marker="s", label="2026")
plt.title("Comparacion de ventas: 2025 y 2026")
plt.xlabel("Mes")
plt.ylabel("Unidades vendidas")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# ==========================================================
# 9. FUNCIONES MATEMATICAS
# ==========================================================
print("\n========== 9. FUNCIONES MATEMATICAS ==========")

# Generar 200 valores entre -10 y 10
x = np.linspace(-10, 10, 200)

# Calcular dos funciones
y1 = x ** 2
y2 = 2 * x + 1

plt.figure(figsize=(9, 5))
plt.plot(x, y1, label="y = x²")
plt.plot(x, y2, label="y = 2x + 1")
plt.title("Representacion de funciones matematicas")
plt.xlabel("Eje X")
plt.ylabel("Eje Y")
plt.axhline(0, linewidth=0.8)
plt.axvline(0, linewidth=0.8)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# ==========================================================
# 10. GUARDAR UN GRAFICO EN UN ARCHIVO
# ==========================================================

print("\n========== 10. GUARDAR GRAFICO ==========")

dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
temperaturas = [18, 20, 19, 23, 22]

plt.figure(figsize=(9, 5))
plt.plot(dias, temperaturas, marker="o")
plt.title("Temperaturas durante la semana")
plt.xlabel("Dia")
plt.ylabel("Temperatura (°C)")
plt.grid(True)
plt.tight_layout()

# Guardar el grafico antes de mostrarlo
plt.savefig("temperaturas.png", dpi=300, bbox_inches="tight")
plt.show()

print("Grafico guardado como temperaturas.png")


# ==========================================================
# FIN DEL PROGRAMA
# ==========================================================

print("\n========== FIN DE LOS EJEMPLOS ==========")
