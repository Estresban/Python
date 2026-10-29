# Importamos las clases desde los archivos
from proyecto import Proyecto
from tarea import Tarea
from usuario import Usuario


def ejecutar_sistema():
    print("=== INICIALIZANDO EL SISTEMA ===")

    # Creamos los usuarios
    juan = Usuario("Juan Pérez", "juan@email.com")
    maria = Usuario("María Gómez", "maria@email.com")

    # Creamos un proyecto
    proyecto_investor = Proyecto(
        titulo="Plataforma Investor",
        descripcion="Analítica del S&P 500",
    )

    # Creamos tareas en el proyecto
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
    proyecto_investor.tareas[0].asignar(juan)
    proyecto_investor.tareas[0].iniciar()

    # Tarea 1: Crear clase Plotter
    proyecto_investor.tareas[1].asignar(maria)
    proyecto_investor.tareas[1].completar()

    # Creamos una tarea externa y la añadimos al proyecto
    print("[Sistema]: Añadiendo una tarea externa...")
    tarea_externa = Tarea(
        titulo="Analizar volatilidad",
        descripcion="Calcular desviaciones estándar",
    )
    tarea_externa.asignar(juan)
    
    proyecto_investor.añadir_tarea(tarea_externa)

    # ==========================================
    # VISUALIZAR LOS RESULTADOS
    # ==========================================

    # Consultamos el estado de las tareas del proyecto
    proyecto_investor.consultar_tarea()

    # Consultamos las tareas pasando la lista interna del proyecto
    juan.consultar_tarea_asignada(proyecto_investor.tareas)
    maria.consultar_tarea_asignada(proyecto_investor.tareas)


if __name__ == "__main__":
    ejecutar_sistema()