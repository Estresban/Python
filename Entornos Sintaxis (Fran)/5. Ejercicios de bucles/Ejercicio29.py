'''Ejercicio 29. Factorial
Solicita un número entero positivo y calcula su factorial.

Ejemplo:

5! = 120
No utilices ninguna función de librería.'''

num = int(input("Número: "))
factorial = 1
for i in range(1, num + 1):
    factorial *= i
print(f"{num}! = {factorial}")
