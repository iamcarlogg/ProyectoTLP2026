"""Lexer de mini-C: convierte el código fuente en una lista de tokens."""
import re


class ErrorDeAnalisis(Exception):
    """Error del lexer o del parser. El mensaje dice dónde ocurrió."""
    # Cada pieza: (nombre del tipo, patrón). EL ORDEN IMPORTA.
TOKENS = [
    ("COMENTARIO", r"//[^\n]*"),          # va ANTES que OP_MULT
    ("NUM",        r"\d+(?:\.\d+)?"),     # 5, 3.14
    ("ID",         r"[A-Za-z_]\w*"),      # x, contador, _temp
    ("OP_REL",     r"==|!=|<=|>=|<|>"),   # va ANTES que ASIGNA
    ("ASIGNA",     r"="),
    ("OP_SUMA",    r"[+\-]"),
    ("OP_MULT",    r"[*/]"),
    ("LPAREN",     r"\("),
    ("RPAREN",     r"\)"),
    ("LLAVE_A",    r"\{"),
    ("LLAVE_C",    r"\}"),
    ("PUNTOYCOMA", r";"),
    ("SALTO",      r"\n"),
    ("ESPACIO",    r"[ \t\r]+"),
    ("DESCONOCIDO", r"."),               # cualquier otra cosa = error
]

PALABRAS_RESERVADAS = {"int", "float", "if", "else", "while"}

# Une todos los patrones en uno solo: (?P<COMENTARIO>...)|(?P<NUM>...)|...
PATRON = re.compile("|".join(f"(?P<{nombre}>{regex})" for nombre, regex in TOKENS))

class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo        # por ejemplo "NUM"
        self.valor = valor      # por ejemplo "5"
        self.linea = linea
        self.columna = columna

    def __repr__(self):
        return f"{self.tipo}({self.valor!r})"

def tokenizar(codigo):
    """Devuelve la lista de tokens del código. Termina siempre con un token EOF."""
    tokens = []
    linea = 1
    inicio_de_linea = 0     # posición donde empezó la línea actual

    for pieza in PATRON.finditer(codigo):
        tipo = pieza.lastgroup          # qué patrón coincidió
        valor = pieza.group()           # el texto exacto
        columna = pieza.start() - inicio_de_linea + 1

        if tipo == "SALTO":
            linea += 1
            inicio_de_linea = pieza.end()
            continue
        if tipo in ("ESPACIO", "COMENTARIO"):
            continue
        if tipo == "DESCONOCIDO":
            raise ErrorDeAnalisis(
                f"Línea {linea}, columna {columna}: carácter no válido {valor!r}"
            )
        if tipo == "ID" and valor in PALABRAS_RESERVADAS:
            tipo = valor.upper()        # "if" pasa a ser tipo "IF"

        tokens.append(Token(tipo, valor, linea, columna))

    tokens.append(Token("EOF", "", linea, 0))   # marca de "se acabó el código"
    return tokens


if __name__ == "__main__":
    #Puedes asignar a la variable el codigo que quieras tokenizar.
    code = "int x = 5; // comentario\nif (x >= 2) x = x * 3;"
    print(tokenizar(code))