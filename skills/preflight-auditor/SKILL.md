---
name: preflight-auditor
description: "Aduana e inspección pre-vuelo obligatoria antes de enviar trabajos a la impresora 3D (Elegoo Centauri Carbon / SDCP). Audita el G-code y el payload de inicio contra el FABRICATION_PASSPORT.md y la telemetría viva de Canvas/AMS. Bloquea incondicionalmente la orden de impresión si falta alguna configuración crítica."
triggers:
  - "auditar impresion"
  - "preflight"
  - "aduana impresion"
  - "validar gcode"
  - "verificar antes de imprimir"
  - "pre-flight audit"
---

# Skill: Pre-Flight Auditor & Fabrication Gatekeeper

## 🎯 Rol y Mandato de Seguridad
Esta skill actúa como el **Inspector de Calidad y Aduana Pre-Vuelo Inquebrantable**. 

> [!CAUTION]
> **Doble Bloqueo Innegociable (Hard Gates 3MF + G-code):**
> Queda terminantemente prohibido laminar un `.3mf` que no haya pasado `audit_3mf`, y prohibido ejecutar `start_print` con un `.gcode` que no haya pasado `audit_gcode --live`. Cada gate tiene su veredicto: el 3MF autoriza **laminado**, solo el G-code autoriza **impresión**.

---

## 🔍 Protocolo de Auditoría (Puntos de Control)

Gate 1 — proyecto 3MF contra pasaporte (ANTES de laminar):
```bash
python3 scripts/preflight_audit.py <proyecto.3mf> --passport <FABRICATION_PASSPORT.md>
```

Gate 2 — G-code contra pasaporte + hardware (ANTES de imprimir):
```bash
python3 scripts/preflight_audit.py <archivo.gcode> --passport <FABRICATION_PASSPORT.md> --live
```

El script valida de manera binaria e implacable:
1. **Auditoría de Contrato Técnico:** Verifica que el `FABRICATION_PASSPORT.md` exista y defina tolerancias, bucles, rellenos y asignación de materiales.
2. **Auditoría de Proyecto 3MF (Gate 1, pre-laminado):**
   - Inspecciona `Metadata/project_settings.config` dentro del zip: tipado string de escalares, valores exactos del pasaporte (`support_type`, `support_style`, `support_top_z_distance`, `support_interface_spacing`, `wall_loops`, `xy_hole_compensation`), cobertura en `different_settings_to_system` y anclaje a `0.20mm Standard @Elegoo CC2 0.4 nozzle`.
   - Un 3MF con defaults del intent (ej. `tree(auto)` / `0.20` cuando el pasaporte exige `normal(auto)` / `0.15`) da `[FAIL — LAMINADO BLOQUEADO]`.
3. **Auditoría Cinemática de G-code (Gate 2, pre-impresión):****
   - Comprueba bucles de pared mínimos (`wall_loops`).
   - Comprueba parámetros de soporte Zero-Gap (`support_top_z_distance: 0.00 mm`, `support_interface_spacing: 0.00 mm`).
   - Si el trabajo es multi-material: Verifica la presencia de comandos `T0`, `T1` y las macros de corte motorizado `M6211`.
4. **Auditoría de Hardware en Vivo (Elegoo Canvas):**
   - Consulta `centauri canvas` vía MQTT/SDCP.
   - Certifica que las bahías físicas contengan el filamento requerido (ej. Tray 0 = ABS, Tray 1 = PETG).
5. **Auditoría de Payload de Lanzamiento (`start_print`):**
   - En trabajos multi-material, la llamada **DEBE incluir obligatoriamente:**
     ```python
     start_print(filename, use_ams=True, ams_mapping=[0, 1])
     ```
   - Prohibido omitir `use_ams` en piezas con soporte incompatible o bicolor.
6. **Inspección Óptica de Cama (`get_snapshot`):**
   - Confirma visualmente que la placa PEI esté completamente desocupada y limpia.
