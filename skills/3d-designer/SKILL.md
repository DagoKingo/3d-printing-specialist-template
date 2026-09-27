---
name: 3d-designer
description: "Diseño técnico de criterios de aceptación y pasaportes de fabricación aditiva (FDM). Formaliza el artefacto FABRICATION_PASSPORT.md vinculando cotas críticas de datasheets, cargas mecánicas, selección de materiales y asignación estricta de bahías Canvas/AMS antes de laminar o mandar a fabricar."
triggers:
  - "ficha tecnica"
  - "criterios aceptacion"
  - "pasaporte fabricacion"
  - "especificacion tecnica"
  - "fabrication passport"
  - "diseñar pieza"
  - "definir criterios"
---

# Skill: 3D Designer & Fabrication Passport Architect

## 🎯 Propósito y Filosofía
Esta skill actúa como el **Ingeniero de Diseño y Calidad Mecánica**. Su responsabilidad es formular los criterios de aceptación innegociables y emitir el artefacto canónico **`FABRICATION_PASSPORT.md`** para cualquier pieza o prototipo antes de que pase a las fases de laminación o fabricación física.

> [!IMPORTANT]
> **Ninguna pieza puede enviarse a corte o fabricación sin su `FABRICATION_PASSPORT.md` formalizado y aprobado.**
> El pasaporte es el contrato técnico que auditará la skill `preflight-auditor`.

---

## 📋 Flujo de Trabajo del Diseñador

```
[Entrevista 3d-grill-me + Datasheet]
              │
              ▼
    [Skill: 3d-designer]
              │
              ├─► 1. Extracción de cotas críticas (Ejes, chaveteros, espesores)
              ├─► 2. Análisis de esfuerzos (Torsión, tracción, temperatura)
              ├─► 3. Matriz de Materiales y Bahías Canvas (ABS/PETG/PLA)
              └─► 4. Emisión de FABRICATION_PASSPORT.md
              │
              ▼
    [Modelado CAD / Laminación Slicer]
              │
              ▼
    [Skill: preflight-auditor (Aduana Pre-Vuelo)]
```

---

## 🛠️ Estructura Obligatoria de `FABRICATION_PASSPORT.md`

El diseñador debe instanciar la plantilla `resources/templates/FABRICATION_PASSPORT.template.md` en:
- `pieces/<nombre_pieza>/artifacts/FABRICATION_PASSPORT.md` (para la versión maestra final).
- `pieces/<nombre_pieza>/prototypes/draft-[N]/FABRICATION_PASSPORT.md` (para iteraciones o variantes de prueba).

### Secciones Clave que el Diseñador Debe Fijar:
1. **Hardware Receptor Inalterable:** Número de parte comercial exacto sin abreviaturas (ej. `Honeywell Slate R8001M1150`).
2. **Cotas Críticas y Tolerancias:** Cotas nominales del eje, chavetero o pernos con su holgura paramétrica `$slop` asociada.
3. **Matriz Multi-Material Canvas:**
   - Si la pieza requiere soportes incompatibles (Zero-Gap) o insertos bicolores, fijar:
     - `task_use_ams: true`
     - `ams_mapping: "[0, 1]"` (o el mapeo correspondiente)
     - Herramienta 0 (`T0`): Material base (ej. ABS Gris en Tray 0).
     - Herramienta 1 (`T1`): Material de interfaz (ej. PETG Negro en Tray 1).
4. **Criterios de Aceptación de Slicer:**
   - Bucles de pared mínimos (mínimo 4 a 6 para esfuerzo mecánico).
   - Patrón de relleno (Giroide para isotropía).
   - Compensación XY de agujeros (0.00 mm para preservar el ajuste del CAD).
   - Z-distance de soporte (0.00 mm en Zero-Gap, 0.16 mm en soporte regular).
