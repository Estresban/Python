'''
for i in range(1,1000,1):
    if i % 2 == 0:
        print("El numero", i, "es par")
    else:
        print("El numero", i, "no es par")
      
for i in range(2,11,1):
    print("2 x", i, "=", 2*i)
    
nombre = 'Esteban'
    
for letra in nombre:
    print(letra)
    
    
for letra in nombre:
    if letra == 'e':
        letra = '-'
    print(letra)

for letra in nombre:
    if letra == 'e' or letra == 'E':
        letra = '-'
    print(letra)
    
lista = ['Carlos','Diego','Esteban']

print(lista[2])
print(lista[-1])

lista.append('Juan')
print(lista)

#actualizacion de valores
lista[0] = 'Pedro'
visualizar_lista = lista[0]

#eliminar elementos de una lista
del lista[1]

lista.remove('Esteban')


#ordenar una lista
lista.sort()
print(lista)


lista.sort(reverse=True)
print(lista)


lista_numeros = [1,2,8,4,9,6,7,5,3]

lista_numeros.sort()

lista_numeros.sort(reverse=True)

lista1 = [1,2,3,4,5]
lista2 = lista1.copy()

lista1.append(6)
print(lista2)

lista1 = [1,2,3,4,5]
lista2 = lista1

lista1.append(6)
print(lista2)

lista_alumnos = ['Carlos','Diego','Esteban']
lista_alumnos.pop()
print(lista_alumnos)

lista_alumnos = ['Carlos','Diego','Esteban']
elemento = lista_alumnos.pop()
print(lista_alumnos)
print(elemento)

'''
#
#
#tengo que hacer un menu de calculadora que tenga las siguientes opciones:

def menu():
    print("Menu de calculadora")
    print("1. Operacion")
    print("2. Resultado")
    print("3. Salir")

resultados = []
def operaciones():
    global resultados
    numero1 = int(input("Ingrese el primer numero: "))
    numero2 = int(input("Ingrese el segundo numero: "))
    operacion = input("Ingrese la operacion (+, -, *, /): ")
    if operacion == "+":
        resultado = numero1 + numero2
    elif operacion == "-":
        resultado = numero1 - numero2
    elif operacion == "*":
        resultado = numero1 * numero2
    elif operacion == "/":
        resultado = numero1 / numero2
    print(f"Resultado: {resultado}")
    resultados.append(resultado)
     
    
def mostrar_resultados():
    print(f"Resultado de la ultima operacion realizada:{resultados[-1]}")


if __name__ == "__main__":
    while True:
        menu()  
        
        opc = input("Ingrese una opcion: ") 
        
        if opc == "1":
                operaciones()
        elif opc == "2":
                mostrar_resultados()
        elif opc == "3":
                print("Saliendo del programa...")
                break


############################################################
############################################################
############################################################
############################################################
############################################################
############################################################
            
def menu():
    print("Menu de calculadora")
    print("1. Operacion")
    print("2. Resultado")
    print("3. Salir")           
            
resultados = []

def operaciones():
    numero1 = int(input("Ingrese el primer numero: "))
    numero2 = int(input("Ingrese el segundo numero: "))
    operacion = input("Ingrese la operacion (+, -, *, /): ")

    if operacion == "+":
        resultado = numero1 + numero2
    elif operacion == "-":
        resultado = numero1 - numero2
    elif operacion == "*":
        resultado = numero1 * numero2
    elif operacion == "/":
        resultado = numero1 / numero2
    else:
        print("Operacion no valida")
        return None

    print(f"Resultado: {resultado}")
    return resultado

def mostrar_resultados():
    print(f"Resultado de la ultima operacion realizada:{resultados[-1]}")


if __name__ == "__main__":
    while True:
        menu()  
        
        opc = input("Ingrese una opcion: ") 
        
        if opc == "1":
                resultado = operaciones()
                if resultado is not None:
                    resultados.append(resultado)
        elif opc == "2":
                mostrar_resultados()
        elif opc == "3":
                print("Saliendo del programa...")
                break