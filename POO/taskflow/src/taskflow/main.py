from proyecto import Proyecto
from usuario import Usuario
# from tarea import Tarea

def main():
    print("=== TASKFLOW ===\n")

    # Crear usuarios con el constructor
    print("--- Registro de Usuarios ---")
    Ariel = Usuario(nombre="Ariel V", correo="ariel@email.com")
    Abril = Usuario(nombre="Abril V", correo="abril@email.com")
    print (f"Usuario creado: {Ariel._nombre} | Correo: {Ariel._correo}")

    # Probar el metodo registrar_usuario()
    Ariel.registrar_usuario("Ariel V", "ariel@email.com")
    Abril.registrar_usuario("Abril V", "abril@email.com")

    # Crear un proyecto
    print("\n--- Creación de Proyecto ---")
    proyecto_bordon = Proyecto(
        identificador="ID-001", 
        titulo="comunicacion ODB II con Can BUS", 
        descripcion="Creación de ODB II comunicación con bus CAN"
    )
    print(f"Proyecto creado: {proyecto_bordon.titulo} (Estado: {proyecto_bordon.estado_proyecto})")

    # Crear tareas dentro del proyecto
    print("\n--- Creación de Tareas ---")
    proyecto_bordon.crear_tarea(ID_tarea="T-01", titulo="Diseñar interface grafica", descripcion="Crear los graficos del menu")
    proyecto_bordon.crear_tarea(ID_tarea="T-02", titulo="Codificar ordenes", descripcion="convertir ordenes en hexadecimal")
    proyecto_bordon.crear_tarea(ID_tarea="T-03", titulo="Desarrollar consultas UDS", descripcion="Agregar consultas UDS")

    # Consultar tareas del proyecto tras la creación
    proyecto_bordon.consultar_tarea()

    # Asignar y vincular tareas
    print("\n--- Asignación de Tareas ---")
    tarea1 = proyecto_bordon.tareas[0]
    tarea2 = proyecto_bordon.tareas[1]
    
    #################################################
    # Prueba 1 metodo asignar()
    print("Asignando T-01 a Ariel desde la tarea:")
    tarea1.asignar(Ariel)

    # Prueba 2
    print("Asignando T-02 a Abril desde el usuario:")
    Abril.recibir_tarea(tarea2)
    #################################################
    
    # Consultar tareas asignadas
    Ariel.consultar_tarea_asignada()
    Abril.consultar_tarea_asignada()

    # Iniciar tarea
    print("\n--- Progreso de Tareas ---")
    print("Iniciando la tarea de Ariel...")
    tarea1.iniciar()
    
    # Cambiar prioridad
    print("Cambiando prioridad y completando la tarea de Abril...")
    tarea2.cambiar_prioridad("ALTA")
    tarea2.completar()

    # Consultar tarea
    print("\nConsultando estado global del proyecto:")
    proyecto_bordon.consultar_tarea()

    # Modificar
    print("\n--- Mantenimiento del Proyecto ---")
    # Cambiar estado del proyecto
    proyecto_bordon.cambiar_estado("Finalizado")

    # Eliminar una tarea por ID
    print("\nEliminando la tarea T-03...")
    proyecto_bordon.eliminar_tarea("T-03")

if __name__ == "__main__":
    main()