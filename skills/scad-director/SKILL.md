---
name: scad-director
description: "Dirección visual de ensambles OpenSCAD: contrato de orientación, parámetros Customizer manipulables por el usuario y protocolo de corrección sobre captura."
triggers:
  - "mover el tornillo"
  - "acomodar elementos"
  - "enfrente / atrás / arriba"
  - "customizer"
  - "no te entiendo"
  - "así no, quiero"
---

# Skill: SCAD Director (Dirección Visual de Ensambles)

## 0. Problema que resuelve

El usuario ve una vista 3D y dice "enfrente"; el agente lee ejes Y/Z sin ver su cámara.
Esta skill impone un marco común para que ambos hablen del mismo espacio.

## 1. Contrato de Orientación (obligatorio en todo ensamble visual)

- `+Z` = **arriba**, siempre. Sin excepciones.
- `-Y` = **enfrente** (lado cuarto / usuario, donde se para quien opera el equipo).
- `+Y` = **atrás** (lado tapa / costilla, donde vive la tornillería existente).
- `±X` = **lados** (izquierda/derecha visto de frente).
- Todo `.scad` de ensamble DEBE llevar este bloque en el encabezado:
  `// ORIENTACION: +Z arriba, -Y enfrente (usuario), +Y atras (tapa).`

## 2. Vistas canónicas (nombrarlas siempre igual)

| Vista   | Cámara OpenSCAD (ojo -> centro)                | Uso                          |
|---------|------------------------------------------------|------------------------------|
| frente  | `[CX,-200,CZ] -> [CX,4,CZ]`                    | Cara que ve el usuario       |
| atras   | `[CX,200,CZ] -> [CX,4,CZ]`                     | Lado tapa                    |
| perfil  | `[CX+200,4,CZ] -> [CX,4,CZ]`                   | Grosores y stacks en Y       |
| oblicua | `[CX+150,-150,CZ+60] -> [CX,4,CZ]`             | Verificación general         |
| general | `--autocenter --viewall`                       | Escala contra la pieza madre |

`CX/CZ` = centro del detalle (ej. `PIN_X`, `PIN_Z+30`).
Toda verificación visual entrega mínimo `frente` + `oblicua`.

## 3. Parámetros Customizer (el usuario mueve, el agente fija)

Toda variable que el usuario pueda querer mover en vivo DEBE exponerse con
anotaciones Customizer, agrupada por pestaña. Sintaxis OpenSCAD válida:

```openscad
/* [Posicion del tornillo] */
TORN_DZ = 60; // [40:0.5:80] - altura sobre el punto rojo (eje Z)
TORN_LADO = "frente"; // ["frente", "atras"] - cara de entrada del tornillo
```

Reglas:
- Sliders con paso útil (`0.5` para cotas, `1` para conteos). Rango = ±50% del nominal.
- Dropdowns con vocabulario del contrato (`frente`/`atras`, nunca `+Y`/`-Y` solos).
- La geometría se deriva de estas variables con `?:` (ej. asiento de arandela
  según `TORN_LADO`), jamás con fórmulas editadas a mano por el usuario.
- Los comentarios CLI (`openscad -D ...`) siguen funcionando: Customizer son comentarios.

## 4. Protocolo de corrección sobre captura

1. El agente entrega renders nombrados por vista (`ensamble_frente.png`, ...).
2. El usuario corrige con captura anotada (flecha + cota + nombre de vista).
3. El agente responde con: variable + número de línea + render de verificación
   **desde esa misma vista**. Prohibido responder solo con texto.
4. Si la indicación admite dos lecturas (eje vs. lado), preguntar con opciones
   cerradas antes de editar (una sola pregunta, con los ejes explícitos).

## 5. Vocabulario prohibido / obligatorio

- Prohibido: "muévelo para allá", "voltear" (sin eje), "más adentro" (sin cara).
- Obligatorio: verbo + eje + magnitud + referencia
  (ej. "sube el tornillo 5 mm en Z sobre el punto rojo").
