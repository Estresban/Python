'''cadena = "esteban"
print(cadena.upper())  # Salida: "S"
print (cadena.lower())  # Salida: "s"
cadena_mayusculas = cadena.upper()
print(cadena_mayusculas)  # Salida: "ESTEBAN"  


Camisetas de futbol


El usuaro no puede ponerle de nombre Ronaldo, si es ese nombre te dice que nanai'''


nombre = input("Introduce el nombre que quieres en tu camiseta: ")
if not nombre:
    print("No has introducido un nombre.")

else:
    nombredepurado = nombre.strip().isalpha().replace(" " , "")
    if nombredepurado.lower() != "ronaldo" or nombredepurado.upper() != "RONALDO" :
        print("Nanai, no puedes poner ese nombre en tu camiseta.")  
    else:
        print(f"Tu camiseta tendrá el nombre: {nombredepurado.upper()}")    