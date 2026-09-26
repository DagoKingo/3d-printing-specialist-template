#!/usr/bin/env python3
"""
generate_gallery.py — Generador de vistas previas multiángulo y visor HTML 3D interactivo
Inspirado en el GalleryView workflow de chriscantey/skill-3d-printing.
"""

import sys
import os
import subprocess
import shutil

def run_command(cmd):
    try:
        res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, res.stdout.decode()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()

def generate_gallery(scad_or_stl_path, render_part="preview"):
    base_dir = os.path.dirname(os.path.abspath(scad_or_stl_path))
    file_name = os.path.basename(scad_or_stl_path)
    name_without_ext, ext = os.path.splitext(file_name)
    
    output_dir = os.path.join(base_dir, "gallery")
    os.makedirs(output_dir, exist_ok=True)

    print(f"🎨 Generando galería para: {file_name} en {output_dir}")

    # Si es archivo .scad, generar renders con OpenSCAD CLI
    if ext.lower() == ".scad":
        stl_output = os.path.join(output_dir, f"{name_without_ext}.stl")
        print(f"📦 Compilando a STL ({render_part})...")
        cmd_stl = f"openscad -D 'RENDER=\"{render_part}\"' -o \"{stl_output}\" \"{scad_or_stl_path}\""
        ok, out = run_command(cmd_stl)
        if not ok:
            print(f"⚠️ Nota: Para compilar directo, asegúrate de tener instalado 'openscad' (sudo apt install openscad).")
        else:
            print(f"✅ STL generado: {stl_output}")

        # Renderizar vistas previas PNG si openscad está disponible
        print("📸 Capturando vistas en perspectiva...")
        angles = [
            ("iso", "0,0,0,55,0,35,0"),
            ("top", "0,0,0,90,0,0,0"),
            ("front", "0,0,0,15,0,15,0")
        ]
        
        for name, cam in angles:
            png_out = os.path.join(output_dir, f"render-{name}.png")
            cmd_img = f"openscad --autocenter --viewall --colorscheme='Tomorrow Night' --camera={cam} --imgsize=800,600 -D 'RENDER=\"{render_part}\"' -o \"{png_out}\" \"{scad_or_stl_path}\""
            ok, _ = run_command(cmd_img)
            if ok:
                print(f"  • Vista {name}: {png_out}")

    elif ext.lower() == ".stl":
        # Ya es un STL, copiar al directorio de galería
        stl_output = os.path.join(output_dir, file_name)
        shutil.copyfile(scad_or_stl_path, stl_output)

    # Copiar plantilla del visor Three.js
    template_src = os.path.join(os.path.dirname(__file__), "../skills/parametric-cad/templates/viewer.html")
    viewer_dst = os.path.join(output_dir, "index.html")
    
    if os.path.exists(template_src):
        # Ajustar para que cargue el STL correspondiente
        with open(template_src, "r", encoding="utf-8") as f:
            html = f.read()
        target_stl = f"{name_without_ext}.stl" if ext.lower() == ".scad" else file_name
        html = html.replace("model.stl", target_stl)
        with open(viewer_dst, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"🌐 Visor 3D interactivo creado en: file://{viewer_dst}")
        print("💡 Puedes abrir ese enlace en tu navegador para rotar e inspeccionar el modelo.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/generate_gallery.py <archivo.scad | archivo.stl> [render_part]")
        sys.exit(1)
    
    part = sys.argv[2] if len(sys.argv) > 2 else "preview"
    generate_gallery(sys.argv[1], part)
