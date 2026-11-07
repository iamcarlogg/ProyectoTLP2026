"""P1 - Parser descendente recursivo de mini-C. Una función por cada regla de la gramática."""
from nltk import Tree

from lexer import ErrorDeAnalisis, tokenizar

# Cómo mostrar cada tipo de token en los mensajes de error
NOMBRES = {
    "ID": "un nombre de variable", "NUM": "un número", "ASIGNA": "'='",
    "PUNTOYCOMA": "';'", "LPAREN": "'('", "RPAREN": "')'",
    "LLAVE_A": "'{'", "LLAVE_C": "'}'", "OP_REL": "una comparación (<, >, ==...)",
    "EOF": "el fin del código",
}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0                      # índice del token que estamos mirando

    # ---------- Herramientas básicas ----------

    def actual(self):
        """El token que toca revisar ahora."""
        return self.tokens[self.pos]

    def ver(self, *tipos):
        """¿El token actual es de alguno de estos tipos? (no avanza)"""
        return self.actual().tipo in tipos

    def consumir(self, tipo):
        """Exige un token de este tipo y avanza. Si no está, lanza un error."""
        token = self.actual()
        if token.tipo != tipo:
            self.error(f"se esperaba {NOMBRES.get(tipo, tipo)}")
        self.pos += 1
        return token

    def error(self, mensaje):
        """Lanza ErrorDeAnalisis con la línea y lo que se encontró en lugar de lo esperado."""
        token = self.actual()
        encontrado = f"'{token.valor}'" if token.valor else "el fin del código"
        raise ErrorDeAnalisis(f"Línea {token.linea}: {mensaje} y se encontró {encontrado}")

    # ---------- Una función por regla ----------

    def programa(self):
        # programa → sentencia* EOF
        hijos = []
        while not self.ver("EOF"):
            hijos.append(self.sentencia())
        self.consumir("EOF")
        return Tree("programa", hijos)

    def sentencia(self):
        # sentencia → declaracion | asignacion | si | mientras | bloque
        # Miramos el primer token para decidir qué regla usar.
        if self.ver("INT", "FLOAT"):
            return self.declaracion()
        if self.ver("ID"):
            return self.asignacion()
        if self.ver("IF"):
            return self.si()
        if self.ver("WHILE"):
            return self.mientras()
        if self.ver("LLAVE_A"):
            return self.bloque()
        self.error("se esperaba el inicio de una instrucción")

    def declaracion(self):
        # declaracion → tipo ID ( '=' expr )? ';'
        hijos = [self.tipo(), self.consumir("ID").valor]
        if self.ver("ASIGNA"):                          # el "= valor" es opcional
            self.consumir("ASIGNA")
            hijos.append(self.expr())
        self.consumir("PUNTOYCOMA")
        return Tree("declaracion", hijos)

    def tipo(self):
        # tipo → 'int' | 'float'
        if self.ver("INT"):
            return Tree("tipo", [self.consumir("INT").valor])
        return Tree("tipo", [self.consumir("FLOAT").valor])

    def asignacion(self):
        # asignacion → ID '=' expr ';'
        nombre = self.consumir("ID")
        self.consumir("ASIGNA")
        valor = self.expr()
        self.consumir("PUNTOYCOMA")
        return Tree("asignacion", [nombre.valor, valor])

    def si(self):
        # si → 'if' '(' condicion ')' sentencia ( 'else' sentencia )?
        self.consumir("IF")
        self.consumir("LPAREN")
        cond = self.condicion()
        self.consumir("RPAREN")
        hijos = [cond, self.sentencia()]
        if self.ver("ELSE"):        # el else se pega al if más cercano
            self.consumir("ELSE")
            hijos.append(Tree("sino", [self.sentencia()]))
        return Tree("si", hijos)

    def mientras(self):
        # mientras → 'while' '(' condicion ')' sentencia
        self.consumir("WHILE")
        self.consumir("LPAREN")
        cond = self.condicion()
        self.consumir("RPAREN")
        return Tree("mientras", [cond, self.sentencia()])

    def bloque(self):
        # bloque → '{' sentencia* '}'
        self.consumir("LLAVE_A")
        hijos = []
        while not self.ver("LLAVE_C", "EOF"):   # EOF: llave sin cerrar → error en consumir
            hijos.append(self.sentencia())
        self.consumir("LLAVE_C")
        return Tree("bloque", hijos)

    def condicion(self):
        # condicion → expr OP_REL expr
        izquierda = self.expr()
        operador = self.consumir("OP_REL")
        derecha = self.expr()
        return Tree("condicion", [izquierda, operador.valor, derecha])

    def expr(self):
        # expr → termino ( ( '+' | '-' ) termino )*
        hijos = [self.termino()]
        while self.ver("OP_SUMA"):
            hijos.append(self.consumir("OP_SUMA").valor)
            hijos.append(self.termino())
        return Tree("expr", hijos)

    def termino(self):
        # termino → factor ( ( '*' | '/' ) factor )*
        hijos = [self.factor()]
        while self.ver("OP_MULT"):
            hijos.append(self.consumir("OP_MULT").valor)
            hijos.append(self.factor())
        return Tree("termino", hijos)

    def factor(self):
        # factor → NUM | ID | '(' expr ')'
        if self.ver("NUM"):
            return Tree("factor", [self.consumir("NUM").valor])
        if self.ver("ID"):
            return Tree("factor", [self.consumir("ID").valor])
        if self.ver("LPAREN"):
            self.consumir("LPAREN")
            dentro = self.expr()
            self.consumir("RPAREN")
            return Tree("factor", ["(", dentro, ")"])
        self.error("se esperaba un número, una variable o '('")


def parsear_codigo(codigo):
    """Recibe texto de mini-C. Devuelve el árbol o lanza ErrorDeAnalisis."""
    return Parser(tokenizar(codigo)).programa()


if __name__ == "__main__":
    ejemplo = """
    int x = 2 + 3 * 4;   // el 3 * 4 queda junto en un termino
    while (x > 0) {
        x = x - 1;
    }
    """
    arbol = parsear_codigo(ejemplo)
    print(arbol)            # en notación de corchetes
    arbol.pretty_print()    # dibujado en la terminal

    try:
        parsear_codigo("int y = 5")
    except ErrorDeAnalisis as e:
        print("Error:", e)
