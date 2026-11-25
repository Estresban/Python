from src.altavoz.cancion241126 import Cancion
from src.altavoz.playlist import Playlist


def main() -> None:
    c1 = Cancion("La vereda de la puerta de atras","Extremo",305)
    print (c1)
    print (repr(c1))
    
    
    
    c2 = Cancion("Deltoya","Extremo",234)
    print (c1 == c2)
    
    if (c1 > c2):
        print ("No es mayor")
    else :
        print ("Es mayor")
    



mi_lista = Playlist('Estudio')
mi_lista.añadir(Cancion('Sol', 'Ana', 180))
mi_lista.añadir(Cancion('Luna', 'Ana', 200))




len(mi_lista)                      # 2
for c in mi_lista: print(c)        # recorre con for
Cancion('Sol', 'Ana', 999) in mi_lista   # True
sorted(mi_lista)                   # de la más corta a la más larga