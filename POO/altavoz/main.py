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