'''Ejercicio 34. Contar positivos y negativos
Solicita números hasta introducir 0.

Al finalizar muestra:

Positivos: X
Negativos: Y
Los ceros no deben contabilizarse.'''

positivos = 0
negativos = 0
while True:
    num = int(input("Número: "))
    if num == 0:
        break
    elif num > 0:
        positivos += 1
    else:
        negativos += 1

print(f"Positivos: {positivos}")
print(f"Negativos: {negativos}")
