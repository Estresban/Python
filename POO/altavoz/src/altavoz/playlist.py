class Playlist:
    def __init__(self, nombre):
        # nombre podría ser propiedad, en este ejemplo se deja así por simplificar
        self.nombre = nombre
        self._canciones = []

    def añadir(self, cancion):
        self._canciones.append(cancion)

    @property
    def duracion_total(self):
        return sum(c.segundos for c in self._canciones)

    def __len__(self):
        return len(self._canciones)

    def __iter__(self):
        return iter(self._canciones)

    def __contains__(self, cancion):
        return cancion in self._canciones