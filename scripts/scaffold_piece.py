#!/usr/bin/env python3
"""
scaffold_piece.py — Generador de estructura para una nueva pieza con sus artefactos.
Crea el directorio 'pieces/<nombre_pieza>/' con su código CAD inicial, ficha técnica y carpeta de renders.
"""

import sys
import os
import argparse
import re

def sanitize_name(name):
    # Convertir a minúsculas y reemplazar espacios o caracteres inválidos por guiones bajos
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', name.lower().strip())
    clean = re.sub(r'_+', '_', clean)
    return clean.strip('_')

def scaffold_piece(piece_name, template="starter", material="PLA", description=""):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    clean_name = sanitize_name(piece_name)
    piece_dir = os.path.join(root_dir, "pieces", clean_name)
    renders_dir = os.path.join(piece_dir, "renders")

    if os.path.exists(piece_dir):
        print(f"⚠️ El directorio para la pieza '{clean_name}' ya existe en: {piece_dir}")
        return piece_dir

    os.makedirs(renders_dir, exist_ok=True)
    with open(os.path.join(renders_dir, ".gitkeep"), "w") as f:
        f.write("")

    # 1. Crear el archivo CAD paramétrico inicial
    scad_path = os.path.join(piece_dir, f"{clean_name}.scad")
    scad_content = f"""// =====================================================================
// Pieza: {clean_name}
// Material previsto: {material}
// Máquina: Elegoo Centauri Carbon (CoreXY, 256x256x256 mm)
// =====================================================================

include <BOSL2/std.scad>
include <BOSL2/screws.scad>

// --- RESOLUCIÓN DINÁMICA ---
$preview_fn = 32;
$export_fn = 96;
$fn = $preview ? $preview_fn : $export_fn;
$slop = 0.2; // Tolerancia de holgura diametral FDM

// --- PARÁMETROS PRINCIPALES (mm) ---
ANCHO  = 50.0;
LARGO  = 40.0;
ALTURA = 15.0;
GROSOR_PARED = 2.4; // 6 perímetros con boquilla 0.4 mm

// --- SELECTOR RENDER ("preview", "cuerpo", "tapa") ---
RENDER = "preview";

module cuerpo() {{
    diff()
    cuboid([ANCHO, LARGO, ALTURA], rounding=2, edges="Z", anchor=BOTTOM) {{
        // Cavidad interior (shiftout=0.01 mandatorio para corte limpio)
        attach(TOP, TOP, inside=true, shiftout=0.01)
            cuboid([ANCHO - GROSOR_PARED*2, LARGO - GROSOR_PARED*2, ALTURA - GROSOR_PARED], 
                   rounding=1, edges="Z");
                   
        // Barrenos de montaje M3 en las esquinas
        attach(TOP, TOP, inside=true, shiftout=0.01)
            grid_copies(spacing=[ANCHO - 10, LARGO - 10])
                screw_hole("M3,12", head="socket", counterbore=true, anchor=TOP);
    }}
}}

// --- CONTROL DE RENDERIZADO ---
if (RENDER == "preview" || RENDER == "cuerpo") {{
    cuerpo();
}}
"""
    with open(scad_path, "w", encoding="utf-8") as f:
        f.write(scad_content)

    # 2. Crear ficha técnica README.md
    readme_path = os.path.join(piece_dir, "README.md")
    readme_content = f"""# Pieza: {clean_name}

{description if description else "Pieza diseñada para fabricación aditiva FDM en Elegoo Centauri Carbon."}

---

## 🎯 Especificaciones de Diseño
- **Material recomendado:** `{material}`
- **Volumen de impresión:** Elegoo Centauri Carbon (256 × 256 × 256 mm)
- **Boquilla recomendada:** 0.4 mm acero endurecido
- **Holgura de ajuste ($slop):** `0.2 mm`
- **Espesor de pared base:** Múltiplo de 0.4 mm (e.g. 2.0 mm / 2.4 mm)

---

## 📦 Artefactos de la Pieza

| Artefacto | Descripción | Estado |
| :--- | :--- | :--- |
| [`{clean_name}.scad`](./{clean_name}.scad) | Código CAD paramétrico editable (OpenSCAD + BOSL2) | ✅ Creado |
| [`{clean_name}.stl`](./{clean_name}.stl) | Malla exportada hermética (Z=0, Z-up) | ⏳ Pendiente de compilar |
| [`{clean_name}.3mf`](./{clean_name}.3mf) | Proyecto OrcaSlicer con perfiles y placa nombrada | ⏳ Pendiente de empaquetar |
| [`manifest.json`](./manifest.json) | Certificado de calidad y auditoría (Printability Gate) | ⏳ Pendiente de verificar |
| [`viewer.html`](./viewer.html) | Visor 3D interactivo en navegador | ⏳ Pendiente de generar |
| [`renders/`](./renders/) | Capturas multiángulo PNG (isométrica, planta, frontal) | ⏳ Pendiente de capturar |

---

## 🛠️ Comandos de Pipeline para esta Pieza

```bash
# 1. Compilar STL desde OpenSCAD
openscad -D 'RENDER="cuerpo"' -o pieces/{clean_name}/{clean_name}.stl pieces/{clean_name}/{clean_name}.scad

# 2. Auditar imprimibilidad y generar manifest.json
python3 scripts/verify_mesh.py pieces/{clean_name}/{clean_name}.stl --manifest --material {material}

# 3. Generar visor Three.js y vistas previas PNG
python3 scripts/generate_gallery.py pieces/{clean_name}/{clean_name}.scad

# 4. Empaquetar a 3MF para OrcaSlicer
python3 scripts/export_3mf.py -o pieces/{clean_name}/{clean_name}.3mf pieces/{clean_name}/{clean_name}.stl:"{clean_name}"
```
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✨ Estructura de pieza creada exitosamente en: pieces/{clean_name}/")
    print(f"  ├── {clean_name}.scad (Modelo paramétrico)")
    print(f"  ├── README.md (Ficha técnica y lista de artefactos)")
    print(f"  └── renders/ (Directorio de vistas previas)")

    return piece_dir

def main():
    parser = argparse.ArgumentParser(description="Scaffold de nueva pieza con sus artefactos para 3D Printing Specialist")
    parser.add_argument("name", help="Nombre descriptivo de la pieza (ej. soporte_sensor_btt, clip_cable_2020)")
    parser.add_argument("--material", default="PLA", choices=["PLA", "PETG", "ABS", "ASA", "TPU", "PA-CF"], help="Material objetivo")
    parser.add_argument("--desc", default="", help="Breve descripción del propósito de la pieza")
    parser.add_argument("--template", default="starter", choices=["starter", "remix"], help="Plantilla base CAD")

    args = parser.parse_args()
    scaffold_piece(args.name, template=args.template, material=args.material, description=args.desc)

if __name__ == "__main__":
    main()
