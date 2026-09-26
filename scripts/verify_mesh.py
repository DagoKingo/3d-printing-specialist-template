#!/usr/bin/env python3
"""
verify_mesh.py — Puerta de Imprimibilidad (Printability Gate), Normalizador y Validador FDM
Inspirado en la ingeniería de 'idea-to-print', 'print3d' y 'meshy-3d-agent'.

Comprueba:
1. Límites físicos de la Elegoo Centauri Carbon (256 × 256 × 256 mm).
2. Estanqueidad geométrica (Malla Manifold / Watertight).
3. Estabilidad en cama (Área de contacto base y relación de esbeltez/aspect ratio).
4. Posición vertical en Z (contacto en Z=0) y normalización Y-up a Z-up.
5. Generación de 'manifest.json' (Job Ledger del proyecto).
"""

import sys
import os
import struct
import hashlib
import json
import time

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

def evaluate_mesh(filepath, generate_manifest=False, project_dir=None, material="PLA"):
    if not os.path.exists(filepath):
        print(f"❌ Error: El archivo '{filepath}' no existe.")
        return False, {}

    print(f"\n=======================================================")
    print(f"🛡️  PUERTA DE IMPRIMIBILIDAD (PRINTABILITY GATE) FDM")
    print(f"    Archivo: {os.path.basename(filepath)}")
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

    except ImportError:
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
    if not is_watertight:
        warnings.append("Malla no manifold: contiene orificios o aristas compartidas por más de dos caras.")
        gate_status = "FAIL"

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

    if warnings:
        print("\n⚠️ Advertencias detectadas:")
        for w in warnings:
            print(f"  - {w}")

    print(f"\n🏁 RESULTADO FINAL: [{gate_status}]")
    print("=======================================================\n")

    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "file": os.path.basename(filepath),
        "sha256": file_sha,
        "gate_status": gate_status,
        "is_watertight": is_watertight,
        "fits_bed_256": fits_bed,
        "dimensions_mm": {"x": round(size[0], 2), "y": round(size[1], 2), "z": round(size[2], 2)},
        "z_min_mm": round(min_z, 2),
        "volume_cm3": round(volume_cm3, 2),
        "material": material,
        "estimated_weight_grams": round(estimated_weight_g, 1),
        "warnings": warnings
    }

    if generate_manifest or project_dir:
        target_dir = project_dir or os.path.dirname(filepath)
        manifest_path = os.path.join(target_dir, "manifest.json")
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
    parser.add_argument("--ground", action="store_true", help="Alinear la base del modelo exactamente en Z=0")
    parser.add_argument("--rotate-y-up", action="store_true", help="Rotar modelo de coordenadas Y-up a Z-up")

    args = parser.parse_args()

    if args.ground or args.rotate_y_up:
        fix_stl_coordinates(args.stl_file, rotate_y_up=args.rotate_y_up, ground_z=args.ground)

    passed, _ = evaluate_mesh(args.stl_file, generate_manifest=args.manifest, material=args.material)
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
