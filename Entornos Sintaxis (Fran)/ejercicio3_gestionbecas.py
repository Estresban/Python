'''Ejercicio 4. Sistema de concesión de becas
Un centro educativo quiere desarrollar un programa en Python para determinar qué tipo de beca puede recibir un alumno.
El programa debe solicitar los siguientes datos: 
- Nombre del alumno. 
- Nota media del curso. 
- Renta familiar anual. 
- Porcentaje de asistencia a clase. 
- Si pertenece a una familia numerosa (s o n). 

El centro establece las siguientes condiciones:
1. Beca de excelencia
El alumno obtiene esta beca si cumple todas estas condiciones: 
- Tiene una nota media igual o superior a 9. 
- Tiene una asistencia igual o superior al 90 %. 
- Su renta familiar es inferior a 30.000 €. 

2. Beca general
Si no cumple los requisitos de la beca de excelencia, podrá obtener la beca general si: 
- Tiene una nota media igual o superior a 6,5. 
- Tiene una asistencia igual o superior al 80 %. 
- Además, cumple al menos una de estas condiciones: 
- Su renta familiar es inferior a 20.000 €. 
- Pertenece a una familia numerosa. 

3. Sin beca
Si no cumple ninguna de las condiciones anteriores, no obtiene ninguna beca.

Requisitos del programa: 
1. Solicita todos los datos al usuario. 
2. Comprueba si tiene derecho a una beca de excelencia. 
3. Si no cumple los requisitos, comprueba si puede obtener una beca general. 
4. Si tampoco cumple esos requisitos, indica que no tiene derecho a ninguna beca. 
5. Muestra el nombre del alumno y el tipo de beca obtenido.'''

nombre = input("Introduce el nombre del alumno: ")
nota_media = float(input("Introduce la nota media del curso: "))
renta_familiar = float(input("Introduce la renta familiar anual: "))
asistencia = float(input("Introduce el porcentaje de asistencia a clase: "))
familia_numerosa = input("¿Pertenece a una familia numerosa? (s/n): ")

if nota_media >= 9 and asistencia >= 90 and renta_familiar < 30000:
    beca = "Beca de excelencia"
elif (nota_media >= 6.5 and asistencia >= 80)and (renta_familiar < 20000 or familia_numerosa == "s" or familia_numerosa == "S"):
        beca = "Beca general"
    
else:
    beca = "Sin beca"

print(f"El alumno {nombre} tiene derecho a la {beca}.")