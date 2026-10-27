'''Ejercicio 37. Cajero automático
Crea un pequeño cajero automático.

El saldo inicial será:

saldo = 1000
El menú será:

1. Consultar saldo
2. Ingresar dinero
3. Retirar dinero
4. Salir
Condiciones:

No se puede retirar más dinero del disponible.
No se pueden ingresar cantidades negativas.
El menú debe repetirse hasta seleccionar 4.'''

saldo = 1000
while True:
    print("===== CAJERO AUTOMÁTICO =====")
    print("1. Consultar saldo")
    print("2. Ingresar dinero")
    print("3. Retirar dinero")
    print("4. Salir")

    opcion = input("Selecciona una opción: ")

    if opcion == "4":
        print("Saliendo del cajero automático.")
        break
    elif opcion == "1":
        print(f"Saldo actual: {saldo}€")
    elif opcion == "2":
        cantidad = float(input("Introduce la cantidad a ingresar: "))
        if cantidad < 0:
            print("Error: No se pueden ingresar cantidades negativas.")
        else:
            saldo += cantidad
            print(f"Has ingresado {cantidad}€. Nuevo saldo: {saldo}€")
    elif opcion == "3":
        cantidad = float(input("Introduce la cantidad a retirar: "))
        if cantidad < 0:
            print("Error: No se pueden retirar cantidades negativas.")
        elif cantidad > saldo:
            print("Error: No se puede retirar más dinero del disponible.")
        else:
            saldo -= cantidad
            print(f"Has retirado {cantidad}€. Nuevo saldo: {saldo}€")
    else:
        print("Opción no válida. Por favor, selecciona una opción del menú.")
        