'''Ejercicio 3. Conversor de euros
Solicita una cantidad en euros y muestra su equivalente en dólares.

Utiliza un tipo de cambio almacenado en una variable.
Tipo de cambio = 1.08
'''

cambio = 1.08

euros = float(input("Cuanto dinero quieres convertir en euros: "))
dolares = euros * cambio
print("La cantidad en dólares es: ", dolares)
 
dolares = float(input("Cuanto dinero quieres convertir en dolares: "))
euros = dolares / cambio
print("La cantidad en euros es: ", euros)