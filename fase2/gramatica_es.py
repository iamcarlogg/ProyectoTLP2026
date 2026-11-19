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


# FASE 2: extensión declarativa. Mantenemos íntegra la CFG de Fase 1.
# Tiempo verbal: presente (sv_s/sv_p heredados), pretérito (sv_*_pret).
# Persona: los SN explícitos anteriores son de tercera persona;
# se añaden pronombres de primera persona y predicados concordantes.
# El motor de P1 solo consulta GRAMATICA e INICIAL: no cambia.

# Nuevas alternativas para tercera persona en pretérito.
GRAMATICA["oracion"].extend([
    ["sn_ms", "sv_s_pret"], ["sn_fs", "sv_s_pret"],
    ["sn_mp", "sv_p_pret"], ["sn_fp", "sv_p_pret"],
    ["pron_1s", "sv_1s_pres"], ["pron_1s", "sv_1s_pret"],
    ["pron_1p", "sv_1p_pres"], ["pron_1p", "sv_1p_pret"],
])

# Función de construcción estática de alternativas (sin validaciones externas).
def _alternativas_sv(v, vt):
    return [
        [v], [v, "adv"], [v, "sp"], [v, "adv", "sp"],
        [vt, "sn"], [vt, "sn", "adv"],
        [vt, "sn", "sp"], [vt, "sn", "adv", "sp"],
    ]

GRAMATICA.update({
    "sv_s_pret": _alternativas_sv("v_s_pret", "vt_s_pret"),
    "sv_p_pret": _alternativas_sv("v_p_pret", "vt_p_pret"),
    "sv_1s_pres": _alternativas_sv("v_1s_pres", "vt_1s_pres"),
    "sv_1p_pres": _alternativas_sv("v_1p_pres", "vt_1p_pres"),
    "sv_1s_pret": _alternativas_sv("v_1s_pret", "vt_1s_pret"),
    "sv_1p_pret": _alternativas_sv("v_1p_pret", "vt_1p_pret"),
    "pron_1s": [["yo"]],
    "pron_1p": [["nosotros"], ["nosotras"]],
    "v_s_pret": [["comió"], ["durmió"]],
    "v_p_pret": [["comieron"], ["durmieron"]],
    "vt_s_pret": [["comió"], ["persiguió"]],
    "vt_p_pret": [["comieron"], ["persiguieron"]],
    "v_1s_pres": [["como"], ["duermo"]],
    "v_1p_pres": [["comemos"], ["dormimos"]],
    "vt_1s_pres": [["como"], ["persigo"]],
    "vt_1p_pres": [["comemos"], ["perseguimos"]],
    "v_1s_pret": [["comí"], ["dormí"]],
    "v_1p_pret": [["comimos"], ["dormimos"]],
    "vt_1s_pret": [["comí"], ["perseguí"]],
    "vt_1p_pret": [["comimos"], ["perseguimos"]],
    "rel_suj_s_pret": [["que", "sv_s_pret"]],
    "rel_suj_p_pret": [["que", "sv_p_pret"]],
    "rel_obj_pret": [
        ["que", "sn_ms", "vt_s_pret"], ["que", "sn_fs", "vt_s_pret"],
        ["que", "sn_mp", "vt_p_pret"], ["que", "sn_fp", "vt_p_pret"],
    ],
})

# Relativas en pretérito y preposición con; se conserva la concordancia.
for _rasgo, _numero in (("ms", "s"), ("fs", "s"), ("mp", "p"), ("fp", "p")):
    GRAMATICA[f"mod_{_rasgo}"].extend([
        [f"rel_suj_{_numero}_pret"], ["rel_obj_pret"],
        [f"adj_{_rasgo}", f"rel_suj_{_numero}_pret"],
        [f"adj_{_rasgo}", "rel_obj_pret"],
    ])

GRAMATICA["p"].append(["con"])

# Negación de verbos intransitivos y coordinación de dos verbos simples;
# no se implementa la coordinación de sujetos ni de oraciones completas.
for _pred, _v in (("sv_s", "v_s"), ("sv_p", "v_p"),
                  ("sv_s_pret", "v_s_pret"), ("sv_p_pret", "v_p_pret")):
    GRAMATICA[_pred].extend([["no", _v], [_v, "y", _v]])

# Rasgos del vocabulario verbal: documentan persona, número y tiempo.
# Son metadatos para el estudio; el motor continúa usando solo GRAMATICA.
RASGOS_VERBALES = {
    "come": (3, "s", "presente"), "comen": (3, "p", "presente"),
    "duerme": (3, "s", "presente"), "duermen": (3, "p", "presente"),
    "persigue": (3, "s", "presente"), "persiguen": (3, "p", "presente"),
    "comió": (3, "s", "pretérito"), "comieron": (3, "p", "pretérito"),
    "durmió": (3, "s", "pretérito"), "durmieron": (3, "p", "pretérito"),
    "persiguió": (3, "s", "pretérito"), "persiguieron": (3, "p", "pretérito"),
    "como": (1, "s", "presente"), "comemos": (1, "p", "presente"),
    "duermo": (1, "s", "presente"),
    "dormimos": (1, "p", "presente/pretérito"),
    "persigo": (1, "s", "presente"), "perseguimos": (1, "p", "presente/pretérito"),
    "comí": (1, "s", "pretérito"), "comimos": (1, "p", "pretérito"),
    "dormí": (1, "s", "pretérito"), "perseguí": (1, "s", "pretérito"),
}
