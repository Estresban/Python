'''Ejercicio 24. Cuenta atrás
Solicita un número y realiza una cuenta atrás hasta llegar a cero.

Ejemplo:

Número: 5

5
4
3
2
1
0'''

num = int(input("Número: "))
for i in range(num, -1, -1):
    print(i)

