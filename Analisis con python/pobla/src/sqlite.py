import sqlite3

# Matriz de ejemplo (cada sublista representa una fila de la tabla)
matriz_productos = [
    ["Monitor", 220.00, 15],
    ["Ratón inalámbrico", 25.50, 40],
    ["Auriculares", 79.90, 12],
]

# --- 1. EXPORTAR MATRIZ A SQLITE ---
with sqlite3.connect("inventario.db") as conexion:
    cursor = conexion.cursor()

    # Crear la tabla con las columnas correspondientes a la matriz
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL
        )
    """)

    # Insertar toda la matriz de una sola vez
    cursor.executemany(
        "INSERT INTO stock (producto, precio, cantidad) VALUES (?, ?, ?)",
        matriz_productos,
    )
    conexion.commit()

# --- 2. LEER DATOS DESDE SQLITE ---
with sqlite3.connect("inventario.db") as conexion:
    cursor = conexion.cursor()

    # Consultar los registros
    cursor.execute("SELECT producto, precio, cantidad FROM stock")

    # fetchall() devuelve una lista de tuplas (similar a una matriz)
    filas_leidas = cursor.fetchall()

    # Si necesitas exactamente una lista de listas como la original:
    matriz_recuperada = [list(fila) for fila in filas_leidas]

for fila in matriz_recuperada:
    print(fila)