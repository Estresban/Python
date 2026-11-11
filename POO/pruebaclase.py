class Empleado:
    def __init__(self):
        self.nombre = "Carlos"          # Público
        self._codigo_empleado = "E412"  # Protegido
        self.__sueldo = 2000            # Privado

    def mostrar_datos(self):
        # Estamos DENTRO de la clase. Usamos 'self' para leer todo sin problemas.
        print("--- Datos desde DENTRO de la clase ---")
        print(f"Nombre: {self.nombre}")
        print(f"Código: {self._codigo_empleado}")
        print(f"Sueldo: {self.__sueldo}")


# ==========================================================
# AQUÍ ESTAMOS FUERA DE LA CLASE (Código Principal)
# ==========================================================

# 1. Creamos al objeto 'jefe' (afuera)
jefe = Empleado()

# 2. Vemos cómo están sus datos originales usando su método interno
jefe.mostrar_datos()
print("\n" + "="*40 + "\n")

# 3. Intentamos modificar TODO desde AFUERA usando el objeto 'jefe'
print("--- Intentando modificar desde AFUERA ---")

jefe.nombre = "Ana"              # ✅ Público: Cambia sin problemas
jefe._codigo_empleado = "A999"   # ⚠️ Protegido: Python te deja, pero es mala práctica
jefe.__sueldo = 999999           # ❌ Privado: ¡Python no te va a dejar cambiar el original!

print("¡Modificaciones realizadas!\n")

# 4. Comprobamos el resultado final volviendo a mirar DENTRO de la clase
jefe.mostrar_datos()
