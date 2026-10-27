'''Ejercicio 33. Suma hasta cero
Solicita números al usuario hasta que introduzca 0.

Al finalizar muestra:

Cantidad de números introducidos.
Suma.
Media.
Ejemplo:

Número: 10
Número: 20
Número: 30
Número: 0

Cantidad: 3
Suma: 60
Media: 20'''

cantidad = 0
suma = 0
while True:
    num = int(input("Número: "))
    if num == 0:
        break
    cantidad += 1
    suma += num

if cantidad > 0:
    media = suma / cantidad
else:
    media = 0

print(f"Cantidad: {cantidad}")
print(f"Suma: {suma}")
print(f"Media: {media}")
