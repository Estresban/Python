'''Ejercicio 31. Adivina el número
El programa tendrá almacenado un número secreto.

El usuario debe intentar adivinarlo.

Después de cada intento se mostrará:

El número secreto es mayor.
o:

El número secreto es menor.
Cuando acierte:

¡Correcto!
Cuenta también el número de intentos.'''

import random

numero_secreto = random.randint(1, 100)
intentos = 0

while True:
    intento = int(input("Adivina el número (1-100): "))
    intentos += 1

    if intento < numero_secreto:
        print("El número secreto es mayor.")
    elif intento > numero_secreto:
        print("El número secreto es menor.")
    else:
        print(f"¡Correcto! El número era {numero_secreto}.")
        print(f"Numero de intentos: {intentos}")
        break