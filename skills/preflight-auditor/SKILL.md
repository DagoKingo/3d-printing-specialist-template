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
> **Bloqueo Innegociable de Lanzamiento (Hard Launch Gate):**
> Queda terminantemente prohibido que cualquier agente ejecute `start_print` o mande a fabricar un modelo sin haber ejecutado y aprobado previamente la auditoría con `scripts/preflight_audit.py`. Si el resultado no es `[PASS]`, la impresión está **BLOQUEADA**.

---

## 🔍 Protocolo de Auditoría Pre-Vuelo (Puntos de Control)

Antes de cualquier impresión, el auditor ejecuta:
```bash
python3 scripts/preflight_audit.py <archivo.gcode> --passport <FABRICATION_PASSPORT.md> --live
```

El script valida de manera binaria e implacable:
1. **Auditoría de Contrato Técnico:** Verifica que el `FABRICATION_PASSPORT.md` exista y defina tolerancias, bucles, rellenos y asignación de materiales.
2. **Auditoría Cinemática de G-code:**
   - Comprueba bucles de pared mínimos (`wall_loops`).
   - Comprueba parámetros de soporte Zero-Gap (`support_top_z_distance: 0.00 mm`, `support_interface_spacing: 0.00 mm`).
   - Si el trabajo es multi-material: Verifica la presencia de comandos `T0`, `T1` y las macros de corte motorizado `M6211`.
3. **Auditoría de Hardware en Vivo (Elegoo Canvas):**
   - Consulta `centauri canvas` vía MQTT/SDCP.
   - Certifica que las bahías físicas contengan el filamento requerido (ej. Tray 0 = ABS, Tray 1 = PETG).
4. **Auditoría de Payload de Lanzamiento (`start_print`):**
   - En trabajos multi-material, la llamada **DEBE incluir obligatoriamente:**
     ```python
     start_print(filename, use_ams=True, ams_mapping=[0, 1])
     ```
   - Prohibido omitir `use_ams` en piezas con soporte incompatible o bicolor.
5. **Inspección Óptica de Cama (`get_snapshot`):**
   - Confirma visualmente que la placa PEI esté completamente desocupada y limpia.
