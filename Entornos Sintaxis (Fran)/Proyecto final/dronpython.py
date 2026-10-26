'''Proyecto: Control de vuelo simulado
En este proyecto vamos a aplicar las estructuras de control a un escenario relacionado con una de las aplicaciones que veremos posteriormente: la programación de drones con Python.

No será necesario disponer todavía de un dron físico.

El programa simulará el control básico de un dron.

Requisitos
El programa deberá comenzar mostrando:

=========================
     DRON PYTHON
=========================
Después mostrará un menú:

1. Despegar
2. Avanzar
3. Retroceder
4. Girar a la derecha
5. Girar a la izquierda
6. Consultar batería
7. Aterrizar
0. Salir
Condiciones
El dron comenzará con:

bateria = 100
Y estará inicialmente en tierra.

El programa deberá controlar:

Despegue
El dron solamente podrá despegar si:

batería >= 20%
Movimiento
Cada movimiento consumirá un porcentaje de batería.

Por ejemplo:

Avanzar → -5%
Retroceder → -5%
Girar → -2%
Batería
Cuando la batería sea inferior al 20%:

ADVERTENCIA: batería baja
Cuando llegue al 0%:

Batería agotada.
Aterrizaje de emergencia.
Aterrizaje
El dron deberá estar en vuelo para poder aterrizar.

Menú
El menú debe repetirse mediante un while.

Condiciones
Utiliza if, elif y else para controlar las diferentes opciones.

Repeticiones
Utiliza bucles cuando sean necesarios.

Ejemplo de ejecución
=========================
     DRON PYTHON
=========================

Batería: 100%
Estado: EN TIERRA

1. Despegar
2. Avanzar
3. Retroceder
4. Girar derecha
5. Girar izquierda
6. Consultar batería
7. Aterrizar
0. Salir

Opción: 1

Dron despegando...

Opción: 2

Avanzando...
Batería: 95%

Opción: 4

Girando a la derecha...
Batería: 93%

Opción: 6

Batería: 93%

Opción: 7

Aterrizando...

Opción: 0

Programa finalizado.
⭐ Ampliación
Para alumnado que termine antes:

Añade coordenadas (x, y) para representar la posición.
Haz que avanzar modifique la coordenada.
Permite girar 90 grados.
Registra los movimientos realizados.
Añade un modo de vuelo automático.
Permite introducir una ruta.
Comprueba que la batería sea suficiente antes de ejecutar una ruta.
Añade un límite de distancia.
Simula obstáculos.
Añade un aterrizaje automático cuando la batería sea baja.'''



print("=========================")
print("     DRON PYTHON")
print("=========================")

bateria = 100
en_vuelo = False

while True:
    print("\nBatería:", bateria, "%")
    
    if en_vuelo:
        print("Estado: EN VUELO")
    else:
        print("Estado: EN TIERRA")

    print("\n1. Despegar")
    print("2. Avanzar")
    print("3. Retroceder")
    print("4. Girar a la derecha")
    print("5. Girar a la izquierda")
    print("6. Consultar batería")
    print("7. Aterrizar")
    print("0. Salir")

    opcion = input("\nOpción: ")

    if opcion == "1":
        if en_vuelo:
            print("El dron ya está en vuelo.")
        elif bateria >= 20:
            print("\nDron despegando...")
            en_vuelo = True
        else:
            print("Batería insuficiente para despegar.")

    elif opcion == "2":
        if en_vuelo:
            bateria -= 5
            print("\nAvanzando...")
        else:
            print("El dron debe estar en vuelo.")

    elif opcion == "3":
        if en_vuelo:
            bateria -= 5
            print("\nRetrocediendo...")
        else:
            print("El dron debe estar en vuelo.")

    elif opcion == "4":
        if en_vuelo:
            bateria -= 2
            print("\nGirando a la derecha...")
        else:
            print("El dron debe estar en vuelo.")

    elif opcion == "5":
        if en_vuelo:
            bateria -= 2
            print("\nGirando a la izquierda...")
        else:
            print("El dron debe estar en vuelo.")

    elif opcion == "6":
        print("\nBatería:", bateria, "%")

    elif opcion == "7":
        if en_vuelo:
            print("\nAterrizando...")
            en_vuelo = False
        else:
            print("El dron ya está en tierra.")

    elif opcion == "0":
        if en_vuelo:
            print("Aterrizando antes de salir...")
            en_vuelo = False
        print("Programa finalizado.")
        break

    else:
        print("Opción no válida.")

    # Comprobar que la batería no baje de cero
    if bateria < 0:
        bateria = 0

    # Comprobar si la batería se ha agotado
    if bateria == 0 and en_vuelo:
        print("\nBatería agotada.")
        print("Aterrizaje de emergencia.")
        en_vuelo = False

    # Avisar cuando la batería sea inferior al 20 %
    elif bateria < 20:
        print("ADVERTENCIA: batería baja")

    if opcion in ["2", "3", "4", "5"] and bateria > 0:
        print("Batería:", bateria, "%")
