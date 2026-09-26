#!/usr/bin/env python3
"""
export_3mf.py — Empaquetador nativo de proyectos 3MF para Elegoo Slicer / OrcaSlicer (Elegoo Centauri Carbon)

Convierte archivos STL en proyectos .3mf completamente configurados, posicionados en la cama (Z-up, Z=0,
centrados en X=128, Y=128), con metadatos nativos para evitar diálogos de incompatibilidad y con parámetros
de corte (paredes, relleno, soportes, filamentos, tolerancias) precargados por defecto.

REGLAS DE ORO DEL MOTOR C++ DE ELEGOOSLICER:
1. Todos los valores escalares en project_settings.config DEBEN ser strings ("1", "6", "0.15").
   Los números puros (int/float) provocan "invalid json type" y son descartados silenciosamente.
2. Todo parámetro modificado DEBE listarse en different_settings_to_system[0]. De lo contrario,
   ElegooSlicer lo sobreescribe con el valor del perfil base de fábrica.
3. print_settings_id debe vincularse a un preset de sistema válido (ej. "0.20mm Standard @Elegoo CC2 0.4 nozzle")
   para evitar el fallback a Preset 0 ("Default Setting").
4. 3D/3dmodel.model y slice_info.config deben declarar ElegooSlicer-1.5.3.5 para evitar la ventana
   "The 3MF file you are importing may be incompatible".

Uso:
    # Perfil mecánico reforzado (6 paredes, 40% giroide, árbol auto, +0.15 mm compensación):
    python3 scripts/export_3mf.py pieces/aguja_slate_r8001m/aguja_slate_r8001m.stl -o aguja.3mf --intent mechanical --material PETG

    # Personalizado:
    python3 scripts/export_3mf.py pieza.stl -o proyecto.3mf --material PLA --support --walls 4 --infill 30%
"""

import sys
import os
import json
import struct
import argparse
import zipfile

# Materiales y perfiles reconocidos
DEFAULT_MATERIALS = {
    "PETG":   {"color": "#1A1A1A", "type": "PETG",  "id": "Generic PETG @System", "density": "1.27", "nozzle_temp": "240", "nozzle_temp_initial": "245", "bed_temp": "80", "bed_temp_initial": "85"},
    "PLA":    {"color": "#E0E0E0", "type": "PLA",   "id": "Elegoo PLA @ECC2",      "density": "1.24", "nozzle_temp": "210", "nozzle_temp_initial": "215", "bed_temp": "55", "bed_temp_initial": "60"},
    "ABS":    {"color": "#808080", "type": "ABS",   "id": "Generic ABS @Elegoo Centauri", "density": "1.04", "nozzle_temp": "260", "nozzle_temp_initial": "260", "bed_temp": "100", "bed_temp_initial": "105"},
    "ASA":    {"color": "#A0A0A0", "type": "ASA",   "id": "Generic ASA @System",   "density": "1.07", "nozzle_temp": "260", "nozzle_temp_initial": "260", "bed_temp": "100", "bed_temp_initial": "105"},
    "TPU":    {"color": "#FF8C00", "type": "TPU",   "id": "Generic TPU @System",   "density": "1.21", "nozzle_temp": "230", "nozzle_temp_initial": "230", "bed_temp": "45", "bed_temp_initial": "50"},
    "PA-CF":  {"color": "#1A1A1A", "type": "PA-CF", "id": "Generic PA-CF @System", "density": "1.20", "nozzle_temp": "280", "nozzle_temp_initial": "285", "bed_temp": "100", "bed_temp_initial": "105"}
}

INTENT_PRESETS = {
    "mechanical": {
        "wall_loops": "6",
        "sparse_infill_density": "40%",
        "sparse_infill_pattern": "gyroid",
        "enable_support": "1",
        "support_type": "tree(auto)",
        "xy_hole_compensation": "0.15",
        "bottom_shell_layers": "5",
        "top_shell_layers": "5"
    },
    "standard": {
        "wall_loops": "3",
        "sparse_infill_density": "15%",
        "sparse_infill_pattern": "rectilinear",
        "enable_support": "0",
        "support_type": "tree(auto)",
        "xy_hole_compensation": "0",
        "bottom_shell_layers": "3",
        "top_shell_layers": "4"
    },
    "fast": {
        "wall_loops": "2",
        "sparse_infill_density": "10%",
        "sparse_infill_pattern": "lightning",
        "enable_support": "0",
        "support_type": "tree(auto)",
        "xy_hole_compensation": "0",
        "bottom_shell_layers": "3",
        "top_shell_layers": "3"
    },
    "aesthetic": {
        "wall_loops": "3",
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "enable_support": "0",
        "support_type": "tree(auto)",
        "xy_hole_compensation": "0",
        "bottom_shell_layers": "4",
        "top_shell_layers": "5",
        "ironing_type": "top",
        "ironing_pattern": "rectilinear",
        "ironing_flow": "10%",
        "ironing_speed": "30",
        "ironing_spacing": "0.15",
        "top_surface_pattern": "monotonicline"
    }
}

def parse_stl(filepath):
    """Lee un archivo STL y devuelve vértices únicos y triángulos indexados."""
    vertices = []
    triangles = []
    vert_map = {}

    def get_vert_idx(x, y, z):
        key = (round(x, 4), round(y, 4), round(z, 4))
        if key in vert_map:
            return vert_map[key]
        idx = len(vertices)
        vertices.append(key)
        vert_map[key] = idx
        return idx

    with open(filepath, "rb") as f:
        header = f.read(80)
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        f.seek(80)

        is_binary = False
        if file_size >= 84:
            count_bytes = f.read(4)
            num_triangles = struct.unpack("<I", count_bytes)[0]
            expected_size = 84 + (num_triangles * 50)
            if file_size == expected_size:
                is_binary = True

        if is_binary:
            f.seek(84)
            for _ in range(num_triangles):
                f.read(12)  # Normal
                v1 = struct.unpack("<fff", f.read(12))
                v2 = struct.unpack("<fff", f.read(12))
                v3 = struct.unpack("<fff", f.read(12))
                f.read(2)   # Attribute

                i1 = get_vert_idx(*v1)
                i2 = get_vert_idx(*v2)
                i3 = get_vert_idx(*v3)
                triangles.append((i1, i2, i3))
        else:
            f.seek(0)
            text = f.read().decode("utf-8", errors="ignore")
            current_tri = []
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("vertex"):
                    parts = line.split()
                    vx, vy, vz = float(parts[1]), float(parts[2]), float(parts[3])
                    current_tri.append(get_vert_idx(vx, vy, vz))
                    if len(current_tri) == 3:
                        triangles.append(tuple(current_tri))
                        current_tri = []

    return vertices, triangles

def load_or_create_base_config():
    """Carga la plantilla base de 657 parámetros de ElegooSlicer."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(repo_root, "resources", "elegoo", "project_settings_base.json")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def package_elegoo_3mf(stl_path, output_path, intent="mechanical", material="PETG",
                       color=None, overrides=None):
    """
    Empaqueta un modelo STL en un proyecto nativo para ElegooSlicer / OrcaSlicer.
    """
    stl_name = os.path.splitext(os.path.basename(stl_path))[0]
    mat_key = material.upper()
    mat_data = DEFAULT_MATERIALS.get(mat_key, DEFAULT_MATERIALS["PETG"])
    hex_color = color if color else mat_data["color"]

    # 1. Analizar vértices y orientar Z=0, centrado en cama (128, 128)
    verts, tris = parse_stl(stl_path)
    if len(verts) == 0:
        raise ValueError(f"No se pudieron leer vértices de {stl_path}")

    min_x = min(v[0] for v in verts)
    max_x = max(v[0] for v in verts)
    min_y = min(v[1] for v in verts)
    max_y = max(v[1] for v in verts)
    min_z = min(v[2] for v in verts)

    # Offset para centrar en cama Elegoo Centauri (256x256x256 mm)
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    offset_x = 128.0 - center_x
    offset_y = 128.0 - center_y
    offset_z = -min_z  # Z apoyado exactamente en la cama (Z=0)

    # 2. Configuración de parámetros de corte por intención
    cfg = load_or_create_base_config()
    intent_settings = INTENT_PRESETS.get(intent, INTENT_PRESETS["mechanical"]).copy()
    if overrides:
        intent_settings.update(overrides)

    # Optimización anti-fusión térmica para soportes según material
    if mat_key == "PETG" and intent_settings.get("enable_support") == "1":
        intent_settings.setdefault("support_top_z_distance", "0.26")
        intent_settings.setdefault("support_bottom_z_distance", "0.26")
        intent_settings.setdefault("support_object_xy_distance", "0.5")
        intent_settings.setdefault("support_interface_top_layers", "1")
        intent_settings.setdefault("support_interface_spacing", "1.0")
        intent_settings.setdefault("support_style", "tree_slim")
        intent_settings.setdefault("tree_support_tip_diameter", "0.6")
    elif mat_key in ("ABS", "ASA") and intent_settings.get("enable_support") == "1":
        intent_settings.setdefault("support_top_z_distance", "0.24")
        intent_settings.setdefault("support_bottom_z_distance", "0.24")
        intent_settings.setdefault("support_object_xy_distance", "0.6")
        intent_settings.setdefault("support_interface_top_layers", "2")
        intent_settings.setdefault("support_interface_spacing", "1.2")
        intent_settings.setdefault("support_style", "tree_slim")
        intent_settings.setdefault("tree_support_tip_diameter", "0.5")

    # REGLA CRÍTICA 1: TODOS LOS VALORES ESCALARES DEBEN SER STRINGS
    for k, v in intent_settings.items():
        cfg[k] = str(v)

    # REGLA CRÍTICA 3: VINCULAR A PRESET BASE DEL SISTEMA
    cfg["printer_settings_id"] = "Elegoo Centauri Carbon 2 0.4 nozzle"
    cfg["default_print_profile"] = "0.20mm Standard @Elegoo CC2 0.4 nozzle"
    cfg["print_settings_id"] = "0.20mm Standard @Elegoo CC2 0.4 nozzle"

    # Configurar filamento mono-material
    for k, v in cfg.items():
        if isinstance(v, list) and len(v) == 3:
            cfg[k] = [str(v[0])]

    cfg["filament_colour"] = [hex_color]
    cfg["filament_multi_colour"] = [hex_color]
    cfg["filament_type"] = [mat_data["type"]]
    cfg["filament_vendor"] = ["Generic"]
    cfg["filament_settings_id"] = [mat_data["id"]]
    cfg["default_filament_profile"] = [mat_data["id"]]
    cfg["filament_self_index"] = ["1"]
    cfg["filament_printable"] = ["3"]
    cfg["filament_density"] = [mat_data["density"]]
    cfg["filament_cost"] = ["30"]
    cfg["filament_flow_ratio"] = ["1"]
    cfg["default_filament_colour"] = [hex_color]

    filament_diffs = ["filament_colour"]
    if "nozzle_temp" in mat_data:
        cfg["nozzle_temperature"] = [mat_data["nozzle_temp"]]
        cfg["nozzle_temperature_initial_layer"] = [mat_data.get("nozzle_temp_initial", mat_data["nozzle_temp"])]
        filament_diffs.extend(["nozzle_temperature", "nozzle_temperature_initial_layer"])
    if "bed_temp" in mat_data:
        cfg["textured_plate_temp"] = [mat_data["bed_temp"]]
        cfg["textured_plate_temp_initial_layer"] = [mat_data.get("bed_temp_initial", mat_data["bed_temp"])]
        cfg["hot_plate_temp"] = [mat_data["bed_temp"]]
        cfg["hot_plate_temp_initial_layer"] = [mat_data.get("bed_temp_initial", mat_data["bed_temp"])]
        filament_diffs.extend(["textured_plate_temp", "textured_plate_temp_initial_layer", "hot_plate_temp", "hot_plate_temp_initial_layer"])

    # REGLA CRÍTICA 2: REGISTRAR TODAS LAS MODIFICACIONES EN different_settings_to_system
    diff_keys = list(intent_settings.keys())
    cfg["different_settings_to_system"] = [
        ";".join(diff_keys),
        ";".join(filament_diffs),
        "", ""
    ]

    # 3. Construir XMLs de estructura 3MF
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
        ' <Default Extension="png" ContentType="image/png"/>\n'
        ' <Default Extension="gcode" ContentType="text/x.gcode"/>\n'
        '</Types>'
    )

    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
        ' <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>\n'
        '</Relationships>'
    )

    model_rels = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        f' <Relationship Target="/3D/Objects/{stl_name}.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
        '</Relationships>'
    )

    # REGLA CRÍTICA 4: Declarar ElegooSlicer-1.5.3.5 para evitar la advertencia de incompatibilidad
    model_root = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
        ' <metadata name="Application">ElegooSlicer-1.5.3.5</metadata>\n'
        ' <metadata name="OrcaSlicer">2.4.2</metadata>\n'
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        ' <resources>\n'
        '  <object id="2" p:UUID="00000007-61cb-4c03-9d28-80fed5dfa1dc" type="model">\n'
        '   <components>\n'
        f'    <component p:path="/3D/Objects/{stl_name}.model" objectid="1" p:UUID="00070000-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n'
        '   </components>\n'
        '  </object>\n'
        ' </resources>\n'
        ' <build p:UUID="2c7c17d8-22b5-4d84-8835-1976022ea369">\n'
        f'  <item objectid="2" p:UUID="00000002-b1ec-4553-aec9-835e5b724bb4" transform="1 0 0 0 1 0 0 0 1 {offset_x:.4f} {offset_y:.4f} {offset_z:.4f}" printable="1" auto_drop="1"/>\n'
        ' </build>\n'
        '</model>\n'
    )

    slice_info = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<config>\n'
        '  <header>\n'
        '    <header_item key="X-BBL-Client-Type" value="slicer"/>\n'
        '    <header_item key="X-BBL-Client-Version" value="01.05.03.05"/>\n'
        '    <header_item key="X-BBL-Client-Name" value="ElegooSlicer"/>\n'
        '    <header_item key="OrcaSlicer-Version" value="2.4.2"/>\n'
        '  </header>\n'
        '</config>\n'
    )

    # Objeto de malla específico
    obj_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">',
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
        ' <resources>',
        '  <object id="1" p:UUID="00070000-81cb-4c03-9d28-80fed5dfa1dc" type="model">',
        '   <mesh>',
        '    <vertices>'
    ]
    for vx, vy, vz in verts:
        obj_lines.append(f'     <vertex x="{vx:.6f}" y="{vy:.6f}" z="{vz:.6f}"/>')
    obj_lines.append('    </vertices>')
    obj_lines.append('    <triangles>')
    for v1, v2, v3 in tris:
        obj_lines.append(f'     <triangle v1="{v1}" v2="{v2}" v3="{v3}"/>')
    obj_lines.append('    </triangles>')
    obj_lines.append('   </mesh>')
    obj_lines.append('  </object>')
    obj_lines.append(' </resources>')
    obj_lines.append('</model>')
    obj_model_xml = "\n".join(obj_lines)

    # 4. Escribir archivo .3mf ZIP
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    res_dir = os.path.join(repo_root, "resources", "elegoo")

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model_root)
        z.writestr("3D/_rels/3dmodel.model.rels", model_rels)
        z.writestr(f"3D/Objects/{stl_name}.model", obj_model_xml)
        z.writestr("Metadata/slice_info.config", slice_info)
        z.writestr("Metadata/project_settings.config", json.dumps(cfg, indent=4))
        z.writestr("Metadata/filament_sequence.json", json.dumps({"plate_1": {"nozzle_sequence": [], "optimal_assignment": [], "sequence": []}}))
        z.writestr("Metadata/plate_1.json", json.dumps({
            "bed_type": "textured_plate",
            "filament_colors": [hex_color],
            "filament_ids": [1],
            "first_extruder": 0,
            "nozzle_diameter": 0.4,
            "version": 2
        }))

        # Incrustar miniaturas si están disponibles
        for thumb in ["plate_1.png", "plate_1_small.png", "plate_no_light_1.png", "top_1.png", "pick_1.png"]:
            t_path = os.path.join(res_dir, thumb)
            if os.path.exists(t_path):
                with open(t_path, "rb") as tf:
                    z.writestr(f"Metadata/{thumb}", tf.read())

    print(f"✅ Proyecto 3MF nativo generado con éxito:")
    print(f"   ↳ Destino:  {output_path}")
    print(f"   ↳ Intención: {intent.upper()} ({intent_settings['wall_loops']} paredes, {intent_settings['sparse_infill_density']} {intent_settings['sparse_infill_pattern']})")
    print(f"   ↳ Soportes: {'Activados (' + intent_settings['support_type'] + ')' if intent_settings['enable_support'] == '1' else 'Desactivados'}")
    print(f"   ↳ Barreno:  +{intent_settings.get('xy_hole_compensation', '0')} mm holgura X-Y")
    print(f"   ↳ Material: {mat_key} ({hex_color})")

def main():
    parser = argparse.ArgumentParser(description="Empaquetador nativo 3MF para Elegoo Centauri Carbon y OrcaSlicer.")
    parser.add_argument("stl", help="Ruta del archivo STL a empaquetar")
    parser.add_argument("-o", "--output", required=True, help="Ruta de destino del archivo .3mf")
    parser.add_argument("--intent", choices=["mechanical", "standard", "fast", "aesthetic"], default="mechanical",
                        help="Perfil de intención de corte (default: mechanical)")
    parser.add_argument("--material", choices=list(DEFAULT_MATERIALS.keys()), default="PETG",
                        help="Material del filamento (default: PETG)")
    parser.add_argument("--color", help="Color HEX para el filamento (ej. #1A1A1A)")
    parser.add_argument("--support", dest="support", action="store_true", help="Forzar soportes activados")
    parser.add_argument("--no-support", dest="support", action="store_false", help="Forzar soportes desactivados")
    parser.set_defaults(support=None)
    parser.add_argument("--walls", type=int, help="Número de bucles de pared")
    parser.add_argument("--infill", help="Densidad de relleno (ej. 40%%)")
    parser.add_argument("--infill-pattern", help="Patrón de relleno (ej. gyroid, rectilinear)")
    parser.add_argument("--hole-compensation", type=float, help="Compensación de agujeros X-Y en mm (ej. 0.15)")
    parser.add_argument("--ironing", dest="ironing", action="store_true", help="Activar planchado térmico (ironing) en capas superiores")

    args = parser.parse_args()

    if not os.path.exists(args.stl):
        print(f"❌ Error: Archivo STL no encontrado: {args.stl}")
        sys.exit(1)

    overrides = {}
    if args.support is not None:
        overrides["enable_support"] = "1" if args.support else "0"
    if args.walls is not None:
        overrides["wall_loops"] = str(args.walls)
    if args.infill is not None:
        inf = args.infill if "%" in args.infill else f"{args.infill}%"
        overrides["sparse_infill_density"] = inf
    if args.infill_pattern is not None:
        overrides["sparse_infill_pattern"] = args.infill_pattern
    if args.hole_compensation is not None:
        overrides["xy_hole_compensation"] = str(args.hole_compensation)
    if args.ironing:
        overrides["ironing_type"] = "top"
        overrides["ironing_pattern"] = "rectilinear"
        overrides["ironing_flow"] = "10%"
        overrides["ironing_speed"] = "30"
        overrides["ironing_spacing"] = "0.15"
        overrides["top_surface_pattern"] = "monotonicline"

    package_elegoo_3mf(
        stl_path=args.stl,
        output_path=args.output,
        intent=args.intent,
        material=args.material,
        color=args.color,
        overrides=overrides
    )

if __name__ == "__main__":
    main()
