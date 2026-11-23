'''

Requisito 1. Validar el nombre
Debe ser una cadena de texto.
No puede estar vacío ni contener únicamente espacios.
Se eliminarán los espacios exteriores antes de almacenar el nombre.


Requisito 2. Validar el volumen
Debe ser un número entero.
Su valor estará comprendido entre 0 y 100, ambos incluidos.
La misma validación debe aplicarse tanto al crear el objeto como al modificar el volumen.


Requisito 3. Controlar el estado
Un altavoz nuevo comienza apagado.
El estado podrá consultarse mediante altavoz.estado.
El resto del programa no debe poder cambiarlo mediante una asignación ordinaria a altavoz.estado.
El método encender() permitirá encender el dispositivo.
El método apagar() permitirá apagarlo.




Requisito 4. Mantener una interfaz clara
El código que utiliza la clase debería poder escribir:

altavoz = Altavoz("Salón", 30)

print(altavoz.nombre)
print(altavoz.volumen)
print(altavoz.estado)

altavoz.volumen = 50
altavoz.encender()
altavoz.apagar()

No debería necesitar acceder a los atributos internos para utilizar las operaciones habituales.'''


class Altavoz:
    def __init__(self, nombre, volumen):
        self.nombre = nombre
        self.volumen = volumen
        self._encendido = False
        
    @property
    def nombre(self):
        return self._nombre

    @property
    def volumen(self):
        return self._volumen
        
    @property
    def estado(self):
        return "Encendido" if self._encendido else "Apagado"
    

    @nombre.setter
    def nombre(self, nuevo_nombre):
        if not isinstance(nuevo_nombre,str):
            raise ValueError("El nombre debe ser cadena de texto")
        if not nuevo_nombre.strip():
            raise ValueError("El nombre no puede estar vacio")
        self._nombre = nuevo_nombre.strip()
        
    @volumen.setter
    def volumen(self, nuevo_volumen):
        if isinstance(nuevo_volumen, bool) or not isinstance(nuevo_volumen, int):
            raise ValueError("El volumen debe ser un numero entero")
        if nuevo_volumen < 0 or nuevo_volumen > 100:
            raise ValueError("El volumen debe estar entre 0 y 100")    
        self._volumen = nuevo_volumen
        
        
    def encender(self):
        self._encendido = True

    def apagar(self):
        self._encendido = False