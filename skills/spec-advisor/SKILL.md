---
name: spec-advisor
description: "Asesor de especificaciones físicas, tolerancias de ajuste FDM, uniones mecánicas (snap-fits, dovetails, bayoneta), estanqueidad IP67, fijaciones métricas (M2-M5, insertos roscados), nervaduras y propiedades de materiales para la Elegoo Centauri Carbon."
triggers:
  - "tolerancia"
  - "medidas de tornillo"
  - "inserto roscado"
  - "heat-set insert"
  - "ajuste a presión"
  - "snap fit"
  - "cola de milano"
  - "estanco"
  - "IP67"
  - "junta TPU"
  - "qué material usar"
  - "PETG o PLA"
  - "datasheet"
---

# Skill: Spec Advisor (Especificaciones, Tolerancias, Uniones y Materiales)

Garantiza precisión dimensional, solidez estructural y física en las piezas. **Regla de oro: No inventar dimensiones de componentes comerciales ni forzar tolerancias sin calibrar.**

---

## 📐 Tolerancias de Ajuste FDM (Boquilla 0.4 mm)

En la Elegoo Centauri Carbon (precisión CoreXY calibrada):

| Tipo de Ajuste | Holgura Diametral Total | Uso Típico |
| :--- | :--- | :--- |
| **Press Fit (A presión)** | `+0.10 mm` a `+0.15 mm` | Pasadores fijos, imanes de neodimio, rodamientos fijos. |
| **Snug Fit (Ajuste firme)** | `+0.20 mm` | Tapas a presión, carcasas desmontables sin tornillo. |
| **Sliding Fit (Deslizante)** | `+0.25 mm` a `+0.35 mm` | Correderas, guías, bisagras impresas, ejes giratorios. |
| **Loose / Clearance (Paso libre)** | `+0.40 mm` a `+0.50 mm` | Agujeros pasantes para tornillos M3/M4/M5 sin roscar. |

> Consulta `references/tolerances.md` para detalles por material.

---

## 🧩 Uniones Mecánicas y Cajas Estancas (IP67)

- **Snap-fits y clips:** Ecuación de deformación admisible y regla de orientación de capas en el plano X-Y.
- **Colas de milano (Dovetails):** Para ensambles rígidos o para dividir piezas mayores al volumen de 256 mm.
- **Carcasas estancas IP67:** Compresión de junta de TPU (25-35%), limitadores de aplastamiento (*crush limiters*) y tornillos fuera del perímetro sellado.

> Consulta `references/joints.md` para parámetros y fórmulas completas.

---

## 🏗️ Nervaduras Estructurales y Texturas

- **Nervaduras (Ribs):** Espesor del 50% al 70% de la pared base para máxima rigidez sin pandeo.
- **Zonas Protegidas:** Prohibición estricta de aplicar texturas, estrías o *fuzzy skin* en caras de sellado, agujeros de fijación o la base de la cama PEI.

> Consulta `references/textures_and_ribs.md` para la guía completa.

---

## 🔩 Fijaciones Métricas e Insertos Roscados de Calor

- **Insertos térmicos (Heat-set inserts de latón):** La mejor práctica para ensambles mecánicos resistentes y reutilizables.
- **Tornillo autorroscante en plástico:** Válido solo para ensambles que nunca se van a desmontar.

> Consulta las tablas exactas de taladro previo y avellanado en `references/fasteners.md`.

---

## 🧵 Guía de Materiales (Elegoo Centauri Carbon)

La Elegoo Centauri Carbon cuenta con cámara cerrada y hotend de 300°C con boquilla endurecida, lo que le permite imprimir una gama completa de filamentos técnicos:

- **PLA / PLA+:** Rigidez alta, fácil impresión, nula deformación (warping). No apto para >55°C ni intemperie continua.
- **PETG:** Resistencia al impacto, tenacidad química e intemperie (UV). Temperatura hasta ~70°C.
- **ABS / ASA:** Alta resistencia térmica (~90°C-95°C) y facilidad de postprocesado. ASA es el rey del exterior (resistencia UV total). Requiere cámara cerrada precalentada.
- **TPU 95A / 90A:** Elasticidad, juntas de estanqueidad, amortiguadores.
- **PA-CF / PETG-CF:** Poliamida o PETG reforzado con fibra de carbono. Rigidez extrema, baja deformación térmica y aspecto mate profesional.

> Consulta `references/materials.md` para configuraciones de temperatura y retracción.
