'''Ejercicio 10. Mayor de dos números
Solicita dos números e indica:

Cuál es mayor.
Si son iguales.
Ejemplo:

Número 1: 15
Número 2: 20

El segundo número es mayor.'''

numero1 = int(input("Introduce el primer número: "))
numero2 = int(input("Introduce el segundo número: "))

if numero1 > numero2:
    print("El primer número es mayor.")
elif numero2 > numero1:
    print("El segundo número es mayor.")
else:
    print("Los dos números son iguales.")   
    