'''Ejercicio 28. Contar múltiplos
Solicita un número y muestra todos sus múltiplos entre 1 y 100.

Ejemplo:

Número: 7

7
14
21
28
...
98'''
num = int(input("Número: "))    
for i in range(num, 101, num):
    print(i)
    