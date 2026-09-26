---
name: slicer-advisor
description: "Asesor de perfiles y ajustes de corte en OrcaSlicer y Elegoo Slicer. Optimiza parámetros según la intención de la pieza (resistencia mecánica, prototipado rápido, estética fina, materiales técnicos) para la Elegoo Centauri Carbon."
triggers:
  - "slicer"
  - "parámetros de corte"
  - "OrcaSlicer"
  - "Elegoo Slicer"
  - "infill"
  - "relleno"
  - "perímetros"
  - "costura"
  - "seam"
  - "soporte"
---

# Skill: Slicer Advisor (OrcaSlicer & Elegoo Centauri Carbon)

Optimiza los parámetros de corte (slicing) en **OrcaSlicer** o **Elegoo Slicer** en función del objetivo real de la pieza física.

---

## 🎯 Perfiles por Intención (Intent-Based Slicing)

No existe una configuración única. Clasifica la intención del usuario en una de estas 4 categorías:

### 1. Resistencia Mecánica Máxima (Piezas Funcionales / Soportes)
- **Loops de pared (Wall loops):** 5 a 6 paredes (más efectivo para resistencia que aumentar el % de infill).
- **Capas superior / inferior:** 5 a 6 capas.
- **Patrón de relleno:** `Gyroid` o `3D Honeycomb` al 25% - 40% (resistencia isotrópica sin solapamiento de líneas).
- **Ancho de línea:** 0.45 mm (para boquilla de 0.4 mm, mejora la adhesión inter-capas).
- **Ventilador de capa:** Moderado (30-50% en PETG/ABS; 70-80% en PLA) para maximizar la fusión inter-capas.

### 2. Prototipado Rápido (Draft / Verificación de Encaje)
- **Altura de capa:** 0.28 mm.
- **Loops de pared:** 2 paredes.
- **Relleno:** `Grid` o `Lightning` al 10% - 15%.
- **Velocidad de impresión:** 300 - 450 mm/s (aprovechando la cinemática CoreXY de la Centauri Carbon).
- **Capas superiores:** 3 a 4.

### 3. Alta Definición y Estética (Miniaturas / Carcasas Visibles)
- **Altura de capa:** 0.12 mm a 0.16 mm (o altura de capa adaptativa).
- **Loops de pared:** 3 paredes.
- **Posición de costura (Seam):** `Alineada` (Aligned) o `Trasera` (Back), o colocada manualmente en aristas vivas ocultas.
- **Modo planchado (Ironing):** Activado en la capa superior más alta (Topmost surface) a 30 mm/s y 15% de flujo para acabado suave como molde de inyección.

### 4. Materiales Técnicos (ABS / ASA / PA-CF en Cámara Caliente)
- **Cámara:** Completamente cerrada.
- **Brim (Borde):** Activado (5 mm con holgura de 0.1 mm) para prevenir despegado de esquinas.
- **Enfriamiento:** Mínimo (0-15%) para evitar delaminación por contracción térmica.
- **Velocidad de pared exterior:** Reducir a 80-120 mm/s para asegurar brillo y unión molecular.

---

## 🖨️ Especificaciones del Perfil Elegoo Centauri Carbon

Consulta `references/centauri_carbon_specs.md` para las aceleraciones máximas, volumen de cama (256x256x256 mm) y cinemática.

---

## 📦 Empaquetado Nativo de Proyectos 3MF para Elegoo Slicer / OrcaSlicer

Para que un archivo `.3mf` se cargue sin errores, sin ventanas de advertencia y con las opciones de corte y soportes seleccionadas por defecto, se deben cumplir **estrictamente las 4 reglas del motor C++ de ElegooSlicer**:

### 1. Tipado Estricto de Cadenas (String Typing)
En `Metadata/project_settings.config`, todos los valores escalares **DEBEN ser strings**:
- `"enable_support": "1"` (NUNCA `1` numérico).
- `"wall_loops": "6"` (NUNCA `6` numérico).
- `"xy_hole_compensation": "0.15"` (NUNCA `0.15` float).
- `"bottom_shell_layers": "5"`, `"top_shell_layers": "5"`.
> **Origen en código:** En `src/libslic3r/Config.cpp:927-1005`, ElegooSlicer solo deserializa si `it.value().is_string()`. Los tipos numéricos activan `invalid json type` y se descartan silenciosamente, dejando los soportes desmarcados y las paredes en valores por defecto.

### 2. Lista de Retención (`different_settings_to_system`)
En `src/libslic3r/PrintConfig.cpp:10170-10175`, ElegooSlicer sobreescribe con los valores del perfil de fábrica cualquier parámetro que no esté explícitamente registrado en la lista:
```json
"different_settings_to_system": [
    "enable_support;support_type;wall_loops;sparse_infill_density;sparse_infill_pattern;xy_hole_compensation;bottom_shell_layers;top_shell_layers",
    "", "", ""
]
```

### 3. Vinculación a Preset Base del Sistema
`print_settings_id` debe ser un nombre de perfil de sistema reconocido:
`"print_settings_id": "0.20mm Standard @Elegoo CC2 0.4 nozzle"`
Si se usa un nombre arbitrario no instalado previamente en los presets de usuario, `PresetCollection::select_preset_by_name` cae en el fallback de Preset 0 (`Default Setting`) y resetea todos los valores.

### 4. Metadatos de Aplicación Nativos
Para evitar el popup *"The 3MF file you are importing may be incompatible..."* (`Plater.cpp:6117`):
- En `3D/3dmodel.model`: `<metadata name="Application">ElegooSlicer-1.5.3.5</metadata>`
- En `Metadata/slice_info.config`: `<header_item key="X-BBL-Client-Name" value="ElegooSlicer"/>`

---

### 🛠️ Herramienta CLI Automatizada (`scripts/export_3mf.py`)
Genera proyectos 3MF nativos listos para imprimir con:
```bash
# Perfil mecánico funcional (6 paredes, 40% giroide, soportes árbol, +0.15 mm compensación)
python3 scripts/export_3mf.py pieces/<pieza>/<pieza>.stl -o pieces/<pieza>/<pieza>.3mf --intent mechanical --material PETG

# Personalizado
python3 scripts/export_3mf.py pieza.stl -o proyecto.3mf --material PLA --support --walls 4 --infill 30%
```

