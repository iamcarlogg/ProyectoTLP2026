# 5. Dónde sí falla una CFG: dependencias cruzadas — P2 (análisis formal)

Los documentos 3 y 4 concluyen que **ninguna de nuestras fallas demuestra que el español no sea libre de contexto**: todas son reglas que faltan, y la concordancia de género y número se puede codificar en una CFG a cambio de más reglas. Este documento responde la pregunta que queda: entonces, **¿qué fenómeno sí rompe a una CFG y a qué nivel de Chomsky pertenece?**

## 1. Por qué nuestras pruebas nunca salieron de Tipo 2

En una oración como la 15 de la tarea 1:

```text
El perro  que  la gata  persigue  duerme
   └──────────── 1 ──────────────────┘     perro ↔ duerme
              └─── 2 ──────┘               gata  ↔ persigue
```

Las dependencias están **anidadas**: la de adentro (gata ↔ persigue) se abre y se cierra dentro de la de afuera (perro ↔ duerme). Si se anidan más relativas, el patrón sigue igual:

```text
El perro que la gata que el ratón mira persigue duerme
sujeto₁ sujeto₂ sujeto₃ verbo₃ verbo₂ verbo₁
```

Ese patrón es el lenguaje **aⁿ bⁿ** (n sujetos seguidos de n verbos en orden inverso), el ejemplo clásico de lenguaje **libre de contexto**: una pila lo reconoce porque el último sujeto que entra es el primer verbo que sale. Por eso la gramática extendida resolvió bien la concordancia dentro de las relativas sin salir de Tipo 2.

## 2. Lo que una pila no puede hacer: dependencias cruzadas

El problema aparece cuando las dependencias se **cruzan** en lugar de anidarse:

```text
anidadas:  A₁ A₂ A₃  B₃ B₂ B₁    ← una pila lo resuelve (CFG)
cruzadas:  A₁ A₂ A₃  B₁ B₂ B₃    ← una pila NO lo resuelve
```

En el patrón cruzado, el primer elemento que entra tiene que ser el primero que sale. Una pila devuelve el último, así que un autómata de pila (y por tanto una CFG) no puede emparejarlos cuando la cantidad no tiene límite.

### Ejemplo en español: «respectivamente»

```text
Juan  y  Ana   son  alto  y  alta,  respectivamente.
 m       f           m       f
 └───────────────────┘                Juan ↔ alto
         └──────────────────┘         Ana  ↔ alta
```

El primer sustantivo concuerda con el primer adjetivo y el segundo con el segundo: las dependencias se cruzan. Si la lista puede crecer sin límite, la secuencia de géneros de los adjetivos tiene que **copiar** la de los sustantivos. Eso forma el lenguaje copia **{ w w : w ∈ {m, f}* }**, que no es libre de contexto.

**Advertencia para la defensa:** este ejemplo sirve para ilustrar la idea, pero no se acepta como prueba. Pullum y Gazdar (1982) señalaron que no está claro si esa concordancia es una regla sintáctica o un efecto del significado. Además, los hablantes no siempre rechazan los desacuerdos en listas largas.

### La prueba aceptada: alemán suizo (Shieber, 1985)

En alemán suizo, los objetos y los verbos que los rigen aparecen en orden cruzado, y el caso gramatical lo hace visible:

```text
… das mer  d'chind   em Hans   es huus   lönd   hälfe   aastriiche
… que nosotros  a los niños  a Hans  la casa  dejamos  ayudar  pintar
              (acusativo)  (dativo)          (pide acus.) (pide dat.)
```

«lönd» (dejar) exige un objeto en acusativo y «hälfe» (ayudar) uno en dativo, y el orden es objeto₁ objeto₂ verbo₁ verbo₂. Aquí sí es una regla sintáctica: si el caso no coincide, la oración es agramatical. Shieber intersecta ese fragmento con un lenguaje regular y obtiene un lenguaje de la forma **aᵐ bⁿ cᵐ dⁿ**, que no es libre de contexto. Como los lenguajes libres de contexto son cerrados bajo intersección con lenguajes regulares, el alemán suizo tampoco puede ser libre de contexto.

## 3. Demostración: aᵐ bⁿ cᵐ dⁿ no es libre de contexto

Por el **lema de bombeo** para lenguajes libres de contexto:

1. Suponemos que L = { aᵐ bⁿ cᵐ dⁿ | m, n ≥ 1 } es libre de contexto, con constante de bombeo p.
2. Tomamos z = aᵖ bᵖ cᵖ dᵖ, que está en L y tiene longitud mayor que p.
3. El lema dice que z = u v w x y, con |v w x| ≤ p y |v x| ≥ 1, y que u vⁱ w xⁱ y ∈ L para todo i ≥ 0.
4. Como |v w x| ≤ p, ese tramo toca **a lo sumo dos bloques vecinos** (por ejemplo, a y b, o b y c). Nunca alcanza a la vez la a y la c, ni la b y la d.
5. Al bombear (i = 2) cambia la cantidad de, como mucho, dos letras vecinas. Para seguir en L tendrían que cambiar juntas las a y las c (o las b y las d), que no son vecinas. Si v o x mezclan letras, además se rompe el orden de los bloques.
6. Contradicción: L no es libre de contexto. ∎

## 4. A qué nivel de Chomsky corresponde

| Patrón | Ejemplo | Lenguaje formal | Nivel |
| --- | --- | --- | --- |
| Concordancia finita (género, número) | el perro / *la perro | finito, se enumera | **Tipo 2** (cuesta reglas, ver documento 4) |
| Dependencias anidadas | relativas encajadas | aⁿ bⁿ | **Tipo 2** |
| Dependencias cruzadas sin límite | alemán suizo; «respectivamente» | aᵐ bⁿ cᵐ dⁿ, { w w } | **Fuera de Tipo 2**; dentro de **Tipo 1** |

Más precisamente, estos fenómenos caen en los lenguajes **ligeramente sensibles al contexto** (Joshi, 1985): una clase entre Tipo 2 y Tipo 1, que reconocen formalismos como las gramáticas de adjunción de árboles (TAG). No hace falta todo el poder de Tipo 1, pero sí más que una CFG.

## 5. Cómo se conecta con nuestro trabajo

- **Tareas 1 a 4:** todas las fallas eran reglas ausentes, porque nuestras oraciones solo tenían dependencias anidadas y rasgos finitos. Era lo esperable según este análisis.
- **Tarea 5:** si se limita la lista de «respectivamente» a k elementos, una CFG sí la cubre, enumerando las 2ᵏ combinaciones de género. Es la misma explosión de reglas del documento 4, pero exponencial. El límite práctico (cada vez más reglas) y el límite teórico (sin cota, ninguna CFG alcanza) son dos caras del mismo problema.
- **Conclusión para el informe:** el español controlado que probamos es libre de contexto. Lo que excede a las CFG en el lenguaje natural son las dependencias cruzadas no acotadas. En español solo hay ejemplos discutibles; la prueba aceptada viene del alemán suizo.

## Referencias

- Bar-Hillel, Y. y Shamir, E. (1960). Primer argumento con «respectively» contra la libertad de contexto del inglés.
- Pullum, G. K. y Gazdar, G. (1982). *Natural languages and context-free languages*. Linguistics and Philosophy, 4.
- Shieber, S. M. (1985). *Evidence against the context-freeness of natural language*. Linguistics and Philosophy, 8.
- Joshi, A. K. (1985). Lenguajes ligeramente sensibles al contexto y gramáticas de adjunción de árboles.
