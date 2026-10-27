'''Reto 40. Máquina expendedora
Simula una máquina expendedora.

Productos:

1. Agua       1.00 €
2. Refresco   1.50 €
3. Café       1.20 €
4. Snack      1.80 €
El programa debe:

Mostrar el menú.
Solicitar producto.
Solicitar dinero.
Comprobar si es suficiente.
Calcular el cambio.
Mostrar un mensaje de compra.
Repetir el proceso hasta seleccionar salir.'''

agua = 1.00
refresco = 1.50
cafe = 1.20
snack = 1.80

while True:
    print("\nMáquina Expendedora")
    print("1. Agua       1.00 €")
    print("2. Refresco   1.50 €")
    print("3. Café       1.20 €")
    print("4. Snack      1.80 €")
    print("5. Salir")

    opcion = input("Seleccione un producto (1-5): ")

    if opcion == "5":
        print("Saliendo de la máquina expendedora.")
        break

    if opcion not in ["1", "2", "3", "4"]:
        print("Opción no válida. Por favor, seleccione una opción del 1 al 5.")
        continue

    cantidad = float(input("Ingrese la cantidad de dinero: "))

    if opcion == "1":
        precio = agua
        producto = "Agua"
    elif opcion == "2":
        precio = refresco
        producto = "Refresco"
    elif opcion == "3":
        precio = cafe
        producto = "Café"
    elif opcion == "4":
        precio = snack
        producto = "Snack"

    if cantidad >= precio:
        cambio = cantidad - precio
        print(f"Compra realizada: {producto}. Cambio: {cambio:.2f} €")
    else:
        print(f"Dinero insuficiente para comprar {producto}.")
        print(f"Precio: {precio:.2f} €, Dinero ingresado: {cantidad:.2f} €")
        print(f"Te faltan: {precio - cantidad:.2f} €")
