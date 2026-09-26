#!/usr/bin/env python3
"""
export_3mf.py — Empaquetador multi-pieza STL a 3MF con asignación de materiales y colores
Inspirado en 'VibePrint3D' (Circus-Systems).

Permite empaquetar múltiples archivos STL en un único archivo .3mf manteniendo las posiciones relativas
y asignando materiales/colores para OrcaSlicer, Elegoo Slicer, Bambu Studio o PrusaSlicer.

Uso:
    python3 scripts/export_3mf.py base.stl:PETG tapa.stl:PETG junta.stl:TPU -o ensamble.3mf --title "Carcasa IP67"
"""

import sys
import os
import struct
import argparse
import zipfile
import xml.etree.ElementTree as ET

DEFAULT_MATERIALS = {
    "PETG":   {"color": "#646464FF", "desc": "Gris Oscuro - Estructural"},
    "TPU":    {"color": "#FF8C00FF", "desc": "Naranja - Flexible / Juntas"},
    "PLA":    {"color": "#E0E0E0FF", "desc": "Blanco - Prototipos"},
    "ASA":    {"color": "#A0A0A0FF", "desc": "Gris Claro - Intemperie / UV"},
    "ABS":    {"color": "#303030FF", "desc": "Negro - Temperatura"},
    "PA-CF":  {"color": "#1A1A1AFF", "desc": "Negro Carbón - Alto Rendimiento"},
    "NYLON":  {"color": "#E8DCC8FF", "desc": "Crema - Desgaste y Resistencia"}
}

def parse_stl(filepath):
    """Lee un archivo STL (binario o ASCII) y retorna (vertices, triangles)."""
    vertices = []
    triangles = []
    vert_map = {}

    def get_vert_idx(x, y, z):
        # Redondeo para deduplicación de vértices compartidos
        key = (round(x, 4), round(y, 4), round(z, 4))
        if key in vert_map:
            return vert_map[key]
        idx = len(vertices)
        vertices.append(key)
        vert_map[key] = idx
        return idx

    with open(filepath, "rb") as f:
        header = f.read(80)
        # Comprobar si parece binario
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
                f.read(12) # Normal
                v1 = struct.unpack("<fff", f.read(12))
                v2 = struct.unpack("<fff", f.read(12))
                v3 = struct.unpack("<fff", f.read(12))
                f.read(2) # Attribute

                i1 = get_vert_idx(*v1)
                i2 = get_vert_idx(*v2)
                i3 = get_vert_idx(*v3)
                triangles.append((i1, i2, i3))
        else:
            # Parseo ASCII
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

def create_3mf(parts_info, output_path, title="3D Printing Assembly"):
    """
    Empaqueta las partes en un archivo .3mf estándar.
    parts_info: lista de dicts con:
      - name: str
      - vertices: list of (x,y,z)
      - triangles: list of (i1,i2,i3)
      - material: str
      - color_hex: str
    """
    # 1. Preparar mapa de colores únicos
    materials_list = []
    mat_to_pindex = {}
    for p in parts_info:
        mat = p["material"]
        if mat not in mat_to_pindex:
            mat_to_pindex[mat] = len(materials_list)
            materials_list.append((mat, p["color_hex"]))

    # 2. Generar XML 3D/3dmodel.model
    model_xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">',
        f'  <metadata name="Title">{title}</metadata>',
        f'  <metadata name="Application">3D Printing Specialist Template</metadata>',
        '  <resources>'
    ]

    # Grupo de materiales/colores
    model_xml.append('    <m:colorgroup id="1">')
    for mat_name, col in materials_list:
        model_xml.append(f'      <m:color color="{col}" />')
    model_xml.append('    </m:colorgroup>')

    # Objetos (mallas)
    obj_id = 2
    build_items = []
    for p in parts_info:
        pindex = mat_to_pindex[p["material"]]
        pname = p["name"]
        model_xml.append(f'    <object id="{obj_id}" type="model" name="{pname}" pid="1" pindex="{pindex}">')
        model_xml.append('      <mesh>')
        
        # Vértices
        model_xml.append('        <vertices>')
        for vx, vy, vz in p["vertices"]:
            model_xml.append(f'          <vertex x="{vx:.4f}" y="{vy:.4f}" z="{vz:.4f}" />')
        model_xml.append('        </vertices>')

        # Triángulos
        model_xml.append('        <triangles>')
        for v1, v2, v3 in p["triangles"]:
            model_xml.append(f'          <triangle v1="{v1}" v2="{v2}" v3="{v3}" />')
        model_xml.append('        </triangles>')

        model_xml.append('      </mesh>')
        model_xml.append('    </object>')
        
        build_items.append(f'    <item objectid="{obj_id}" />')
        obj_id += 1

    model_xml.append('  </resources>')
    model_xml.append('  <build>')
    model_xml.extend(build_items)
    model_xml.append('  </build>')
    model_xml.append('</model>')

    full_model_str = "\n".join(model_xml)

    # 3. XMLs de estructura OPC
    content_types_str = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />\n'
        '  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodelxml" />\n'
        '</Types>'
    )

    rels_str = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" />\n'
        '</Relationships>'
    )

    # 4. Escribir archivo ZIP .3mf
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types_str)
        z.writestr("_rels/.rels", rels_str)
        z.writestr("3D/3dmodel.model", full_model_str)

    print(f"✅ Archivo 3MF empaquetado con éxito: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Empaqueta múltiples piezas STL en un contenedor 3MF multi-material.")
    parser.add_argument("parts", nargs="+", help="Rutas de archivos STL, opcionalmente con sufijo :MATERIAL (ej. base.stl:PETG)")
    parser.add_argument("-o", "--output", required=True, help="Ruta de destino del archivo .3mf")
    parser.add_argument("--title", default="Ensamble 3D", help="Título del modelo para el slicer")
    parser.add_argument("--default-material", default="PETG", help="Material por defecto si no se especifica (default: PETG)")
    
    args = parser.parse_args()

    parts_data = []
    print(f"📦 Procesando {len(args.parts)} piezas para generar {args.output}...")

    for spec in args.parts:
        if ":" in spec:
            fpath, mat = spec.split(":", 1)
        else:
            fpath, mat = spec, args.default_material
            
        if not os.path.exists(fpath):
            print(f"❌ Error: Archivo no encontrado: {fpath}")
            sys.exit(1)

        mat_upper = mat.upper()
        mat_info = DEFAULT_MATERIALS.get(mat_upper, {"color": "#888888FF", "desc": "Material Personalizado"})
        
        name = os.path.splitext(os.path.basename(fpath))[0]
        print(f"  • Leyendo '{name}' [{mat_upper}] desde {fpath}...")
        verts, tris = parse_stl(fpath)
        print(f"    ↳ {len(verts):,} vértices, {len(tris):,} triángulos")

        parts_data.append({
            "name": name,
            "vertices": verts,
            "triangles": tris,
            "material": mat_upper,
            "color_hex": mat_info["color"]
        })

    create_3mf(parts_data, args.output, title=args.title)
    print(f"\n💡 Listo para abrir en OrcaSlicer o Elegoo Slicer con colores y posiciones preconfiguradas.")

if __name__ == "__main__":
    main()
