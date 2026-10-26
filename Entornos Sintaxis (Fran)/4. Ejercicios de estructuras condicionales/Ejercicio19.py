'''Ejercicio 19. Horario de apertura
Solicita una hora entre 0 y 23.

El establecimiento está abierto:

09:00 - 14:00
16:00 - 20:00
Indica si está abierto o cerrado.

'''
hora = int(input("Introduce una hora (0-23): "))
if 9 <= hora < 14 or 16 <= hora < 20:
    print("Está abierto.")
else:
    print("Está cerrado.")   
    