from tarea import Tarea

class Proyecto:
    def __init__(self,identificador: str, titulo: str, descripcion: str, estado_proyecto: str = "Iniciado"):
        # Atributos privados
        self.identificador: str = identificador
        self.titulo: str = titulo
        self.descripcion: str = descripcion
        self.estado_proyecto: str = estado_proyecto
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

    #Eliminar tareas
    def eliminar_tarea(self, titulo: str) -> None:
        # Elimina una tarea del proyecto por su título.
        for tarea in self.tareas:
            if tarea.titulo == titulo:
                self.tareas.remove(tarea)
                print(f"Tarea '{titulo}' eliminada del proyecto.")
                return
        print(f"No se encontró la tarea '{titulo}' en el proyecto.")
        
    def cambiar_estado(self, nuevo_estado: str) -> None:
        estados_validos = ["Iniciado", "Finalizado"]
        
        if nuevo_estado in estados_validos:
            self.estado_proyecto = nuevo_estado
            print(f"El estado del proyecto '{self.titulo}' ha cambiado a: {nuevo_estado}")
        else:
            print(f"Error: '{nuevo_estado}'  el estado no es válido. Use: {estados_validos}")   
            