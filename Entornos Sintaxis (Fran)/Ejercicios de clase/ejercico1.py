'''Ejercicio 1. Presupuesto de reparación de un coche
Desarrolla un programa en Python que solicite al usuario los siguientes datos:

Nombre.
Apellido.
Precio del aceite de coche.
Precio de los inyectores.
Precio de las bujías.
Precio del filtro del habitáculo.
Cuando el usuario haya introducido todos los datos, el programa debe mostrar por pantalla:

El nombre y el apellido del usuario.
El precio total de todos los productos, sin IVA.
El precio total con el IVA del 21 % incluido.
Importante: Los precios deben poder introducirse con decimales.

Ejemplo orientativo
Introduce tu nombre: Ana
Introduce tu apellido: López
Precio del aceite de coche: 45.50
Precio de los inyectores: 120
Precio de las bujías: 32.90
Precio del filtro del habitáculo: 18.60

Cliente: Ana López
Precio total sin IVA: 217.00 €
Precio total con IVA (21 %): 262.57 €
Los valores del ejemplo son orientativos. Tu programa debe calcular los resultados a partir de los datos introducidos por el usuario.'''

nombre = input ("Nombre: ")
apellidos = input ("Apellidos: ")
Precio_aceite = 45.50
Precio_inyectores = 120
Precio_bujías = 32.90
Precio_filtro_habitáculo = 18.60

IVA = 21

if nombre and apellidos:
    aceite = input("cambio del aceite de coche: ")
    inyectores = input("cambio de inyectores: ")
    bujias = input("cambio de bujias: ")
    filtro = input("cambio del filtro del habitaculo: ")


subtotal_1 = Precio_aceite + Precio_inyectores + Precio_bujías + Precio_filtro_habitáculo

subtotal_2 = Precio_inyectores + Precio_bujías + Precio_filtro_habitáculo

subtotal_3 = Precio_bujías + Precio_filtro_habitáculo

subtotal_4 = Precio_filtro_habitáculo


total = subtotal_4 + (subtotal_4 * IVA / 100)

    
if aceite == "si" and inyectores == "si" and bujias == "si" and filtro == "si":
    print(f"Cliente: {nombre} {apellidos}")
    print(f"Precio total sin IVA: {subtotal_1:.2f} €")
    print(f"Precio total con IVA (21 %): {subtotal_1 + (subtotal_1 * IVA / 100):.2f} €")

elif aceite == "no" and inyectores == "si" and bujias == "si" and filtro == "si":
    print(f"Cliente: {nombre} {apellidos}")
    print(f"Precio total sin IVA: {subtotal_2:.2f} €")
    print(f"Precio total con IVA (21 %): {subtotal_2 + (subtotal_2 * IVA / 100):.2f} €")   

elif aceite == "no" and inyectores == "no" and bujias == "si" and filtro == "si":
    print(f"Cliente: {nombre} {apellidos}")
    print(f"Precio total sin IVA: {subtotal_3:.2f} €")
    print(f"Precio total con IVA (21 %): {subtotal_3 + (subtotal_3 * IVA / 100):.2f} €")

else:
    subtotal_4 = Precio_filtro_habitáculo
    total = subtotal_4 + (subtotal_4 * IVA / 100)
    print(f"Cliente: {nombre} {apellidos}")
    print(f"Precio total sin IVA: {subtotal_4:.2f} €")
    print(f"Precio total con IVA (21 %): {subtotal_4 + (subtotal_4 * IVA / 100):.2f} €")    
