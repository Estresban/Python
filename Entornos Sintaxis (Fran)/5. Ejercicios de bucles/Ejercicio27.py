'''Ejercicio 27. Suma de pares
Calcula la suma de todos los números pares entre 1 y 100.'''
suma = 0
for i in range(1, 101):
    if i % 2 == 0:
        suma += i
print(suma)
