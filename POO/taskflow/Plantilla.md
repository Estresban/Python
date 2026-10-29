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

| Posible objeto | ¿Por qué existe?                                                                                     | ¿Qué información necesita?                              |
| -------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Proyecto       | Para organizar y crear las tareas del proyecto.                                                      | Nombre, descripción y lista de tareas.                  |
| Tarea          | Para representar las actividades que deben realizarse en cada proyecto.                              | Título, descripción, estado y usuario asignado.         |
| Usuario        | Para designar a las personas que trabajan en los proyectos y que desarrollaran las tareas asignadas. | Nombre, correo electrónico y lista de tareas asignadas. |


### ¿Qué otras entidades podrían existir?
Además de Proyecto, Tarea y Usuario, podemos identificar más entidades según las necesidades.

| Posible entidad | ¿Por qué podría existir?                                                                |
| --------------- | --------------------------------------------------------------------------------------- |
| Comentario      | Para que los usuarios puedan hacer comentarios, aclaraciones o avances sobre una tarea. |
| Prioridad       | Para indicar qué tareas son más urgentes.                                               |
| Notificación    | Para avisar a un usuario cuando se le asigna una tarea o cambia su estado.              |
| Fecha           | Indica cuándo se creó la tarea y las distintas modificaciones.                                                        |
| Historial       | Para registrar los cambios de estado de una tarea y quién los realizó.                  |


### ¿Cuáles son realmente necesarias?

Para la primera versión de la aplicación, considero necesarias estas tres entidades:
–Proyecto: permite organizar las actividades por proyectos.
–Usuario: permite registrar a las personas y asignarles tareas.
–Tarea: permite representar el trabajo pendiente, su responsable y su estado.
Con estas tres clases podemos cumplir todos los requisitos del enunciado.
Las demás entidades podrían ser opcionales. 
Por ejemplo, añadir Comentario por si los usuarios necesitan comunicarse dentro de cada tarea. o añadir prioridad para establecer la urgencia.

### ¿Cuáles son solamente datos o características de otras entidades?

-Comentario: normalmente sería una entidad independiente, porque puede tener contenido, autor y fecha de creación.
-Notificación: puede ser una entidad independiente si necesitamos guardar, consultar o marcar notificaciones como leídas.
-Historial: puede ser una entidad independiente si queremos registrar cada cambio de estado, quién lo realizó y cuándo.
-Fecha: puede ser un atributo de Tarea o de Historial, porque indicaría la fecha de creación, aunque podríamos crearla como un objeto, y determinar distintas fechas, de creación, actualizaciones, o terminación.
-Prioridad: puede ser un atributo de Tarea, porque solo indica el nivel de urgencia.

## Parte 2. Identificar el estado

### 1. PROYECTO.

-Nombre: para identificar el proyecto.  
-Descripción: para conocer qué se va a desarrollar.  
-Tareas: para saber qué tareas pertenecen al proyecto.  

### 2. USUARIO.

-Nombre: para identificar a la persona.  
-Correo electrónico: para distinguir a los usuarios y disponer de una forma de comunicacion.  
-Tareas asignadas: para conocer qué tareas tiene asignadas.  

### 3. TAREA.

-Título: para identificar el trabajo que se debe realizar.  
-Descripción: para explicar en qué consiste.  
-Estado: para saber si está pendiente, en progreso o completada.  
-Responsable: para conocer qué usuario tiene asignada la tarea.  

### 4. OTRAS ENTIDADES.

Se pueden incluir las entidades propuestas, sus estados podrían ser 

-**Comentario**: Contenido, autor y tarea relacionada.  
-**Notificación**: Mensaje, usuario destinatario y estado de lectura.  
-**Historial**: Tarea relacionada, estado anterior, estado nuevo y usuario que realizó el cambio.  
-**Prioridad**: No necesita ser una entidad. Puede ser un atributo de Tarea, pero solo sería necesaria si debe distinguir entre tareas más y menos urgentes.  
-**Fecha**: puede ser un atributo de Tarea, porque indicaria la fecha de creación, aunque podríamos crearla como un objeto, y determinar distintas fechas, de creación, actualizaciones, o terminación.  

## Parte 3. Identificar el comportamiento

Identificamos las acciones que puede realizar cada objeto de la aplicación.

**PROYECTO**  
Puede:  
-crear tareas  
-consultar sus tareas  
-eliminar tareas  

**USUARIO**  
Puede:  
-registrarse  
-consultar sus tareas asignadas  
-recibir tareas asignadas  

**TAREA**  
Puede:
-iniciar  
-completar  
-reasignarse  
-cambiar de estado  
-actualizar su descripción  

**COMENTARIO**  
Puede:  
-crearse  
-editarse  
-eliminarse  

**NOTIFICACIÓN**  
Puede:  
-enviarse  
-marcarse como leída  

**HISTORIAL**  
Puede:  
-registrar un cambio de estado  
-consultar los cambios realizados  

**PRIORIDAD**  
Si la prioridad es un atributo de Tarea, no necesita comportamientos propios. La tarea puede:  
-cambiar de prioridad  
-consultar su prioridad actual  

**FECHA**  
Si consideramos la fecha como un atributo de Tarea o Historial, sus comportamientos podrían ser:  
-registrar la fecha de creación  
-actualizar la fecha de modificación  
-registrar la fecha de finalización  
-consultar las fechas de la tarea  

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

