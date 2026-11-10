# Importamos las clases
from proyecto import Proyecto
from tarea import Tarea
from usuario import Usuario


def ejecutar():
    print("=== INICIALIZANDO EL SISTEMA ===")

    # Creamos los usuarios
    Ariel = Usuario("Ariel Vicario ", "ariel@email.com")
    Abril = Usuario("Abril Vicario", "abril@email.com")

    # Creamos un proyecto
    proyecto_investor = Proyecto(
        titulo="Plataforma Investor",
        descripcion="Analítica del S&P 500",
    )

    # Creamos tareas
    print("\n[Sistema]: Creando tareas en el proyecto...")
    proyecto_investor.crear_tarea(
        titulo="Descargar datos CSV",
        descripcion="Bajar el histórico de precios",
    )
    proyecto_investor.crear_tarea(
        titulo="Crear clase Plotter",
        descripcion="Desarrollar lógica de gráficos",
    )

    # Asignamos y modificamos las tareas usando los índices de la lista
    # Tarea 0: Descargar datos CSV
    proyecto_investor.tareas[0].asignar(Ariel)
    proyecto_investor.tareas[0].iniciar()

    # Tarea 1: Graficar datos
    proyecto_investor.tareas[1].asignar(Abril)
    proyecto_investor.tareas[1].completar()

    # Creamos una tarea nueva
    print("[Sistema]: Añadiendo una tarea nueva...")
    tarea_nueva = Tarea(
        titulo="Analizar volatilidad",
        descripcion="Calcular desviaciones estándar",
    )
    tarea_nueva.asignar(Ariel)
    
    proyecto_investor.añadir_tarea(tarea_nueva)

    # Consulta del estado de las tareas
    proyecto_investor.consultar_tarea()

    # Consulta de las tareas en la lista
    Ariel.consultar_tarea_asignada(proyecto_investor.tareas)
    Abril.consultar_tarea_asignada(proyecto_investor.tareas)


if __name__ == "__main__":
    ejecutar()