from datetime import date

class Tarea:
    def __init__(self, responsable=None, prioridad="MEDIA"):
        self.estado: str = "PENDIENTE"
        self.responsable = responsable
        self.fecha_creacion: date = date.today()
        self.fecha_modificacion: date = self.fecha_creacion
        self.fecha_finalizacion: date = None
        self.prioridad: str = prioridad


    def iniciar(self) -> None:
        self.estado = "EN PROGRESO"
        self.fecha_modificacion = date.today()


    def completar(self) -> None:
        self.estado = "COMPLETADA"
        self.fecha_finalizacion = date.today()
        self.fecha_modificacion = date.today()


    def asignar(self, usuario) -> None:
        self.responsable = usuario
        self.fecha_modificacion = date.today()


    def cambiar_estado(self, estado: str) -> None:
        estados_validos = ["PENDIENTE", "EN PROGRESO", "COMPLETADA"]

        if estado in estados_validos:
            self.estado = estado
            self.fecha_modificacion = date.today()

            if estado == "COMPLETADA":
                self.fecha_finalizacion = date.today()
            else:
                self.fecha_finalizacion = None
        else:
            print("Estado no válido")

    def cambiar_prioridad(self, prioridad: str) -> None:
        prioridades_validas = ["BAJA", "MEDIA", "ALTA"]

        if prioridad in prioridades_validas:
            self.prioridad = prioridad
            self.fecha_modificacion = date.today()
        else:
            print("Prioridad no válida")
