#!/usr/bin/env python3
"""
Open Filament Database (OFD) CLI Client para 3D Printing Specialist & Design Assistant.
Permite buscar filamentos, consultar propiedades físicas (densidad, tolerancias, especificaciones)
y descargar presets verificados directamente compatibles con OrcaSlicer y Elegoo Slicer.

Fuente: Open Filament Collective (https://openfilamentdatabase.org / https://api.openfilamentdatabase.org)
Licencia de datos: MIT
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path

BASE_API_URL = "https://api.openfilamentdatabase.org/api/v1"
ORCA_INDEX_URL = "https://api.openfilamentdatabase.org/orcaslicer/index.json"
ORCA_BASE_URL = "https://api.openfilamentdatabase.org/orcaslicer"
CACHE_DIR = Path.home() / ".cache" / "open-filament-database"
CACHE_TTL = 86400  # 24 horas

def fetch_json(url, use_cache=True, cache_key=None):
    """Descarga JSON con soporte de caché local."""
    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        if not cache_key:
            cache_key = url.replace("https://", "").replace("/", "_").replace("?", "_")
        cache_file = CACHE_DIR / f"{cache_key}.json"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < CACHE_TTL:
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "3d-printing-specialist-template/1.0 (OpenFilamentClient)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            if use_cache and cache_key:
                try:
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(data, f)
                except Exception:
                    pass
            return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except Exception as e:
        print(f"⚠️ Error al conectar con Open Filament Database ({url}): {e}", file=sys.stderr)
        return None

def get_orca_index():
    """Obtiene el índice completo de presets de OrcaSlicer."""
    return fetch_json(ORCA_INDEX_URL, cache_key="orcaslicer_index")

def get_brands_index():
    """Obtiene el índice de marcas."""
    return fetch_json(f"{BASE_API_URL}/brands/index.json", cache_key="brands_index")

def search_filaments(query):
    """Busca filamentos y presets por término de búsqueda en marcas y nombres de producto."""
    q = query.lower()
    orca_data = get_orca_index()
    results = []

    if orca_data and "profiles" in orca_data:
        for p in orca_data["profiles"]:
            brand = p.get("brand", "")
            material = p.get("material", "")
            filament = p.get("filament", "")
            profile_name = p.get("profile_name", "")
            
            search_corpus = f"{brand} {material} {filament} {profile_name}".lower()
            if q in search_corpus:
                results.append({
                    "brand": brand,
                    "brand_slug": p.get("brand_slug"),
                    "material": material,
                    "filament": filament,
                    "filament_slug": p.get("filament_slug"),
                    "profile_name": profile_name,
                    "inherits": p.get("inherits"),
                    "orca_code": p.get("orca_filament_code"),
                    "path": p.get("path"),
                    "source": p.get("source")
                })
    return results

def get_filament_info(brand_slug, material_slug, filament_slug):
    """Consulta la ficha técnica detallada de un filamento en la API."""
    url = f"{BASE_API_URL}/brands/{brand_slug}/materials/{material_slug}/filaments/{filament_slug}/index.json"
    return fetch_json(url, cache_key=f"filament_{brand_slug}_{material_slug}_{filament_slug}")

def download_preset(rel_path, output_path=None):
    """Descarga el preset JSON oficial de OrcaSlicer."""
    url = f"{ORCA_BASE_URL}/{rel_path}"
    data = fetch_json(url, use_cache=False)
    if not data:
        return None
    
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return out
    return data

def main():
    parser = argparse.ArgumentParser(
        description="Cliente CLI para Open Filament Database (OFD) y Presets de OrcaSlicer"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: search
    search_parser = subparsers.add_parser("search", help="Buscar filamentos en el catálogo")
    search_parser.add_argument("query", help="Término de búsqueda (ej. 'elegoo rapid', 'polylite asa', 'esun')")

    # Comando: info
    info_parser = subparsers.add_parser("info", help="Ver ficha técnica y propiedades de un filamento")
    info_parser.add_argument("brand", help="Slug o nombre de la marca (ej. elegoo)")
    info_parser.add_argument("material", help="Material (ej. PETG, PLA, ABS, ASA)")
    info_parser.add_argument("filament", help="Slug o nombre del filamento (ej. rapid_petg)")

    # Comando: preset
    preset_parser = subparsers.add_parser("preset", help="Descargar preset oficial de OrcaSlicer (.json)")
    preset_parser.add_argument("brand", help="Slug de la marca (ej. elegoo)")
    preset_parser.add_argument("material", help="Material (ej. PETG)")
    preset_parser.add_argument("filament", help="Slug del filamento (ej. rapid_petg)")
    preset_parser.add_argument("-o", "--output", default=None, help="Ruta de archivo destino (opcional)")

    # Comando: list-presets
    list_parser = subparsers.add_parser("list-presets", help="Listar presets disponibles en OrcaSlicer")
    list_parser.add_argument("--brand", default=None, help="Filtrar por marca (ej. elegoo)")
    list_parser.add_argument("--material", default=None, help="Filtrar por material (ej. PETG)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "search":
        print(f"🔍 Buscando filamentos coincidentes con '{args.query}' en Open Filament Database...")
        results = search_filaments(args.query)
        if not results:
            print("❌ No se encontraron filamentos con ese término.")
            sys.exit(0)

        print(f"\n✅ Se encontraron {len(results)} preset(s) en OrcaSlicer:\n")
        print(f"{'Marca':<15} {'Material':<10} {'Filamento':<25} {'Preset OrcaSlicer':<35}")
        print("-" * 88)
        for r in results[:25]:  # Máximo 25 para no saturar terminal
            print(f"{r['brand']:<15} {r['material']:<10} {r['filament']:<25} {r['profile_name']:<35}")
        if len(results) > 25:
            print(f"... y {len(results) - 25} resultados adicionales.")

    elif args.command == "info":
        brand = args.brand.lower().replace(" ", "_")
        material = args.material.upper()
        filament = args.filament.lower().replace(" ", "_")

        info = get_filament_info(brand, material, filament)
        if not info:
            print(f"❌ No se encontró información para '{brand}/{material}/{filament}'.")
            sys.exit(1)

        print(f"\n📋 Ficha Técnica Open Filament Database: {info.get('name', filament)}")
        print("=" * 60)
        print(f"• Marca:               {brand.upper()}")
        print(f"• Material Base:       {info.get('material', material)}")
        print(f"• Densidad:            {info.get('density', 'No declarada')} g/cm³")
        print(f"• Tolerancia Diámetro: ±{info.get('diameter_tolerance', '0.02')} mm")
        
        slicer = info.get("slicer_settings", {})
        if "orcaslicer" in slicer:
            orca = slicer["orcaslicer"]
            print(f"• Preset OrcaSlicer:   {orca.get('profile_name', 'N/A')} (ID: {orca.get('id', 'N/A')})")

        variants = info.get("variants", [])
        if variants:
            print(f"• Colores/Variantes ({len(variants)}):")
            col_list = [f"{v.get('name')} ({v.get('color_hex')})" for v in variants[:6]]
            print("  " + ", ".join(col_list))
            if len(variants) > 6:
                print(f"  ... y {len(variants) - 6} variantes más.")

    elif args.command == "preset":
        brand = args.brand.lower().replace(" ", "_")
        material = args.material.upper()
        filament = args.filament.lower().replace(" ", "_")

        rel_path = f"brands/{brand}/materials/{material}/filaments/{filament}.json"
        
        if not args.output:
            args.output = f"{brand}_{filament}_OFD.json"

        data = download_preset(rel_path, output_path=args.output)
        if not data:
            print(f"❌ No se pudo descargar el preset para '{rel_path}'.")
            sys.exit(1)

        print(f"✨ Preset de OrcaSlicer guardado exitosamente en: {args.output}")
        print("💡 Para importarlo en OrcaSlicer / Elegoo Slicer: Menú File -> Import -> Import Configs.")

    elif args.command == "list-presets":
        orca_data = get_orca_index()
        if not orca_data or "profiles" not in orca_data:
            print("❌ No se pudo cargar el índice de OrcaSlicer.")
            sys.exit(1)

        profiles = orca_data["profiles"]
        if args.brand:
            profiles = [p for p in profiles if p.get("brand_slug") == args.brand.lower()]
        if args.material:
            profiles = [p for p in profiles if p.get("material", "").upper() == args.material.upper()]

        print(f"\n📦 Presets disponibles ({len(profiles)} encontrados):")
        print(f"{'Marca':<15} {'Material':<10} {'Filamento':<25} {'Preset':<35}")
        print("-" * 88)
        for p in profiles[:30]:
            print(f"{p.get('brand',''):<15} {p.get('material',''):<10} {p.get('filament',''):<25} {p.get('profile_name',''):<35}")
        if len(profiles) > 30:
            print(f"... y {len(profiles) - 30} presets más.")

if __name__ == "__main__":
    main()
