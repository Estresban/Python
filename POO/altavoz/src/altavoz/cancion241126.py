class Cancion:
    def __init__(self, titulo, artista, segundos):
        # Podrían ser propiedades, en este ejemplo se deja así por simplificar
        self.titulo = titulo
        self.artista = artista
        self.segundos = segundos

    def __str__(self):
        minutos, seg = divmod(self.segundos, 60)
        return f'{self.titulo} - {self.artista} ({minutos}:{seg:02d})'

    def __repr__(self):
        return f'Cancion({self.titulo!r}, {self.artista!r}, {self.segundos})'