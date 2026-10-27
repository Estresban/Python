'''Ejercicio 18. Clasificación por edad
Solicita la edad e indica:

0-12     → Niño/a
13-17    → Adolescente
18-64    → Adulto/a
65+      → Persona mayor
Controla valores negativos.

'''

edad = int(input("Introduce la edad: "))

if edad <= 12:
    print("Niño/a")
elif edad <= 17:
    print("Adolescente")
elif edad <= 64:
    print("Adulto/a")
else:
    print("Persona mayor")