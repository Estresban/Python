


class Carta:
    PALOS_VALIDOS = ('Oros', 'Copas', 'Espadas', 'Bastos')

    def __init__(self, valor, palo):
        self.valor = valor
        self.palo = palo
        
        @property
        def valor(self): 
            return self._valor
        
        
        @valor.setter
        def valor(self, nuevo_valor):
            if not isinstance(nuevo_valor, int) or isinstance(nuevo_valor, bool) or not (1 <= nuevo_valor <= 12):
                raise ValueError('El valor debe ser un número entre 1 y 12')
            self._valor = nuevo_valor
            
        @property
        def palo(self): 
            return self._palo
        
        @palo.setter
        def palo(self, nuevo_palo):
            if nuevo_palo not in self.PALOS_VALIDOS:
                raise ValueError (f'Palo no válido. Debe ser uno de: {self.PALOS_VALIDOS}')
            self._palo = nuevo_palo
            
            
        def __str__(self):
            return f'{self.valor} de {self.palo}'
            
        def __repr__(self):
            return f"Carta({self.valor}, '{self.palo}')"
        
        def __hash__(self):
            return hash((self.valor, self.palo))
        
        def __eq__(self, otra):
            if not isinstance(otra, Carta):
                return NotImplemented
            return self.valor == otra.valor and self.palo == otra.palo
                
        def __lt__(self,otra):
            if not isinstance(otra, Carta):
                return NotImplemented
            return self.valor < otra.valor
        
        
