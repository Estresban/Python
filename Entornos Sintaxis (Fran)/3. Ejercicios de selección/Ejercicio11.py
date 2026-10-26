'''Ejercicio 11. Mayor de tres números
Solicita tres números y muestra cuál es el mayor.

No utilices max(). '''

numero1 = int(input("Introduce el primer número: "))
numero2 = int(input("Introduce el segundo número: "))   
numero3 = int(input("Introduce el tercer número: "))
if numero1 > numero2 and numero1 > numero3:
    print("El primer número es el mayor.")  
elif numero2 > numero1 and numero2 > numero3:
    print("El segundo número es el mayor.") 
elif numero3 > numero1 and numero3 > numero2:
    print("El tercer número es el mayor.")

