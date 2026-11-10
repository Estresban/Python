import matplotlib.pyplot as plt
import numpy as np

# 1. CREAMOS EL LIENZO GENERAL (2 filas, 5 columnas)
# Usamos un tamaño muy grande (24x10 pulgadas) para que quepan bien los 10 gráficos
fig, axs = plt.subplots(2, 5, figsize=(24, 10))

# ==========================================================
# 1. GRAFICO DE LINEAS -> Fila 0, Columna 0
# ==========================================================
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"]
ventas = [120, 150, 135, 180, 210, 240]

axs[0, 0].plot(meses, ventas, marker="o", linestyle="-", label="Ventas")
axs[0, 0].set_title("1. Evolucion de las ventas")
axs[0, 0].set_xlabel("Mes")
axs[0, 0].set_ylabel("Unidades")
axs[0, 0].grid(True)
axs[0, 0].legend()
axs[0, 0].set_xticklabels(meses, rotation=45, ha='right') # Inclinamos meses

# ==========================================================
# 2. GRAFICO DE BARRAS -> Fila 0, Columna 1
# ==========================================================
productos = ["Portatil", "Monitor", "Teclado", "Raton"]
unidades = [25, 40, 60, 85]

axs[0, 1].bar(productos, unidades, label="Unidades", color="orange")
axs[0, 1].set_title("2. Unidades por producto")
axs[0, 1].set_xlabel("Producto")
axs[0, 1].set_ylabel("Unidades")
axs[0, 1].legend()

# ==========================================================
# 3. GRAFICO DE BARRAS HORIZONTALES -> Fila 0, Columna 2
# ==========================================================
ciudades = ["Madrid", "Toledo", "Sevilla", "Valencia"]
facturacion = [5200, 3100, 4200, 2800]

axs[0, 2].barh(ciudades, facturacion, color="green")
axs[0, 2].set_title("3. Facturacion por ciudad")
axs[0, 2].set_xlabel("Euros")
axs[0, 2].set_ylabel("Ciudad")

# ==========================================================
# 4. GRAFICO CIRCULAR -> Fila 0, Columna 3
# ==========================================================
categorias = ["Informatica", "Mobiliario", "Telefonia", "Otros"]
porcentajes = [45, 25, 20, 10]

axs[0, 3].pie(porcentajes, labels=categorias, autopct="%1.1f%%", startangle=90)
axs[0, 3].set_title("4. Ventas por categoria")

# ==========================================================
# 5. HISTOGRAMA -> Fila 0, Columna 4
# ==========================================================
edades = [
    18, 20, 21, 22, 22, 23, 24, 25, 25, 26,
    27, 28, 29, 30, 30, 31, 32, 33, 34, 35,
    36, 38, 40, 42, 45, 46, 48, 50, 55, 60
]

axs[0, 4].hist(edades, bins=10, edgecolor="black", color="purple") # bajé bins a 10 por espacio
axs[0, 4].set_title("5. Distribucion de edades")
axs[0, 4].set_xlabel("Edad")
axs[0, 4].set_ylabel("Clientes")
axs[0, 4].grid(axis="y")

# ==========================================================
# 6. DIAGRAMA DE DISPERSION -> Fila 1, Columna 0
# ==========================================================
horas_estudio = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
notas = [3, 4, 5, 5, 6, 7, 7, 8, 9, 10]

axs[1, 0].scatter(horas_estudio, notas, label="Alumnos", color="red")
axs[1, 0].set_title("6. Horas de estudio vs Nota")
axs[1, 0].set_xlabel("Horas")
axs[1, 0].set_ylabel("Nota")
axs[1, 0].set_xlim(0, 11)
axs[1, 0].set_ylim(0, 10.5)
axs[1, 0].grid(True)
axs[1, 0].legend()

# ==========================================================
# 7. GRAFICO DE CAJA (BOXPLOT) -> Fila 1, Columna 1
# ==========================================================
grupo_a = [5, 6, 6, 7, 7, 8, 8, 9]
grupo_b = [4, 5, 5, 6, 6, 7, 8, 9]
grupo_c = [6, 7, 7, 8, 8, 8, 9, 10]

notas_grupos = [grupo_a, grupo_b, grupo_c]

axs[1, 1].boxplot(notas_grupos, tick_labels=["Grupo A", "Grupo B", "Grupo C"])
axs[1, 1].set_title("7. Notas por grupo")
axs[1, 1].set_xlabel("Grupo")
axs[1, 1].set_ylabel("Nota")
axs[1, 1].grid(axis="y")

# ==========================================================
# 8. DOS SERIES EN EL MISMO GRAFICO -> Fila 1, Columna 2
# ==========================================================
meses_comp = ["Enero", "Febrero", "Marzo", "Abril", "Mayo"]
ventas_2025 = [100, 130, 125, 160, 190]
ventas_2026 = [120, 140, 150, 175, 220]

axs[1, 2].plot(meses_comp, ventas_2025, marker="o", label="2025")
axs[1, 2].plot(meses_comp, ventas_2026, marker="s", label="2026")
axs[1, 2].set_title("8. Comparacion 2025-2026")
axs[1, 2].set_xlabel("Mes")
axs[1, 2].set_ylabel("Unidades")
axs[1, 2].grid(True)
axs[1, 2].legend()

# ==========================================================
# 9. FUNCIONES MATEMATICAS -> Fila 1, Columna 3
# ==========================================================
x_mat = np.linspace(-10, 10, 200)
y1 = x_mat ** 2
y2 = 2 * x_mat + 1

axs[1, 3].plot(x_mat, y1, label="y = x²")
axs[1, 3].plot(x_mat, y2, label="y = 2x + 1")
axs[1, 3].set_title("9. Funciones matemáticas")
axs[1, 3].set_xlabel("X")
axs[1, 3].set_ylabel("Y")
axs[1, 3].axhline(0, linewidth=0.8, color="black")
axs[1, 3].axvline(0, linewidth=0.8, color="black")
axs[1, 3].grid(True)
axs[1, 3].legend()

# ==========================================================
# 10. TEMPERATURAS -> Fila 1, Columna 4
# ==========================================================
dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
temperaturas = [18, 20, 19, 23, 22]

axs[1, 4].plot(dias, temperaturas, marker="o", color="teal")
axs[1, 4].set_title("10. Temperaturas")
axs[1, 4].set_xlabel("Día")
axs[1, 4].set_ylabel("°C")
axs[1, 4].grid(True)

# ==========================================================
# CIERRE Y AJUSTES FINALES
# ==========================================================
# Título general para todo el panel
fig.suptitle("Visualizaciones de Datos", fontsize=18, fontweight='bold')

# Ajustamos espacios para que NO se amontonen las etiquetas y títulos entre ellos
plt.tight_layout()

# Guardamos el macro-gráfico final completo
plt.savefig("panel_completo_10_graficos.png", dpi=300, bbox_inches="tight")
plt.show()

print("¡Hecho! Todos los gráficos se han unido y guardado en 'panel_completo_10_graficos.png'")
