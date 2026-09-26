# Guía Rápida de Patrones OpenSCAD para FDM

Esta referencia contiene los patrones y trucos más habituales para diseñar piezas imprimibles robustas.

---

## 1. Patrón Básico de Orificio Limpio (Evitar Z-fighting)

Nunca cortes con la misma altura o posición que la cara de la pieza. Añade siempre `0.1` o `1.0` de margen para que la resta booleana corte caras abiertas:

```openscad
// BIEN:
difference() {
    cube([20, 20, 10]);
    // El cilindro empieza en Z=-1 y mide H=12 (sobresale por arriba y abajo)
    translate([10, 10, -1]) cylinder(d=3.4, h=12);
}

// MAL (Provoca artefactos no-manifold y z-fighting):
difference() {
    cube([20, 20, 10]);
    translate([10, 10, 0]) cylinder(d=3.4, h=10);
}
```

---

## 2. Esquinas Redondeadas con `hull()`

Para cajas y soportes con esquinas redondeadas, `hull()` entre 4 cilindros es la técnica más limpia y paramétrica:

```openscad
module caja_redondeada(l, w, h, r) {
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=h);
        translate([l-r, r, 0]) cylinder(r=r, h=h);
        translate([r, w-r, 0]) cylinder(r=r, h=h);
        translate([l-r, w-r, 0]) cylinder(r=r, h=h);
    }
}
```

---

## 3. Chaflán Antideformación (Pie de Elefante)

Añadir un chaflán a 45° en la base evita que la primera capa aplastada interfiera con el encaje:

```openscad
module chaflan_base(l, w, chaf=0.6) {
    // Sustracción en cuña de 45 grados a lo largo del perímetro inferior
}
```

---

## 4. Importación y Manipulación de STLs Externos

```openscad
// 1. Importar y rotar para orientar cara de apoyo
rotate([90, 0, 0]) import("soporte.stl", convexity=5);

// 2. Extraer una sección o corte 2D de un STL
projection(cut=true) translate([0, 0, -5]) import("escaneo.stl");
```
