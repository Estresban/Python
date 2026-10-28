'''Ejercicio 2. Compra en el supermercado
Imagina que tienes 200 euros en tu cuenta corriente y vas a hacer la compra en el supermercado.

Desarrolla un programa en Python que:

Inicialice el saldo de la cuenta corriente en 200 euros.
Pregunte el precio de los siguientes cuatro productos:
Una docena de huevos.
Una caja de helados.
Una barra de pan.
Un racimo de uvas.
Reste del saldo inicial el precio de cada producto.
Cuando el usuario haya introducido el precio del último producto, muestre el saldo final que queda en la cuenta corriente.
Importante: Los precios pueden contener decimales. Para este ejercicio, puedes suponer que hay saldo suficiente para pagar todos los productos.

Ejemplo orientativo
Saldo inicial: 200.00 €
Precio de una docena de huevos: 3.20
Precio de una caja de helados: 5.50
Precio de una barra de pan: 1.10
Precio de un racimo de uvas: 4.80

Saldo final en la cuenta corriente: 185.40 €
Los valores del ejemplo son orientativos. El programa debe calcular el saldo final utilizando los precios introducidos por el usuario.'''

'''
SALDO_INICIAL = 200.00
huevos = float(input("Precio de una docena de huevos: "))
helados = float(input("Precio de una caja de helados: "))
pan = float(input("Precio de una barra de pan: "))
uvas = float(input("Precio de un racimo de uvas: "))

resto = SALDO_INICIAL - (huevos + helados + pan + uvas)
print(f"Saldo final en la cuenta corriente: {resto:.2f} €")'''



'''Ampliación del ejercicio 2: IVA por producto
Cuando termines el ejercicio básico, añade una mejora al programa.

Aplica los siguientes tipos de IVA:

Producto	IVA
Una docena de huevos	10 %
Una caja de helados	21 %
Una barra de pan	10 %
Un racimo de uvas	21 %
Nuevos requisitos:

Añade un menú para elegir si se quiere calcular la compra con IVA.
Calcula el precio de cada producto con su IVA incluido.
Muestra el importe total de la compra.
Calcula el saldo final después de pagar.'''


SALDO_INICIAL = 200.00
IVA_HUEVOS = 10
IVA_HELADOS = 21
IVA_PAN = 10
IVA_UVAS = 21

menu = input("¿Desea calcular la compra con IVA? (si/no): ")
if menu == "si":
    huevos = float(input("Precio de una docena de huevos: "))
    helados = float(input("Precio de un helados: "))
    pan = float(input("Precio de una barra de pan: "))
    uvas = float(input("Precio de un racimo de uvas: "))

    precio_huevos_iva = huevos + (huevos * IVA_HUEVOS / 100)
    precio_helados_iva = helados + (helados * IVA_HELADOS / 100)
    precio_pan_iva = pan + (pan * IVA_PAN / 100)
    precio_uvas_iva = uvas + (uvas * IVA_UVAS / 100)

    total_compra = precio_huevos_iva + precio_helados_iva + precio_pan_iva + precio_uvas_iva
    saldo_final = SALDO_INICIAL - total_compra

    print(f"Importe total de la compra con IVA: {total_compra} €")
    print(f"Importe total del IVA: {total_compra - (huevos + helados + pan + uvas)} €")
    print(f"Saldo final en la cuenta : {saldo_final} €")
    
else:
    huevos = float(input("Precio de una docena de huevos: "))
    helados = float(input("Precio de un helados: "))
    pan = float(input("Precio de una barra de pan: "))
    uvas = float(input("Precio de un racimo de uvas: "))

    total_compra = huevos + helados + pan + uvas
    saldo_final = SALDO_INICIAL - total_compra

    print(f"Importe total de la compra sin IVA: {total_compra} €")
    print(f"Saldo final en la cuenta : {saldo_final} €")
