---
name: parametric-cad
description: "Modelado 3D paramétrico ligero y robusto con OpenSCAD (o Python/Build123d). Soporta diseño desde cero (Greenfield) y adaptación/remix de STLs existentes. Incluye patrón de selector RENDER, resolución $fn y preparación para exportación a STL."
triggers:
  - "OpenSCAD"
  - "diseñar en 3D"
  - "código SCAD"
  - "exportar STL"
  - "modificar modelo"
  - "importar STL"
  - "remix modelo"
---

# Skill: Parametric CAD (OpenSCAD & Modelado 3D)

## 0. Identidad del Repositorio, Plantilla Base y Git Upstream

Cualquier agente que ejecute esta skill debe reconocer de inmediato la naturaleza y límites de este repositorio:

1. **Plantilla Base del Repositorio:**
   - Este repositorio implementa la plantilla corporativa **`laga-solutions/3d-printing-specialist-template`**, formalizada en el manifiesto raíz [`template.yaml`](template.yaml).
   - Su rol es **exclusivamente de Especialista en Fabricación Aditiva e Ingeniería CAD 3D** (`role: 3d-printing-specialist`): código CAD paramétrico OpenSCAD (`.scad`), verificación de imprimibilidad FDM (`verify_mesh.py`), empaquetado 3MF (`export_3mf.py`) y artefactos canónicos en `pieces/<nombre_pieza>/`.
   - **PROHIBICIÓN ABSOLUTA DE DESARROLLO DE SOFTWARE DE APLICACIÓN:** Queda terminantemente prohibido crear directorios de código fuente de aplicaciones web, móviles o backend (`/frontend`, `/backend`, `/src`, etc.), inicializar herramientas de empaquetado/scaffolding de software general (`npm create vite`, `cargo new`, `go mod init`, etc.) o implementar lógica de negocio ajena al modelado 3D y la manufactura aditiva.

2. **Verificación Inmediata de Plantilla y Git Upstream:**
   - Comprueba remotos con `git remote -v | grep upstream`. En repositorios derivados, `upstream` DEBE apuntar a `https://github.com/DagoKingo/3d-printing-specialist-template.git`.
   - Ejecuta `./scripts/verify-environment.sh` para auditar el estado del entorno y sincronización con la plantilla base (`upstream/main`).

3. **Respuesta Rápida de Identidad:**
   - Si se consulta la plantilla de este proyecto, responde de inmediato: *"Este proyecto implementa la plantilla `laga-solutions/3d-printing-specialist-template` (rastreada vía remote `upstream` hacia `https://github.com/DagoKingo/3d-printing-specialist-template.git`), cuyo manifiesto canónico es `template.yaml`"*.

---

OpenSCAD es el motor CAD paramétrico principal de esta plantilla: es texto plano, ligero, determinista y permite que tanto el agente como el usuario modifiquen cualquier medida cambiando variables numéricas.

---

## 📐 Principios de Modelado FDM en OpenSCAD

1. **Empieza en 2D (Start in 2D):**
   - Antes de modelar formas complejas en 3D, describe o dibuja mentalmente el perfil 2D en planta o sección.
   - Usa `linear_extrude(height)` o `rotate_extrude()` a partir de figuras 2D (`polygon`, `circle`, `square`) siempre que simplifique la geometría.

2. **Resolución `$fn` Dinámica:**
   - Durante la fase de diseño/iteración: usa `$fn = 32` para que el renderizado F5 sea instantáneo.
   - Para la exportación final a STL: usa `$fn = 96` a `$fn = 128` para cilindros y roscas perfectamente suaves.

3. **Operaciones Booleanas Limpias (Evitar Z-fighting):**
   - En diferencias (`difference()`), haz que los cuerpos que restan (agujeros, cortes) sobresalgan ligeramente (`+0.02 mm` a `+0.1 mm`) respecto a la cara cortada para evitar caras coincidentes de espesor infinitesimal (z-fighting / non-manifold errors).

4. **Patrón de Selector `RENDER` (Exportación Multicomponente):**
   Permite ver el ensamble completo o compilar piezas individuales para el slicer:
   ```openscad
   RENDER = "preview"; // "preview", "base", "tapa"

   if (RENDER == "preview") {
       ensamble();
   } else if (RENDER == "base") {
       base();
   } else if (RENDER == "tapa") {
       tapa();
   }
   ```

---

## 🔄 Adaptación / Remix de Archivos STL Existentes

OpenSCAD permite importar mallas STL existentes mediante `import("archivo.stl")`.

### Casos de Uso Habituales:
1. **Sustracción (Cortes en una pieza existente):**
   ```openscad
   difference() {
       import("pieza_original.stl", convexity=3);
       // Cortar un nuevo orificio o rebajar una pared
       translate([10, 20, -1]) cylinder(d=5.2, h=30);
   }
   ```

2. **Adición / Ensamble (Añadir anclajes o soportes a una pieza existente):**
   ```openscad
   union() {
       import("soporte_existente.stl", convexity=3);
       // Añadir una orejeta o montura para tornillo
       translate([0, 50, 0]) montura_adicional();
   }
   ```

3. **Reingeniería Inversa (Reverse Engineering):**
   Si la malla STL original está dañada o es muy facetada, el agente puede usar el STL como guía de referencia (`%import("pieza.stl");` para renderizado transparente) mientras recrea la geometría paramétrica limpia con variables.

---

## 🛠️ Comandos CLI de Exportación

Compilar el ensamble o piezas a STL:
```bash
# Exportar pieza base
openscad -D 'RENDER="base"' -o pieces/mi_pieza/artifacts/base.stl pieces/mi_pieza/artifacts/modelo.scad

# Exportar con alta resolución
openscad -D 'RENDER="base"' -D '$fn=128' -o pieces/mi_pieza/artifacts/base.stl pieces/mi_pieza/artifacts/modelo.scad
```

---

## 📚 Librería BOSL2 (Recomendada para Mecánica FDM)

Para piezas con tornillería ISO, aristas redondeadas sin artefactos, roscas imprimibles reales o engranajes, utiliza **BOSL2**:
- Documentación y modismos verificados: [`references/bosl2_guide.md`](references/bosl2_guide.md).
- Utiliza siempre `anchor=BOTTOM` para posar sobre la cama y `diff()` + `attach(inside=true, shiftout=0.01)` para operaciones de vaciado sin solapamientos.

---

## ⚙️ Validación Cinemática de Mecanismos (`sweep.py`)

Para ensambles con piezas móviles (levas, bisagras, engranajes, correderas):
- Una interferencia de 0.5 mm en un ángulo intermedio del ciclo atasca la pieza física.
- Utiliza la plantilla [`templates/sweep_template.scad`](templates/sweep_template.scad) junto con `scripts/sweep.py`:
  ```bash
  python3 scripts/sweep.py chk.scad --parts base engranaje manivela --var angulo 0 360 --step 10
  ```
  El script calcula el volumen de colisión entre cada par de piezas a lo largo del recorrido y garantiza cero interferencias mecánicas antes de imprimir.

---

## 🐍 Automatización Headless en FreeCAD (Ruta Alternativa STEP/Python)

Si se automatiza FreeCAD por línea de comandos (`freecadcmd`):
- Consulta obligatoria: [`references/freecad_headless_gotchas.md`](references/freecad_headless_gotchas.md) para evitar las 10 trampas empíricas (exit code 0 en fallos, deflexión angular en radianes, pérdida de salida en `sys.exit()`, etc.).

