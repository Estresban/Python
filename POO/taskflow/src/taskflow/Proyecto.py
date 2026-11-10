from tarea import Tarea

class Proyecto:
    def __init__(self,identificador: str, titulo: str, descripcion: str, estado_proyecto: str = "Iniciado"):
        self.identificador: str = identificador
        self.titulo: str = titulo
        self.descripcion: str = descripcion
        self.estado_proyecto: str = estado_proyecto
        # Lista para almacenar los objetos de tipo Tarea
        self.tareas: list = []
    # Métodos públicos
    def crear_tarea(self, ID_tarea:str,titulo: str, descripcion: str) -> None:
        # Insta una nueva Tarea y la añade al proyecto.
        tarea = Tarea(ID_tarea = ID_tarea, proyecto = self.identificador, titulo=titulo, descripcion=descripcion)
        self.tareas.append(tarea)


    def consultar_tarea(self) -> None:
        # Muestra las tareas
        if not self.tareas:
            print("El proyecto no tiene tareas.")
            return

        for tarea in self.tareas:
            print(f"{self.identificador} - {tarea.ID_tarea} - {tarea.titulo} - {tarea.estado} - {tarea.prioridad} - CREADA: {tarea.fecha_creacion}")
            print("--------------------")

    #Eliminar tareas
    def eliminar_tarea(self, ID_tarea: str) -> None:
        for tarea in self.tareas:
            if tarea.ID_tarea == ID_tarea:
                self.tareas.remove(tarea)
                print(f"Tarea '{ID_tarea}' eliminada del proyecto.")
                return
        print(f"No se encontró la tarea '{ID_tarea}' en el proyecto.")
        
    def cambiar_estado(self, nuevo_estado: str) -> None:
        estados_validos = ["Pendiente", "Iniciado", "Finalizado"]
        
        if nuevo_estado in estados_validos:
            self.estado_proyecto = nuevo_estado
            print(f"El estado del proyecto '{self.titulo}' ha cambiado a: {nuevo_estado}")
        else:
            print(f"Error: '{nuevo_estado}'  el estado no es válido. Use: {estados_validos}")   
            