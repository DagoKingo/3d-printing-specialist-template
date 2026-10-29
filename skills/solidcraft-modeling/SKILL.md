---
name: solidcraft-modeling
description: "Modelado greenfield preferido en SolidCraft vía MCP: sketches paramétricos, features sólidas, parámetros, verificación con measure y exportación a STEP/STL/3MF."
triggers:
  - "SolidCraft"
  - "modelar en solidcraft"
  - "diseño nuevo solidcraft"
  - "pieza nueva"
---

# Skill: SolidCraft Modeling (Track A1, preferido)

Fuente canónica de comandos: el propio servidor MCP (`list_commands` + `describe_command`).
Referencia: `https://docs.solidcraft.io/guide/mcp.html`.

## 0. Arranque y carpetas

```sh
solidcraft-cli mcp --in pieza.sc        # headless, parte de un diseño
solidcraft-cli mcp --allow-path ~/repos/pry-gmsc00055-3dpieces   # permite guardar/exportar en el repo
```

Solo se puede leer/escribir dentro de: carpeta del diseño abierto,
carpetas abiertas/guardadas en la sesión, scratch del servidor y cada
`--allow-path`. El repo vive en `~`, así que queda cubierto con el flag.

## 1. Flujo de modelado

1. `list_commands` (con `filter` si hace falta) y `describe_command {id}`
   antes de usar un comando nuevo. No inventar parámetros.
2. Construir en `batch` (pasos ordenados, para al primer error, `rollback: true`
   restaura el diseño). Ejemplo documentado:
   `sketch.create` (plano XY) → `sketch.rectangle.two_point` → `sketch.finish`
   → `solid.extrude` → `solid.fillet`.
3. Cotas que el usuario pueda cambiar después van a parámetros
   (`set_parameter {name, value|expression}`), nunca hardcodeadas dos veces.
4. Tras cada feature relevante: `inspect_design` (timeline, bodies, sketches)
   y `measure` (volumen, bbox, `closed` por cuerpo).
5. `screenshot {view: iso}` para inspección visual; enseñable al usuario.

## 2. Reglas del repo

- El `.sc` editable vive bloqueado al draft (`pieces/<pieza>/prototypes/draft-[N]/`).
- Exportar a STL con `export {path, format: stl}` en Z-up, Z=0, y pasar
  `scripts/verify_mesh.py --manifest` + `scripts/export_3mf.py` como
  cualquier otro track. El Gate no se salta por modelar en SolidCraft.
- Ante la duda de acabados/tolerancias/soporte, aplica igual Reglas 4, 11 y 13
  de `AGENTS.md` ($slop, zonificación A/B/C, anti-spaghetti).
- `undo`/`redo` para retroceder; `document.revision` para saber si el diseño
  cambió sin releerlo todo.
