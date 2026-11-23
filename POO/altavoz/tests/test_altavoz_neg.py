import pytest
from src.altavoz.altavoz import Altavoz

'''
# Crear un altavoz con nombre ""
def test_negat01_nombre_vacio():
    with pytest.raises(ValueError):
        Altavoz("", 50)

# Crear un altavoz con nombre 25
def test_negat03_nombre_no_string():
    with pytest.raises(ValueError):
        Altavoz(25, 50)


# Crear un altavoz con volumen -1
def test_negat04_volumen_negativo():
    with pytest.raises(ValueError):
        Altavoz("Salón", -1)
        
'''
# Crear un altavoz con volumen 101
def test_negat05_volumen_mayor_100():
    with pytest.raises(ValueError):
        Altavoz("Salón", 101)