---
name: solidcraft-editing
description: "Modificar diseños SolidCraft existentes o remodelar sobre STEP importado: timeline, parámetros, rollback seguro y re-exportación."
triggers:
  - "editar solidcraft"
  - "modificar pieza solidcraft"
  - "remodelar step"
---

# Skill: SolidCraft Editing (Track A1)

## 0. Apertura

- Diseño propio: `open {path: pieza.sc}`.
- Base de otro CAD (p. ej. FreeCAD): `open {path: base.step}` lo importa como
  sólido base; es geometría muerta (sin historial). Si el STEP viene con +Y
  arriba, abrir con `up: "y"` o enderezar con
  `solid.move {bodies: [...], axis: [1,0,0], angle: 90}` (grados).
- `new_design` reemplaza el diseño abierto (destructivo): solo para empezar
  de cero.

## 1. Edición segura

1. Leer definición del feature con `timeline.inspect {feature}` y cambiar
   campos con `timeline.edit {feature, set}` (los campos por tipo figuran en
   el capítulo *Solid features* del libro; ante duda, `describe_command`).
2. Preferir `set_parameter` para cambios dimensionales: un solo rebuild.
3. Agrupar ediciones encadenadas en un `batch` con `rollback: true`:
   si un paso falla, el diseño vuelve al checkpoint previo al batch
   (`rolled_back: true` lo confirma).
4. No reenviar un cambio si una llamada anterior sigue corriendo
   (`still running:`): consultar `pending` o `running` primero e inspeccionar
   el diseño antes de actuar.

## 2. Mirror: sólido y corte van separados

- Un Mirror admite varias fuentes, pero si el corte depende de la cara
  del extruido (padre-hijo, ej. `towersExtrude` + `towersHoles` tipo Hole),
  el Mirror conjunto pierde referencia y el corte sale parcial.
- Patrón fiable: `Mirror1` solo el extruido, `Mirror2` solo el corte,
  mismo plano. Verificar 4 copias antes del Fillet.
- Excepción verificada (case-12v, 0.26.0): el Mirror del corte puede dar
  falso positivo `1 of 1 cut copies remove no material` aun con sketch en
  plano global y geometría correcta (agujeros espejados medidos en su sitio).
  Fix definitivo: círculos espejados con `sketch.mirror` dentro del mismo
  sketch (constraints symmetric, paramétrico) y un solo corte; o centros
  directos y eliminar el Mirror del corte. Timeline sin warnings.
- **Agujeros amarrados a su geometría receptora (lección case-12v):**
  prohibido fijar centros de agujero por coordenadas absolutas. El centro
  se amarra al mid de su torre (aristas proyectadas como referencia en el
  mismo sketch, o cotas manejadas a muros/origen). Verificar no solo
  posición sino asociatividad: si la torre cambia de tamaño, el centro
  debe seguirla. Fijar con `Fix` solo centros ya amarrados.
  Técnica probada: diagonal de construcción entre esquinas opuestas
  proyectadas + `midpoint` del centro a la diagonal (el mid de la diagonal
  es el centro del rectángulo a cualquier tamaño); test de resize
  (d12 7->9) movió torre y agujero juntos al centro exacto.
- El plano debe ser el de simetría real: torres frente->atrás = plano XZ
  (o su Offset al centro), no YZ. Si la copia flota fuera de la pared,
  el plano está mal.

## 3. Remix sobre importado

- Medir la base (`measure`, `body_topology`, secciones con `inspect.section`)
  antes de cortar o añadir. Nunca inventar medidas (Regla 1).
- Rasgos a conservar intactos vs. rasgos a modificar se acuerdan con el
  usuario (Regla 3) y se registran en el `README.md` de la pieza.
- Re-exportar (`export` a `step`/`stl`) y revalidar Gate completo: la edición
  no hereda el `manifest.json` anterior.
