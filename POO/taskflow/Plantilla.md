# Laboratorio 1
## Pensar antes de programar

Imagina que una pequeña empresa necesita una aplicación para organizar sus proyectos de desarrollo.
La aplicación debe permitir:
crear proyectos;
registrar usuarios;
crear tareas;
asignar tareas a usuarios;
cambiar el estado de una tarea;
Una tarea puede encontrarse en diferentes estados:
PENDIENTE → EN PROGRESO → COMPLETADA
Nuestro objetivo es únicamente diseñar el modelo de objetos y realizar una primera implementación en Python

## Parte 1. Analizar el problema

Antes de escribir código, identifica las entidades importantes del problema.
Completa una tabla como esta:







### ¿Qué otras entidades podrían existir?
Además de Proyecto, Tarea y Usuario, podemos identificar más entidades según las necesidades.



### ¿Cuáles son realmente necesarias?



### ¿Cuáles son solamente datos o características de otras entidades?



## Parte 2. Identificar el estado

### 1. PROYECTO.
### 2. USUARIO.
### 3. TAREA.
### 4. OTRAS ENTIDADES.


## Parte 3. Identificar el comportamiento


## Parte 4. Responsabilidades


## Parte 5. Diseñar el modelo


## Parte 6. Diseñar las clases con UML


## Parte 7. Primera implementación con Python


## Parte 8. El historial de Git

Durante el laboratorio utiliza Git para registrar la evolución del proyecto.
No esperes hasta el final.
Realiza commits cuando completes partes significativas.
Por ejemplo:
git add .
git commit -m "chore: crear proyecto TaskFlow"
Después:
git add .
git commit -m "feat: crear clase Tarea"
Y posteriormente:
git add .
git commit -m "feat: implementar comportamiento de Tarea"
Finalmente:
git push
Consulta el historial:
git log --oneline
Tu repositorio debe permitir observar cómo ha evolucionado el diseño.


## Parte 9. La IA como analista

En este laboratorio vamos a utilizar IA, pero no para que nos diseñe y programe TaskFlow.
Primero realiza tu propio análisis.
Después puedes utilizar una IA para contrastarlo.
Utiliza un prompt como:

Estoy diseñando una aplicación de gestión de proyectos
llamada TaskFlow.

He identificado estos objetos:

- Proyecto
- Usuario
- Tarea

Para cada uno he definido este estado:
[PEGA AQUÍ TU PROPUESTA]

Y estos comportamientos:
[PEGA AQUÍ TU PROPUESTA]

Analiza mi diseño como si fueras un analista de software.

No escribas código.

Indica:
1. qué decisiones parecen coherentes;
2. qué responsabilidades podrían estar mal asignadas;
3. qué información podría faltar;
4. qué información podría sobrar;
5. qué preguntas debería hacerme antes de programar.

No rediseñes la solución completa.

Si no sabes algo, no te lo inventes.


## Entregables del laboratorio

taskflow/
└── src/
    └── taskflow/
        ├── __init__.py
        ├── main.py
        ├── tarea.py
        ├── usuario.py
        └── proyecto.py
└── doc/
    └── 01-analisis.md
    └── 02-modelo-uml.png
    └── 03-ia-prompt.md

## Aclaraciones
__init__.py
    ↓
"Este directorio forma parte de un paquete Python"

main.py
    ↓
"Desde aquí arranca nuestra aplicación"

tarea.py
    ↓
"Define la clase Tarea"

usuario.py
    ↓
"Define la clase Usuario"

proyecto.py
    ↓
"Define la clase Proyecto"

En main.py para hacer uso de Tarea y poder crear instancias, por ejemplo, tendríamos que hacer:

from taskflow.tarea import Tarea


def main() -> None:
    tarea = Tarea("Diseñar la página de inicio")

    print(tarea.titulo)


if __name__ == "__main__":
    main()

## ➕ Ampliación
Investiga cómo podríamos:

Listar las tareas de un responsable en concreto
Listar los proyectos y las tareas asociadas

