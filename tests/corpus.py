"""Corpus de detecciones reales: patrones de uso común con cadenas etiquetadas.

Cada categoría tiene una ER y una lista de (cadena, esperado), donde
esperado es True si la cadena debe aceptarse. Las etiquetas se escribieron
a mano a partir de la definición de cada formato, no a partir de la salida
del programa.
"""

OCTETO = r"(\N|[1-9]\N|1\N\N|2[0-4]\N|25[0-5])"

CORPUS = {
    "Identificador (estilo C)": (
        r"(\z|_)(\z|\N|_)*",
        [
            ("x", True), ("contador", True), ("_temp", True), ("var1", True),
            ("MAX_VALOR", True), ("a1b2c3", True),
            ("1abc", False), ("", False), ("mi-var", False), ("hola mundo", False),
            ("9", False), ("año", False),
        ],
    ),
    "Entero con signo": (
        r"(\+|-|ε)\N\N*",
        [
            ("0", True), ("42", True), ("-17", True), ("+300", True), ("007", True),
            ("", False), ("-", False), ("+-1", False), ("12a", False), ("1.5", False),
            ("--3", False),
        ],
    ),
    "Número decimal": (
        r"\N\N*\.\N\N*",
        [
            ("3.1416", True), ("0.5", True), ("10.00", True),
            ("3.", False), (".5", False), ("3", False), ("3..1", False), ("3,14", False),
        ],
    ),
    "Número real con exponente": (
        r"(\+|-|ε)\N\N*(\.\N\N*|ε)((e|E)(\+|-|ε)\N\N*|ε)",
        [
            ("6.022e23", True), ("1E-9", True), ("-2.5", True), ("42", True),
            ("+1.0e+10", True),
            ("1e", False), ("e10", False), ("1.e5", False), ("2.5E", False),
            ("1e5.0", False),
        ],
    ),
    "Expresión aritmética": (
        r"\N\N*((\+|-|\*|/)\N\N*)*",
        [
            ("1+2*3", True), ("42", True), ("10/2-3", True), ("7*7*7", True),
            ("1+", False), ("+1", False), ("1++2", False), ("1 + 2", False),
        ],
    ),
    "Correo electrónico": (
        r"[a-z0-9_.][a-z0-9_.]*@\a\a*(\.\a\a*)*\.(com|org|net|gt)",
        [
            ("josue@miumg.edu.gt", True), ("juan.perez@gmail.com", True),
            ("a_1@org.org", True), ("x@y.net", True),
            ("@gmail.com", False), ("juan@", False), ("juan@gmail", False),
            ("juan@gmail.c", False), ("Juan@gmail.com", False),
            ("juan perez@gmail.com", False),
        ],
    ),
    "Teléfono de Guatemala": (
        r"(\+502\ |ε)[2-7]\N\N\N(-|ε)\N\N\N\N",
        [
            ("5555-1234", True), ("22223333", True), ("+502 4123-4567", True),
            ("+502 78901234", True),
            ("1234-5678", False), ("5555-123", False), ("+5025555-1234", False),
            ("5555--1234", False), ("8555-1234", False),
        ],
    ),
    "Placa vehicular de Guatemala": (
        r"[PMCAOTU](-|ε)\N\N\N\A\A\A",
        [
            ("P-123ABC", True), ("P123ABC", True), ("M-001XYZ", True), ("C555DFG", True),
            ("X-123ABC", False), ("P-12ABC", False), ("P-123abc", False),
            ("P-123ABCD", False), ("p-123ABC", False),
        ],
    ),
    "Carné UMG": (
        r"\N\N\N\N-\N\N-\N\N\N\N\N*",
        [
            ("0900-22-12345", True), ("1290-21-1234", True), ("5190-24-123456", True),
            ("0900-22-123", False), ("090-22-12345", False), ("0900/22/12345", False),
            ("0900-2-12345", False), ("0900-22-1234a", False),
        ],
    ),
    "DPI de Guatemala": (
        r"\N\N\N\N\ \N\N\N\N\N\ \N\N\N\N",
        [
            ("1234 56789 0101", True), ("2987 65432 0108", True),
            ("1234567890101", False), ("1234 5678 0101", False),
            ("1234 56789 010", False), ("1234-56789-0101", False),
        ],
    ),
    "Fecha dd/mm/aaaa": (
        r"(0[1-9]|[12]\N|3[01])/(0[1-9]|1[0-2])/\N\N\N\N",
        [
            ("31/10/2026", True), ("01/01/2000", True), ("29/02/2024", True),
            ("15/09/1821", True),
            ("32/10/2026", False), ("00/10/2026", False), ("10/13/2026", False),
            ("1/10/2026", False), ("31-10-2026", False), ("31/10/26", False),
        ],
    ),
    "Hora de 24 horas": (
        r"([01]\N|2[0-3]):[0-5]\N",
        [
            ("00:00", True), ("09:30", True), ("23:59", True), ("12:05", True),
            ("24:00", False), ("7:30", False), ("12:60", False), ("12:5", False),
            ("1230", False),
        ],
    ),
    "Dirección IPv4": (
        OCTETO + r"\." + OCTETO + r"\." + OCTETO + r"\." + OCTETO,
        [
            ("192.168.1.1", True), ("10.0.0.255", True), ("255.255.255.255", True),
            ("8.8.8.8", True), ("0.0.0.0", True),
            ("256.1.1.1", False), ("192.168.1", False), ("192.168.01.1", False),
            ("1.2.3.4.5", False), ("192.168.1.300", False), ("a.b.c.d", False),
        ],
    ),
    "Número hexadecimal": (
        r"0(x|X)[0-9a-fA-F][0-9a-fA-F]*",
        [
            ("0xFF", True), ("0X1a2B", True), ("0x0", True),
            ("0x", False), ("FF", False), ("0xG1", False), ("x12", False), ("00x1", False),
        ],
    ),
    "Color hexadecimal CSS": (
        r"#[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]|ε)",
        [
            ("#fff", True), ("#1A2B3C", True), ("#000000", True),
            ("#ff", False), ("#ffff", False), ("fff", False), ("#ggg", False),
            ("#1234567", False),
        ],
    ),
    "Palabras reservadas": (
        r"if|else|while|for|return",
        [
            ("if", True), ("else", True), ("while", True), ("for", True), ("return", True),
            ("iff", False), ("For", False), ("whil", False), ("returns", False), ("", False),
        ],
    ),
    "Literal de cadena": (
        r'"[^"]*"',
        [
            ('"hola"', True), ('""', True), ('"a b c"', True), ('"123"', True),
            ('"hola', False), ('hola"', False), ('"a"b"', False), ("'hola'", False),
        ],
    ),
    "Comentario de bloque C": (
        r"/\*[^*]*\*\**([^/*][^*]*\*\**)*/",
        [
            ("/* hola */", True), ("/**/", True), ("/* a * b */", True),
            ("/*** x ***/", True),
            ("/* hola", False), ("/* a */ b */", False), ("// hola", False), ("/*/", False),
        ],
    ),
    "URL simplificada": (
        r"http(s|ε)://\z(\z|\N|-)*(\.\z(\z|\N|-)*)*(/(\z|\N|-|_|\.)*)*",
        [
            ("https://umg.edu.gt", True), ("http://example.com/index.html", True),
            ("https://www.google.com/", True), ("http://localhost", True),
            ("htp://umg.edu.gt", False), ("https//umg.edu.gt", False), ("https://", False),
            ("ftp://x.com", False), ("https://-umg.com", False),
        ],
    ),
    "Nombre propio": (
        r"\A\a*(\h20\A\a*)*",
        [
            ("Josue", True), ("Josue Garcia", True), ("Ana Maria Lopez", True), ("X", True),
            ("josue", False), ("Josue  Garcia", False), ("Josue garcia", False),
            ("JOSUE", False), ("Josue ", False),
        ],
    ),
    "Binario con cantidad par de unos": (
        r"0*(10*10*)*",
        [
            ("", True), ("0", True), ("11", True), ("1010", True), ("0110", True),
            ("1111", True),
            ("1", False), ("10", False), ("111", False), ("0100", False),
        ],
    ),
    "Contiene la palabra umg": (
        r".*umg.*",
        [
            ("umg", True), ("la umg es grande", True), ("xumgx", True), ("UMGumg", True),
            ("um g", False), ("UMG", False), ("", False), ("mug", False),
        ],
    ),
    "Libro del Dragón (a|b)*abb": (
        r"(a|b)*abb",
        [
            ("abb", True), ("aabb", True), ("babb", True), ("ababb", True),
            ("ab", False), ("abba", False), ("", False), ("abc", False),
        ],
    ),
}
