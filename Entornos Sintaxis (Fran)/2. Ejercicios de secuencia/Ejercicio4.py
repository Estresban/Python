'''Ejercicio 4. Conversor de temperatura
Solicita una temperatura en grados centigrados y conviértela a Fahrenheit.

Fórmula: F = C * 9 / 5 + 32'''

# centrigrados = int(input("Temperatura en º centígrados: "))
# print(f"La temperatura en º Fahrenheit es: {centrigrados * 9 / 5 + 32}")

def centigrados_a_fahrenheit(centigrados):
    return (centigrados * 9/5) + 32


def fahrenheit_a_centigrados(fahrenheit):
    return (fahrenheit - 32) * 5/9


print("CONVERSOR DE TEMPERATURA")
print("1. centigrados a Fahrenheit")
print("2. Fahrenheit a centigrados")

opcion = input("Elige una conversión (1 o 2): ")

if opcion == "1":
    centigrados = float(input("Introduce la temperatura en º Centigrados: "))
    resultado = centigrados_a_fahrenheit(centigrados)
    print(f"{centigrados} °C son {resultado:.2f} °F")

elif opcion == "2":
    fahrenheit = float(input("Introduce la temperatura en Fahrenheit: "))
    resultado = fahrenheit_a_centigrados(fahrenheit)
    print(f"{fahrenheit} °F son {resultado:.2f} °C")

else:
    print("Hay que ser tonto para elegir una opción no válida.")