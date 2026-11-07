"""Errores del programa."""


class ErrorSintaxis(Exception):
    """Error en la sintaxis de una expresión regular, con su posición."""

    def __init__(self, mensaje: str, expresion: str, posicion: int):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.expresion = expresion
        self.posicion = posicion

    def __str__(self) -> str:
        return "%s (posición %d)\n  %s\n  %s^" % (
            self.mensaje,
            self.posicion + 1,
            self.expresion,
            " " * self.posicion,
        )
