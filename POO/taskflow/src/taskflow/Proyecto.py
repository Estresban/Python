import Tarea

class Proyecto:
    def __init__(self, titulo: str, descripcion: str):
        # Atributos privados
        self.titulo: str = titulo
        self.descripcion: str = descripcion
        # Lista para almacenar los objetos de tipo Tarea
        self.tareas: list = []
    # Métodos públicos
    def crear_tarea(self, titulo: str, descripcion: str) -> None:
        # Insta una nueva Tarea y la añade al proyecto.
        tarea = Tarea(titulo=titulo, descripcion=descripcion)
        self.tareas.append(tarea)


    def consultar_tarea(self) -> None:
        # Muestra las tareas
        if not self.tareas:
            print("El proyecto no tiene tareas.")
            return

        for tarea in self.tareas:
            print(tarea.titulo, "-", tarea.estado, "-", tarea.prioridad)
            print("--------------------")

    def añadir_tarea(self, tarea: Tarea) -> None:
        # Añade una tarea a la lista del proyecto.
        self.tareas.append(tarea)
