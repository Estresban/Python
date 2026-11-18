
while True:

    try:
        num = int(input("dime un numero para dividirlo entre 10"))
        resultado = 10/ num
        break
        
    except ValueError as error:
        print(f"No se ha introducido un numero {error}")

    except ZeroDivisionError:
        print(f"El resultado de la aplicacion es cero")

    except Exception:
        print(f"se ha producido un error en la aplicacion")
        
 #   "si se produce un error que siga preguntando el numero"
    
#tambien se puede juntar errores
    except (ValueError, ZeroDivisionError)as error:
        print(f"Error general")
        
alumnos = ["Carlos","David","Esteban"]

#print (alumnos[3])
for alumno in alumnos:
    alumnos.remove("Carlos")
    print(alumnos[2])
