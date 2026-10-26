'''Ejercicio 35. Máximo y mínimo
Solicita números hasta que el usuario introduzca 0.

Al finalizar muestra:

Número mayor.
Número menor.
No utilices max() ni min().'''

num = int(input("Introduce un número (0 para terminar): "))
if num == 0:
    print("No se han introducido números.")
else:
    max_num = num
    min_num = num

    while True:
        num = int(input("Introduce un número (0 para terminar): "))
        if num == 0:
            break
        if num > max_num:
            max_num = num
        if num < min_num:
            min_num = num

    print(f"Número mayor: {max_num}")
    print(f"Número menor: {min_num}")
