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
openscad -D 'RENDER="base"' -o projects/mi_proyecto/base.stl projects/mi_proyecto/modelo.scad

# Exportar con alta resolución
openscad -D 'RENDER="base"' -D '$fn=128' -o projects/mi_proyecto/base.stl projects/mi_proyecto/modelo.scad
```
