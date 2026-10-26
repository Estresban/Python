'''Ejercicio 30. Potencias
Solicita una base y un exponente.

Calcula la potencia utilizando un bucle.

No utilices **.

Ejemplo:

Base: 2
Exponente: 5

Resultado: 32'''

base = int(input("Base: "))
exponente = int(input("Exponente: "))
resultado = 1
for i in range(exponente):
    resultado *= base
print(f"Resultado: {resultado}")
