from tarea import Tarea

class Usuario:

    def __init__(self, nombre: str, correo: str):
        # Atributos privados
        self._nombre: str = nombre
        self._correo: str = correo
        self.tareas_asignadas: list = []

    # Metodos publicos

    # Registrar Usuarios
    def registrar_usuario(self, nombre: str, correo: str):
        self._nombre = nombre
        self._correo = correo
        print(f"Usuario {self._nombre} registrado con éxito.")

    # Recibir y añadir Tareas a la lista
    def recibir_tarea(self, tarea: Tarea) -> None:
        if tarea not in self.tareas_asignadas:
            self.tareas_asignadas.append(tarea)
            # Asegura la consistencia en el objeto Tarea
            if tarea.responsable != self:
                tarea.asignar(self)      
    
    # Consultar Tareas Asignadas
    def consultar_tarea_asignada(self) -> None:
        print(f"\nTareas asignadas a {self._nombre}:")

        encontradas = 0
        for tarea in self.tareas_asignadas:
            if tarea.responsable == self:
                encontradas += 1
                print(f"  {encontradas}.Titulo: {tarea.titulo} | Estado: {tarea.estado} | Prioridad: {tarea.prioridad}")

        if encontradas == 0:
            print("  No tienes tareas asignadas.")
