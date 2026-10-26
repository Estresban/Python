'''Ejercicio 38. Registro de alumnos
Solicita el número de alumnos.

Para cada alumno pide:

Nombre.
Nota.
Al finalizar muestra:

Número de aprobados.
Número de suspensos.
Nota media.
Nota más alta.
Nota más baja.'''

num_alumnos = int(input("Número de alumnos: "))
aprobados = 0
suspensos = 0
notas = []

for _ in range(num_alumnos):
    nombre = input("Nombre del alumno: ")
    nota = float(input("Nota del alumno: "))
    notas.append(nota)
    if nota >= 5:
        aprobados += 1
    else:
        suspensos += 1

if notas:
    print(f"Número de aprobados: {aprobados}")
    print(f"Número de suspensos: {suspensos}")
    print(f"Nota media: {sum(notas) / len(notas):.2f}")
    print(f"Nota más alta: {max(notas)}")
    print(f"Nota más baja: {min(notas)}")
else:
    print("No se han introducido notas.")
    