# Guía de BOSL2 para Modelado Paramétrico en OpenSCAD

[BOSL2](https://github.com/BelfrySCAD/BOSL2) (*Belfry OpenSCAD Library v2*) es la librería estándar de facto para OpenSCAD moderno. Permite diseñar piezas mecánicas con aristas biseladas o redondeadas paramétricas, barrenos métricos estandarizados, roscas reales, engranajes y uniones mecánicas sin recurrir a operaciones lentas y problemáticas como `minkowski()` o uniones complejas por `hull()`.

---

## 📥 Instalación de BOSL2

OpenSCAD busca librerías en la ruta de usuario (`~/.local/share/OpenSCAD/libraries` en Linux o `~/Documents/OpenSCAD/libraries` en macOS/Windows):

```bash
mkdir -p ~/.local/share/OpenSCAD/libraries
git clone --depth 1 https://github.com/BelfrySCAD/BOSL2.git ~/.local/share/OpenSCAD/libraries/BOSL2
```

Para verificar que OpenSCAD lo reconoce:
```bash
openscad --info | grep -A2 "OpenSCAD library path"
```

---

## 🛠️ Inclusión de Módulos (Usar `include`, nunca `use`)

```scad
include <BOSL2/std.scad>        // Base: formas, transformaciones, anclajes y distribuidores
include <BOSL2/screws.scad>     // screw(), screw_hole(), nut(), tablas métricas ISO
include <BOSL2/threading.scad>  // threaded_rod(), threaded_nut(), roscas trapezoidales
include <BOSL2/gears.scad>      // spur_gear(), worm(), worm_gear(), cremalleras
include <BOSL2/hinges.scad>     // Bisagras print-in-place (knuckle_hinge)
include <BOSL2/rounding.scad>   // Redondeos 2D y 3D (round_corners, offset_sweep)
include <BOSL2/joiners.scad>    // Colas de milano (dovetail), snap-pins, clips
```

> [!IMPORTANT]
> Usa **`include <BOSL2/std.scad>`** y no `use`. El sistema de sujeción (*attachments*) y las variables `$` dependen de que el código se incluya en el alcance global.

---

## 🎯 Modismos Fundamentales para FDM

### 1. Orientación y Anclajes (`anchor=`)
En lugar de calcular `translate([x, y, z])` a mano:
- Usa `anchor=BOTTOM` para que la pieza repose automáticamente sobre la cama ($Z=0$).
- Usa `edges="Z"` para redondear solo las esquinas verticales, manteniendo la base plana y limpia para la primera capa:

```scad
// Caja con aristas verticales redondeadas (radio 2 mm), apoyada en Z=0
cuboid([40, 30, 10], rounding=2, edges="Z", anchor=BOTTOM);

// Cilindro apoyado en Z=0 con chaflán superior de 1 mm (sin soporte)
cyl(d=8, h=6, chamfer2=1, anchor=BOTTOM);
```

### 2. Fijación de Elementos a Caras (`attach()` + `diff()`)
Los hijos se colocan respecto a los anclajes de la pieza padre:
- `attach(TOP)` coloca una pieza orientada hacia afuera en la cara superior.
- `attach(face, child_anchor, inside=true)` incrusta el hijo dentro del padre para restarlo con `diff()`.

```scad
diff()
cuboid([50, 40, 15], rounding=2, edges="Z", anchor=BOTTOM) {
    // Barreno M3 con cajera (counterbore) para tornillo cilíndrico allen:
    attach(TOP) screw_hole("M3,12", head="socket", counterbore=true, anchor=TOP);

    // Torón / Poste en la cara lateral derecha:
    attach(RIGHT, BOTTOM) cyl(d=8, h=6, chamfer2=1);

    // Ranura restada en la cara frontal:
    // ¡OJO! shiftout=0.01 es OBLIGATORIO para evitar caras coincidentes en la resta
    attach(FRONT, TOP, inside=true, shiftout=0.01) cuboid([12, 6, 4], rounding=1.2, edges="Y");

    // Cuatro agujeros M3 pasantes en patrón de rejilla:
    attach(TOP, TOP, inside=true, shiftout=0.01) grid_copies(spacing=[35, 25]) cyl(d=3.4, h=16);
}
```

> [!WARNING]
> **`shiftout=0.01` es mandatorio en operaciones `inside=true`:** Sin `shiftout`, la cara exterior del cortador y la del padre son idénticas en $Z$, lo que genera membranas de grosor cero (*non-manifold*) y fallos de estanqueidad.

### 3. Tornillería Estandarizada (`screws.scad`)
Evita inventar diámetros de broca o tornillo. BOSL2 conoce las tablas métricas:

```scad
// Agujero pasante M3 con cajera embutida:
attach(TOP) screw_hole("M3,10", head="socket", counterbore=true, anchor=TOP);

// Avellanado para cabeza cónica:
attach(TOP) screw_hole("M3,10", head="flat", anchor=TOP);

// Barreno piloto para autorroscante en plástico:
attach(TOP) screw_hole("M3,10", head="none", tolerance="self tap", anchor=TOP);

// Tuerca M3 embutida (Nut trap):
nut("M3", thickness=2.4);
```

Define la tolerancia global `$slop = 0.2;` en el encabezado de tu archivo `.scad` para compensar la expansión térmica del FDM.

### 4. Roscas Funcionales Imprimibles (`threading.scad`)
```scad
// Tornillo roscado exterior (paso 1.5 mm, M10):
threaded_rod(d=10, l=20, pitch=1.5, anchor=BOTTOM);

// Tuerca hexagonal interior roscada (M10):
threaded_nut(nutwidth=17, id=10, h=10, pitch=1.5);
```
*Regla FDM:* Para boquillas de 0.4 mm, el paso de rosca mínimo recomendado es de **1.5 mm** a **2.0 mm** para garantizar filetes limpios y resistentes. Imprime siempre las roscas con el eje vertical.

### 5. Engranajes Paramétricos (`gears.scad`)
```scad
// Módulo común para que engranen (mod = 1.5)
spur_gear(mod=1.5, teeth=20, thickness=6, shaft_diam=5, anchor=BOTTOM);
spur_gear(mod=1.5, teeth=40, thickness=6, shaft_diam=5, anchor=BOTTOM);
```
- La distancia entre centros entre dos engranajes rectos es exacta: `gear_dist(mod=1.5, teeth1=20, teeth2=40);`.

---

## 🚫 Cuándo NO usar BOSL2
1. **Perfiles copiados de un escaneo/malla con `measure.py`:** Si extrajiste una sección compleja o una curva irregular con `measure.py profile`, reprodúcela directamente como polígono en lugar de aproximarla con primitivas BOSL2.
2. **Aristas menores a 0.4 mm:** En boquillas de 0.4 mm, los redondeos menores a 0.4 mm consumen cómputo y no se aprecian en la pieza física.
