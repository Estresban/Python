'''Ejercicio 17. Acceso con condiciones
Para acceder a una instalación se deben cumplir las siguientes condiciones:

Tener al menos 18 años.
Tener entrada válida.
Solicita ambos datos y determina si puede acceder.

Ejemplo:

Edad: 20
Entrada válida: si

Acceso permitido
'''

edad = int(input("Introduce tu edad: "))
entrada_valida = input("¿Tienes entrada válida? (si/no): ").strip().lower()
if edad >= 18 and entrada_valida == "si":
    print("Acceso permitido")
elif edad <= 18 or entrada_valida == "no":
    print("Acceso denegado") 
   