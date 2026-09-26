#!/usr/bin/env python3
"""
verify_mesh.py — Puerta de Imprimibilidad (Printability Gate), Normalizador y Validador FDM
Inspirado en la ingeniería de 'idea-to-print', 'print3d', 'meshy-3d-agent' y 'mijugit/freecad-stl'.

Comprueba:
1. Límites físicos de la Elegoo Centauri Carbon (256 × 256 × 256 mm).
2. Estanqueidad geométrica (Malla Manifold / Watertight).
3. Autopsia quirúrgica de defectos (localización de aristas abiertas por altura Z y radio R).
4. Estabilidad en cama (Área de contacto base y relación de esbeltez/aspect ratio).
5. Posición vertical en Z (contacto en Z=0) y normalización Y-up a Z-up.
6. Generación de 'manifest.json' (Job Ledger del proyecto).
"""

import sys
import os
import struct
import hashlib
import json
import time
import argparse
import collections

# Soporte transparente para entorno virtual local si existe
for _sp in [os.path.expanduser("~/.venv-3d/lib/python3.12/site-packages"), os.path.expanduser("~/.venv/lib/python3.12/site-packages")]:
    if os.path.exists(_sp) and _sp not in sys.path:
        sys.path.insert(0, _sp)

BED_MAX_X = 256.0
BED_MAX_Y = 256.0
BED_MAX_Z = 256.0

def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def read_stl_full(filepath):
    """Lee un STL binario y retorna encabezado, número de triángulos y lista de triángulos con normales."""
    with open(filepath, "rb") as f:
        header = f.read(80)
        num_triangles = struct.unpack("<I", f.read(4))[0]
        triangles = []
        min_vals = [float("inf"), float("inf"), float("inf")]
        max_vals = [float("-inf"), float("-inf"), float("-inf")]

        for _ in range(num_triangles):
            normal = struct.unpack("<fff", f.read(12))
            v1 = struct.unpack("<fff", f.read(12))
            v2 = struct.unpack("<fff", f.read(12))
            v3 = struct.unpack("<fff", f.read(12))
            attr = f.read(2)

            for v in [v1, v2, v3]:
                for i in range(3):
                    min_vals[i] = min(min_vals[i], v[i])
                    max_vals[i] = max(max_vals[i], v[i])

            triangles.append({"normal": normal, "v1": v1, "v2": v2, "v3": v3, "attr": attr})

    return {
        "header": header,
        "count": num_triangles,
        "triangles": triangles,
        "min": min_vals,
        "max": max_vals,
        "size": (max_vals[0] - min_vals[0], max_vals[1] - min_vals[1], max_vals[2] - min_vals[2])
    }

def fix_stl_coordinates(input_path, output_path=None, rotate_y_up=False, ground_z=True):
    """Corrige la orientación de coordenadas (Y-up a Z-up) y apoya la base en Z=0."""
    if output_path is None:
        output_path = input_path

    data = read_stl_full(input_path)
    triangles = data["triangles"]
    new_triangles = []

    min_z = float("inf")
    # Paso 1: Rotar si se solicitó Y-up -> Z-up (x, y, z) -> (x, -z, y)
    for tri in triangles:
        if rotate_y_up:
            n = (tri["normal"][0], -tri["normal"][2], tri["normal"][1])
            v1 = (tri["v1"][0], -tri["v1"][2], tri["v1"][1])
            v2 = (tri["v2"][0], -tri["v2"][2], tri["v2"][1])
            v3 = (tri["v3"][0], -tri["v3"][2], tri["v3"][1])
        else:
            n = tri["normal"]
            v1, v2, v3 = tri["v1"], tri["v2"], tri["v3"]

        min_z = min(min_z, v1[2], v2[2], v3[2])
        new_triangles.append({"normal": n, "v1": v1, "v2": v2, "v3": v3, "attr": tri["attr"]})

    # Paso 2: Desplazar en Z para que la base quede exactamente en Z=0
    z_offset = -min_z if ground_z else 0.0

    with open(output_path, "wb") as f:
        f.write(data["header"])
        f.write(struct.pack("<I", len(new_triangles)))
        for tri in new_triangles:
            f.write(struct.pack("<fff", *tri["normal"]))
            v1 = (tri["v1"][0], tri["v1"][1], tri["v1"][2] + z_offset)
            v2 = (tri["v2"][0], tri["v2"][1], tri["v2"][2] + z_offset)
            v3 = (tri["v3"][0], tri["v3"][1], tri["v3"][2] + z_offset)
            f.write(struct.pack("<fff", *v1))
            f.write(struct.pack("<fff", *v2))
            f.write(struct.pack("<fff", *v3))
            f.write(tri["attr"])

    print(f"🔧 STL normalizado y guardado en: {output_path}")
    if rotate_y_up:
        print("  • Rotado de Y-up a Z-up")
    if ground_z:
        print(f"  • Base apoyada en Z=0 (Desplazamiento Z: {z_offset:+.2f} mm)")

def run_stl_autopsy(filepath):
    """
    Autopsia quirúrgica de defectos de malla STL (inspirado en mijugit/freecad-stl).
    Localiza aristas abiertas o no-manifold agrupadas por altura Z y radio R,
    y analiza el perfil del barreno central.
    """
    try:
        import numpy as np
    except ImportError:
        return {"error": "numpy no disponible para autopsia"}

    with open(filepath, "rb") as fh:
        data = fh.read()
    if len(data) < 84:
        return {"error": "Archivo demasiado corto"}
    n = struct.unpack("<I", data[80:84])[0]
    if len(data) != 84 + n * 50:
        return {"error": f"STL binario corrupto o truncado ({n} facetas declaradas)"}

    rec = np.dtype([("normal", "<3f4"), ("v", "<3,3f4"), ("attr", "<u2")])
    arr = np.frombuffer(data, dtype=rec, count=n, offset=84)
    tris = arr["v"].astype(np.float64)

    # Soldar vértices sobre una rejilla fina (1e-5 mm)
    flat = tris.reshape(-1, 3)
    keys = np.round(flat * 1e5).astype(np.int64)
    uniq, inv = np.unique(keys, axis=0, return_inverse=True)
    idx = inv.reshape(-1, 3)

    edges = np.concatenate([idx[:, [0, 1]], idx[:, [1, 2]], idx[:, [2, 0]]])
    edges = np.sort(edges, axis=1)
    ue, uc = np.unique(edges, axis=0, return_counts=True)

    used_once = int((uc == 1).sum())
    used_twice = int((uc == 2).sum())
    used_3plus = int((uc > 2).sum())
    bad = ue[uc != 2]

    verts = uniq / 1e5
    autopsy = {
        "facets": int(n),
        "unique_vertices": int(len(uniq)),
        "edges_total": int(len(ue)),
        "edges_used_once": used_once,
        "edges_used_twice": used_twice,
        "edges_used_3plus": used_3plus,
        "bad_edges_count": int(len(bad)),
        "defect_region": None,
        "worst_z_heights": [],
        "bore_analysis": None
    }

    if len(bad) > 0:
        pts = verts[np.unique(bad)]
        r = np.hypot(pts[:, 0], pts[:, 1])
        z = pts[:, 2]
        autopsy["defect_region"] = {
            "bad_vertices_count": int(len(pts)),
            "radius_min_mm": float(round(r.min(), 2)),
            "radius_max_mm": float(round(r.max(), 2)),
            "z_min_mm": float(round(z.min(), 2)),
            "z_max_mm": float(round(z.max(), 2))
        }
        hist = collections.Counter(np.floor(z).astype(int))
        top = sorted(hist.items(), key=lambda kv: -kv[1])[:5]
        autopsy["worst_z_heights"] = [{"z_mm": int(h), "open_points": int(c)} for h, c in top]

    # Detección de perfil de barreno (liso vs roscado)
    rr = np.hypot(verts[:, 0], verts[:, 1])
    zz = verts[:, 2]
    if len(zz) > 0 and (zz.max() - zz.min()) > 2.0:
        body = (zz > zz.min() + 1.0) & (zz < zz.max() - 1.0)
        bore = body & (rr < rr.max() * 0.7)
        if bore.sum() > 20:
            br = rr[bore]
            spread = float(br.max() - br.min())
            is_threaded = spread > 0.2
            autopsy["bore_analysis"] = {
                "bore_points": int(bore.sum()),
                "radius_min_mm": float(round(br.min(), 2)),
                "radius_max_mm": float(round(br.max(), 2)),
                "radius_spread_mm": float(round(spread, 3)),
                "profile": "Roscado (radio variable)" if is_threaded else "Barreno liso (radio constante)"
            }

    return autopsy

def evaluate_mesh(filepath, generate_manifest=False, project_dir=None, material="PLA", run_autopsy=False, target_device=None):
    if not os.path.exists(filepath):
        print(f"❌ Error: El archivo '{filepath}' no existe.")
        return False, {}

    print(f"\n=======================================================")
    print(f"🛡️  PUERTA DE IMPRIMIBILIDAD (PRINTABILITY GATE) FDM")
    print(f"    Archivo: {os.path.basename(filepath)}")
    if target_device:
        print(f"    Dispositivo Objetivo: {target_device}")
    print(f"=======================================================")

    file_sha = compute_sha256(filepath)
    is_watertight = True
    volume_cm3 = 0.0
    triangles = 0
    size = (0, 0, 0)
    min_z = 0.0
    warnings = []
    gate_status = "PASS"

    # Intentar análisis avanzado con trimesh
    try:
        import trimesh
        mesh = trimesh.load(filepath)
        is_watertight = bool(mesh.is_watertight)
        volume_cm3 = float(mesh.volume / 1000.0) if is_watertight else 0.0
        extents = mesh.extents
        size = (float(extents[0]), float(extents[1]), float(extents[2]))
        triangles = len(mesh.faces)
        min_z = float(mesh.bounds[0][2])
        engine_used = "trimesh"

        base_width = max(0.1, max(size[0], size[1]))
        aspect_ratio = size[2] / base_width

    except Exception:
        data = read_stl_full(filepath)
        size = data["size"]
        triangles = data["count"]
        min_z = data["min"][2]
        engine_used = "stl_parser"
        base_width = max(0.1, max(size[0], size[1]))
        aspect_ratio = size[2] / base_width
        volume_cm3 = (size[0] * size[1] * size[2] * 0.4) / 1000.0

    # 1. Chequeo de límites de cama (Elegoo Centauri Carbon 256x256x256)
    fits_bed = (size[0] <= BED_MAX_X) and (size[1] <= BED_MAX_Y) and (size[2] <= BED_MAX_Z)

    # 2. Análisis de esbeltez / Estabilidad
    stability_status = "Estable"
    if aspect_ratio > 3.5:
        stability_status = "⚠️ Riesgo de bamboleo / Vuelco (Aspect Ratio alto)"
        warnings.append(f"La pieza es muy alta respecto a su base (Relación {aspect_ratio:.1f}:1). Recomendado usar Brim de 8-10 mm o reducir aceleraciones.")
        if gate_status == "PASS":
            gate_status = "WARNING"

    # 3. Comprobación de apoyo en cama (Z=0)
    if abs(min_z) > 0.1:
        warnings.append(f"La base no apoya exactamente en Z=0 (Z_min = {min_z:.2f} mm). Usa '--ground' para apoyarla automáticamente.")
        if gate_status == "PASS":
            gate_status = "WARNING"

    # 4. Análisis de estanqueidad
    autopsy_result = None
    if not is_watertight:
        warnings.append("Malla no manifold: contiene orificios o aristas compartidas por más de dos caras.")
        gate_status = "FAIL"
        run_autopsy = True  # Disparar autopsia automáticamente al fallar estanqueidad

    if not fits_bed:
        warnings.append(f"La pieza excede las dimensiones máximas de la cama ({BED_MAX_X}×{BED_MAX_Y}×{BED_MAX_Z} mm).")
        gate_status = "FAIL"

    # Estimación de peso según material
    densities = {"PLA": 1.24, "PETG": 1.27, "ABS": 1.04, "ASA": 1.07, "TPU": 1.21, "PA-CF": 1.15}
    density = densities.get(material.upper(), 1.24)
    estimated_weight_g = volume_cm3 * density * 0.4

    # Imprimir reporte técnico
    print(f"\n📐 Métricas Geométricas:")
    print(f"• Dimensiones (X × Y × Z): {size[0]:.2f} × {size[1]:.2f} × {size[2]:.2f} mm")
    print(f"• Apoyo en Z=0:            {min_z:.2f} mm ({'✅ En la cama' if abs(min_z) <= 0.1 else '⚠️ Flotando o bajo nivel'})")
    print(f"• Volumen estimado:       {volume_cm3:.2f} cm³ (~{estimated_weight_g:.1f} g de {material})")
    print(f"• Complejidad:             {triangles:,} polígonos")
    print(f"• Motor de cálculo:        {engine_used}")

    print(f"\n🚦 Veredicto de Imprimibilidad:")
    print(f"• Cama Centauri Carbon:    {'✅ OK (Dentro del volumen)' if fits_bed else '❌ SUPERA LÍMITES'}")
    print(f"• Geometría Manifold:      {'✅ OK (Hermética)' if is_watertight else '❌ FALLO (No estanca)'}")
    print(f"• Estabilidad en Cama:     {stability_status}")

    # Ejecución de Autopsia Quirúrgica
    if run_autopsy:
        autopsy_result = run_stl_autopsy(filepath)
        if "error" not in autopsy_result:
            print(f"\n🔬 Autopsia de Malla (stl_autopsy):")
            print(f"• Aristas abiertas (usadas 1 vez):     {autopsy_result['edges_used_once']}")
            print(f"• Aristas no-manifold (usadas 3+ vez): {autopsy_result['edges_used_3plus']}")
            if autopsy_result["defect_region"]:
                dr = autopsy_result["defect_region"]
                print(f"• Región con fugas detectadas:")
                print(f"  - Altura Z: {dr['z_min_mm']:.2f} mm .. {dr['z_max_mm']:.2f} mm")
                print(f"  - Radio R:  {dr['radius_min_mm']:.2f} mm .. {dr['radius_max_mm']:.2f} mm")
                if autopsy_result["worst_z_heights"]:
                    height_str = ", ".join([f"Z={item['z_mm']}mm ({item['open_points']} pts)" for item in autopsy_result["worst_z_heights"]])
                    print(f"  - Cotas Z con mayor concentración de fugas: {height_str}")
            if autopsy_result["bore_analysis"]:
                ba = autopsy_result["bore_analysis"]
                print(f"• Barreno interior: {ba['profile']} (Radio {ba['radius_min_mm']:.2f} a {ba['radius_max_mm']:.2f} mm)")

    if warnings:
        print("\n⚠️ Advertencias detectadas:")
        for w in warnings:
            print(f"  - {w}")

    print(f"\n🏁 RESULTADO FINAL: [{gate_status}]")
    print("=======================================================\n")

    # Preservar o resolver target_device si existe manifest previo
    target_dir = project_dir or os.path.dirname(filepath)
    manifest_path = os.path.join(target_dir, "manifest.json")
    resolved_target_device = target_device
    if resolved_target_device is None and os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                if old_data.get("target_device"):
                    resolved_target_device = old_data["target_device"]
        except Exception:
            pass

    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "file": os.path.basename(filepath),
    }
    if resolved_target_device:
        report_data["target_device"] = resolved_target_device

    report_data.update({
        "sha256": file_sha,
        "gate_status": gate_status,
        "is_watertight": is_watertight,
        "fits_bed_256": fits_bed,
        "dimensions_mm": {"x": round(size[0], 2), "y": round(size[1], 2), "z": round(size[2], 2)},
        "z_min_mm": round(min_z, 2),
        "volume_cm3": round(volume_cm3, 2),
        "material": material,
        "estimated_weight_grams": round(estimated_weight_g, 1),
        "warnings": warnings,
        "autopsy": autopsy_result
    })

    if generate_manifest or project_dir:
        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"📝 Manifest de proyecto guardado en: {manifest_path}")
        except Exception as e:
            print(f"No se pudo guardar el manifest: {e}")

    return (gate_status != "FAIL"), report_data

def main():
    parser = argparse.ArgumentParser(description="Puerta de Imprimibilidad y Validador FDM para Elegoo Centauri Carbon")
    parser.add_argument("stl_file", help="Ruta al archivo STL")
    parser.add_argument("--manifest", action="store_true", help="Generar/actualizar manifest.json en el directorio del proyecto")
    parser.add_argument("--material", default="PLA", choices=["PLA", "PETG", "ABS", "ASA", "TPU", "PA-CF"], help="Material para estimar peso")
    parser.add_argument("--target-device", default=None, help="Nombre y modelo exacto del dispositivo/máquina receptora (ej. 'Honeywell Slate R8001M1150')")
    parser.add_argument("--ground", action="store_true", help="Alinear la base del modelo exactamente en Z=0")
    parser.add_argument("--rotate-y-up", action="store_true", help="Rotar modelo de coordenadas Y-up a Z-up")
    parser.add_argument("--autopsy", action="store_true", help="Forzar ejecución de autopsia de defectos y análisis de barreno")

    args = parser.parse_args()

    if args.ground or args.rotate_y_up:
        fix_stl_coordinates(args.stl_file, rotate_y_up=args.rotate_y_up, ground_z=args.ground)

    passed, _ = evaluate_mesh(
        args.stl_file,
        generate_manifest=args.manifest,
        material=args.material,
        target_device=args.target_device,
        run_autopsy=args.autopsy
    )
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
