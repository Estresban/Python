'''Ejercicio 6. Tiempo
Solicita una cantidad de segundos y conviértela a:

Horas.
Minutos.
Segundos.
Ejemplo:

Segundos: 3672

1 hora
1 minuto
12 segundos'''

segundos = int(input("Introduce una cantidad de segundos: "))

horas = segundos // 3600
segundos %= 3600
minutos = segundos // 60
segundos %= 60

print(f"{horas} horas")
print(f"{minutos} minutos")
print(f"{segundos} segundos")