import pytest
from src.altavoz.altavoz import Altavoz


# Crear un altavoz con nombre ""
def test_negat01_nombre_vacio():
    with pytest.raises(ValueError):
        Altavoz("", 50)

