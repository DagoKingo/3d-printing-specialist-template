---
name: blender-mcp
description: "Modelado 3D orgánico, escultural y ergonómico interactivo en Blender mediante Model Context Protocol (BlenderMCP). Inyecta restricciones estrictas de fabricación aditiva (FDM): mallas herméticas (manifold), escala real en milímetros, aplicación obligatoria de modificadores y transformaciones, y espesor mínimo de pared."
triggers:
  - "Blender"
  - "BlenderMCP"
  - "modelado orgánico"
  - "escultura 3D"
  - "figura"
  - "miniatura"
  - "ergonómico"
  - "personaje"
---

# Skill: Blender MCP (Modelado Orgánico & Escultórico para FDM)

Complemento del flujo de ingeniería de OpenSCAD. Mientras OpenSCAD se encarga de piezas geométricas y tolerancias de precisión, **Blender es el motor para formas orgánicas, figuras, superficies esculpidas y geometrías estéticas complejas**.

Esta skill está diseñada para trabajar en conjunto con [BlenderMCP](https://github.com/ahujasid/blender-mcp) e integra los filtros de calidad de [blender-mcp-skills](https://github.com/benhardaway77/blender-mcp-skills).

---

## ⛔ Restricciones Obligatorias de FDM para Blender (Filtro Activo)

Cada vez que el agente genere código Python para la consola de Blender o envíe órdenes vía MCP para crear una pieza imprimible, **DEBE inyectar y verificar estas restricciones antes de dar el modelo por finalizado**:

### 1. Geometría Estanca (Manifold)
- **Cero caras abiertas:** La malla debe ser un sólido hermético (watertight).
- **Sin geometría interna flotante:** No deben quedar vértices, aristas o caras internas desconectadas tras uniones booleanas.
- **Normales exteriores consistentes:** Todas las normales deben apuntar hacia afuera (`bpy.ops.mesh.normals_make_consistent(inside=False)`).
- **Limpieza de malla antes de exportar:**
  - `bpy.ops.mesh.select_all(action='SELECT')`
  - `bpy.ops.mesh.fill_holes()`
  - `bpy.ops.mesh.dissolve_degenerate()`

### 2. Escala Real y Aplicación de Transformaciones (Critical)
- **Unidades:** Escena configurada en milímetros (`scene.unit_settings.length_unit = 'MILLIMETERS'`, escala de unidad = 0.001 o escala 1.0 según la plantilla).
- **Aplicar transformaciones:** NUNCA exportar con escala o rotación sin aplicar. Ejecutar siempre:
  ```python
  bpy.ops.object.select_all(action='SELECT')
  bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
  ```

### 3. Espesor Mínimo de Pared (Wall Thickness)
- **FDM (Elegoo Centauri Carbon, boquilla 0.4 mm):**
  - Mínimo absoluto: **1.2 mm** (3 perímetros).
  - Partes salientes finas (alas, cuernos, espadas): engrosar la base (root thickening) para que no se quiebren por vibración en la cama.

### 4. Orientación y Contacto con la Cama
- Orientar la pieza con una cara plana hacia el plano inferior Z=0.
- Minimizar voladizos que superen los 45°-50° para reducir la necesidad de soportes.

### 5. Modificadores
- Colapsar/aplicar todos los modificadores (Subdivision Surface, Boolean, Solidify, Remesh) antes de la exportación a `.stl`.

---

## 🛠️ Conexión con BlenderMCP

Para que tu agente de IA controle Blender en tu pantalla:
1. Asegúrate de tener instalado el servidor MCP de Blender:
   ```bash
   uvx blender-mcp
   ```
2. Consulta `references/mcp_setup.md` para agregarlo a la configuración de Claude Desktop, Antigravity u OpenCode.
