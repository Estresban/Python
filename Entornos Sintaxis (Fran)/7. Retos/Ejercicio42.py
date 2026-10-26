'''Reto 42. Juego de preguntas
Crea un pequeño concurso de preguntas.

El programa deberá realizar al menos cinco preguntas.

Por cada pregunta:

Mostrar el enunciado.
Mostrar varias opciones.
Comprobar la respuesta.
Incrementar la puntuación si es correcta.
Al finalizar:

Puntuación: 4/5'''

preguntas = [
    {
        "enunciado": "¿Cuál es el lenguaje de programación más utilizado en el desarrollo web?",
        "opciones": ["Python", "JavaScript", "Java", "C++"],
        "respuesta_correcta": "JavaScript"
    },
    {
        "enunciado": "¿Qué paradigma de programación se caracteriza por el uso de clases y objetos?",
        "opciones": ["Funcional", "Imperativo", "Orientado a objetos", "Lógico"],
        "respuesta_correcta": "Orientado a objetos"
    },
    {
        "enunciado": "¿Cuál es la capital de Francia?",
        "opciones": ["Londres", "Berlín", "París", "Roma"],
        "respuesta_correcta": "París"
    },
    {
        "enunciado": "¿Qué lenguaje de programación es conocido por su sintaxis simple y legible?",
        "opciones": ["C++", "Python", "Java", "JavaScript"],
        "respuesta_correcta": "Python"
    },
    {
        "enunciado": "¿Cuál es la base de datos relacional más utilizada en aplicaciones empresariales?",
        "opciones": ["MongoDB", "PostgreSQL", "Oracle Database", "SQLite"],
        "respuesta_correcta": "Oracle Database"
    }
]

puntuacion = 0

for pregunta in preguntas:
    print("\n" + pregunta["enunciado"])
    for i, opcion in enumerate(pregunta["opciones"], start=1):
        print(f"{i}. {opcion}")

    respuesta = input("Seleccione la opción correcta (1-4): ")

    if respuesta not in ["1", "2", "3", "4"]:
        print("Opción no válida. Por favor, seleccione una opción del 1 al 4.")
        continue

    if pregunta["opciones"][int(respuesta) - 1] == pregunta["respuesta_correcta"]:
        print("¡Respuesta correcta!")
        puntuacion += 1
        print(f"¡Puntuacion: {puntuacion}!")
    else:
        print(f"Respuesta incorrecta. La respuesta correcta es: {pregunta['respuesta_correcta']}")
        print(f"Tu puntuación es: {puntuacion}/{len(preguntas)}")