'''Ejercicio 25. Tabla de multiplicar
Solicita un número y muestra su tabla de multiplicar del 1 al 10.

Ejemplo:

Número: 7

7 x 1 = 7
7 x 2 = 14
...
7 x 10 = 70'''
num = int(input("Número: "))
for i in range(1, 11):
    print(f"{num} x {i} = {num * i}")
