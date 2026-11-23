from src.altavoz.altavoz import Altavoz


def main() -> None:
    altavoz = Altavoz("Salón", 30)

    print(altavoz.nombre)
    print(altavoz.volumen)
    print(altavoz.encendido)

    altavoz.nombre = ""
    altavoz.volumen = -50
    altavoz.encendido = "quizá"

    print(altavoz.nombre)
    print(altavoz.volumen)
    print(altavoz.encendido)


if __name__ == "__main__":
    main()
    
#####################################################
# PRUEBAS DIRECTAS


#Altavoz("", 50)

#Altavoz("   ", 50)

#Altavoz(25, 50)

#Altavoz("Salón", -1)
       
#Altavoz("Salón", 101)

#altavoz = Altavoz("Salón", 50)
#altavoz.volumen = 25.5
        
#altavoz = Altavoz("Salón", 50)
#altavoz.volumen = "alto"
      
#altavoz = Altavoz("Salón", 50)
#altavoz.estado = "encendido"