# 🖨️ 3D Printing Specialist Template

Plantilla y marco de trabajo asistido por IA para concebir, diseñar, validar y cortar modelos 3D listos para impresión FDM. Diseñado específicamente con soporte nativo para la **Elegoo Centauri Carbon** y 100% agnóstico respecto al asistente o agente de IA que utilices (**Claude Code, Google Antigravity / AGY, OpenCode, Cursor, Windsurf, Copilot**, etc.).

---

## 💡 Filosofía y Principios de Diseño

1. **Grill First, Code Later:** No se genera código CAD de inmediato ante una petición ambigua. La skill [`3d-grill-me`](file:///home/dago/repos/3d-printing-specialist-template/skills/3d-grill-me/SKILL.md) interroga metódicamente al usuario para entender esfuerzos, cargas mecánicas, entorno y método de montaje.
2. **Greenfield vs. Remix / Adaptación:**
   - **Greenfield:** Creación desde cero con enfoque 2D-to-3D.
   - **Remix & Adaptación:** Cuando se parte de una pieza previa (`.stl`, `.step` o muestra física), el agente tiene como **regla obligatoria** preguntar:
     - *¿Qué características o interfaces geométricas de la pieza muestra se deben conservar intactas?* (e.g. patrón de orificios, cavidad interna, clips, contorno).
     - *¿Qué aspectos se deben modificar, reforzar o agregar?*
3. **Estrategia Dual de Modelado (Dual-Track Modeling):**
   - **Ruta Mecánica & Paramétrica:** Se utiliza **OpenSCAD** (`skills/parametric-cad`) como motor estándar por su formato en texto plano, facilidad de control de versiones y determinismo.
   - **Ruta Orgánica & Escultórica:** Se utiliza **Blender** interactivo mediante **BlenderMCP** (`skills/blender-mcp`), inyectando restricciones estrictas de grosor de pared, aplicación de escala y orientación de normales.
4. **Never Guess Dimensions (Búsqueda primero):** Prohibido alucinar medidas de componentes estándar (rodamientos, tuercas, microcontroladores). Se consultan datasheets reales o tablas de fijaciones.
5. **Puerta de Imprimibilidad (Printability Gate):** Verificación técnica antes del corte mediante [`scripts/verify_mesh.py`](file:///home/dago/repos/3d-printing-specialist-template/scripts/verify_mesh.py): estabilidad en cama, relación de aspecto, estanqueidad manifold y generación de `manifest.json`.
6. **Corte Guiado por Intención (Intent-Based Slicing):** Se optimizan los parámetros de **OrcaSlicer / Elegoo Slicer** en función de la función real de la pieza (resistencia extrema, prototipo rápido, acabado estético o materiales técnicos en cámara cerrada).
7. **Integración Hardware SDCP:** Control y monitoreo en tiempo real de la Elegoo Centauri Carbon vía WebSockets.

---

## 🗺️ Flujo de Trabajo en 6 Fases

```
[Idea o Pieza Muestra]
         │
         ▼
[1. Entrevista de Requisitos] ────► skills/3d-grill-me/
         │                         (Greenfield vs Remix, conservación de geometrías)
         ▼
[2. Tolerancias & Datasheets] ────► skills/spec-advisor/
         │                         (Fijaciones M2-M5, insertos térmicos, ajustes FDM)
         ▼
[3. Modelado 3D] ─────────────────► ¿Mecánico u Orgánico?
         ├────────────────────────► Ruta A (Mecánico): skills/parametric-cad/ (OpenSCAD)
         └────────────────────────► Ruta B (Orgánico): skills/blender-mcp/ (Blender + MCP)
         │
         ▼
[4. Auditoría & Galería 3D] ──────► scripts/verify_mesh.py (Printability Gate & manifest.json)
         │                         scripts/generate_gallery.py (Renders PNG y visor Three.js)
         ▼
[5. Asesor de Slicing] ───────────► skills/slicer-advisor/
         │                         (Perfiles OrcaSlicer por intención para Centauri Carbon)
         ▼
[6. Control de Impresora] ────────► skills/elegoo-centauri/
         │                         (SDCP WebSocket: status, precalentamiento, luces)
         ▼ (Post-Impresión / Fallos)
[7. Diagnóstico: Print Doctor] ───► skills/print-doctor/
                                   (Resolución de warping, stringing, atascos y secado)
```

---

## 📁 Estructura del Repositorio

```text
3d-printing-specialist-template/
├── template.yaml               # Manifiesto canónico de identidad y límites de la plantilla (LAGA Solutions)
├── AGENTS.md                   # Instrucciones maestras para cualquier agente de IA
├── CLAUDE.md                   # Puntero para Claude Code
├── GEMINI.md                   # Puntero para Gemini CLI / Antigravity
├── config.toml                 # Configuración de impresora (IP, volumen) y slicer
├── mcp_servers.example.json    # Configuración de servidores MCP (BlenderMCP)
├── requirements.txt            # Dependencias Python opcionales
│
├── skills/
│   ├── 3d-grill-me/            # Entrevista socrática de requisitos y checklist DFM
│   │   ├── SKILL.md
│   │   └── references/         # questions.md, dfm_checklist.md
│   │
│   ├── spec-advisor/           # Tolerancias, fijaciones estándar, uniones mecánicas y texturas
│   │   ├── SKILL.md
│   │   ├── references/         # fasteners.md, tolerances.md, materials.md, joints.md, textures_and_ribs.md
│   │   └── scripts/            # search_specs.py
│   │
│   ├── parametric-cad/         # Modelado paramétrico OpenSCAD (Ruta Mecánica)
│   │   ├── SKILL.md
│   │   ├── templates/          # starter_template.scad, remix_template.scad, sweep_template.scad, viewer.html
│   │   └── references/         # openscad_guide.md, bosl2_guide.md, freecad_headless_gotchas.md
│   │
│   ├── blender-mcp/            # Modelado en Blender interactivo (Ruta Orgánica)
│   │   ├── SKILL.md
│   │   └── references/         # 3dprint_constraints.md, mcp_setup.md
│   │
│   ├── slicer-advisor/         # Perfiles y settings para OrcaSlicer / Elegoo Slicer
│   │   ├── SKILL.md
│   │   └── references/         # centauri_carbon_specs.md, slicer_settings.md
│   │
│   ├── elegoo-centauri/        # Control SDCP WebSocket para Elegoo Centauri Carbon
│   │   ├── SKILL.md
│   │   ├── scripts/            # centauri_ctl.py
│   │   └── references/         # sdcp_protocol.md
│   │
│   └── print-doctor/           # Diagnóstico clínico y resolución de fallos FDM
│       ├── SKILL.md
│       └── references/         # fdm_troubleshooting.md, filament_doctor.md
│
├── pieces/                     # Directorio canónico de piezas y artefactos
│   └── <nombre_pieza>/         # .scad, .stl, .3mf, manifest.json, viewer.html, renders/ y README.md
├── projects/                   # Directorio alternativo de trabajo o proyectos compuestos
└── scripts/                    # Herramientas de verificación, empaquetado y galería
    ├── verify-environment.sh   # Auditor canónico de entorno, dependencias FDM y sincronización upstream
    ├── scaffold_piece.py       # Inicializador de estructura completa para una nueva pieza
    ├── measure.py              # Ingeniería inversa: mide cotas, planos, barrenos y perfiles en STL/3MF
    ├── sweep.py                # Verificación cinemática: detecta colisiones e interferencias en piezas móviles
    ├── verify_mesh.py          # Printability Gate con autopsia de defectos (stl_autopsy) y manifest.json
    ├── export_3mf.py           # Empaquetador multi-pieza 3MF con colores y materiales
    ├── generate_coupon.py      # Generador de probetas de calibración de tolerancias (Fit Coupons)
    └── generate_gallery.py     # Generador de capturas y visor Three.js interactivo
```

---

## 🚀 Instalación y Requisitos Previos

### 1. Motor CAD (OpenSCAD)
Para compilar modelos mecánicos a STL y renderizar vistas previas desde terminal:
```bash
# Ubuntu / Debian
sudo apt install openscad

# macOS
brew install openscad
```

### 2. Motor Orgánico (Blender + BlenderMCP - Opcional)
Para habilitar el modelado interactivo en vivo de figuras y formas orgánicas:
```bash
uvx blender-mcp
```
Consulta [`mcp_servers.example.json`](file:///home/dago/repos/3d-printing-specialist-template/mcp_servers.example.json) y [`skills/blender-mcp/references/mcp_setup.md`](file:///home/dago/repos/3d-printing-specialist-template/skills/blender-mcp/references/mcp_setup.md).

### 3. Dependencias Python (Recomendado)
Para el cliente de comunicación con la impresora y validación de mallas:
```bash
pip install -r requirements.txt
```

---

## 🎮 Cómo Utilizar la Plantilla

Simplemente abre el repositorio con tu agente de IA preferido:
- **Claude Code:** `claude`
- **Google Antigravity:** `agy` o abre el espacio de trabajo
- **OpenCode / Cursor / Windsurf:** Abre la carpeta del repositorio

Y dile lo que quieres hacer. Por ejemplo:
- *"Quiero diseñar un soporte para auriculares que se fije a mi escritorio."*
- *"Tengo este archivo `pieza.stl` de un soporte de cámara y quiero adaptarlo para que use un tornillo M4 y tenga 20 mm más de largo."*
- *"Genera una probeta rápida para calibrar el ajuste de un rodamiento 608 (8mm) en mi Centauri Carbon."*
- *"Quiero diseñar una carcasa hermética IP67 con junta de TPU para mi Raspberry Pi Zero."*
- *"Empaqueta el ensamble de `base.stl:PETG`, `tapa.stl:PETG` y `junta.stl:TPU` en un solo archivo 3MF para OrcaSlicer."*
- *"Consulta el estado de mi Elegoo Centauri Carbon."*

El agente activará automáticamente las skills correspondientes respetando todo el proceso de ingeniería.

---

## 🙏 Agradecimientos e Inspiración

Esta plantilla sintetiza y adapta las mejores prácticas de destacados proyectos comunitarios:
- **Matt Pocock** ([`grill-me`](https://github.com/mattpocock/skills)): Método socrático de interrogatorio previo al diseño.
- **Kilatev** ([`design-parametric-3d-prints`](https://github.com/kilatev/design-parametric-3d-prints)): Flujo de probetas de tolerancia (*test coupons*), diseño autoportante y separación estricta de cotas nominales y holguras.
- **Zabaglione** ([`3d-printing-design-skills`](https://github.com/zabaglione/3d-printing-design-skills)): Ingeniería de uniones mecánicas (snap-fits, dovetails, bayoneta), zonas protegidas y nervaduras FDM.
- **Circus Systems** ([`VibePrint3D`](https://github.com/Circus-Systems/VibePrint3D)): Empaquetado multi-material a `.3mf`, diseño de carcasas IP67 y registro de antipatrones mecánicos.
- **Parham DB** ([`3d-print-skill`](https://github.com/parhamdb/3d-print-skill)): Ingeniería paramétrica, análisis de esfuerzos y tablas de fijaciones.
- **EdwinjJ1** ([`3d-print-skill`](https://github.com/EdwinjJ1/3d-print-skill)): Filosofía *Search-First* de especificaciones reales.
- **Ben Hardaway** ([`blender-mcp-skills`](https://github.com/benhardaway77/blender-mcp-skills)): Inyección de restricciones y reglas FDM para BlenderMCP.
- **Rjxshr1** ([`idea-to-print`](https://github.com/Rjxshr1/idea-to-print)): Conceptos de Puerta de Imprimibilidad (*Printability Gate*) y registro de auditoría (*manifest.json*).
- **Flatsher** ([`elegoo-centauri-skill`](https://github.com/Flatsher/elegoo-centauri-skill)): Comunicación nativa SDCP WebSocket con la Elegoo Centauri Carbon.
- **Santiago Moneta** ([`3DPrintAdvisor`](https://github.com/santiagomoneta/3DPrintAdvisor) & [`3d-printing-skills`](https://github.com/santiagomoneta/3d-printing-skills)): Ajustes de slicer por intención y gestión Klipper/OrcaSlicer.
- **Marco Franzon** ([`print3d`](https://github.com/mfranzon/print3d)): Bucle de verificación automatizada.
- **Chris Cantey** ([`skill-3d-printing`](https://github.com/chriscantey/skill-3d-printing)): Patrones de OpenSCAD, selector RENDER y GalleryView multiángulo.
