---
name: solidcraft-checking
description: "Verificación de diseños SolidCraft: measure, topología, screenshots de detalle, regresión y Gate de imprimibilidad."
triggers:
  - "verificar solidcraft"
  - "medir pieza solidcraft"
  - "auditar diseño"
---

# Skill: SolidCraft Checking (Track A1)

## 1. Medición

- `measure` por cuerpo: área, bbox, conteo topológico y `closed`.
  Volumen/masa solo se reportan en cuerpos cerrados y bien orientados.
- `measure {items: [...]}` sobre caras/aristas/vértices o curvas de sketch:
  diámetro/radio/centro/eje en cilindros; `slot` en ranuras; con dos ítems,
  `min`, `max`, `center_distance` y `angle_deg` entre planos o aristas.
- `body_topology {body}`: caras (nombre, área, centroide, normal, punto de
  agarre) y aristas (punto medio para `fillet`/`chamfer`).
- `inspect_design`: timeline (suprimidos, errores, warnings, tiempos),
  sketches (DOF, estado de resolución), bodies (volumen, bbox).

## 2. Inspección visual de detalle (receta documentada, sesión headless)

1. Recortar la región (`solid.box` con `operation: intersect`).
2. Cortar sección (`inspect.section`) y ocultar lo que estorba
   (`browser.visibility`).
3. `screenshot` ortográfico con `camera {target, yaw, pitch, distance}`,
   `source: model`, `grid: false` si la región cruza Z=0.
   Distancia ≈ 1.5× el tamaño de la región.

## 3. Regresión y Gate

- `document.revision` tras cada cambio: si no se movió, el diseño no cambió.
- `batch` con `timings: true` / `profile: true` para localizar features
  costosas (booleanos, teselado).
- Exportar STL y correr el Gate del repo sin excepciones:
  `scripts/verify_mesh.py <stl> --manifest` (hermético, Z-up, Z=0) y
  `scripts/export_3mf.py`. Un PASS en SolidCraft no sustituye el
  `manifest.json`.
