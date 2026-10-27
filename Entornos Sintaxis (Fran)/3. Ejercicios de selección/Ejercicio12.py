'''Ejercicio 12. Calificación
Solicita una nota entre 0 y 10.

Muestra:

Nota	Resultado
< 5	Suspenso
5 - 6.9	Aprobado
7 - 8.9	Notable
9 - 10	Sobresaliente
Controla también que la nota esté dentro del rango válido.'''

nota = float(input("Introduce una nota entre 0 y 10: "))
if nota < 0 or nota > 10:
    print("La nota no es válida.")  
else:
    if nota < 5:
        print("Suspenso")
    elif nota < 7:
        print("Aprobado")
    elif nota < 9:
        print("Notable")
    else:
        print("Sobresaliente")
