'''Ejercicio 5. Precio final
Solicita:

Precio de un producto.
Porcentaje de IVA.
Calcula:

Importe del IVA.
Precio final.
Ejemplo:

Precio: 100
IVA: 21

IVA: 21 €
Precio final: 121 €'''

precio = float(input("Introduce el precio del producto: "))
iva = float(input("Introduce el porcentaje de IVA: "))

importe_iva = precio * iva / 100
precio_final = precio + importe_iva

print(f"IVA: {importe_iva:.2f} €")
print(f"Precio final: {precio_final:.2f} €")
