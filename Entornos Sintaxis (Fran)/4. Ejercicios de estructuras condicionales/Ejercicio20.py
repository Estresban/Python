'''Ejercicio 20. Precio de entrada
Un museo tiene estas tarifas:

Menores de 5 años → Gratis
5-12 años         → 5 €
13-17 años        → 8 €
Adultos           → 12 €
Mayores de 65     → 6 €
Solicita la edad y muestra el precio.'''

edad = int(input("Introduce la edad: "))

if edad < 5:
    print("Gratis")
elif edad <= 12:
    print("5 €")
elif edad <= 17:
    print("8 €")
elif edad <= 65:
    print("12 €")
else:
    print("6 €")
