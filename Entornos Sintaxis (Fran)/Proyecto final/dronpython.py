'''Proyecto: Control de vuelo simulado
En este proyecto vamos a aplicar las estructuras de control a un escenario relacionado con una de las aplicaciones que veremos posteriormente: la programación de drones con Python.

No será necesario disponer todavía de un dron físico.

El programa simulará el control básico de un dron.

Requisitos
El programa deberá comenzar mostrando:

=========================
     DRON PYTHON
=========================
Después mostrará un menú:

1. Despegar
2. Avanzar
3. Retroceder
4. Girar a la derecha
5. Girar a la izquierda
6. Consultar batería
7. Aterrizar
0. Salir
Condiciones
El dron comenzará con:

bateria = 100
Y estará inicialmente en tierra.

El programa deberá controlar:

Despegue
El dron solamente podrá despegar si:

batería >= 20%
Movimiento
Cada movimiento consumirá un porcentaje de batería.

Por ejemplo:

Avanzar → -5%
Retroceder → -5%
Girar → -2%
Batería
Cuando la batería sea inferior al 20%:

ADVERTENCIA: batería baja
Cuando llegue al 0%:

Batería agotada.
Aterrizaje de emergencia.
Aterrizaje
El dron deberá estar en vuelo para poder aterrizar.

Menú
El menú debe repetirse mediante un while.

Condiciones
Utiliza if, elif y else para controlar las diferentes opciones.

Repeticiones
Utiliza bucles cuando sean necesarios.

Ejemplo de ejecución
=========================
     DRON PYTHON
=========================

Batería: 100%
Estado: EN TIERRA

1. Despegar
2. Avanzar
3. Retroceder
4. Girar derecha
5. Girar izquierda
6. Consultar batería
7. Aterrizar
0. Salir

Opción: 1

Dron despegando...

Opción: 2

Avanzando...
Batería: 95%

Opción: 4

Girando a la derecha...
Batería: 93%

Opción: 6

Batería: 93%

Opción: 7

Aterrizando...

Opción: 0

Programa finalizado.
⭐ Ampliación
Para alumnado que termine antes:

Añade coordenadas (x, y) para representar la posición.
Haz que avanzar modifique la coordenada.
Permite girar 90 grados.
Registra los movimientos realizados.
Añade un modo de vuelo automático.
Permite introducir una ruta.
Comprueba que la batería sea suficiente antes de ejecutar una ruta.
Añade un límite de distancia.
Simula obstáculos.
Añade un aterrizaje automático cuando la batería sea baja.'''


