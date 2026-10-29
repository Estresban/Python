'''Ejercicio 3. Entradas para un parque de atracciones
Enunciado
Un parque de atracciones quiere crear un programa para calcular cuánto debe pagar una persona por su entrada.

El programa debe pedir los siguientes datos:

Nombre del visitante.
Edad del visitante.
Si quiere añadir un menú de comida. El usuario responderá s si quiere menú o n si no lo quiere.
El precio de la entrada depende de la edad:

Menores de 4 años: entrada gratuita.
Desde los 4 hasta los 12 años, ambos incluidos: descuento del 30 % sobre el precio normal.
Mayores de 12 años y menores de 65: pagan el precio normal.
Personas de 65 años o más: descuento del 20 % sobre el precio normal.
El precio normal de la entrada es de 30 €.

Si el visitante quiere menú, se añadirán 8 € al importe final. El precio del menú no tiene descuento.

Requisitos del programa
Solicita el nombre y la edad del visitante.
Calcula el precio de la entrada según la edad.
Pregunta si quiere añadir un menú.
Si responde s, añade 8 € al precio calculado.
Si responde n, no añade ningún importe.
Muestra el nombre del visitante, el precio de la entrada, el coste del menú y el importe total que debe pagar.
Condiciones: resuelve las decisiones utilizando únicamente if y else. No utilices elif. Puedes utilizar condicionales anidados, es decir, escribir un if dentro de un else.

Para este ejercicio, puedes suponer que el usuario introduce una edad válida y responde s o n cuando se le pregunta por el menú.

Ejemplo orientativo 1
Introduce tu nombre: Lucía
Introduce tu edad: 10
¿Quieres añadir un menú por 8 euros? (s/n): s

Visitante: Lucía
Precio de la entrada: 21.00 €
Precio del menú: 8.00 €
Total a pagar: 29.00 €
Ejemplo orientativo 2
Introduce tu nombre: Manuel
Introduce tu edad: 70
¿Quieres añadir un menú por 8 euros? (s/n): n

Visitante: Manuel
Precio de la entrada: 24.00 €
Precio del menú: 0.00 €
Total a pagar: 24.00 €
Ampliación opcional
Añade una pregunta para saber si el visitante quiere comprar una foto de recuerdo por 5 €.

Si responde s, añade 5 € al total.
Si responde n, no añadas nada.
Actualiza el resumen final para mostrar el precio de la foto y el nuevo total.'''

