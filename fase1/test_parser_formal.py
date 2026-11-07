"""P1 - Pruebas del parser de mini-C. Ejecutar con: pytest -v"""
import pytest

from lexer import ErrorDeAnalisis
from parser_formal import parsear_codigo

VALIDOS = [
    "int x;",
    "float y = 3.5;",
    "x = 2 + 3 * 4;",
    "x = (a + b) / 2;",
    "if (x > 1) x = 0;",
    "if (x > 1) { x = 0; } else { x = 1; }",
    "while (i < 10) { i = i + 1; }",
    "while (i < 10) { if (i == 5) { i = 0; } }",
    "{ }",
    "",
    "int x = 1; // comentario\nx = x / 2; // x / 2 no es comentario",
]

INVALIDOS = [
    "int x",                 # falta ;
    "x = ;",                 # falta el valor
    "if x > 1) x = 0;",      # falta (
    "while (i < 10 { }",     # falta )
    "else x = 1;",           # else sin if
    "int 5x = 3;",           # nombre que empieza con número
    "x = 2 +;",              # cuenta incompleta
    "{ int x;",              # llave sin cerrar
    "x = 5 @ 2;",            # carácter que no existe en el lenguaje
    "if (x) x = 0;",         # condición sin comparación
]


@pytest.mark.parametrize("codigo", VALIDOS)
def test_acepta_codigo_valido(codigo):
    assert parsear_codigo(codigo) is not None


@pytest.mark.parametrize("codigo", INVALIDOS)
def test_rechaza_codigo_invalido(codigo):
    with pytest.raises(ErrorDeAnalisis):
        parsear_codigo(codigo)


def test_la_multiplicacion_va_primero():
    asignacion = parsear_codigo("x = 2 + 3 * 4;")[0]
    expr = asignacion[1]
    assert expr[1] == "+"           # la suma está arriba
    assert len(expr[2]) == 3        # el lado derecho es "3 * 4" (factor, *, factor)


def test_el_else_se_pega_al_if_mas_cercano():
    arbol = parsear_codigo("if (a > 1) if (b > 1) x = 1; else x = 2;")
    si_externo = arbol[0]
    si_interno = si_externo[1]
    assert len(si_externo) == 2     # el if de afuera NO tiene else
    assert len(si_interno) == 3     # el else quedó en el if de adentro


def test_el_error_dice_la_linea():
    with pytest.raises(ErrorDeAnalisis, match="Línea 2"):
        parsear_codigo("int x;\nint y")
