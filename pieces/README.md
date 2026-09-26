# 📁 Directorio de Piezas y Artefactos (`pieces/`)

Este directorio alberga todas las piezas diseñadas, adaptadas o validadas en el proyecto. Cada pieza cuenta con su propia subcarpeta aislada y autosuficiente, conteniendo todo su ciclo de vida y artefactos.

---

## 🏗️ Estructura Estándar de una Pieza

Para cada pieza generada (ej. `pieces/soporte_camara/`), se generan los siguientes artefactos:

```
pieces/
└── <nombre_pieza>/
    ├── <nombre_pieza>.scad       # Código fuente CAD paramétrico (OpenSCAD + BOSL2)
    ├── <nombre_pieza>.stl        # Malla binaria exportada, hermética y apoyada en Z=0
    ├── <nombre_pieza>.3mf        # Paquete multicomponente para OrcaSlicer (placas y presets)
    ├── manifest.json             # Certificado de auditoría técnica (Printability Gate)
    ├── viewer.html               # Visor 3D interactivo Three.js para abrir en navegador
    ├── README.md                 # Ficha técnica: especificaciones, material y notas de corte
    └── renders/                  # Vistas previas multiángulo en PNG
        ├── render-iso.png        # Perspectiva isométrica
        ├── render-top.png        # Vista en planta
        └── render-front.png      # Vista frontal
```

---

## ⚡ Cómo Crear una Nueva Pieza (Scaffolding Automático)

Usa el script asistente para inicializar una nueva pieza con toda su estructura:

```bash
# Crear estructura inicial de la pieza
python3 scripts/scaffold_piece.py mi_nueva_pieza --material PLA --desc "Soporte para sensor"
```

Esto generará automáticamente la carpeta en `pieces/mi_nueva_pieza/` con el código base `.scad`, la ficha `.md` y la carpeta `renders/`.

---

## 🔄 Flujo de Generación de Artefactos

Una vez modelada la pieza en `pieces/<nombre_pieza>/<nombre_pieza>.scad`:

```bash
PIECE="pieces/mi_nueva_pieza/mi_nueva_pieza"

# 1. Compilar a STL (si tienes openscad instalado)
openscad -D 'RENDER="preview"' -o "${PIECE}.stl" "${PIECE}.scad"

# 2. Auditar imprimibilidad y generar manifest.json
python3 scripts/verify_mesh.py "${PIECE}.stl" --manifest --material PLA

# 3. Generar vistas previas PNG y visor interactivo viewer.html
python3 scripts/generate_gallery.py "${PIECE}.scad"

# 4. Empaquetar proyecto 3MF para la Elegoo Centauri Carbon
python3 scripts/export_3mf.py -o "${PIECE}.3mf" "${PIECE}.stl":"Mi Pieza"
```
