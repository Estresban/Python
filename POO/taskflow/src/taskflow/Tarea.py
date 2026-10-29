class Tarea:

    def __init__(self, responsable, prioridad: str):
        self.estado: str = "Pendiente"
        self.responsable = responsable
        self.prioridad: str = prioridad

    def iniciar(self) -> None:
        self.cambiar_estado("En curso")

    def completar(self) -> None:
        self.cambiar_estado("Completada")

    def asignar(self, nuevo_responsable) -> None:
        self.responsable = nuevo_responsable

    def cambiar_estado(self, nuevo_estado: str) -> None:
        self.estado = nuevo_estado

    def cambiar_prioridad(self, nueva_prioridad: str) -> None:
        self.prioridad = nueva_prioridad
