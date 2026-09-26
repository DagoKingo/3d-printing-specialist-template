#!/usr/bin/env python3
"""
generate_coupon.py — Generador rápido de probetas de calibración de tolerancias (Fit Coupon Plates)
Inspirado en 'kilatev/design-parametric-3d-prints'.

Permite crear una probeta de 15 minutos para validar físicamente ajustes a presión, deslizantes o
holguras de tornillos/rodamientos en tu Elegoo Centauri Carbon antes de imprimir la pieza definitiva.

Uso:
    python3 scripts/generate_coupon.py --type hole --nominal 8.0 --steps 0.10,0.15,0.20,0.25,0.30 -o probeta_608.scad
    python3 scripts/generate_coupon.py --type slot --nominal 10.0 --compile
"""

import sys
import os
import argparse
import subprocess

OPENSCAD_TEMPLATE = """// Probeta de calibración generada automáticamente por generate_coupon.py
tipo_probeta     = "{tipo}";
nominal          = {nominal:.2f};
espesor_probeta  = {espesor:.2f};
paso_holguras    = [{holguras}];
margen_borde     = 6.0;
separacion       = 14.0;

$fn = ($preview) ? 32 : 96;

num_pruebas = len(paso_holguras);
ancho_total = (num_pruebas * nominal) + ((num_pruebas - 1) * separacion) + (2 * margen_borde);
profundo_total = nominal + (2 * margen_borde) + 6.0;

module probeta() {{
    difference() {{
        cube([ancho_total, profundo_total, espesor_probeta]);

        for (i = [0 : num_pruebas - 1]) {{
            c = paso_holguras[i];
            pos_x = margen_borde + (nominal / 2) + i * (nominal + separacion);
            pos_y = margen_borde + (nominal / 2);

            if (tipo_probeta == "orificio") {{
                translate([pos_x, pos_y, -1])
                    cylinder(d = nominal + c, h = espesor_probeta + 2);
            }} else {{
                translate([pos_x - (nominal + c)/2, pos_y - (nominal + c)/2, -1])
                    cube([nominal + c, nominal + c, espesor_probeta + 2]);
            }}

            translate([pos_x, profundo_total - 4.5, espesor_probeta - 0.6])
                linear_extrude(1.0)
                    text(str("+", c), size = 2.8, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
        }}
    }}
}}

probeta();
"""

def generate(tipo, nominal, steps, output_scad, espesor=4.0, compile_stl=False):
    holguras_str = ", ".join(f"{float(s):.2f}" for s in steps)
    scad_content = OPENSCAD_TEMPLATE.format(
        tipo="orificio" if tipo in ["hole", "orificio"] else "ranura",
        nominal=nominal,
        espesor=espesor,
        holguras=holguras_str
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_scad)), exist_ok=True)
    with open(output_scad, "w", encoding="utf-8") as f:
        f.write(scad_content)

    print(f"✅ Archivo OpenSCAD generado: {output_scad}")

    if compile_stl:
        stl_output = os.path.splitext(output_scad)[0] + ".stl"
        cmd = f"openscad -o \"{stl_output}\" \"{output_scad}\""
        print(f"📦 Compilando a STL con OpenSCAD...")
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"🎉 STL listo para imprimir en la Centauri Carbon: {stl_output}")
        except Exception as e:
            print(f"⚠️ No se pudo compilar a STL automáticamente: {e}")
            print(f"Puedes abrir '{output_scad}' en OpenSCAD y exportar con F6.")

def main():
    parser = argparse.ArgumentParser(description="Generador rápido de probetas de calibración de holguras.")
    parser.add_argument("--type", choices=["hole", "slot", "orificio", "ranura"], default="hole", help="Tipo de geometría a calibrar")
    parser.add_argument("--nominal", type=float, required=True, help="Cota nominal exacta del objeto (mm), ej. 8.0 para rodamiento 608")
    parser.add_argument("--steps", default="0.10,0.15,0.20,0.25,0.30", help="Lista de holguras separadas por comas (mm)")
    parser.add_argument("-o", "--output", default="projects/test_coupon.scad", help="Ruta de salida del archivo .scad")
    parser.add_argument("--thickness", type=float, default=4.0, help="Espesor de la placa (mm)")
    parser.add_argument("--compile", action="store_true", help="Compilar inmediatamente a STL con OpenSCAD")

    args = parser.parse_args()
    steps_list = [float(x.strip()) for x in args.steps.split(",")]
    generate(args.type, args.nominal, steps_list, args.output, espesor=args.thickness, compile_stl=args.compile)

if __name__ == "__main__":
    main()
