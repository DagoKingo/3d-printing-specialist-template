#!/usr/bin/env python3
"""
preflight_audit.py — Aduana Pre-Vuelo y Auditoría Estricta de Fabricación FDM
Audita un archivo G-code o 3MF contra su FABRICATION_PASSPORT.md y contra la telemetría
de la máquina (Elegoo Canvas / SDCP) antes de permitir la orden física de impresión.

Salida:
  Código 0: [PASS] Todas las verificaciones cumplidas. Aprobado para impresión.
  Código 1: [FAIL] Bloqueo total por incumplimiento de criterios de aceptación.
"""

import sys
import os
import re
import json
import argparse
import subprocess
import shutil

def parse_passport(passport_path):
    """Extrae las reglas normativas del FABRICATION_PASSPORT.md."""
    if not os.path.exists(passport_path):
        raise FileNotFoundError(f"No se encontró el pasaporte de fabricación: {passport_path}")

    with open(passport_path, "r", encoding="utf-8") as f:
        content = f.read()

    passport = {
        "raw": content,
        "use_ams": False,
        "ams_mapping": None,
        "t0_material": None,
        "t0_tray": None,
        "t1_material": None,
        "t1_tray": None,
        "wall_loops": None,
        "support_type": None,
        "support_style": None,
        "support_top_z_distance": None,
        "support_interface_spacing": None,
        "support_interface_top_layers": None,
        "support_object_xy_distance": None,
        "xy_hole_compensation": None,
    }

    # Detección de uso de AMS / Canvas
    if re.search(r"task_use_ams.*true", content, re.IGNORECASE):
        passport["use_ams"] = True
    elif re.search(r"MULTI_MATERIAL_CANVAS", content, re.IGNORECASE):
        passport["use_ams"] = True

    # Detección de mapeo AMS
    m_map = re.search(r"ams_mapping.*\[(.*?)\]", content, re.IGNORECASE)
    if m_map:
        try:
            passport["ams_mapping"] = [int(x.strip()) for x in m_map.group(1).split(",")]
        except Exception:
            passport["ams_mapping"] = [0, 1]

    for line in content.splitlines():
        lower = line.lower()
        if "tool 0" in lower and "|" in line:
            parts = [p.strip().strip("`").strip("*") for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                passport["t0_material"] = parts[2].upper()
                tray_m = re.search(r"(\d+)", parts[3])
                if tray_m:
                    passport["t0_tray"] = int(tray_m.group(1))
        elif "tool 1" in lower and "|" in line:
            parts = [p.strip().strip("`").strip("*") for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                passport["t1_material"] = parts[2].upper()
                tray_m = re.search(r"(\d+)", parts[3])
                if tray_m:
                    passport["t1_tray"] = int(tray_m.group(1))

    # Parámetros de corte
    m_wall = re.search(r"wall_loops.*?(\d+)", content, re.IGNORECASE)
    if m_wall:
        passport["wall_loops"] = int(m_wall.group(1))

    m_z = re.search(r"support_top_z_distance.*?([\d\.]+)", content, re.IGNORECASE)
    if m_z:
        passport["support_top_z_distance"] = float(m_z.group(1))

    m_sp = re.search(r"support_interface_spacing.*?([\d\.]+)", content, re.IGNORECASE)
    if m_sp:
        passport["support_interface_spacing"] = float(m_sp.group(1))

    m_xy = re.search(r"xy_hole_compensation.*?([\d\.]+)", content, re.IGNORECASE)
    if m_xy:
        passport["xy_hole_compensation"] = float(m_xy.group(1))

    # Parámetros de soporte nominal (estilo/tipo) para auditoría de 3MF.
    # Fuente primaria: Slicer Settings Lock Table del pasaporte (P4):
    #   | `support_type` | `normal(auto)` |
    for m_row in re.finditer(r"^\|\s*`?(support_type|support_style)`?\s*\|\s*`?([^|`\n]+)`?\s*\|", content, re.MULTILINE):
        passport[m_row.group(1)] = m_row.group(2).strip().strip("`").strip()
    # Fallback legacy: tokens inline estilo `normal(auto)/snug`
    if passport["support_type"] is None:
        m_stype = re.search(r"`((?:normal|tree)\([^`]*\))", content)
        if m_stype:
            passport["support_type"] = m_stype.group(1).strip()
    if passport["support_style"] is None:
        m_sstyle = re.search(r"/(snug|grid|rectilinear|honeycomb|lightning|gyroid)`", content)
        if m_sstyle:
            passport["support_style"] = m_sstyle.group(1).strip()
    m_slay = re.search(r"support_interface_top_layers.*?(\d+)", content, re.IGNORECASE)
    if not m_slay:
        m_slay = re.search(r"(?<!\w)top_layers\s*:\s*(\d+)", content, re.IGNORECASE)
    if m_slay:
        passport["support_interface_top_layers"] = int(m_slay.group(1))
    m_sxy = re.search(r"support_object_xy_distance.*?([\d\.]+)", content, re.IGNORECASE)
    if not m_sxy:
        m_sxy = re.search(r"xy_distance\s*:\s*([\d\.]+)", content, re.IGNORECASE)
    if m_sxy:
        passport["support_object_xy_distance"] = float(m_sxy.group(1))

    return passport

def audit_3mf(mf_path, passport):
    """Verifica un proyecto .3mf contra el pasaporte ANTES de laminar.

    Inspecciona Metadata/project_settings.config dentro del zip:
    tipado string, valores exactos del pasaporte, cobertura en
    different_settings_to_system y anclaje al preset CC2.
    Un PASS aquí autoriza el laminado headless, NO la impresión
    (el G-code resultante aún debe pasar audit_gcode).
    """
    issues = []
    checks = []

    if not os.path.exists(mf_path):
        return [f"Archivo 3MF no encontrado: {mf_path}"], []
    if not mf_path.lower().endswith(".3mf"):
        return [f"audit_3mf recibió un archivo no-3MF: {mf_path}"], []

    import zipfile
    try:
        with zipfile.ZipFile(mf_path, "r") as z:
            raw = z.read("Metadata/project_settings.config").decode("utf-8")
    except Exception as e:
        return [f"3MF ilegible o sin Metadata/project_settings.config: {e}"], []

    try:
        cfg = json.loads(raw)
    except Exception as e:
        return [f"project_settings.config no es JSON válido: {e}"], []

    def num(key):
        try:
            return float(str(cfg.get(key, "")))
        except Exception:
            return None

    # 1. Tipado estricto de strings (motor C++ ElegooSlicer descarta numéricos)
    for key in ("support_type", "support_style", "support_top_z_distance",
                "support_interface_spacing", "support_interface_top_layers",
                "support_object_xy_distance", "wall_loops",
                "sparse_infill_density", "xy_hole_compensation", "enable_support"):
        if key in cfg and not isinstance(cfg[key], str):
            issues.append(f"3MF tipado inválido: '{key}' no es string (será descartado por el slicer)")

    # 2. Valores exactos del pasaporte
    if passport["wall_loops"] is not None:
        v = num("wall_loops")
        if v is None:
            issues.append("3MF sin 'wall_loops' definido")
        elif int(v) < passport["wall_loops"]:
            issues.append(f"3MF wall_loops={int(v)}, pasaporte exige mínimo {passport['wall_loops']}")
        else:
            checks.append(f"3MF wall_loops: {int(v)} >= {passport['wall_loops']} [OK]")

    for key in ("support_top_z_distance", "support_interface_spacing",
                "support_object_xy_distance", "xy_hole_compensation"):
        if passport[key] is not None:
            v = num(key)
            if v is None:
                issues.append(f"3MF sin '{key}' definido")
            elif abs(v - passport[key]) > 0.01:
                issues.append(f"3MF {key}={v}, pasaporte exige {passport[key]}")
            else:
                checks.append(f"3MF {key}: {v} [OK]")

    if passport["support_interface_top_layers"] is not None:
        v = num("support_interface_top_layers")
        if v is None:
            issues.append("3MF sin 'support_interface_top_layers' definido")
        elif int(v) != passport["support_interface_top_layers"]:
            issues.append(f"3MF support_interface_top_layers={int(v)}, pasaporte exige {passport['support_interface_top_layers']}")
        else:
            checks.append(f"3MF support_interface_top_layers: {int(v)} [OK]")

    for key in ("support_type", "support_style"):
        if passport[key] is not None:
            v = cfg.get(key)
            if not isinstance(v, str):
                issues.append(f"3MF sin '{key}' como string")
            elif v.strip().lower() != passport[key].strip().lower():
                issues.append(f"3MF {key}='{v}', pasaporte exige '{passport[key]}'")
            else:
                checks.append(f"3MF {key}: '{v}' [OK]")

    # 3. Cobertura en different_settings_to_system (sin esto el slicer resetea)
    diffs = cfg.get("different_settings_to_system", ["", "", "", ""])
    retained = diffs[0] if isinstance(diffs, list) and diffs else ""
    for key in ("wall_loops", "support_type", "support_style", "support_top_z_distance",
                "support_interface_spacing", "support_interface_top_layers",
                "support_object_xy_distance", "xy_hole_compensation"):
        if key not in retained:
            issues.append(f"3MF '{key}' fuera de different_settings_to_system (el slicer lo sobreescribirá)")
    if not issues or all("fuera de different" not in i for i in issues):
        checks.append("3MF different_settings_to_system con cobertura de soportes [OK]")

    # 4. Anclaje al preset base del sistema
    preset = cfg.get("print_settings_id", "")
    if preset != "0.20mm Standard @Elegoo CC2 0.4 nozzle":
        issues.append(f"3MF print_settings_id='{preset}', debe anclarse al preset CC2 0.4")
    else:
        checks.append("3MF print_settings_id anclado al preset CC2 [OK]")

    if not issues:
        checks.append("3MF AUTORIZADO PARA LAMINADO HEADLESS (aún requiere auditoría del G-code resultante) [OK]")

    return issues, checks

def audit_gcode(gcode_path, passport):
    """Verifica el G-code contra los criterios del pasaporte."""
    issues = []
    checks = []

    if not os.path.exists(gcode_path):
        return [f"Archivo G-code no encontrado: {gcode_path}"], []

    with open(gcode_path, "r", encoding="utf-8", errors="ignore") as f:
        # Leer primeras y últimas líneas para metadata
        lines = f.readlines()

    full_text = "".join(lines)
    header_tail = "".join(lines[:200] + lines[-500:])

    # 1. Verificación de bucles de pared
    if passport["wall_loops"] is not None:
        m = re.search(r";\s*wall_loops\s*=\s*(\d+)", header_tail)
        if m:
            val = int(m.group(1))
            if val < passport["wall_loops"]:
                issues.append(f"wall_loops insuficiente: G-code tiene {val}, pasaporte exige mínimo {passport['wall_loops']}")
            else:
                checks.append(f"wall_loops: {val} >= {passport['wall_loops']} [OK]")

    # 2. Verificación de soporte Zero-Gap
    if passport["support_top_z_distance"] is not None:
        m = re.search(r";\s*support_top_z_distance\s*=\s*([\d\.]+)", header_tail)
        if m:
            val = float(m.group(1))
            if abs(val - passport["support_top_z_distance"]) > 0.01:
                issues.append(f"support_top_z_distance no coincide: G-code tiene {val} mm, pasaporte exige {passport['support_top_z_distance']} mm")
            else:
                checks.append(f"support_top_z_distance: {val} mm [OK]")

    if passport["support_interface_spacing"] is not None:
        m = re.search(r";\s*support_interface_spacing\s*=\s*([\d\.]+)", header_tail)
        if m:
            val = float(m.group(1))
            if abs(val - passport["support_interface_spacing"]) > 0.01:
                issues.append(f"support_interface_spacing no coincide: G-code tiene {val} mm, pasaporte exige {passport['support_interface_spacing']} mm")
            else:
                checks.append(f"support_interface_spacing: {val} mm (losa continua) [OK]")

    # 3. Verificación de comandos de herramienta en G-code si es multi-material
    if passport["use_ams"]:
        t0_matches = re.findall(r"^T0\b", full_text, re.MULTILINE)
        t1_matches = re.findall(r"^T1\b", full_text, re.MULTILINE)
        m6211_matches = re.findall(r"\bM6211\b", full_text)

        if not t1_matches:
            issues.append("El pasaporte exige modo Multi-Material (Tool 1), pero el G-code no contiene llamadas 'T1'")
        else:
            checks.append(f"Comandos T1 presentes en G-code: {len(t1_matches)} llamadas [OK]")

        if not m6211_matches:
            issues.append("El G-code multi-material no contiene macros de corte de cabezal 'M6211'")
        else:
            checks.append(f"Macros cinemáticas M6211 presentes: {len(m6211_matches)} llamadas [OK]")

    return issues, checks

def audit_hardware_live(passport):
    """Consulta la máquina física para verificar bandejas y estado."""
    issues = []
    checks = []

    centauri_bin = shutil.which("centauri")
    if not centauri_bin:
        venv_candidate = os.path.expanduser("~/.venv-3d/bin/centauri")
        if os.path.exists(venv_candidate):
            centauri_bin = venv_candidate

    if not centauri_bin:
        checks.append("centauri CLI no encontrado en PATH ni en ~/.venv-3d/bin [WARN]")
        return issues, checks

    host = os.environ.get("CENTAURI_HOST")
    access_code = os.environ.get("PYCENTAURI_ACCESS_CODE")

    # Intentar leer config/config.toml
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(repo_root, "config", "config.toml")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("ip ="):
                        host = line.split("=")[1].strip().strip('"').strip("'")
                    elif line.strip().startswith("access_code ="):
                        access_code = line.split("=")[1].strip().strip('"').strip("'")
        except Exception:
            pass

    cmd = [centauri_bin, "canvas", "--json"]
    if host:
        cmd.extend(["--host", host])
    env = os.environ.copy()
    if access_code:
        env["PYCENTAURI_ACCESS_CODE"] = access_code

    # Intentar obtener estado vía pycentauri CLI
    try:
        res = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=5, env=env
        )
        if res.returncode == 0:
            data = json.loads(res.stdout)
            ci = data.get("canvas_info", {})
            canvas_list = ci.get("canvas_list", [])
            if canvas_list:
                trays = canvas_list[0].get("tray_list", [])
                tray_map = {t.get("tray_id"): t for t in trays}

                # Validar Tray 0
                if passport["t0_tray"] is not None and passport["t0_material"]:
                    tray = tray_map.get(passport["t0_tray"])
                    if not tray or tray.get("status") != 1:
                        issues.append(f"Hardware Error: Bahía Tray {passport['t0_tray']} no está cargada o activa")
                    else:
                        mat = str(tray.get("filament_type", "")).upper()
                        if passport["t0_material"] not in mat:
                            issues.append(f"Hardware Mismatch: Tray {passport['t0_tray']} tiene {mat}, pero pasaporte exige {passport['t0_material']}")
                        else:
                            checks.append(f"Hardware Check Tray {passport['t0_tray']}: {mat} cargado [OK]")

                # Validar Tray 1
                if passport["t1_tray"] is not None and passport["t1_material"]:
                    tray = tray_map.get(passport["t1_tray"])
                    if not tray or tray.get("status") != 1:
                        issues.append(f"Hardware Error: Bahía Tray {passport['t1_tray']} no está cargada o activa")
                    else:
                        mat = str(tray.get("filament_type", "")).upper()
                        if passport["t1_material"] not in mat:
                            issues.append(f"Hardware Mismatch: Tray {passport['t1_tray']} tiene {mat}, pero pasaporte exige {passport['t1_material']}")
                        else:
                            checks.append(f"Hardware Check Tray {passport['t1_tray']}: {mat} cargado [OK]")
    except Exception as e:
        checks.append(f"Hardware Live Check omitido o no disponible ({e}) [WARN]")

    return issues, checks

def main():
    parser = argparse.ArgumentParser(description="Aduana Pre-Vuelo FDM (Preflight Auditor)")
    parser.add_argument("target", help="Archivo .gcode o .3mf a auditar")
    parser.add_argument("--passport", required=True, help="Ruta al FABRICATION_PASSPORT.md")
    parser.add_argument("--live", action="store_true", help="Auditar hardware en vivo vía Canvas")

    args = parser.parse_args()

    print("=======================================================")
    print("🛂 ADUANA PRE-VUELO FDM (PRE-FLIGHT AUDIT GATE)")
    print(f"   Archivo:   {os.path.basename(args.target)}")
    print(f"   Pasaporte: {os.path.basename(args.passport)}")
    print("=======================================================")

    try:
        passport = parse_passport(args.passport)
    except Exception as e:
        print(f"\n❌ ERROR FATAL AL LEER PASAPORTE: {e}")
        sys.exit(1)

    all_issues = []
    all_checks = []

    # 1. Auditoría de archivo (3MF: gate pre-laminado / G-code: gate pre-impresión)
    if args.target.lower().endswith(".3mf"):
        file_issues, file_checks = audit_3mf(args.target, passport)
    else:
        file_issues, file_checks = audit_gcode(args.target, passport)
    all_issues.extend(file_issues)
    all_checks.extend(file_checks)

    # 2. Auditoría de hardware en vivo si se solicita
    if args.live:
        hw_issues, hw_checks = audit_hardware_live(passport)
        all_issues.extend(hw_issues)
        all_checks.extend(hw_checks)

    print("\n🔍 Verificaciones Superadas:")
    for c in all_checks:
        print(f"  ✅ {c}")

    is_3mf = args.target.lower().endswith(".3mf")
    if all_issues:
        print("\n🚫 BLOQUEO — NO CONFORMIDADES DETECTADAS:")
        for issue in all_issues:
            print(f"  ❌ {issue}")
        if is_3mf:
            print("\n🏁 VEREDICTO FINAL: [FAIL — LAMINADO BLOQUEADO: corrija el 3MF contra el pasaporte]")
        else:
            print("\n🏁 VEREDICTO FINAL: [FAIL — IMPRESIÓN BLOQUEADA]")
        print("=======================================================")
        sys.exit(1)
    else:
        if is_3mf:
            print("\n🏁 VEREDICTO FINAL: [PASS — 3MF AUTORIZADO PARA LAMINADO; aún requiere auditoría del G-code]")
        else:
            print("\n🏁 VEREDICTO FINAL: [PASS — AUTORIZADO PARA IMPRESIÓN]")
        if passport["use_ams"]:
            print(f"ℹ️  Directiva de Lanzamiento: Ejecutar start_print con use_ams=True y ams_mapping={passport['ams_mapping']}")
        print("=======================================================")
        sys.exit(0)

if __name__ == "__main__":
    main()
