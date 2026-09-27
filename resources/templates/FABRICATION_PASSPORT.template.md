# FABRICATION PASSPORT & QUALITY ACCEPTANCE CONTRACT
<!-- Documento Normativo Inviolable — Aduana Pre-Vuelo FDM -->

**Pieza:** `{{PIECE_NAME}}`  
**Iteración / Draft:** `{{DRAFT_NAME}}`  
**Hardware Receptor:** `{{TARGET_DEVICE}}`  
**Impresora de Destino:** `{{TARGET_PRINTER}}`  
**Fecha de Emisión:** `{{DATE}}`  
**Estado:** `{{STATUS}}` <!-- PENDING_AUDIT | APPROVED_FOR_PRINT | REJECTED -->

---

## 1. 🎯 Requerimientos y Cotas Críticas de Acople (Target Dossier)

| Cota / Característica Mecánica | Nominal Teórico | Tolerancia Permitida | $slop / Holgura CAD | Método de Validación |
| :--- | :--- | :--- | :--- | :--- |
| Diámetro de Eje / Barreno | `{{BORE_NOMINAL}}` | `±0.05 mm` | `{{SLOP_BORE}}` | Calibre pie de rey / Pin gage |
| Ancho / Alto de Chavetero | `{{KEY_NOMINAL}}` | `±0.05 mm` | `{{SLOP_KEY}}` | Calibre pie de rey |
| Espesor de Pared Mínimo | `{{MIN_WALL}}` | `+0.20 mm / -0.0 mm` | N/A | Slicer check |
| Resistencia Requerida | `{{TORQUE_LOAD}}` | N/A | N/A | Orientación de capas y bucles |

---

## 2. 🖨️ Matriz Obligatoria de Materiales y Asignación de Bahías (Canvas / AMS)

> [!CAUTION]
> **Bloqueo de Seguridad Multi-Material:** Si la pieza es multi-material o utiliza interfaz incompatible para desmoldeo Zero-Gap, `task_use_ams` DEBE ser `true` y `ams_mapping` DEBE estar estrictamente vinculado a las bahías físicas cargadas con los filamentos correctos.

- **Modo de Impresión:** `{{PRINT_MODE}}` <!-- SINGLE_MATERIAL | MULTI_MATERIAL_CANVAS -->
- **Uso de Sistema Multi-Material (`task_use_ams`):** `{{TASK_USE_AMS}}` <!-- true | false -->
- **Mapeo de Herramientas a Bahías (`ams_mapping`):** `{{AMS_MAPPING}}` <!-- ej. "[0, 1]" -->

### Asignación de Herramientas Virtuales (G-code) a Bandejas Físicas (Canvas):
| Herramienta | Rol FDM | Material Requerido | Bahía Física (Tray ID) | Color Esperado | Temp Extrusión | Temp Cama |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tool 0 (`T0`)** | Cuerpo principal / Paredes | `{{T0_MATERIAL}}` | `Tray {{T0_TRAY}}` | `{{T0_COLOR}}` | `{{T0_TEMP_NOZZLE}}°C` | `{{T0_TEMP_BED}}°C` |
| **Tool 1 (`T1`)** | Interfaz de Soporte / Detalle | `{{T1_MATERIAL}}` | `Tray {{T1_TRAY}}` | `{{T1_COLOR}}` | `{{T1_TEMP_NOZZLE}}°C` | `{{T1_TEMP_BED}}°C` |

---

## 3. ⚙️ Criterios de Aceptación de Laminación (Slicer Acceptance Gate)

Cualquier G-code enviado a máquina DEBE cumplir de forma binaria e innegociable los siguientes parámetros:

- [ ] **Orientación de Esfuerzos:** Eje Z orientado para evitar que las cargas de tracción o torsión actúen perpendiculares a las capas.
- [ ] **Bucles de Pared (`wall_loops`):** Mínimo `{{MIN_WALL_LOOPS}}` bucles continuos.
- [ ] **Densidad y Patrón de Relleno:** Mínimo `{{MIN_INFILL_DENSITY}}` en patrón `{{INFILL_PATTERN}}`.
- [ ] **Compensación de Agujeros (`xy_hole_compensation`):** Fijada estrictamente en `{{XY_HOLE_COMPENSATION}} mm` (respetando la cota paramétrica de CAD sin doble compensación).
- [ ] **Estrategia de Soportes:**
  - Tipo: `{{SUPPORT_TYPE}}` (Snug / Normal / Tree).
  - Brecha Z (`support_top_z_distance`): `{{SUPPORT_Z_DISTANCE}} mm` (0.00 mm para Zero-Gap multimaterial; 0.14-0.18 mm para monomaterial).
  - Espaciado de Interfaz (`support_interface_spacing`): `{{SUPPORT_INTERFACE_SPACING}} mm` (0.00 mm para losa continua anti-velcro).
  - Capas de Interfaz (`support_interface_top_layers`): Mínimo `{{SUPPORT_INTERFACE_LAYERS}}` capas.
- [ ] **Torre de Purga (Prime Tower):** `{{PRIME_TOWER_STATUS}}` (Ancho `{{PRIME_TOWER_WIDTH}} mm`).

---

## 4. 🛂 Lista de Verificación Pre-Vuelo (Pre-Flight Auditor Checklist)

Antes de emitir `start_print`, el auditor agéntico `skills/preflight-auditor` debe certificar con `scripts/preflight_audit.py`:

1. [ ] **Verificación de Malla:** `manifest.json` presente, Z=0 en cama, 100% Manifold (estanco).
2. [ ] **Verificación de Comandos Cinemáticos en G-code:**
   - Si es multi-material: Presencia obligatoria de comandos de cambio de herramienta `T0`, `T1` y macros de corte `M6211`.
3. [ ] **Auditoría de Hardware en Vivo (`centauri canvas` / `get_canvas_status`):**
   - Las bahías físicas de la máquina tienen cargado el material y color declarado en la Sección 2.
4. [ ] **Auditoría de Payload de Impresión:**
   - La llamada de inicio incluye explícitamente `task_use_ams: true` y `ams_mapping` coincidente.
5. [ ] **Inspección Óptica de Cama (`get_snapshot`):**
   - Placa PEI limpia, libre de residuos, piezas anteriores o herramientas.

---

## 5. ✍️ Dictamen y Aprobación de Fabricación

- **Auditor Responsable:** `{{AUDITOR_NAME}}`
- **Resultado de la Auditoría:** `{{AUDIT_VERDICT}}` <!-- PASS | FAIL -->
- **Hash / Checksum de G-code Aprobado:** `{{GCODE_HASH}}`
- **Observaciones Técnicas:** `{{AUDIT_NOTES}}`
