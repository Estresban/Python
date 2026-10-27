'''Reto 39. Sistema de parking
Desarrolla un programa para gestionar un pequeño parking.

El programa tendrá:

1. Registrar entrada
2. Registrar salida
3. Consultar plazas
4. Salir
El parking dispone de 20 plazas.

El programa debe:

Aumentar las plazas ocupadas al registrar una entrada.
Liberar una plaza al registrar una salida.
Impedir entradas cuando el parking esté completo.
Impedir salidas cuando no haya vehículos.
Mostrar las plazas libres.'''

entradas = 0
plazas_totales = 20
plazas_libres = plazas_totales - entradas


while True:
    print("\nSistema de Parking")
    print("1. Registrar entrada")
    print("2. Registrar salida")
    print("3. Consultar plazas")
    print("4. Salir")

    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        if entradas < plazas_totales:
            entradas += 1
            plazas_libres = plazas_totales - entradas
            print(f"Entrada registrada. Plazas ocupadas: {entradas}, Plazas libres: {plazas_libres}")
        else:
            print("El parking está completo. No se puede registrar más entradas.")

    elif opcion == "2":
        if entradas > 0:
            entradas -= 1
            plazas_libres = plazas_totales - entradas
            print(f"Salida registrada. Plazas ocupadas: {entradas}, Plazas libres: {plazas_libres}")
        else:
            print("No hay vehículos en el parking para registrar una salida.")

    elif opcion == "3":
        print(f"Plazas totales: {plazas_totales}, Plazas ocupadas: {entradas}, Plazas libres: {plazas_libres}")

    elif opcion == "4":
        print("Saliendo del sistema de parking.")
        break

    else:
        print("Opción no válida. Por favor, seleccione una opción del 1 al 4.")
