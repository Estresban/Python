'''Ejercicio 14. Calculadora
Solicita:

Primer número.
Segundo número.
Operación.
Las operaciones disponibles serán:

+
-
*
/
Muestra el resultado correspondiente.

Controla la división entre cero.'''

primer_numero = float(input("Introduce el primer número: "))
segundo_numero = float(input("Introduce el segundo número: "))  
operacion = input("Introduce la operación (+, -, *, /): ")

if operacion == "+":
    resultado = primer_numero + segundo_numero
elif operacion == "-":
    resultado = primer_numero - segundo_numero
elif operacion == "*":
    resultado = primer_numero * segundo_numero
elif operacion == "/":
    if segundo_numero != 0:
        resultado = primer_numero / segundo_numero
    else:
        print("Error: División entre cero.")
        resultado = None

if resultado is not None:
    print(f"El resultado de {primer_numero} {operacion} {segundo_numero} es: {resultado}")
