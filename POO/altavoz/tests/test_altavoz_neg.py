import pytest
from src.altavoz.altavoz import Altavoz

'''
# Crear un altavoz con nombre ""
def test_negat01_nombre_vacio():
    with pytest.raises(ValueError):
        Altavoz("", 50)
'''
# Crear un altavoz con nombre 25
def test_negat03_nombre_no_string():
    with pytest.raises(ValueError):
        Altavoz(25, 50)
