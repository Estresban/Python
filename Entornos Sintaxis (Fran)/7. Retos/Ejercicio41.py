'''Reto 41. Sistema de votación
Crea un sistema de votación sencillo.

Las opciones serán:

1. Python
2. Java
3. JavaScript
4. C++
0. Finalizar
Los usuarios podrán votar hasta seleccionar 0.

Al finalizar muestra:

Votos de cada opción.
Total de votos.
Opción ganadora.'''

votos = {
    "Python": 0,
    "Java": 0,
    "JavaScript": 0,
    "C++": 0
}

total_votos = 0

while True:
    print("\nSistema de Votación")
    print("1. Python")
    print("2. Java")
    print("3. JavaScript")
    print("4. C++")
    print("0. Finalizar")

    opcion = input("Seleccione una opción (0-4): ")

    if opcion == "0":
        break

    if opcion not in ["1", "2", "3", "4"]:
        print("Opción no válida. Por favor, seleccione una opción del 0 al 4.")
        continue

    if opcion == "1":
        votos["Python"] += 1
        total_votos += 1
    elif opcion == "2":
        votos["Java"] += 1
        total_votos += 1
    elif opcion == "3":
        votos["JavaScript"] += 1
        total_votos += 1
    elif opcion == "4":
        votos["C++"] += 1
        total_votos += 1

# Mostrar resultados
print("\nResultados de la votación:")
for opcion, cantidad in votos.items():
    print(f"{opcion}: {cantidad} votos")

print(f"Total de votos: {total_votos}")

if total_votos > 0:
    ganadora = max(votos, key=votos.get)
    print(f"Opción ganadora: {ganadora}")

