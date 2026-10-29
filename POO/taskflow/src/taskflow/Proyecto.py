import Tarea

class Proyecto:

    def __init__(self, titulo: str, descripcion: str):
        # Atributos privados
        self._titulo: str = titulo
        self._descripcion: str = descripcion
        # Lista para almacenar los objetos de tipo Tarea
        self._tareas = []

    # Métodos públicos
    def crear_tarea(self, responsable, prioridad: str) -> None:
        # Insta una nueva Tarea y la añade al proyecto.
        nueva_tarea = Tarea(responsable, prioridad)
        self.añadir_tarea(nueva_tarea)

    def añadir_tarea(self, tarea) -> None:
        # Añade una tarea a la lista del proyecto.
        self._tareas.append(tarea)

    def consultar_tarea(self) -> None:
        # Muestra las tareas
        print(f"\n--- Tareas del Proyecto: {self._titulo} ---")
        if not self._tareas:
            print("  No hay tareas registradas en este proyecto.")
            return

        for i, tarea in enumerate(self._tareas, 1):
            nombre_responsable = getattr(tarea.responsable, '_nombre', tarea.responsable)
            print(f"  {i}. Estado: {tarea.estado} | Prioridad: {tarea.prioridad} | Responsable: {nombre_responsable}")
