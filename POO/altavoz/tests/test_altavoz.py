
# uv run pytest

##########################################
##########################################
#   Pruebas  manuales
##########################################
##########################################

from src.altavoz.altavoz import Altavoz

def test_man01_crear_altavoz_valido():
    altavoz = Altavoz("Salón", 30)
    assert altavoz.nombre == "Salón"
    assert altavoz.volumen == 30
    assert altavoz.estado == "Apagado"


def test_man02_consultar_nombre():
    altavoz = Altavoz("Salón", 30)
    assert altavoz.nombre == "Salón"


def test_man03_consultar_volumen():
    altavoz = Altavoz("Salón", 30)
    assert altavoz.volumen == 30


def test_man04_consultar_estado_inicial():
    altavoz = Altavoz("Salón", 30)
    assert altavoz.estado == "Apagado"


def test_man05_cambiar_volumen_50():
    altavoz = Altavoz("Salón", 30)
    altavoz.volumen = 50
    assert altavoz.volumen == 50


def test_man06_cambiar_volumen_0():
    altavoz = Altavoz("Salón", 30)
    altavoz.volumen = 0
    assert altavoz.volumen == 0


def test_man07_cambiar_volumen_100():
    altavoz = Altavoz("Salón", 30)
    altavoz.volumen = 100
    assert altavoz.volumen == 100


def test_man08_encender():
    altavoz = Altavoz("Salón", 30)
    altavoz.encender()
    assert altavoz.estado == "Encendido"


def test_man09_apagar():
    altavoz = Altavoz("Salón", 30)
    altavoz.encender()
    altavoz.apagar()
    assert altavoz.estado == "Apagado"


def test_man10_nombre_con_espacios():
    altavoz = Altavoz("  Cocina  ", 30)
    assert altavoz.nombre == "Cocina"


