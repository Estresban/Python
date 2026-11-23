# SmartSpeaker: diseñar y proteger un objeto

## Contexto

Una empresa está desarrollando una aplicación para controlar altavoces
inteligentes. Antes de conectar los dispositivos a una aplicación
gráfica o a una API, necesita implementar la clase Python que representa
cada altavoz.

La primera versión funciona, pero permite situaciones incoherentes:
altavoces sin nombre, volúmenes negativos y estados que no tienen
sentido.

Tu trabajo consiste en analizar el problema, diseñar una interfaz
pública y desarrollar una clase que controle sus propios datos.

### Restricciones del laboratorio

-   Solo se implementará una clase: `Altavoz`.
-   La validación se realizará con las herramientas de Python
    estudiadas.
-   La IA podrá ayudarte a analizar reglas y revisar el diseño, pero
    tendrás que verificar personalmente el comportamiento.

---

## Parte 1. Analizamos el problema

### 1.1. Primera versión

Crea un archivo `altavoz.py` con la siguiente implementación:

``` python
class Altavoz:
    def __init__(self, nombre, volumen):
        self.nombre = nombre
        self.volumen = volumen
        self.encendido = False

    def encender(self):
        self.encendido = True

    def apagar(self):
        self.encendido = False
```

Crea un archivo `main.py`:

``` python
from altavoz import Altavoz


def main() -> None:
    altavoz = Altavoz("Salón", 30)

    print(altavoz.nombre)
    print(altavoz.volumen)
    print(altavoz.encendido)

    altavoz.nombre = ""
    altavoz.volumen = -50
    altavoz.encendido = "quizá"

    print(altavoz.nombre)
    print(altavoz.volumen)
    print(altavoz.encendido)


if __name__ == "__main__":
    main()
```

Ejecuta el programa y observa el resultado.

### 1.2. Identificamos los problemas

Responde a estas preguntas:

-   ¿Qué ocurre cuando el nombre está vacío?
-   ¿Qué ocurre cuando el volumen es negativo?
-   ¿Podemos asignar un texto al atributo `encendido`?
-   ¿Quién debería ser responsable de evitar estos valores: el código
    que utiliza la clase o la propia clase?
-   ¿Qué problemas podría provocar que cualquier parte del programa
    modificase directamente el estado del altavoz?

### 1.3. Definimos las reglas de negocio

Completa la siguiente tabla antes de modificar el código.

| Elemento | Regla que debe cumplir | Ejemplo inválido |
|---|---|---|
| Nombre | Debe ser una cadena de texto no vacía ni formada solo por espacios | `""` o `"   "` |
| Volumen | Debe ser un número entero entre 0 y 100, ambos incluidos | `-5`, `101` o `25.5` |
| Estado | Solo puede representar si el altavoz está encendido o apagado | `"quizá"` |
| Encendido | Debe cambiarse mediante una operación del objeto | `altavoz.encendido = True` |

El último ejemplo representa un problema de diseño: queremos que el
resto del programa utilice operaciones como `encender()` y `apagar()`,
en lugar de modificar directamente el estado.

---

## Parte 2. Diseñamos la interfaz pública

Antes de programar, decide qué elementos podrá utilizar directamente
otro componente de la aplicación y cuáles estarán destinados al
funcionamiento interno de la clase.

Recuerda las convenciones de Python:

| Escritura | Significado | Ejemplo |
|---|---|---|
| `nombre` | Elemento público | `altavoz.nombre` |
| `_nombre` | Elemento interno por convención | `self._volumen` |
| `__nombre` | Activa el *name mangling* | `self.__codigo` |
| `__nombre__` | Nombre especial de Python o de una API | `__init__` |

### 2.1. Diseña la interfaz

| Elemento | ¿Público o interno? | ¿Cómo debería utilizarse? |
|---|---|---|
| Nombre del altavoz | Público (propiedad `nombre`) | Consultar y modificar con validación |
| Volumen | Público (propiedad `volumen`) | Consultar y modificar con validación |
| Estado de encendido | Interno (`_encendido`) | Consultar mediante una propiedad, pero no modificar directamente |
| Operación para encender | Público (`encender()`) | Cambiar el estado a encendido |
| Operación para apagar | Público (`apagar()`) | Cambiar el estado a apagado |

### 2.2. Justifica tus decisiones

Explica brevemente:

-   Por qué el volumen necesita validación.

El volumen necesita validación para evitar valores incorrectos, como números negativos, mayores de 100, decimales o tipos de datos que no sean enteros. Así garantizamos que el altavoz siempre tenga un volumen válido.


-   Por qué no queremos que se modifique directamente el estado de encendido.

Porque queremos que el altavoz controle cuándo se enciende y se apaga mediante los métodos encender() y apagar(). De esta manera, el estado no se modifica libremente y se mantiene el comportamiento previsto del objeto.


-   Qué diferencia existe entre utilizar `_volumen` y utilizar una propiedad pública llamada `volumen`.

_volumen es el atributo interno donde se almacena el valor del volumen. La propiedad pública volumen permite consultar y modificar ese valor de forma controlada, aplicando las validaciones necesarias antes de aceptar un cambio.

No se trata de ocultar los datos por ocultarlos: se trata de diseñar una
interfaz que permita utilizar el objeto sin saltarse sus reglas.

---

## Parte 3. Implementamos la clase

Modifica `altavoz.py` para cumplir los requisitos siguientes.

### Requisito 1. Validar el nombre

-   Debe ser una cadena de texto.
-   No puede estar vacío ni contener únicamente espacios.
-   Se eliminarán los espacios exteriores antes de almacenar el nombre.

### Requisito 2. Validar el volumen

-   Debe ser un número entero.
-   Su valor estará comprendido entre 0 y 100, ambos incluidos.
-   La misma validación debe aplicarse tanto al crear el objeto como al
    modificar el volumen.

### Requisito 3. Controlar el estado

-   Un altavoz nuevo comienza apagado.
-   El estado podrá consultarse mediante `altavoz.estado`.
-   El resto del programa no debe poder cambiarlo mediante una
    asignación ordinaria a `altavoz.estado`.
-   El método `encender()` permitirá encender el dispositivo.
-   El método `apagar()` permitirá apagarlo.

### Requisito 4. Mantener una interfaz clara

El código que utiliza la clase debería poder escribir:

``` python
altavoz = Altavoz("Salón", 30)

print(altavoz.nombre)
print(altavoz.volumen)
print(altavoz.estado)

altavoz.volumen = 50
altavoz.encender()
altavoz.apagar()
```

No debería necesitar acceder a los atributos internos para utilizar las
operaciones habituales.

---

## Parte 4. Comprobamos el comportamiento

Crea un archivo `pruebas_manuales.py`. No utilizaremos todavía `pytest`:
en esta actividad queremos comprobar manualmente los resultados y
preparar el terreno para automatizarlos pronto.

### 4.1. Pruebas válidas

Comprueba las siguientes situaciones:

| ID | Operación | Resultado esperado |
|---|---|---|
| V01 | Crear un altavoz con nombre `"Salón"` y volumen 30 | Se crea correctamente |
| V02 | Consultar el nombre | Devuelve `"Salón"` |
| V03 | Consultar el volumen | Devuelve 30 |
| V04 | Consultar el estado inicial | Devuelve `"apagado"` |
| V05 | Cambiar el volumen a 50 | Se acepta |
| V06 | Cambiar el volumen a 0 | Se acepta |
| V07 | Cambiar el volumen a 100 | Se acepta |
| V08 | Ejecutar `encender()` | El estado pasa a `"encendido"` |
| V09 | Ejecutar `apagar()` | El estado pasa a `"apagado"` |
| V10 | Crear un altavoz con nombre `"  Cocina  "` | Se almacena `"Cocina"` |

### 4.2. Pruebas inválidas

Comprueba cada caso por separado.

| ID | Operación | Resultado esperado |
|---|---|---|
| I01 | Crear un altavoz con nombre `""` | `ValueError` |
| I02 | Crear un altavoz con nombre `"   "` | `ValueError` |
| I03 | Crear un altavoz con nombre `25` | `ValueError` |
| I04 | Crear un altavoz con volumen `-1` | `ValueError` |
| I05 | Crear un altavoz con volumen `101` | `ValueError` |
| I06 | Asignar `altavoz.volumen = 25.5` | `ValueError` |
| I07 | Asignar `altavoz.volumen = "alto"` | `ValueError` |
| I08 | Asignar `altavoz.estado = "encendido"` | `AttributeError` |

No es necesario probar todos los casos con un único programa. Puedes
ejecutar cada comprobación por separado para identificar fácilmente la
excepción que se produce.

### 4.3. Registra los resultados

| ID | Resultado obtenido | ¿Coincide con el esperado? |
|---|---|---|
| V01 | Se crea el altavoz correctamente con nombre "Salón", volumen 30 y estado apagado. | Sí |
| V02 | Se consulta correctamente el nombre "Salón". | Sí |
| V03 | Se consulta correctamente el volumen 30. | Sí |
| V04 | El estado inicial es "Apagado". | Sí |
| V05 | El volumen se cambia correctamente a 50. | Sí |
| V06 | El volumen se cambia correctamente a 0. | Sí |
| V07 | El volumen se cambia correctamente a 100. | Sí |
| V08 | El altavoz se enciende y su estado pasa a "Encendido". | Sí |
| V09 | El altavoz se apaga y su estado pasa a "Apagado". | Sí |
| V10 | El nombre "  Cocina  " se guarda sin espacios exteriores como "Cocina". | Sí |
| I01 | Se rechaza el nombre vacío y se lanza ValueError. | Sí |
| I02 | Se rechaza el nombre compuesto solo por espacios y se lanza ValueError. | Sí |
| I03 | Se rechaza un nombre que no es una cadena y se lanza ValueError. | Sí |
| I04 | Se rechaza el volumen -1 y se lanza ValueError. | Sí |
| I05 | Se rechaza el volumen 101 y se lanza ValueError. | Sí |
| I06 | Se rechaza el volumen decimal 25.5 y se lanza ValueError. | Sí |
| I07 | Se rechaza el volumen de texto "alto" y se lanza ValueError. | Sí |
| I08 | Se impide modificar directamente el estado y se lanza AttributeError. | Sí |

Si una prueba falla, no cambies inmediatamente el resultado esperado para hacerla coincidir con el programa. Primero investiga si el error está en la implementación.

---


## Parte 5. Revisamos las recomendaciones de la IA

En esta actividad, utiliza la revisión de IA que se incluye a continuación como apoyo para analizar tu clase. No copies las recomendaciones sin comprobarlas: contrástalas con los requisitos del laboratorio y, cuando sea posible, con una prueba manual.

### Prompt utilizado para revisar la clase

Estoy desarrollando una clase Altavoz en Python.
### La clase debe cumplir estas reglas:
- El nombre debe ser una cadena no vacía ni formada solo por espacios.
- Se eliminan los espacios exteriores del nombre.
- El volumen debe ser un entero entre 0 y 100, incluidos.
- El estado inicial debe ser "apagado".
- El estado solo se modifica mediante los métodos encender() y apagar().
- El nombre y el volumen se consultan mediante propiedades.
- Los valores inválidos deben provocar ValueError.
- El estado no debe disponer de un setter público.

### Revisa el código que te proporciono.
1. Comprueba cada requisito por separado.
2. Busca errores de validación.
3. Comprueba que los setters no provocan recursión.
4. Señala posibles problemas de diseño.
5. Propón casos de prueba que todavía no haya comprobado.
No reescribas la clase completa.
No afirmes que el código funciona sin haberlo ejecutado.
No introduzcas listas, diccionarios, herencia ni conceptos que todavía no hemos estudiado.


``` python
class Altavoz:
    def __init__(self, nombre, volumen):
        self.nombre = nombre
        self.volumen = volumen
        self._encendido = False
        
    @property
    def nombre(self):
        return self._nombre

    @property
    def volumen(self):
        return self._volumen
        
    @property
    def estado(self):
        return "Encendido" if self._encendido else "Apagado"
    

    @nombre.setter
    def nombre(self, nuevo_nombre):
        if not isinstance(nuevo_nombre,str):
            raise ValueError("El nombre debe ser cadena de texto")
        if not nuevo_nombre.strip():
                    raise ValueError("El nombre no puede estar vacio")
        self._nombre = nuevo_nombre.strip()
        
    @volumen.setter
    def volumen(self, nuevo_volumen):
        if not isinstance(nuevo_volumen,int):
            raise ValueError("El volumen debe ser un numero entero")
        if nuevo_volumen < 0 or nuevo_volumen > 100:
            raise ValueError("El volumen debe estar entre 0 y 100")    
        self._volumen = nuevo_volumen
        
        
    def encender(self):
        self._encendido = True

    def apagar(self):
        self._encendido = False

```

### Prompt devuelto por IA


Tu código está bastante bien estructurado. Has utilizado correctamente @property, setters, atributos privados por convención (_nombre, _volumen, _encendido) y métodos para cambiar el estado.

Voy a revisar cada requisito por separado, sin reescribir la clase completa ni introducir conceptos nuevos.
1. Comprobación de requisitos
| Requisito | Resultado | Observación |
|---|---|---|
| Nombre debe ser una cadena | ✅ Cumple | Compruebas `isinstance(nuevo_nombre, str)`. |
| Nombre no puede estar vacío ni contener solo espacios | ✅ Cumple | `strip()` permite detectar ambos casos. |
| Se eliminan espacios exteriores del nombre | ✅ Cumple | Guardas `nuevo_nombre.strip()` en `_nombre`. |
| Volumen debe ser entero | ⚠️ Parcial | `isinstance(x, int)` también acepta `bool` (`True` y `False`). |
| Volumen entre 0 y 100, incluidos | ✅ Cumple | Controlas los límites correctamente. |
| Estado inicial apagado | ✅ Cumple | `_encendido = False`. |
| Estado solo se cambia con `encender()` y `apagar()` | ✅ Cumple en la interfaz pública | No has creado un setter para estado. |
| Nombre se consulta mediante propiedad | ✅ Cumple | `@property nombre`. |
| Volumen se consulta mediante propiedad | ✅ Cumple | `@property volumen`. |
| Valores inválidos generan `ValueError` | ✅ Cumple en las validaciones que has escrito | Hay un caso especial con `bool` en el volumen. |
| Los setters no provocan recursión | ✅ Cumple | Escribes en atributos internos, no en las propiedades. |


2. Errores y detalles de validación
A. El nombre está correctamente validado
Esta parte está bien:
if not isinstance(nuevo_nombre,str):    raise ValueError("El nombre debe ser cadena de texto")if not nuevo_nombre.strip():    raise ValueError("El nombre no puede estar vacio")self._nombre = nuevo_nombre.strip()



Tu código cubre correctamente:
- 123 → rechazado.
- "" → rechazado.
- "   " → rechazado.
- "  Sony  " → guardado como "Sony".
No necesitas modificar la lógica de validación del nombre.

Como detalle de estilo, podrías poner un espacio después de la coma en isinstance(nuevo_nombre, str), pero es solo legibilidad, no un error.

B. El volumen tiene un caso especial que debes corregir
Tu validación actual:
if not isinstance(nuevo_volumen,int):    raise ValueError("El volumen debe ser un numero entero")



El problema es que en Python bool es un tipo relacionado con int. Por eso:
isinstance(True, int)   # Trueisinstance(False, int)  # True



Esto significa que True pasaría tu validación y se almacenaría como volumen True (que se comporta numéricamente como 1), y False como 0.

Como tu requisito dice que el volumen debe ser un entero, probablemente no quieres permitir valores booleanos.

Una solución sencilla, utilizando algo que ya conoces, es:
if isinstance(nuevo_volumen, bool) or not isinstance(nuevo_volumen, int):    raise ValueError("El volumen debe ser un numero entero")



Así rechazas True y False, pero sigues aceptando enteros.

El resto de tu validación de límites está bien:
if nuevo_volumen < 0 or nuevo_volumen > 100:    raise ValueError("El volumen debe estar entre 0 y 100")




3. ¿Los setters provocan recursión?
No. Los has hecho correctamente.

Por ejemplo, tu setter de nombre:
@nombre.setterdef nombre(self, nuevo_nombre):    ...    self._nombre = nuevo_nombre.strip()



Y tu setter de volumen:
@volumen.setterdef volumen(self, nuevo_volumen):    ...    self._volumen = nuevo_volumen



No hay recursión.

¿Por qué?

Porque estás asignando a self._nombre y self._volumen, que son atributos internos diferentes de las propiedades nombre y volumen.

Un error típico sería hacer esto dentro del setter:
self.nombre = nuevo_nombre



Eso volvería a llamar al setter de nombre una y otra vez, provocando recursión.

En tu caso, has evitado ese problema correctamente.

4. Revisión del estado
Tu propiedad:
@propertydef estado(self):    return "Encendido" if self._encendido else "Apagado"



Y tus métodos:
def encender(self):    self._encendido = Truedef apagar(self):    self._encendido = False



Están bien planteados.
- No tienes @estado.setter, por lo que no permites altavoz.estado = ....
- El estado inicial se establece en False.
- encender() lo activa.
- apagar() lo desactiva.
- El usuario consulta el estado, pero no lo modifica directamente mediante una propiedad.
Esto es justo lo que buscas.

Una pequeña observación: en Python, usar _encendido es una protección por convención, no una restricción absoluta. Alguien podría escribir altavoz._encendido = True, pero para el nivel de encapsulación que estás estudiando, está bien.

5. Posibles problemas de diseño
1. El estado se inicializa después de validar nombre y volumen
self.nombre = nombreself.volumen = volumenself._encendido = False



El orden es correcto. Si el nombre o el volumen son inválidos, se genera el error y no se termina de construir el objeto. No supone un problema.
2. Mayúsculas y minúsculas del estado
Estás devolviendo "Encendido" y "Apagado" con inicial mayúscula. Es correcto si esa es la salida que quieres. Solo procura que los valores sean consistentes con lo que te pidan (por ejemplo, "encendido" en minúscula si así lo exige el ejercicio).
3. No hace falta duplicar validaciones
Has validado los datos en los setters y, además, los usas desde el constructor:
self.nombre = nombreself.volumen = volumen



Esto es una buena decisión de diseño: cuando creas el objeto, reutilizas las mismas validaciones que cuando modificas el nombre o el volumen posteriormente. No hace falta repetir las condiciones dentro de __init__.
4. Detalle de formato
En esta línea tienes una indentación un poco excesiva:
raise ValueError("El nombre no puede estar vacio")



No afecta a la lógica si la indentación sigue siendo válida, pero conviene alinearla con el resto del bloque.

6. Casos de prueba que te recomiendo
No he ejecutado tu código, así que estos son casos propuestos, no resultados de ejecución.
Pruebas del nombre
Prueba	Valor	Resultado esperado
Nombre normal	"Sony"	Aceptado
Con espacios exteriores	"  Sony  "	Guarda "Sony"
Cadena vacía	""	ValueError
Solo espacios	"    "	ValueError
Número	123	ValueError
None	None	ValueError

Pruebas del volumen
Prueba	Valor	Resultado esperado
Límite mínimo	0	Aceptado
Límite máximo	100	Aceptado
Valor intermedio	50	Aceptado
Por debajo del límite	-1	ValueError
Por encima del límite	101	ValueError
Decimal	25.5	ValueError
Texto	"50"	ValueError
Booleano	True	Debería rechazarse
Booleano	False	Debería rechazarse

Pruebas del estado
Prueba	Acción	Resultado esperado
Inicialización	Crear altavoz	Apagado
Encender	encender()	Encendido
Apagar	apagar()	Apagado
Encender varias veces	encender() repetido	Sigue encendido
Apagar varias veces	apagar() repetido	Sigue apagado
Acceso de lectura	Consultar estado	Devuelve el estado actual
Modificación directa	altavoz.estado = "Encendido"	Error, sin setter


7. Veredicto
Tu clase está bien encaminada. Los setters están correctamente construidos y no provocan recursión, el uso de propiedades es adecuado y el estado está encapsulado de acuerdo con el ejercicio.

El único cambio lógico que te recomendaría como importante es rechazar True y False en el setter del volumen, porque Python los considera valores de tipo int al usar isinstance().

Por lo demás, no reescribiría tu clase: mantendría tu estructura y corregiría únicamente ese detalle.

Si quieres, el siguiente paso podría ser que te prepare una serie de pruebas con assert y try/except para comprobar tu clase sin usar todavía unittest.

### Actividad de verificación de las recomendaciones de IA

Selecciona dos recomendaciones de la revisión anterior y decide si son correctas. Puedes usar las siguientes dos como ejemplos, pero debes contrastarlas con los requisitos y con tu código.


| Recomendación de la IA | ¿La acepto? | Justificación | ¿Cómo la he verificado? |
|---|---|---|---|
| Rechazar `True` y `False` como valores de volumen, aunque `isinstance(valor, int)` los considere enteros. | Sí / No | Explica por qué el volumen debería o no aceptar booleanos. | Indica la prueba o el análisis realizado; por ejemplo, comprobar `isinstance(True, int)` y probar el setter. |
| En los setters, guardar los valores en atributos internos (`_nombre` y `_volumen`) en vez de asignar de nuevo a `self.nombre` o `self.volumen`. | Sí / No | Explica cómo esta decisión evita o puede provocar recursión. | Revisa las asignaciones del setter y/o realiza una prueba que permita verificarlo. |


La IA no sustituye a las pruebas: sus propuestas deben contrastarse con
los requisitos y con el comportamiento real del programa.

---

## Entrega y reflexión final

Entrega el proyecto con esta estructura:

``` text
smart-speaker/
├── altavoz.py
├── main.py
├── pruebas_manuales.py
└── docs/
    └── laboratorio.md
```

El documento `docs/laboratorio.md` debe incluir:

# Entrega final del laboratorio

## 1. Reglas de negocio identificadas

Se describen las reglas que debe cumplir la clase `Altavoz`, como el nombre válido, el volumen permitido y el estado inicial del dispositivo.

## 2. Diseño de la interfaz pública

Se incluye la tabla de diseño de la interfaz pública de la clase, indicando los atributos, propiedades y métodos disponibles, así como su finalidad.

## 3. Explicación de las propiedades utilizadas

Se explica el uso de `@property` y de los setters para controlar el acceso y la modificación del nombre y del volumen. También se explica por qué el estado de encendido no tiene setter público.

## 4. Resultados de las pruebas válidas e inválidas

Se presentan las pruebas realizadas para comprobar que la clase acepta valores correctos y rechaza valores incorrectos, incluyendo los resultados obtenidos y si coinciden con los esperados.

## 5. Recomendaciones de la IA y decisiones tomadas

Se recogen dos recomendaciones propuestas por la IA, indicando si se aceptan o rechazan, la justificación de la decisión y cómo se han verificado.

## 6. Reflexión final

### ¿Qué ventajas tiene que la clase controle sus propias reglas?

Que la propia clase controle sus reglas permite evitar que el objeto se encuentre en un estado inválido. Así, cualquier modificación de sus datos pasa por las validaciones correspondientes, lo que hace que el código sea más seguro, coherente y fácil de mantener. Además, evita tener que repetir las mismas comprobaciones en distintas partes del programa.

https://github.com/Estresban/Python/tree/06513f6f9b8e81cb4c0a6541c315220f75997128/POO/altavoz

https://github.com/Estresban/Python/POO/altavoz
