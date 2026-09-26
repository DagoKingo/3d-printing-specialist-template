#!/usr/bin/env python3
"""
search_specs.py — Base de datos local y buscador de especificaciones de componentes estándar
Evita alucinar dimensiones para componentes comerciales comunes.
"""

import sys
import json
import os

CACHE_FILE = os.path.join(os.path.dirname(__file__), "specs_cache.json")

COMMON_SPECS = {
    "bearing_608": {
        "name": "Rodamiento 608 (Patinete / Skate / Guía)",
        "outer_diameter_mm": 22.0,
        "inner_diameter_mm": 8.0,
        "thickness_mm": 7.0,
        "cad_hole_press_fit_mm": 22.1,
        "cad_shaft_press_fit_mm": 7.95
    },
    "bearing_624": {
        "name": "Rodamiento 624 (Impresoras 3D)",
        "outer_diameter_mm": 13.0,
        "inner_diameter_mm": 4.0,
        "thickness_mm": 5.0
    },
    "nema_17": {
        "name": "Motor Paso a Paso NEMA 17",
        "face_size_mm": 42.3,
        "hole_spacing_mm": 31.0,
        "center_boss_diameter_mm": 22.0,
        "mounting_threads": "M3",
        "shaft_diameter_mm": 5.0
    },
    "raspberry_pi_4": {
        "name": "Raspberry Pi 4 Model B",
        "board_length_mm": 85.0,
        "board_width_mm": 56.0,
        "hole_spacing_x_mm": 58.0,
        "hole_spacing_y_mm": 49.0,
        "hole_diameter_mm": 2.75,
        "recommended_screw": "M2.5"
    },
    "raspberry_pi_5": {
        "name": "Raspberry Pi 5",
        "board_length_mm": 85.0,
        "board_width_mm": 56.0,
        "hole_spacing_x_mm": 58.0,
        "hole_spacing_y_mm": 49.0,
        "hole_diameter_mm": 2.75,
        "recommended_screw": "M2.5"
    },
    "fan_4010": {
        "name": "Ventilador 4010 (Hotend/Capa)",
        "outer_size_mm": 40.0,
        "thickness_mm": 10.0,
        "hole_spacing_mm": 32.0,
        "hole_diameter_mm": 3.2
    },
    "fan_5015": {
        "name": "Turbina Blower 5015 (Capa)",
        "outer_size_approx_mm": 51.5,
        "thickness_mm": 15.0,
        "outlet_width_mm": 20.0,
        "outlet_height_mm": 15.0
    },
    "battery_18650": {
        "name": "Batería Li-ion 18650",
        "diameter_mm": 18.3,
        "length_mm": 65.0,
        "cad_slot_diameter_mm": 18.6
    }
}

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                COMMON_SPECS.update(data)
        except Exception:
            pass
    return COMMON_SPECS

def search(query):
    specs = load_cache()
    query_lower = query.lower().replace("-", "_").replace(" ", "_")
    results = {}
    
    for key, val in specs.items():
        if query_lower in key or query.lower() in val.get("name", "").lower():
            results[key] = val
            
    return results

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 search_specs.py <termino_busqueda>")
        print("Ejemplo: python3 search_specs.py 608")
        sys.exit(1)
        
    term = sys.argv[1]
    res = search(term)
    
    if res:
        print(f"Encontradas {len(res)} coincidencias en la base de datos:")
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(f"No se encontró '{term}' en la caché local.")
        print("ACCIÓN PARA EL AGENTE: Utiliza la herramienta de búsqueda web (search_web) para encontrar")
        print("el datasheet oficial del fabricante antes de suponer cualquier medida en el CAD.")

if __name__ == "__main__":
    main()
