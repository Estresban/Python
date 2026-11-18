resultado = 0
historial = []
def menu():
    print("INICIO PROGRAMA CALCULADORA")
    print("1. Operación")
    print("2. Mostrar Resultado última operacion")
    print("3. Quiero que me enseñes el historial de resultados que has tenido")
    print("4. Fin del programa")

def mostrar_ultimo_resultado():
    print(resultado)

def operaciones():

    global resultado
    numero1 = int(input('Dime el numero 1'))
    numero2 = int(input('Dime el numero 2'))
    operacion = input('Dime que operacion quieres hacer * / + -')
    if operacion == "*":
        resultado = numero1 * numero2
    elif operacion == "/":
        resultado = numero1 / numero2
    elif operacion == "+":
        resultado = numero1 + numero2
    print(f"El resultado de la operacion es: {resultado}")
    historial.append(resultado)

def mostrar_historial():
    print(historial)

if __name__ == '__main__':

    while True:
        menu()
        opc = input('Dime que opcion eliges')
        if opc == "1":
            operaciones()
        elif opc == "2":
            mostrar_ultimo_resultado()
        elif opc == "3":
            mostrar_historial()
        else:
            break
