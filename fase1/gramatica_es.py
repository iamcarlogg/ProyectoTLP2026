"""P2 - Gramatica extendida del espanol (Fase 1, tarea 3).

Se utiliza directamente con el motor descendente de P1 (motor.py).
Cubre:
- Concordancia de genero y numero dentro del sintagma nominal.
- Concordancia de numero sujeto-verbo, tambien con una relativa intermedia.
- Clausulas relativas de sujeto ("el perro que come") y de objeto
  ("el perro que la gata persigue").
- Modificadores: adjetivos, adverbios y sintagmas preposicionales.

Es un subconjunto CONTROLADO del espanol, no un parser general.
Las reglas son una CFG expresada como diccionario: no se usan
validaciones imperativas adicionales ni se modifica motor.py.
"""

GRAMATICA = {
    # El sujeto determina el NUMERO del verbo principal.
    "oracion": [
        ["sn_ms", "sv_s"],
        ["sn_fs", "sv_s"],
        ["sn_mp", "sv_p"],
        ["sn_fp", "sv_p"],
    ],

    # Un SN puede ser objeto directo o termino de una preposicion.
    "sn": [["sn_ms"], ["sn_fs"], ["sn_mp"], ["sn_fp"]],

    # Concordancia INTERNA: determinante, nombre y modificadores
    # comparten genero (m/f) y numero (s/p).
    "sn_ms": [["det_ms", "n_ms", "mod_ms"]],
    "sn_fs": [["det_fs", "n_fs", "mod_fs"]],
    "sn_mp": [["det_mp", "n_mp", "mod_mp"]],
    "sn_fp": [["det_fp", "n_fp", "mod_fp"]],

    # [] es epsilon: SN sin modificador. Se evitan reglas recursivas
    # por la izquierda (no admitidas por el motor de P1).
    "mod_ms": [
        [], ["adj_ms"], ["sp"], ["adj_ms", "sp"],
        ["rel_suj_s"], ["rel_obj"],
        ["adj_ms", "rel_suj_s"], ["adj_ms", "rel_obj"],
    ],
    "mod_fs": [
        [], ["adj_fs"], ["sp"], ["adj_fs", "sp"],
        ["rel_suj_s"], ["rel_obj"],
        ["adj_fs", "rel_suj_s"], ["adj_fs", "rel_obj"],
    ],
    "mod_mp": [
        [], ["adj_mp"], ["sp"], ["adj_mp", "sp"],
        ["rel_suj_p"], ["rel_obj"],
        ["adj_mp", "rel_suj_p"], ["adj_mp", "rel_obj"],
    ],
    "mod_fp": [
        [], ["adj_fp"], ["sp"], ["adj_fp", "sp"],
        ["rel_suj_p"], ["rel_obj"],
        ["adj_fp", "rel_suj_p"], ["adj_fp", "rel_obj"],
    ],

    # Relativa de sujeto: el antecedente controla el NUMERO del verbo.
    "rel_suj_s": [["que", "sv_s"]],
    "rel_suj_p": [["que", "sv_p"]],

    # Relativa de objeto: el antecedente es objeto omitido del verbo;
    # el sujeto EXPLICITO dentro de la relativa controla su verbo.
    # Ej.: "el perro que la gata persigue duerme".
    "rel_obj": [
        ["que", "sn_ms", "vt_s"],
        ["que", "sn_fs", "vt_s"],
        ["que", "sn_mp", "vt_p"],
        ["que", "sn_fp", "vt_p"],
    ],

    # Predicados: verbo solo, con adverbio/preposicion, o verbo
    # transitivo con objeto. El SP puede adjuntarse tambien al objeto,
    # generando dos arboles en oraciones estructuralmente ambiguas.
    "sv_s": [
        ["v_s"], ["v_s", "adv"], ["v_s", "sp"],
        ["v_s", "adv", "sp"],
        ["vt_s", "sn"], ["vt_s", "sn", "adv"],
        ["vt_s", "sn", "sp"], ["vt_s", "sn", "adv", "sp"],
    ],
    "sv_p": [
        ["v_p"], ["v_p", "adv"], ["v_p", "sp"],
        ["v_p", "adv", "sp"],
        ["vt_p", "sn"], ["vt_p", "sn", "adv"],
        ["vt_p", "sn", "sp"], ["vt_p", "sn", "adv", "sp"],
    ],

    "sp": [["p", "sn"]],
    "p": [["en"]],
    "adv": [["lentamente"], ["rápidamente"]],

    # Vocabulario reducido, con rasgos codificados en los nombres.
    "det_ms": [["el"]],
    "det_fs": [["la"]],
    "det_mp": [["los"]],
    "det_fp": [["las"]],

    "n_ms": [["perro"], ["jardín"]],
    "n_fs": [["gata"], ["carne"], ["casa"]],
    "n_mp": [["perros"]],
    "n_fp": [["gatas"]],

    "adj_ms": [["negro"]],
    "adj_fs": [["negra"]],
    "adj_mp": [["negros"]],
    "adj_fp": [["negras"]],

    "v_s": [["come"], ["duerme"]],
    "v_p": [["comen"], ["duermen"]],
    "vt_s": [["come"], ["persigue"]],
    "vt_p": [["comen"], ["persiguen"]],
}

INICIAL = "oracion"