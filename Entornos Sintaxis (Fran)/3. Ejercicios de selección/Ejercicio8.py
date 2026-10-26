'''Ejercicio 8. Número positivo o negativo
Solicita un número e indica si es:

Positivo.
Negativo.
Cero.'''

numero = int(input("Introduce un número: "))

if numero > 0:
    print("El número es positivo.")
elif numero < 0:
    print("El número es negativo.")
else:
    print("El número es cero.") 
