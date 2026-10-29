class Usuario:

    def __init__(self, nombre: str, correo: str):
        # Atributos privados
        self._nombre: str = nombre
        self._correo: str = correo
        
        # Metodos publicos
    def consultar_tarea_asignada(self, lista_tareas) -> None:
        print(f"\nTareas asignadas a {self._nombre}:")

        encontradas = 0
        for tarea in lista_tareas:
            if tarea.responsable == self:
                encontradas += 1
                print(f"  {encontradas}.Titulo: {tarea.titulo} | Estado: {tarea.estado} | Prioridad: {tarea.prioridad}")

        if encontradas == 0:
            print("  No tienes tareas asignadas.")
