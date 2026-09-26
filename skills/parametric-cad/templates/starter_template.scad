// =====================================================================
// Plantilla Base Paramétrica — OpenSCAD para Impresión 3D FDM
// =====================================================================

// === PARÁMETROS GLOBALES (En milímetros) ===
// Modifica estos valores para adaptar las dimensiones
longitud        = 80.0;
ancho           = 50.0;
altura          = 25.0;
espesor_pared   = 2.4;  // Múltiplo de 0.4 mm (6 perímetros)
radio_esquinas  = 4.0;
chaf_base       = 0.6;  // Mitigación pie de elefante (elephant's foot)

// Tolerancias y fijaciones
dia_tornillo_m3 = 3.4;  // Holgura libre (clearance)
dia_cabeza_m3   = 6.0;

// Resolución de curvas: 32 para previsualización ágil, 96+ para exportación final
$fn = ($preview) ? 32 : 96;

// Variable de control de renderizado (CLI o GUI)
RENDER = "preview"; // Opciones: "preview", "cuerpo", "tapa"

// === MÓDULOS DEL MODELO ===

module base_redondeada(l, w, h, r) {
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=h);
        translate([l-r, r, 0]) cylinder(r=r, h=h);
        translate([r, w-r, 0]) cylinder(r=r, h=h);
        translate([l-r, w-r, 0]) cylinder(r=r, h=h);
    }
}

module cuerpo_principal() {
    difference() {
        // Cuerpo exterior
        base_redondeada(longitud, ancho, altura, radio_esquinas);

        // Vaciado interior (respetando espesor de pared y suelo)
        translate([espesor_pared, espesor_pared, espesor_pared])
            base_redondeada(
                longitud - 2 * espesor_pared,
                ancho - 2 * espesor_pared,
                altura,
                max(0.1, radio_esquinas - espesor_pared)
            );

        // Orificios de montaje en esquinas
        for (pos = [
            [radio_esquinas, radio_esquinas],
            [longitud - radio_esquinas, radio_esquinas],
            [radio_esquinas, ancho - radio_esquinas],
            [longitud - radio_esquinas, ancho - radio_esquinas]
        ]) {
            translate([pos[0], pos[1], -1])
                cylinder(d=dia_tornillo_m3, h=altura + 2);
        }
    }
}

module tapa() {
    difference() {
        base_redondeada(longitud, ancho, espesor_pared, radio_esquinas);
        
        for (pos = [
            [radio_esquinas, radio_esquinas],
            [longitud - radio_esquinas, radio_esquinas],
            [radio_esquinas, ancho - radio_esquinas],
            [longitud - radio_esquinas, ancho - radio_esquinas]
        ]) {
            translate([pos[0], pos[1], -1])
                cylinder(d=dia_tornillo_m3, h=espesor_pared + 2);
        }
    }
}

// === LÓGICA DE VISUALIZACIÓN / EXPORTACIÓN ===
if (RENDER == "preview") {
    // Vista de ensamble explosionado
    color("SteelBlue") cuerpo_principal();
    color("LightGray") translate([0, 0, altura + 15]) tapa();
} else if (RENDER == "cuerpo") {
    cuerpo_principal();
} else if (RENDER == "tapa") {
    tapa();
}
