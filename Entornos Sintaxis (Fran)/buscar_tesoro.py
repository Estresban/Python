import random


def crear_mapa():
    mapa = [["?" for _ in range(3)] for _ in range(3)] #generamos la matriz de 3 filas y 3 columnas com ?

    fila_tesoro = random.randint(0, 2) # Elegimos fila y columna al azar con ramdon
    columna_tesoro = random.randint(0, 2)

    return mapa, fila_tesoro, columna_tesoro

# Dibujamos el matriz; si revelar_tesoro es True, muestra el diamante
def mostrar_mapa(mapa, revelar_tesoro=False, fila_tesoro=None, columna_tesoro=None): # Funcion para mostrar la matriz
    print(" 1 2 3")
    for fila in range(3):
        # Si coincide la posición, dibujamos el tesoro
        linea = f"{fila + 1}  "
        for columna in range(3):
            if revelar_tesoro and fila == fila_tesoro and columna == columna_tesoro:
                linea += " 💎 "
            else:
                linea += f" {mapa[fila][columna]}  "
        print(linea)
    print()

# Se pide una fila o columna válida 1-2-3 y evitamos que el codigo falle si escriben texto
def solicitar_coordenada(tipo_coordenada): 
    while True:
        try:
            entrada = int(input(f"Introduce la {tipo_coordenada} (1-3): "))
            if 1 <= entrada <= 3:
                # Restamos 1 porque empiezan en la posición 0
                return entrada - 1
            else:
                print("El número debe ser 1 2 o 3.")
        except ValueError: # Capturamos el error si se introducen letras o símbolos
            print("Fallo: Debes introducir un número")

# Funcion para mpstrar el resumen y las estadisticas
def mostrar_estadisticas( 
    intentos_actuales,
    tesoros_encontrados,
    mapas_generados,
    mejor_partida,
    peor_partida,):
    
    texto_mejor = (f"{mejor_partida} intento(s)"
        if mejor_partida is not None
        else "Sin partidas ganadas")
    
    texto_peor = (f"{peor_partida} intento(s)"
        if peor_partida is not None
        else "Sin partidas ganadas")

    print("========= ESTADÍSTICAS =========")
    print(f"Intentos en la partida actual: {intentos_actuales}")
    print(f"Tesoros encontrados: {tesoros_encontrados}")
    print(f"Mapas generados: {mapas_generados}")
    print(f"Mejor partida (mín. intentos): {texto_mejor}")
    print(f"Peor partida (máx. intentos): {texto_peor}")
    print("================================")

# Emppieza la jugada: pide coordenadas y comprueba si acierta
def jugar_turno(mapa, fila_tesoro, columna_tesoro): 
    
    fila = solicitar_coordenada("fila")
    columna = solicitar_coordenada("columna")
    # Comprobamos si la casilla ya tiene una 'X' marcada
    if mapa[fila][columna] == "X":
        print("Esa casilla ya ha sido consultada, y cuenta como intento.")
        return False

    # Comprobamos si se ha encontrado el tesoro
    if fila == fila_tesoro and columna == columna_tesoro:
        return True

    # Marcamos la casilla fallada con 'X' para recordarla
    mapa[fila][columna] = "X"
    print("Aquí no está el tesoro! Sigue intentandolo.")
    return False

# Funcion para iniciar el juego
def main():
    # Inicializamos el tablero y los contadores
    mapa_actual, fila_tesoro, columna_tesoro = crear_mapa()

    intentos_actuales = 0
    tesoros_encontrados = 0
    mapas_generados = 1
    mejor_partida = None
    peor_partida = None

    # Bucle para mantener el menú activo hasta que el usuario pulse 0
    while True: 
        
        print("BUSCAR EL TESORO")
        print("1. Ver mapa actual")
        print("2. Ver mapa resuelto")
        print("3. Jugar")
        print("4. Ver estadísticas")
        print("0. Salir")

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            mostrar_mapa(mapa_actual)
            
        # Llamamos a mostrar_mapa revelando el tesoro sin modificar el tablero original
        elif opcion == "2":
            mostrar_mapa(
                mapa_actual,
                revelar_tesoro=True,
                fila_tesoro=fila_tesoro,
                columna_tesoro=columna_tesoro)

        elif opcion == "3":
            intentos_actuales += 1
            tesoro_encontrado = jugar_turno(
                mapa_actual, fila_tesoro, columna_tesoro)

            if tesoro_encontrado:
                print("¡Enhorabuena! Has encontrado el 💎 en" f" {intentos_actuales} intento(s).")
               
                # Actualizamos el total de victorias y comprobamos si hay nuevo récord
                tesoros_encontrados += 1
                if (mejor_partida is None or intentos_actuales < mejor_partida):
                    mejor_partida = intentos_actuales
                if peor_partida is None or intentos_actuales > peor_partida:
                    peor_partida = intentos_actuales

                # Reiniciamos el tablero y el contador de intentos para la siguiente partida
                print("Nuevo mapa...")
                mapa_actual, fila_tesoro, columna_tesoro = crear_mapa()
                intentos_actuales = 0
                mapas_generados += 1

        elif opcion == "4":
            mostrar_estadisticas(
                intentos_actuales,
                tesoros_encontrados,
                mapas_generados,
                mejor_partida,
                peor_partida)

        elif opcion == "0":
            print("Hasta luego Lucas.")
            break
        else:
            print("Opción no válida. Por favor, selecciona entre 0 y 4")

# Ejecucion del archivo
if __name__ == "__main__":
    main()




