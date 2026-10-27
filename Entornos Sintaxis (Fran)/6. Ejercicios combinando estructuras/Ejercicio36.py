'''Ejercicio 36. Menú de operaciones
Crea un menú que se repita hasta seleccionar la opción 0.

===== CALCULADORA =====

1. Sumar
2. Restar
3. Multiplicar
4. Dividir
0. Salir
Cada opción debe solicitar los datos necesarios.'''

while True:
    print("===== CALCULADORA =====")
    print("1. Sumar")
    print("2. Restar")
    print("3. Multiplicar")
    print("4. Dividir")
    print("0. Salir")

    opcion = input("Selecciona una opción: ")

    if opcion == "0":
        print("Saliendo del programa.")
        break
    elif opcion in ["1", "2", "3", "4"]:
        num1 = float(input("Introduce el primer número: "))
        num2 = float(input("Introduce el segundo número: "))

        if opcion == "1":
            resultado = num1 + num2
            print(f"Resultado: {resultado}")
        elif opcion == "2":
            resultado = num1 - num2
            print(f"Resultado: {resultado}")
        elif opcion == "3":
            resultado = num1 * num2
            print(f"Resultado: {resultado}")
        elif opcion == "4":
            if num2 != 0:
                resultado = num1 / num2
                print(f"Resultado: {resultado}")
            else:
                print("Error: No se puede dividir entre cero.")
    else:
        print("Opción no válida. Por favor, selecciona una opción del menú.")
