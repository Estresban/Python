'''Ejercicio 13. Año bisiesto
Solicita un año e indica si es bisiesto.

Un año es bisiesto cuando:

Es divisible entre 4.
No es divisible entre 100, salvo que también sea divisible entre 400.
Ejemplos:

2024 → Bisiesto
2025 → No bisiesto
2000 → Bisiesto
1900 → No bisiesto'''

año = int(input("Introduce un año: "))
if (año % 4 == 0 and año % 100 != 0) or (año % 400 == 0):
    print("El año es bisiesto.")
else:
    print("El año no es bisiesto.") 