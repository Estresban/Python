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

    # Recibir Tareas
    def recibir_tarea(self, tarea: Tarea):
        
        self.tareas_asignadas.append(tarea)
        print(f"Tarea '{tarea.titulo}' recibida por {self._nombre}.")      
    
    # Consultar Tareas Asignadas
    def consultar_tarea_asignada(self, lista_tareas: list) -> None:
        print(f"\nTareas asignadas a {self._nombre}:")

        encontradas = 0
        for tarea in lista_tareas:
            if tarea.responsable == self:
                encontradas += 1
                print(f"  {encontradas}.Titulo: {tarea.titulo} | Estado: {tarea.estado} | Prioridad: {tarea.prioridad}")

        if encontradas == 0:
            print("  No tienes tareas asignadas.")
